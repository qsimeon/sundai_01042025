import sqlite3
from contextlib import contextmanager
from pathlib import Path

from api.config import settings


def init_db() -> None:
    """Initialize SQLite database with schema"""
    db_path = settings.get_db_path()

    with sqlite3.connect(db_path) as conn:
        migration_file = Path("database/migrations/001_initial_schema.sql")
        if migration_file.exists():
            conn.executescript(migration_file.read_text())
            conn.commit()


@contextmanager
def get_db():
    """Context manager for database connections"""
    db_path = settings.get_db_path()
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def execute_query(query: str, params: tuple = ()) -> list[dict]:
    """Execute a SELECT query and return results as list of dicts"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]


def execute_insert(query: str, params: tuple = ()) -> int:
    """Execute an INSERT query and return last insert ID"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return cursor.lastrowid


def execute_update(query: str, params: tuple = ()) -> int:
    """Execute an UPDATE query and return rows affected"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return cursor.rowcount
