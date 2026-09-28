"""
SQLite Database Connection and Session Management.
Provides lightweight, thread-safe access with foreign key constraints enabled.
"""

from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator


DEFAULT_DB_PATH = os.environ.get("DATABASE_PATH", "content_strategy_agent.db")


class DatabaseConnection:
    """Manages SQLite connection lifecycle and schema initialization."""

    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        self._ensure_db_dir()
        self.init_schema()

    def _ensure_db_dir(self) -> None:
        if self.db_path != ":memory:":
            path = Path(self.db_path)
            path.parent.mkdir(parents=True, exist_ok=True)

    def get_raw_connection(self) -> sqlite3.Connection:
        """Create a new SQLite connection with row_factory and foreign keys."""
        conn = sqlite3.connect(
            self.db_path,
            check_same_thread=False,
            timeout=30.0,
        )
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode = WAL;")
        return conn

    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Context manager for acquiring and releasing a connection with transaction handling."""
        conn = self.get_raw_connection()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def init_schema(self) -> None:
        """Initialize database tables if they do not exist."""
        schema_file = Path(__file__).parent / "schema.sql"
        if schema_file.exists():
            schema_sql = schema_file.read_text(encoding="utf-8")
            with self.get_connection() as conn:
                conn.executescript(schema_sql)


# Global singleton instance for easy import
_global_db: DatabaseConnection | None = None


def get_db(db_path: str | None = None) -> DatabaseConnection:
    global _global_db
    target_path = db_path or os.environ.get("DATABASE_PATH", "content_strategy_agent.db")
    if _global_db is None or _global_db.db_path != target_path:
        _global_db = DatabaseConnection(db_path=target_path)
    return _global_db


def reset_db_instance() -> None:
    """Reset global DB instance (primarily for isolated test fixtures)."""
    global _global_db
    _global_db = None
