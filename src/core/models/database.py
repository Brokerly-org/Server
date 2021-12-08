from functools import lru_cache
from sqlmodel import create_engine


from core.settings import get_settings


__all__ = ["get_db_engine"]


@lru_cache
def get_db_engine():
    return create_engine(f"sqlite:///{get_settings().sqlite_db_file}")
