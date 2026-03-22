import sqlite3
import uuid
from collections.abc import AsyncGenerator
from decimal import Decimal

import pytest
import pytest_asyncio
from sqlalchemy import String, event
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.types import JSON

from app.db.models import Base, Model, ModelBenchmark, ModelTag

# Register UUID adapter for sqlite3 so native uuid.UUID objects are auto-converted
sqlite3.register_adapter(uuid.UUID, lambda u: str(u))


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


_metadata_adapted = False


def _adapt_metadata_for_sqlite():
    """Replace PostgreSQL-specific column types with SQLite-compatible ones.
    Only runs once since metadata is global.
    """
    global _metadata_adapted
    if _metadata_adapted:
        return
    _metadata_adapted = True

    for table in Base.metadata.tables.values():
        for column in table.columns:
            if isinstance(column.type, JSONB):
                column.type = JSON()
            elif isinstance(column.type, PG_UUID):
                column.type = String(36)

        # Remove CheckConstraints (BETWEEN syntax issues in SQLite)
        table.constraints = {
            c for c in table.constraints if not hasattr(c, "sqltext")
        }


def _uuid() -> str:
    """Generate a UUID string compatible with SQLite String(36) column."""
    return str(uuid.uuid4())


@pytest_asyncio.fixture
async def engine():
    _adapt_metadata_for_sqlite()

    eng = create_async_engine("sqlite+aiosqlite://", echo=False)

    @event.listens_for(eng.sync_engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await eng.dispose()


@pytest_asyncio.fixture
async def db_session(engine) -> AsyncGenerator[AsyncSession, None]:
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def sample_model(db_session: AsyncSession) -> Model:
    model = Model(
        id=_uuid(),
        openrouter_id="google/gemini-3-flash-preview",
        name="Gemini 3 Flash",
        provider="openai",
        description="Latest Gemini 3 Flash model",
        context_length=128000,
        pricing_input=Decimal("0.0025"),
        pricing_output=Decimal("0.01"),
        is_free=False,
        is_active=True,
    )
    db_session.add(model)
    await db_session.flush()
    return model


@pytest_asyncio.fixture
async def sample_models(db_session: AsyncSession) -> list[Model]:
    models_data = [
        Model(
            id=_uuid(),
            openrouter_id="google/gemini-3-flash-preview",
            name="Gemini 3 Flash",
            provider="openai",
            context_length=128000,
            pricing_input=Decimal("0.0025"),
            pricing_output=Decimal("0.01"),
            is_free=False,
            is_active=True,
        ),
        Model(
            id=_uuid(),
            openrouter_id="moonshotai/kimi-k2.5",
            name="Kimi K2.5",
            provider="anthropic",
            context_length=200000,
            pricing_input=Decimal("0.003"),
            pricing_output=Decimal("0.015"),
            is_free=False,
            is_active=True,
        ),
        Model(
            id=_uuid(),
            openrouter_id="z-ai/glm-5-turbo",
            name="GLM 5 Turbo",
            provider="google",
            context_length=1000000,
            pricing_input=Decimal("0.0001"),
            pricing_output=Decimal("0.0004"),
            is_free=False,
            is_active=True,
        ),
        Model(
            id=_uuid(),
            openrouter_id="meta/llama-3.1-8b:free",
            name="Llama 3.1 8B (Free)",
            provider="meta",
            context_length=131072,
            pricing_input=Decimal("0"),
            pricing_output=Decimal("0"),
            is_free=True,
            is_active=True,
        ),
        Model(
            id=_uuid(),
            openrouter_id="mistral/mistral-large",
            name="Mistral Large",
            provider="mistral",
            context_length=128000,
            pricing_input=Decimal("0.002"),
            pricing_output=Decimal("0.006"),
            is_free=False,
            is_active=True,
        ),
    ]
    for m in models_data:
        db_session.add(m)
    await db_session.flush()
    return models_data


@pytest_asyncio.fixture
async def sample_benchmarks(
    db_session: AsyncSession, sample_model: Model
) -> list[ModelBenchmark]:
    benchmarks = [
        ModelBenchmark(
            id=_uuid(),
            model_id=sample_model.id,
            benchmark_name="MMLU",
            score=Decimal("88.7"),
            max_score=Decimal("100.0"),
        ),
        ModelBenchmark(
            id=_uuid(),
            model_id=sample_model.id,
            benchmark_name="HumanEval",
            score=Decimal("90.2"),
            max_score=Decimal("100.0"),
        ),
    ]
    for b in benchmarks:
        db_session.add(b)
    await db_session.flush()
    return benchmarks


@pytest_asyncio.fixture
async def sample_tags(
    db_session: AsyncSession, sample_model: Model
) -> list[ModelTag]:
    tags = [
        ModelTag(
            id=_uuid(),
            model_id=sample_model.id,
            category="coding",
            strength_level=4,
        ),
        ModelTag(
            id=_uuid(),
            model_id=sample_model.id,
            category="reasoning",
            strength_level=5,
        ),
    ]
    for t in tags:
        db_session.add(t)
    await db_session.flush()
    return tags


OPENROUTER_MOCK_RESPONSE = {
    "data": [
        {
            "id": "google/gemini-3-flash-preview",
            "name": "Gemini 3 Flash",
            "description": "Latest Gemini 3 Flash",
            "context_length": 128000,
            "pricing": {
                "prompt": "0.0025",
                "completion": "0.01",
                "image": "0.003",
                "request": "0",
            },
            "architecture": {
                "input_modalities": ["text", "image"],
                "output_modalities": ["text"],
            },
            "top_provider": {"max_completion_tokens": 16384},
            "supported_parameters": ["temperature", "top_p"],
        },
        {
            "id": "moonshotai/kimi-k2.5",
            "name": "Kimi K2.5",
            "description": "Anthropic Kimi K2.5",
            "context_length": 200000,
            "pricing": {
                "prompt": "0.003",
                "completion": "0.015",
            },
            "architecture": {
                "input_modalities": ["text"],
                "output_modalities": ["text"],
            },
            "top_provider": {"max_completion_tokens": 8192},
            "supported_parameters": ["temperature"],
        },
    ]
}
