from typing import Set
from functools import lru_cache

from pydantic import (
    BaseSettings,
    DirectoryPath,
    Field,
)


__all__ = ["get_settings"]


class Settings(BaseSettings):
    host: str = "0.0.0.0"
    port: int = 9981

    is_production: bool = Field(default=False, env="IS_PRODUCTION")

    sqlite_db_file: str = "data/data.db"

    dashboard_routes: Set[str] = {"/", "/dashboard", "/register", "/login"}
    dashboard_templates_path: DirectoryPath = "core/views/templates/"
    dashboard_static_path: DirectoryPath = "core/views/static/"


@lru_cache
def get_settings() -> Settings:
    return Settings()
