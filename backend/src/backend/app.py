"""FastAPI application for API Models Connect."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes import history, prompts, providers, system, tasks


def create_app() -> FastAPI:
    app = FastAPI(
        title="API Models Connect",
        version="1.0.0",
        description="Backend API for the multimodal batch processor.",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(system.router, prefix="/api/v1")
    app.include_router(providers.router, prefix="/api/v1")
    app.include_router(prompts.router, prefix="/api/v1")
    app.include_router(tasks.router, prefix="/api/v1")
    app.include_router(history.router, prefix="/api/v1")

    return app


app = create_app()
