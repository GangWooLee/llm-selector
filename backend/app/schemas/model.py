import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class BenchmarkResponse(BaseModel):
    benchmark_name: str
    score: Decimal
    max_score: Decimal | None = None
    source_url: str | None = None

    model_config = {"from_attributes": True}


class TagResponse(BaseModel):
    category: str
    strength_level: int

    model_config = {"from_attributes": True}


class ModelSummary(BaseModel):
    id: uuid.UUID
    openrouter_id: str
    name: str
    provider: str
    context_length: int | None = None
    pricing_input: Decimal | None = None
    pricing_output: Decimal | None = None
    is_free: bool
    modalities: dict | list | None = None
    supported_parameters: list | None = None

    model_config = {"from_attributes": True}


class ModelDetailResponse(BaseModel):
    id: uuid.UUID
    openrouter_id: str
    name: str
    provider: str
    description: str | None = None
    context_length: int | None = None
    pricing_input: Decimal | None = None
    pricing_output: Decimal | None = None
    modalities: dict | list | None = None
    supported_parameters: list | None = None
    max_completion_tokens: int | None = None
    architecture: dict | None = None
    benchmarks: list[BenchmarkResponse] = []
    tags: list[TagResponse] = []
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class PaginationInfo(BaseModel):
    page: int
    per_page: int
    total: int
    total_pages: int


class ModelListResponse(BaseModel):
    data: list[ModelSummary]
    pagination: PaginationInfo


class ModelFilterParams(BaseModel):
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)
    provider: str | None = None
    min_context: int | None = None
    max_price_input: float | None = None
    has_tools: bool | None = None
    has_vision: bool | None = None
    is_free: bool | None = None
    search: str | None = None
    sort_by: str | None = None
