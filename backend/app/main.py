from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.advise import router as advise_router
from app.api.routes.models import router as models_router
from app.api.routes.sync import router as sync_router
from app.config import settings


def create_app() -> FastAPI:
    application = FastAPI(
        title="LLM Selector API",
        version="0.1.0",
        description="실시간 데이터 기반 AI 모델 선택 어드바이저",
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(advise_router)
    application.include_router(models_router)
    application.include_router(sync_router)

    @application.get("/api/v1/health")
    async def health_check():
        return {"status": "ok"}

    return application


app = create_app()
