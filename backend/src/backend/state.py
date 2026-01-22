"""Singleton-like accessors for services used by the API layer."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from backend.core.processor import Processor
from backend.services.config_service import ConfigService
from backend.util import project_root as get_project_root


@lru_cache(maxsize=1)
def get_config_service() -> ConfigService:
    return ConfigService()


@lru_cache(maxsize=1)
def get_processor() -> Processor:
    project_root = get_project_root()
    workspace = project_root / "data" / "inputs" / "_api_uploads"
    return Processor(workspace=workspace)
