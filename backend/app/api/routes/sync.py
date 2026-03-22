from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.sync import SyncResponse
from app.services.sync_service import sync_models

router = APIRouter(prefix="/api/v1", tags=["sync"])


@router.post("/sync", response_model=SyncResponse)
async def trigger_sync(db: AsyncSession = Depends(get_db)) -> SyncResponse:
    result = await sync_models(db)
    return SyncResponse(**result)
