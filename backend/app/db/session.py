from collections.abc import AsyncGenerator
from typing import Any

from app.config import settings

engine: Any = None
async_session: Any = None

if settings.DATABASE_URL:
    from sqlalchemy.ext.asyncio import (
        AsyncSession,
        async_sessionmaker,
        create_async_engine,
    )

    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = async_sessionmaker(engine, expire_on_commit=False)


async def get_db() -> AsyncGenerator[Any, None]:
    if async_session is None:
        yield None
    else:
        async with async_session() as session:
            yield session
