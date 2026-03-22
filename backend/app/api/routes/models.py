import math
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.db import queries
from app.schemas.model import (
    ModelDetailResponse,
    ModelListResponse,
    ModelSummary,
    PaginationInfo,
)

router = APIRouter(prefix="/api/v1/models", tags=["models"])


@router.get("", response_model=ModelListResponse)
async def list_models(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    provider: str | None = Query(default=None),
    min_context: int | None = Query(default=None),
    max_price_input: float | None = Query(default=None),
    is_free: bool | None = Query(default=None),
    search: str | None = Query(default=None),
    sort_by: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> ModelListResponse:
    filters = _build_filters(
        provider=provider,
        min_context=min_context,
        max_price_input=max_price_input,
        is_free=is_free,
    )
    models, total = await queries.list_models(
        db, page=page, per_page=per_page, filters=filters
    )
    total_pages = math.ceil(total / per_page) if total > 0 else 0
    return ModelListResponse(
        data=[ModelSummary.model_validate(m) for m in models],
        pagination=PaginationInfo(
            page=page,
            per_page=per_page,
            total=total,
            total_pages=total_pages,
        ),
    )


@router.get("/{model_id}", response_model=ModelDetailResponse)
async def get_model_detail(
    model_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> ModelDetailResponse:
    model = await queries.get_model_with_details(db, model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    return ModelDetailResponse.model_validate(model)


def _build_filters(
    provider: str | None,
    min_context: int | None,
    max_price_input: float | None,
    is_free: bool | None,
) -> dict | None:
    filters: dict = {}
    if provider:
        filters["provider"] = provider
    if min_context is not None:
        filters["min_context_length"] = min_context
    if max_price_input is not None:
        filters["max_pricing_input"] = max_price_input
    if is_free is not None:
        filters["is_free"] = is_free
    return filters or None
