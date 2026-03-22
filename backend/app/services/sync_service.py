from datetime import datetime, timezone
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.queries import deactivate_missing_models, upsert_model
from app.services.openrouter import fetch_all_models


async def sync_models(db: AsyncSession) -> dict[str, Any]:
    """OpenRouter 모델 데이터를 DB에 동기화.

    1. OpenRouter API에서 전체 모델 목록 fetch
    2. 각 모델을 upsert (INSERT or UPDATE)
    3. API에 없는 모델을 비활성화
    4. 결과 통계 반환
    """
    models_data = await fetch_all_models()

    added = 0
    updated = 0
    active_ids: list[str] = []

    for model_data in models_data:
        openrouter_id = model_data["openrouter_id"]
        active_ids.append(openrouter_id)

        model = await upsert_model(db, model_data)
        # upsert_model은 flush 후 반환 — created_at 존재 여부로 신규/업데이트 판별
        # updated_at != created_at이면 업데이트된 것
        if model.created_at == model.updated_at:
            added += 1
        else:
            updated += 1

    deactivated = await deactivate_missing_models(db, active_ids)
    await db.commit()

    return {
        "status": "success",
        "models_added": added,
        "models_updated": updated,
        "models_deactivated": deactivated,
        "total_active": len(active_ids),
        "synced_at": datetime.now(timezone.utc).isoformat(),
    }
