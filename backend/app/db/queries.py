import uuid
from decimal import Decimal
from typing import Any

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import Model, ModelBenchmark, ModelTag

SORT_OPTIONS = {
    "updated_at": Model.updated_at.desc(),
    "price_asc": Model.pricing_input.asc(),
    "price_desc": Model.pricing_input.desc(),
    "context_length": Model.context_length.desc(),
    "name": Model.name.asc(),
}


async def list_models(
    db: AsyncSession,
    page: int = 1,
    per_page: int = 20,
    filters: dict[str, Any] | None = None,
) -> tuple[list[Model], int]:
    """페이징+필터+정렬로 모델 목록 조회. (models, total_count) 반환."""
    query = select(Model).where(Model.is_active.is_(True))
    count_query = select(func.count(Model.id)).where(Model.is_active.is_(True))

    if filters:
        query = _apply_filters(query, filters)
        count_query = _apply_filters(count_query, filters)

    total = (await db.execute(count_query)).scalar_one()

    sort_key = filters.get("sort_by", "name") if filters else "name"
    order_clause = SORT_OPTIONS.get(sort_key, Model.name.asc())
    query = query.order_by(order_clause)

    offset = (page - 1) * per_page
    query = query.offset(offset).limit(per_page)
    result = await db.execute(query)
    return list(result.scalars().all()), total


def _apply_filters(query: Any, filters: dict[str, Any]) -> Any:
    # 단일 제공사
    if provider := filters.get("provider"):
        query = query.where(Model.provider == provider)

    # 복수 제공사 (IN)
    if providers := filters.get("providers"):
        query = query.where(Model.provider.in_(providers))

    # 컨텍스트 길이
    if min_context := filters.get("min_context_length"):
        query = query.where(Model.context_length >= min_context)

    # 가격 상한
    if max_price := filters.get("max_pricing_input"):
        query = query.where(Model.pricing_input <= Decimal(str(max_price)))

    # 무료 모델만
    if filters.get("is_free") is True:
        query = query.where(Model.is_free.is_(True))

    # 텍스트 검색 (이름 또는 설명)
    if search := filters.get("search"):
        pattern = f"%{search}%"
        query = query.where(
            Model.name.ilike(pattern) | Model.description.ilike(pattern)
        )

    return query


async def get_model_with_details(
    db: AsyncSession, model_id: uuid.UUID
) -> Model | None:
    """benchmarks + tags를 selectinload로 함께 조회."""
    query = (
        select(Model)
        .where(Model.id == model_id)
        .options(selectinload(Model.benchmarks), selectinload(Model.tags))
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_model_by_openrouter_id(
    db: AsyncSession, openrouter_id: str
) -> Model | None:
    """openrouter_id로 모델 조회."""
    query = select(Model).where(
        Model.openrouter_id == openrouter_id, Model.is_active.is_(True)
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def upsert_model(db: AsyncSession, model_data: dict[str, Any]) -> Model:
    """openrouter_id 기준 INSERT or UPDATE."""
    openrouter_id = model_data["openrouter_id"]
    query = select(Model).where(Model.openrouter_id == openrouter_id)
    result = await db.execute(query)
    existing = result.scalar_one_or_none()

    if existing:
        for key, value in model_data.items():
            if key != "openrouter_id":
                setattr(existing, key, value)
        await db.flush()
        return existing

    model = Model(**model_data)
    db.add(model)
    await db.flush()
    return model


async def deactivate_missing_models(
    db: AsyncSession, active_ids: list[str]
) -> int:
    """API에 없는 모델을 is_active=false로 변경."""
    stmt = (
        update(Model)
        .where(Model.openrouter_id.notin_(active_ids), Model.is_active.is_(True))
        .values(is_active=False)
    )
    result = await db.execute(stmt)
    await db.flush()
    return result.rowcount  # type: ignore[return-value]


async def get_model_pricing(
    db: AsyncSession, model_ids: list[uuid.UUID]
) -> list[Model]:
    """모델 ID 목록에 대한 가격 데이터 조회."""
    query = select(Model).where(Model.id.in_(model_ids))
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_models_by_openrouter_ids(
    db: AsyncSession, openrouter_ids: list[str]
) -> list[Model]:
    """openrouter_id 목록으로 모델 조회."""
    query = select(Model).where(
        Model.openrouter_id.in_(openrouter_ids), Model.is_active.is_(True)
    )
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_model_benchmarks(
    db: AsyncSession,
    model_ids: list[uuid.UUID],
    categories: list[str] | None = None,
) -> list[ModelBenchmark]:
    """모델 ID 목록에 대한 벤치마크 데이터 조회."""
    query = select(ModelBenchmark).where(
        ModelBenchmark.model_id.in_(model_ids)
    )
    if categories:
        query = query.where(ModelBenchmark.benchmark_name.in_(categories))
    result = await db.execute(query)
    return list(result.scalars().all())
