import math
import uuid
from decimal import Decimal
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import get_db
from app.db import queries
from app.schemas.model import (
    ModelDetailResponse,
    ModelListResponse,
    ModelSummary,
    PaginationInfo,
)
from app.services.openrouter import fetch_all_models

router = APIRouter(prefix="/api/v1/models", tags=["models"])


@router.get("", response_model=ModelListResponse)
async def list_models(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    provider: str | None = Query(default=None),
    min_context: int | None = Query(default=None),
    max_price_input: float | None = Query(default=None),
    is_free: bool | None = Query(default=None),
    search: str | None = Query(default=None, max_length=500),
    sort_by: str | None = Query(default=None),
    db: Any = Depends(get_db),
) -> ModelListResponse:
    # No-DB 모드: OpenRouter API에서 직접 조회
    if db is None:
        return await _list_models_from_cache(
            page=page,
            per_page=per_page,
            provider=provider,
            min_context=min_context,
            max_price_input=max_price_input,
            is_free=is_free,
        )

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
    model_id: str,
    db: Any = Depends(get_db),
) -> ModelDetailResponse:
    # No-DB 모드: OpenRouter API에서 직접 조회
    if db is None:
        return await _get_model_detail_from_cache(model_id)

    # DB 모드: UUID로 변환하여 조회
    try:
        parsed_id = uuid.UUID(model_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid model ID format")

    model = await queries.get_model_with_details(db, parsed_id)
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


def _apply_filters(
    models: list[dict],
    provider: str | None,
    min_context: int | None,
    max_price_input: float | None,
    is_free: bool | None,
) -> list[dict]:
    """No-DB 모드에서 인메모리 필터링."""
    result = models
    if provider:
        result = [m for m in result if m.get("provider") == provider]
    if min_context is not None:
        result = [m for m in result if (m.get("context_length") or 0) >= min_context]
    if max_price_input is not None:
        limit = Decimal(str(max_price_input))
        result = [
            m for m in result
            if m.get("pricing_input") is not None and m["pricing_input"] <= limit
        ]
    if is_free is not None:
        result = [m for m in result if m.get("is_free") == is_free]
    return result


def _cache_to_summary(m: dict) -> ModelSummary:
    """캐시 dict를 ModelSummary로 변환. DB 없으므로 UUID 생성."""
    return ModelSummary(
        id=uuid.uuid5(uuid.NAMESPACE_URL, m["openrouter_id"]),
        openrouter_id=m["openrouter_id"],
        name=m["name"],
        provider=m["provider"],
        context_length=m.get("context_length"),
        pricing_input=m.get("pricing_input"),
        pricing_output=m.get("pricing_output"),
        is_free=m.get("is_free", False),
        modalities=m.get("modalities"),
        supported_parameters=m.get("supported_parameters"),
    )


def _cache_to_detail(m: dict) -> ModelDetailResponse:
    """캐시 dict를 ModelDetailResponse로 변환."""
    return ModelDetailResponse(
        id=uuid.uuid5(uuid.NAMESPACE_URL, m["openrouter_id"]),
        openrouter_id=m["openrouter_id"],
        name=m["name"],
        provider=m["provider"],
        description=m.get("description"),
        context_length=m.get("context_length"),
        pricing_input=m.get("pricing_input"),
        pricing_output=m.get("pricing_output"),
        modalities=m.get("modalities"),
        supported_parameters=m.get("supported_parameters"),
        max_completion_tokens=m.get("max_completion_tokens"),
        architecture=m.get("architecture"),
        benchmarks=[],
        tags=[],
        updated_at=None,
    )


async def _list_models_from_cache(
    page: int,
    per_page: int,
    provider: str | None,
    min_context: int | None,
    max_price_input: float | None,
    is_free: bool | None,
) -> ModelListResponse:
    """No-DB 모드: OpenRouter API 데이터로 목록 응답 구성."""
    all_models = await fetch_all_models()
    filtered = _apply_filters(all_models, provider, min_context, max_price_input, is_free)
    total = len(filtered)
    total_pages = math.ceil(total / per_page) if total > 0 else 0

    start = (page - 1) * per_page
    end = start + per_page
    page_models = filtered[start:end]

    return ModelListResponse(
        data=[_cache_to_summary(m) for m in page_models],
        pagination=PaginationInfo(
            page=page,
            per_page=per_page,
            total=total,
            total_pages=total_pages,
        ),
    )


async def _get_model_detail_from_cache(model_id: str) -> ModelDetailResponse:
    """No-DB 모드: openrouter_id로 모델 상세 조회."""
    all_models = await fetch_all_models()
    cached = next((m for m in all_models if m["openrouter_id"] == model_id), None)
    if not cached:
        raise HTTPException(status_code=404, detail="Model not found")
    return _cache_to_detail(cached)
