"""POST /api/v1/advise — 에이전트 실행 SSE 스트리밍 엔드포인트."""

from typing import Any

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.agent.advisor import run_advisor
from app.api.deps import get_db
from app.services.openrouter import fetch_all_models
from app.utils.sse import format_sse

router = APIRouter(tags=["advisor"])

MAX_USER_INPUT_LENGTH = 2000
DEFAULT_ANALYSIS_MODEL = "google/gemini-3-flash-preview"


class AdviseRequest(BaseModel):
    user_input: str = Field(..., min_length=1, max_length=MAX_USER_INPUT_LENGTH)
    api_key: str = Field(..., min_length=1)
    analysis_model: str | None = None


@router.post("/api/v1/advise")
async def advise(
    request: AdviseRequest,
    db: Any = Depends(get_db),
) -> StreamingResponse:
    models_cache = None
    if db is None:
        models_cache = await fetch_all_models()

    async def event_generator():
        async for event in run_advisor(
            user_input=request.user_input,
            api_key=request.api_key,
            analysis_model=request.analysis_model or DEFAULT_ANALYSIS_MODEL,
            db=db,
            models_cache=models_cache,
        ):
            yield format_sse(event["event"], event["data"])

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
