import uuid
from decimal import Decimal
from types import SimpleNamespace

from sqlalchemy.ext.asyncio import AsyncSession

from app.db import queries
from app.utils.mappings import BUDGET_TO_MAX_PRICE, CONTEXT_NEED_TO_MIN_LENGTH

_NOT_FOUND = {"fit_score": 0, "strengths": [], "weaknesses": ["모델을 찾을 수 없습니다"]}


async def assess_model_fit(
    db: AsyncSession | None,
    models_cache: list[dict] | None,
    model_id: str,
    user_requirements: dict,
) -> dict:
    """특정 모델이 사용자 용도에 얼마나 적합한지 평가.

    Args:
        db: 데이터베이스 세션. None이면 No-DB 모드.
        models_cache: No-DB 모드에서 사용할 모델 캐시 (OpenRouter API 데이터).
        model_id: 평가 대상 모델 UUID 또는 openrouter_id (둘 다 지원).
        user_requirements: 구조화된 요구사항. 예: {"capabilities": {"coding": 4}, "budget_range": "medium", "context_length_need": "long"}.

    Returns:
        fit_score (0-100), strengths 목록, weaknesses 목록.
    """
    # No-DB 모드: 캐시에서 모델 조회
    if db is None:
        return _assess_from_cache(model_id, user_requirements, models_cache or [])

    try:
        model_uuid = uuid.UUID(model_id)
    except ValueError:
        model_obj = await queries.get_model_by_openrouter_id(db, model_id)
        if not model_obj:
            return {**_NOT_FOUND}
        model_uuid = model_obj.id

    model = await queries.get_model_with_details(db, model_uuid)
    if not model:
        return {**_NOT_FOUND}

    capabilities = user_requirements.get("capabilities", {})
    budget = user_requirements.get("budget_range", "unlimited")
    ctx_need = user_requirements.get("context_length_need", "medium")

    strengths: list[str] = []
    weaknesses: list[str] = []

    tag_map = {t.category: t.strength_level for t in model.tags}
    has_tags = bool(tag_map and capabilities)

    if has_tags:
        # 태그 있을 때: 태그 50 + 가격 25 + 컨텍스트 25 = 100
        tag_score = _calc_tag_score(capabilities, tag_map, strengths, weaknesses, max_score=50)
        price_score = _calc_price_score(model, budget, strengths, weaknesses, max_score=25)
        ctx_score = _calc_context_score(model, ctx_need, strengths, weaknesses, max_score=25)
    else:
        # 태그 없을 때: 가격 50 + 컨텍스트 50 = 100
        tag_score = 0
        price_score = _calc_price_score(model, budget, strengths, weaknesses, max_score=50)
        ctx_score = _calc_context_score(model, ctx_need, strengths, weaknesses, max_score=50)

    fit_score = min(100, tag_score + price_score + ctx_score)

    return {"fit_score": fit_score, "strengths": strengths, "weaknesses": weaknesses}


def _calc_tag_score(
    capabilities: dict,
    tag_map: dict,
    strengths: list,
    weaknesses: list,
    *,
    max_score: int = 50,
) -> int:
    if not capabilities:
        return max_score // 2
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
    return int((matched / max(total, 1)) * max_score)


def _calc_price_score(
    model: object,
    budget: str,
    strengths: list,
    weaknesses: list,
    *,
    max_score: int = 25,
) -> int:
    max_price = BUDGET_TO_MAX_PRICE.get(budget)
    price = getattr(model, "pricing_input", None) or Decimal("0")
    if getattr(model, "is_free", False):
        strengths.append("무료 모델")
        return max_score
    if max_price is None:
        return int(max_score * 0.8)
    if price <= max_price:
        strengths.append(f"예산 범위 내 (${price}/token)")
        return max_score
    weaknesses.append(f"예산 초과 (${price}/token, 한도 ${max_price})")
    return int(max_score * 0.2)


def _calc_context_score(
    model: object,
    ctx_need: str,
    strengths: list,
    weaknesses: list,
    *,
    max_score: int = 25,
) -> int:
    min_ctx = CONTEXT_NEED_TO_MIN_LENGTH.get(ctx_need, 32000)
    ctx_len = getattr(model, "context_length", None) or 0
    if ctx_len >= min_ctx:
        strengths.append(f"컨텍스트 길이 충분 ({ctx_len:,} tokens)")
        return max_score
    if ctx_len > 0:
        weaknesses.append(f"컨텍스트 길이 부족 ({ctx_len:,}, 필요 {min_ctx:,})")
        return int((ctx_len / min_ctx) * max_score)
    weaknesses.append("컨텍스트 길이 정보 없음")
    return int(max_score * 0.4)


def _assess_from_cache(
    model_id: str,
    user_requirements: dict,
    cache: list[dict],
) -> dict:
    """No-DB 모드: models_cache에서 모델을 찾아 적합도 평가."""
    cached = next((m for m in cache if m["openrouter_id"] == model_id), None)
    if not cached:
        return {**_NOT_FOUND}

    model = SimpleNamespace(**cached)
    budget = user_requirements.get("budget_range", "unlimited")
    ctx_need = user_requirements.get("context_length_need", "medium")

    strengths: list[str] = []
    weaknesses: list[str] = []

    # No-DB 모드에서는 태그 없음 → 가격 50 + 컨텍스트 50 = 100
    price_score = _calc_price_score(model, budget, strengths, weaknesses, max_score=50)
    ctx_score = _calc_context_score(model, ctx_need, strengths, weaknesses, max_score=50)
    fit_score = min(100, price_score + ctx_score)

    return {"fit_score": fit_score, "strengths": strengths, "weaknesses": weaknesses}
