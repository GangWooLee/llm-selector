import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.db import queries


async def get_model_details(
    db: AsyncSession,
    model_id: str,
) -> dict | None:
    """특정 모델의 전체 상세 정보 조회 (가격, 성능, 특성, 벤치마크, 태그).

    Args:
        db: 데이터베이스 세션.
        model_id: 대상 모델 UUID 또는 openrouter_id (둘 다 지원).

    Returns:
        모델 전체 프로필. 모델이 없으면 None.
    """
    try:
        model_uuid = uuid.UUID(model_id)
    except ValueError:
        model_obj = await queries.get_model_by_openrouter_id(db, model_id)
        if not model_obj:
            return None
        model_uuid = model_obj.id

    model = await queries.get_model_with_details(db, model_uuid)
    if not model:
        return None

    return {
        "id": str(model.id),
        "openrouter_id": model.openrouter_id,
        "name": model.name,
        "provider": model.provider,
        "description": model.description,
        "context_length": model.context_length,
        "max_completion_tokens": model.max_completion_tokens,
        "pricing_input": str(model.pricing_input) if model.pricing_input else "0",
        "pricing_output": str(model.pricing_output) if model.pricing_output else "0",
        "modalities": model.modalities,
        "supported_parameters": model.supported_parameters,
        "architecture": model.architecture,
        "is_free": model.is_free,
        "benchmarks": [
            {
                "benchmark_name": b.benchmark_name,
                "score": str(b.score),
                "max_score": str(b.max_score) if b.max_score else None,
            }
            for b in model.benchmarks
        ],
        "tags": [
            {"category": t.category, "strength_level": t.strength_level}
            for t in model.tags
        ],
    }
