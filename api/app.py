"""
FastAPI Application Entry Point.
Configures CORS, registers error handlers, mounts API routes, and handles startup initialization via lifespan.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.errors.handlers import register_error_handlers
from api.routes.health import router as health_router
from api.routes.memory import router as memory_router
from api.routes.outcome import router as outcome_router
from api.routes.strategy import router as strategy_router
from database.connection import get_db

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("content_strategy_agent")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Content Strategy Agent backend...")
    db = get_db()
    db.init_schema()
    logger.info("Database initialized successfully.")
    yield


def create_app() -> FastAPI:
    """Create and configure the FastAPI instance."""
    app = FastAPI(
        title="Content Strategy Agent API",
        description="Persistent-memory AI Content Strategy Agent with Hindsight and Social Analytics",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # Configure CORS for frontend integration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register global exception handlers
    register_error_handlers(app)

    # Mount API routers
    app.include_router(health_router)
    app.include_router(strategy_router)
    app.include_router(outcome_router)
    app.include_router(memory_router)

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.app:app", host="0.0.0.0", port=8000, reload=True)
