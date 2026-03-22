import uuid
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.db import queries

BUDGET_TO_MAX_PRICE: dict[str, Decimal | None] = {
    "free": Decimal("0"),
    "low": Decimal("0.001"),
    "medium": Decimal("0.01"),
    "high": Decimal("0.1"),
    "unlimited": None,
}

CONTEXT_NEED_TO_MIN_LENGTH: dict[str, int] = {
    "short": 4096,
    "medium": 32000,
    "long": 128000,
    "very_long": 200000,
}


async def assess_model_fit(
    db: AsyncSession,
    model_id: str,
    user_requirements: dict,
) -> dict:
    """특정 모델이 사용자 용도에 얼마나 적합한지 평가.

    Args:
        db: 데이터베이스 세션.
        model_id: 평가 대상 모델 UUID.
        user_requirements: 구조화된 요구사항. 예: {"capabilities": {"coding": 4}, "budget_range": "medium", "context_length_need": "long"}.

    Returns:
        fit_score (0-100), strengths 목록, weaknesses 목록.
    """
    model = await queries.get_model_with_details(db, uuid.UUID(model_id))
    if not model:
        return {"fit_score": 0, "strengths": [], "weaknesses": ["모델을 찾을 수 없습니다"]}

    capabilities = user_requirements.get("capabilities", {})
    budget = user_requirements.get("budget_range", "unlimited")
    ctx_need = user_requirements.get("context_length_need", "medium")

    strengths: list[str] = []
    weaknesses: list[str] = []

    # Tag matching score (0-50)
    tag_map = {t.category: t.strength_level for t in model.tags}
    tag_score = _calc_tag_score(capabilities, tag_map, strengths, weaknesses)

    # Price fit score (0-25)
    price_score = _calc_price_score(model, budget, strengths, weaknesses)

    # Context length fit score (0-25)
    ctx_score = _calc_context_score(model, ctx_need, strengths, weaknesses)

    fit_score = min(100, tag_score + price_score + ctx_score)

    return {"fit_score": fit_score, "strengths": strengths, "weaknesses": weaknesses}


def _calc_tag_score(
    capabilities: dict, tag_map: dict, strengths: list, weaknesses: list
) -> int:
    if not capabilities:
        return 25
    total, matched = 0, 0
    for cap, importance in capabilities.items():
        total += importance
        level = tag_map.get(cap, 0)
        matched += min(level, importance)
        if level >= importance:
            strengths.append(f"{cap} 역량 우수 (수준 {level}/5)")
        elif level > 0:
            weaknesses.append(f"{cap} 역량 부족 ({level}/5, 요구 {importance}/5)")
        else:
            weaknesses.append(f"{cap} 역량 데이터 없음")
    return int((matched / max(total, 1)) * 50)


def _calc_price_score(
    model: object, budget: str, strengths: list, weaknesses: list
) -> int:
    max_price = BUDGET_TO_MAX_PRICE.get(budget)
    price = getattr(model, "pricing_input", None) or Decimal("0")
    if getattr(model, "is_free", False):
        strengths.append("무료 모델")
        return 25
    if max_price is None:
        return 20
    if price <= max_price:
        strengths.append(f"예산 범위 내 (${price}/token)")
        return 25
    weaknesses.append(f"예산 초과 (${price}/token, 한도 ${max_price})")
    return 5


def _calc_context_score(
    model: object, ctx_need: str, strengths: list, weaknesses: list
) -> int:
    min_ctx = CONTEXT_NEED_TO_MIN_LENGTH.get(ctx_need, 32000)
    ctx_len = getattr(model, "context_length", None) or 0
    if ctx_len >= min_ctx:
        strengths.append(f"컨텍스트 길이 충분 ({ctx_len:,} tokens)")
        return 25
    if ctx_len > 0:
        weaknesses.append(f"컨텍스트 길이 부족 ({ctx_len:,}, 필요 {min_ctx:,})")
        return int((ctx_len / min_ctx) * 25)
    weaknesses.append("컨텍스트 길이 정보 없음")
    return 10
