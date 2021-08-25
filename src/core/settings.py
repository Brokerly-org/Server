from typing import Set

from pydantic import (
    BaseSettings,
    FilePath,
    DirectoryPath,
    Field,
)


class Settings(BaseSettings):
    is_production: bool = Field(default=False, env="IS_PRODUCTION")

    sqlite_db_file: FilePath = "data/data.db"

    dashboard_routes: Set[str] = {"/", "/dashboard", "/register", "/login"}
    dashboard_templates_path: DirectoryPath = "core/views/templates/"
    dashboard_static_path: DirectoryPath = "core/views/static/"

    class Config:
        pass
