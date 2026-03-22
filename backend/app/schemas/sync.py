from datetime import datetime

from pydantic import BaseModel


class SyncResponse(BaseModel):
    status: str
    models_added: int
    models_updated: int
    models_deactivated: int
    total_active: int
    synced_at: datetime
