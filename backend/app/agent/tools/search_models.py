from sqlalchemy.ext.asyncio import AsyncSession

from app.db import queries
from app.utils.mappings import BUDGET_TO_MAX_PRICE, CONTEXT_NEED_TO_MIN_LENGTH


async def search_models(
    db: AsyncSession,
    task_type: str,
    required_capabilities: dict[str, int],
    context_length_need: str,
    budget_range: str,
) -> list[dict]:
    """요구사항 기반 모델 DB 검색.

    Args:
        db: 데이터베이스 세션.
        task_type: 용도 유형 (chatbot, code_generation, analysis, creative, translation 등).
        required_capabilities: 필요 역량과 중요도 (예: {"coding": 4, "multilingual": 3}). 값은 0-5.
        context_length_need: 필요 컨텍스트 길이 (short/medium/long/very_long).
        budget_range: 예산 범위 (free/low/medium/high/unlimited).

    Returns:
        조건에 맞는 모델 목록 (ID, 이름, 제공사, 가격, 컨텍스트 길이, 지원 기능).
    """
    filters: dict = {}

    min_context = CONTEXT_NEED_TO_MIN_LENGTH.get(context_length_need)
    if min_context:
        filters["min_context_length"] = min_context

    if budget_range == "free":
        filters["is_free"] = True
    else:
        max_price = BUDGET_TO_MAX_PRICE.get(budget_range)
        if max_price is not None:
            filters["max_pricing_input"] = max_price

    models, _ = await queries.list_models(db, page=1, per_page=50, filters=filters)

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
