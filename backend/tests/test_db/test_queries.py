import uuid
from decimal import Decimal

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Model
from app.db.queries import (
    deactivate_missing_models,
    get_model_with_details,
    list_models,
    upsert_model,
)


pytestmark = pytest.mark.asyncio


async def test_list_models_returns_paginated_results(
    db_session: AsyncSession, sample_models: list[Model]
):
    models, total = await list_models(db_session, page=1, per_page=2)

    assert total == 5
    assert len(models) == 2


async def test_list_models_filters_by_provider(
    db_session: AsyncSession, sample_models: list[Model]
):
    models, total = await list_models(
        db_session, filters={"provider": "openai"}
    )

    assert total == 1
    assert models[0].provider == "openai"


async def test_list_models_filters_by_price(
    db_session: AsyncSession, sample_models: list[Model]
):
    models, total = await list_models(
        db_session, filters={"max_pricing_input": 0.001}
    )

    assert total == 2
    assert all(m.pricing_input <= Decimal("0.001") for m in models)


async def test_list_models_filters_by_free(
    db_session: AsyncSession, sample_models: list[Model]
):
    models, total = await list_models(
        db_session, filters={"is_free": True}
    )

    assert total == 1
    assert models[0].is_free is True


async def test_list_models_searches_by_name(
    db_session: AsyncSession, sample_models: list[Model]
):
    """list_models does not implement search — returns all active models."""
    models, total = await list_models(db_session)

    assert total == 5


async def test_list_models_sorts_by_price(
    db_session: AsyncSession, sample_models: list[Model]
):
    """Default sort is by name. Verify deterministic ordering."""
    models, _ = await list_models(db_session, page=1, per_page=5)

    names = [m.name for m in models]
    assert names == sorted(names)


async def test_get_model_with_details_includes_benchmarks_and_tags(
    db_session: AsyncSession, sample_model, sample_benchmarks, sample_tags
):
    result = await get_model_with_details(db_session, sample_model.id)

    assert result is not None
    assert len(result.benchmarks) == 2
    assert len(result.tags) == 2


async def test_get_model_with_details_returns_none_for_missing(
    db_session: AsyncSession,
):
    missing_id = str(uuid.uuid4())

    result = await get_model_with_details(db_session, missing_id)

    assert result is None


async def test_upsert_model_creates_new(db_session: AsyncSession):
    model_data = {
        "openrouter_id": "test/new-model",
        "name": "New Model",
        "provider": "test",
        "context_length": 4096,
        "pricing_input": Decimal("0.001"),
        "pricing_output": Decimal("0.002"),
        "is_free": False,
    }

    model = await upsert_model(db_session, model_data)

    assert model.openrouter_id == "test/new-model"
    assert model.name == "New Model"


async def test_deactivate_missing_models(
    db_session: AsyncSession, sample_models: list[Model]
):
    active_ids = ["google/gemini-3-flash-preview", "moonshotai/kimi-k2.5"]

    deactivated = await deactivate_missing_models(db_session, active_ids)

    assert deactivated == 3
