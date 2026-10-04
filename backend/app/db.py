import duckdb

from app.config import settings


def connect() -> duckdb.DuckDBPyConnection:
    settings.db_path.parent.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(str(settings.db_path))
