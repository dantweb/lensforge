"""FastAPI application factory."""

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from lensforge.container import Container


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Initialize DI container on startup."""
    container = Container()
    container.config.from_pydantic(container.settings())
    app.state.container = container
    yield


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(title="LensForge", version="0.1.0", lifespan=lifespan)

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    from lensforge.routes.analyze import router as analyze_router

    app.include_router(analyze_router)

    return app
