"""search_models — 요구사항 기반 모델 DB 검색."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.db import queries
from app.utils.mappings import BUDGET_TO_MAX_PRICE, CONTEXT_NEED_TO_MIN_LENGTH

# task_type별 관련성 높은 주요 제공사
TASK_TYPE_PROVIDERS: dict[str, list[str]] = {
    "chatbot": ["anthropic", "openai", "google", "meta-llama", "meta", "moonshotai", "z-ai", "cohere"],
    "code_generation": ["anthropic", "openai", "google", "deepseek", "meta-llama", "meta"],
    "analysis": ["anthropic", "openai", "google", "moonshotai"],
    "creative": ["anthropic", "openai", "google", "meta-llama", "meta"],
    "translation": ["anthropic", "google", "moonshotai", "cohere"],
}


async def search_models(
    db: AsyncSession,
    task_type: str,
    required_capabilities: dict[str, int],
    context_length_need: str,
    budget_range: str,
) -> list[dict]:
    """요구사항 기반 모델 DB 검색. 최신 모델 우선, 주요 제공사 필터링.

    Args:
        db: 데이터베이스 세션.
        task_type: 용도 유형 (chatbot, code_generation, analysis, creative, translation).
        required_capabilities: 필요 역량 (예: {"coding": 4, "multilingual": 3}). 현재 참고용.
        context_length_need: 필요 컨텍스트 (short/medium/long/very_long).
        budget_range: 예산 범위 (free/low/medium/high/unlimited).

    Returns:
        최신순으로 정렬된 관련 모델 목록 (최대 20개).
    """
    filters: dict = {"sort_by": "updated_at"}

    # task_type → 주요 제공사 필터
    providers = TASK_TYPE_PROVIDERS.get(task_type, [])
    if providers:
        filters["providers"] = providers

    # 컨텍스트 길이 필터
    min_context = CONTEXT_NEED_TO_MIN_LENGTH.get(context_length_need)
    if min_context:
        filters["min_context_length"] = min_context

    # 예산 필터
    if budget_range == "free":
        filters["is_free"] = True
    else:
        max_price = BUDGET_TO_MAX_PRICE.get(budget_range)
        if max_price is not None:
            filters["max_pricing_input"] = max_price

    models, _ = await queries.list_models(db, page=1, per_page=20, filters=filters)

    return [
        {
            "id": str(m.id),
            "openrouter_id": m.openrouter_id,
            "name": m.name,
            "provider": m.provider,
            "pricing_input": str(m.pricing_input) if m.pricing_input else "0",
            "pricing_output": str(m.pricing_output) if m.pricing_output else "0",
            "context_length": m.context_length,
            "is_free": m.is_free,
        }
        for m in models
    ]
