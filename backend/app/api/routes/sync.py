from fastapi import APIRouter, HTTPException

from app.schemas.sync import SyncResponse

router = APIRouter(prefix="/api/v1", tags=["sync"])


@router.post("/sync", response_model=SyncResponse)
async def trigger_sync() -> SyncResponse:
    try:
        from app.services.sync_service import run_sync
        return await run_sync()
    except ImportError:
        raise HTTPException(
            status_code=501,
            detail="Sync service not yet implemented",
        )
