"""
Base repository pattern for SQLite data access.
"""

from __future__ import annotations

from typing import Optional
from database.connection import DatabaseConnection, get_db


class BaseRepository:
    def __init__(self, db: Optional[DatabaseConnection] = None):
        self.db = db or get_db()
