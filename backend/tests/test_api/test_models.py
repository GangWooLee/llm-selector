import uuid
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.main import app


pytestmark = pytest.mark.asyncio


def _make_model(**overrides) -> SimpleNamespace:
    """Create a mock model object with from_attributes-compatible attributes."""
    defaults = {
        "id": uuid.uuid4(),
        "openrouter_id": "google/gemini-3-flash-preview",
        "name": "Gemini 3 Flash",
        "provider": "google",
        "context_length": 128000,
        "pricing_input": Decimal("0.0025"),
        "pricing_output": Decimal("0.01"),
        "is_free": False,
        "is_active": True,
        "modalities": None,
        "supported_parameters": None,
    }
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


async def test_get_models_returns_200_with_data(client: AsyncClient):
    model = _make_model()
    mock_result = ([model], 1)

    with patch("app.db.queries.list_models", new_callable=AsyncMock, return_value=mock_result):
        response = await client.get("/api/v1/models")

    assert response.status_code == 200
    body = response.json()
    assert len(body["data"]) == 1
    assert body["data"][0]["name"] == "Gemini 3 Flash"


async def test_get_models_pagination_works(client: AsyncClient):
    models = [
        _make_model(
            id=uuid.uuid4(),
            openrouter_id=f"test/model-{i}",
            name=f"Model {i}",
        )
        for i in range(3)
    ]
    mock_result = (models[:2], 3)

    with patch("app.db.queries.list_models", new_callable=AsyncMock, return_value=mock_result):
        response = await client.get("/api/v1/models?page=1&per_page=2")

    assert response.status_code == 200
    body = response.json()
    assert body["pagination"]["total"] == 3
    assert body["pagination"]["total_pages"] == 2
    assert len(body["data"]) == 2


async def test_get_model_detail_returns_200(client: AsyncClient):
    model_id = uuid.uuid4()
    model = _make_model(
        id=model_id,
        description="A great model",
        max_completion_tokens=16384,
        architecture=None,
        benchmarks=[],
        tags=[],
        updated_at=None,
    )

    with patch("app.db.queries.get_model_with_details", new_callable=AsyncMock, return_value=model):
        response = await client.get(f"/api/v1/models/{model_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Gemini 3 Flash"
    assert body["id"] == str(model_id)


async def test_get_model_detail_returns_404_for_missing(client: AsyncClient):
    missing_id = uuid.uuid4()

    with patch("app.db.queries.get_model_with_details", new_callable=AsyncMock, return_value=None):
        response = await client.get(f"/api/v1/models/{missing_id}")

    assert response.status_code == 404
