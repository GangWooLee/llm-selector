from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.sync import SyncResponse
from app.services.benchmark_sync import sync_benchmarks
from app.services.sync_service import sync_models

router = APIRouter(prefix="/api/v1", tags=["sync"])


@router.post("/sync", response_model=SyncResponse)
async def trigger_sync(db: AsyncSession = Depends(get_db)) -> SyncResponse:
    result = await sync_models(db)
    return SyncResponse(**result)


@router.post("/sync/benchmarks")
async def trigger_benchmark_sync(db: AsyncSession = Depends(get_db)) -> dict:
    return await sync_benchmarks(db)
