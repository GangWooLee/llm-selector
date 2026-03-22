"""POST /api/v1/advise endpoint tests."""

from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.main import app


pytestmark = pytest.mark.asyncio


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


async def test_advise_returns_sse_stream(client: AsyncClient):
    async def mock_advisor(**kwargs):
        yield {"event": "thinking", "data": {"message": "분석 중..."}}
        yield {"event": "done", "data": {}}

    with patch("app.api.routes.advise.run_advisor", side_effect=mock_advisor):
        response = await client.post(
            "/api/v1/advise",
            json={"user_input": "coding assistant", "api_key": "test-key"},
        )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    body = response.text
    assert "event: thinking" in body
    assert "event: done" in body


async def test_advise_returns_422_without_user_input(client: AsyncClient):
    response = await client.post(
        "/api/v1/advise",
        json={"api_key": "test-key"},
    )

    assert response.status_code == 422


async def test_advise_returns_422_without_api_key(client: AsyncClient):
    response = await client.post(
        "/api/v1/advise",
        json={"user_input": "test"},
    )

    assert response.status_code == 422
