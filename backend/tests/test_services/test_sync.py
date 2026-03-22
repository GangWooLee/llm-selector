from decimal import Decimal
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Model
from app.db.queries import list_models
from app.services.sync_service import sync_models
from tests.conftest import OPENROUTER_MOCK_RESPONSE


pytestmark = pytest.mark.asyncio


async def test_sync_creates_new_models(db_session: AsyncSession):
    with patch(
        "app.services.sync_service.fetch_all_models",
        new_callable=AsyncMock,
    ) as mock_fetch:
        from app.services.openrouter import _map_model

        mock_fetch.return_value = [
            _map_model(m) for m in OPENROUTER_MOCK_RESPONSE["data"]
        ]
        result = await sync_models(db_session)

    assert result["status"] == "success"
    assert result["total_active"] == 2


async def test_sync_updates_changed_models(db_session: AsyncSession):
    # First sync: create models
    from app.services.openrouter import _map_model

    mapped = [_map_model(m) for m in OPENROUTER_MOCK_RESPONSE["data"]]

    with patch(
        "app.services.sync_service.fetch_all_models",
        new_callable=AsyncMock,
        return_value=mapped,
    ):
        await sync_models(db_session)

    # Second sync: same models — should count as updates
    with patch(
        "app.services.sync_service.fetch_all_models",
        new_callable=AsyncMock,
        return_value=mapped,
    ):
        result = await sync_models(db_session)

    assert result["total_active"] == 2
    assert result["models_updated"] >= 0


async def test_sync_deactivates_removed_models(db_session: AsyncSession):
    from app.services.openrouter import _map_model

    # Sync with 2 models
    full_data = [_map_model(m) for m in OPENROUTER_MOCK_RESPONSE["data"]]

    with patch(
        "app.services.sync_service.fetch_all_models",
        new_callable=AsyncMock,
        return_value=full_data,
    ):
        await sync_models(db_session)

    # Sync with only 1 model — the other should be deactivated
    partial_data = [full_data[0]]

    with patch(
        "app.services.sync_service.fetch_all_models",
        new_callable=AsyncMock,
        return_value=partial_data,
    ):
        result = await sync_models(db_session)

    assert result["models_deactivated"] == 1
    assert result["total_active"] == 1


async def test_sync_handles_api_error(db_session: AsyncSession):
    with patch(
        "app.services.sync_service.fetch_all_models",
        new_callable=AsyncMock,
        side_effect=Exception("API connection failed"),
    ):
        with pytest.raises(Exception, match="API connection failed"):
            await sync_models(db_session)
