import uuid
from collections import defaultdict

from sqlalchemy.ext.asyncio import AsyncSession

from app.db import queries


async def get_benchmarks(
    db: AsyncSession,
    model_ids: list[str],
    benchmark_categories: list[str] | None = None,
) -> dict[str, list[dict]]:
    """특정 모델들의 벤치마크 데이터 조회.

    Args:
        db: 데이터베이스 세션.
        model_ids: 모델 UUID 또는 openrouter_id 목록 (둘 다 지원).
        benchmark_categories: 필터링할 벤치마크 카테고리 (coding, reasoning, multilingual, math, creative 등). None이면 전체.

    Returns:
        모델 ID별 벤치마크 점수 목록.
    """
    uuid_ids = []
    openrouter_ids = []
    for mid in model_ids:
        try:
            uuid_ids.append(uuid.UUID(mid))
        except ValueError:
            openrouter_ids.append(mid)

    if openrouter_ids:
        models = await queries.get_models_by_openrouter_ids(db, openrouter_ids)
        uuid_ids.extend([m.id for m in models])

    if not uuid_ids:
        return {}

    benchmarks = await queries.get_model_benchmarks(
        db, uuid_ids, categories=benchmark_categories
    )

    grouped: dict[str, list[dict]] = defaultdict(list)
    for b in benchmarks:
        grouped[str(b.model_id)].append({
            "benchmark_name": b.benchmark_name,
            "score": str(b.score),
            "max_score": str(b.max_score) if b.max_score else None,
            "source_url": b.source_url,
            "measured_at": b.measured_at.isoformat() if b.measured_at else None,
        })

    return dict(grouped)
