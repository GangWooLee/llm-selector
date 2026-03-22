"""search_models — 요구사항 기반 모델 DB 검색."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.db import queries
from app.utils.mappings import BUDGET_TO_MAX_PRICE, CONTEXT_NEED_TO_MIN_LENGTH

# task_type별 관련성 높은 주요 제공사
TASK_TYPE_PROVIDERS: dict[str, list[str]] = {
    "chatbot": ["anthropic", "openai", "google", "moonshotai", "z-ai", "qwen", "deepseek", "meta-llama", "meta", "minimax", "cohere"],
    "code_generation": ["anthropic", "openai", "google", "deepseek", "qwen", "z-ai", "moonshotai", "meta-llama", "meta"],
    "analysis": ["anthropic", "openai", "google", "moonshotai", "qwen", "deepseek", "z-ai"],
    "creative": ["anthropic", "openai", "google", "qwen", "moonshotai", "meta-llama", "meta"],
    "translation": ["anthropic", "google", "moonshotai", "qwen", "deepseek", "cohere"],
}


def _search_from_cache(
    models_cache: list[dict],
    task_type: str,
    context_length_need: str,
    budget_range: str,
) -> list[dict]:
    """models_cache에서 필터링하여 검색 결과 반환 (No-DB 모드)."""
    providers = TASK_TYPE_PROVIDERS.get(task_type, [])
    min_context = CONTEXT_NEED_TO_MIN_LENGTH.get(context_length_need)

    results = []
    for m in models_cache:
        # 유효 데이터 필터: is_free와 pricing_input 둘 다 없으면 제외
        if m.get("is_free") is None and m.get("pricing_input") is None:
            continue

        # provider 필터
        if providers and m.get("provider") not in providers:
            continue

        # context_length 필터
        if min_context and (m.get("context_length") or 0) < min_context:
            continue

        # 예산 필터
        if budget_range == "free":
            if not m.get("is_free"):
                continue
        else:
            max_price = BUDGET_TO_MAX_PRICE.get(budget_range)
            if max_price is not None:
                price = m.get("pricing_input")
                if price is not None and Decimal(str(price)) > max_price:
                    continue

        results.append(m)

    # 이름순 정렬 (캐시에는 updated_at 없음)
    results.sort(key=lambda x: x.get("name", ""))

    return [
        {
            "id": m["openrouter_id"],
            "openrouter_id": m["openrouter_id"],
            "name": m.get("name", ""),
            "provider": m.get("provider", ""),
            "pricing_input": str(m["pricing_input"]) if m.get("pricing_input") else "0",
            "pricing_output": str(m["pricing_output"]) if m.get("pricing_output") else "0",
            "context_length": m.get("context_length"),
            "is_free": m.get("is_free"),
        }
        for m in results[:20]
    ]


async def search_models(
    db: AsyncSession | None,
    models_cache: list[dict] | None,
    task_type: str,
    required_capabilities: dict[str, int],
    context_length_need: str,
    budget_range: str,
) -> list[dict]:
    """요구사항 기반 모델 DB 검색. 최신 모델 우선, 주요 제공사 필터링.

    Args:
        db: 데이터베이스 세션. None이면 No-DB 모드.
        models_cache: OpenRouter API 캐시 데이터. No-DB 모드에서 사용.
        task_type: 용도 유형 (chatbot, code_generation, analysis, creative, translation).
        required_capabilities: 필요 역량 (예: {"coding": 4, "multilingual": 3}). 현재 참고용.
        context_length_need: 필요 컨텍스트 (short/medium/long/very_long).
        budget_range: 예산 범위 (free/low/medium/high/unlimited).

    Returns:
        최신순으로 정렬된 관련 모델 목록 (최대 20개).
    """
    if db is None:
        return _search_from_cache(
            models_cache or [], task_type, context_length_need, budget_range,
        )

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
