from __future__ import annotations

from fastapi import FastAPI

from src.core.config import Settings
from src.core.logging import setup_logging
from src.entrypoints.api.v1.routes import router as v1_router

settings = Settings.from_env()
setup_logging(settings.log_level)

app = FastAPI(title="AI MCP Agent")
app.include_router(v1_router)
