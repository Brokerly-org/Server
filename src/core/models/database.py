from functools import lru_cache
from sqlmodel import create_engine, SQLModel


from core.settings import get_settings


__all__ = ["get_db_engine"]


@lru_cache
def get_db_engine():
    engine = create_engine(f"sqlite:///{get_settings().sqlite_db_file}")
    SQLModel.metadata.create_all(engine)
    return engine
