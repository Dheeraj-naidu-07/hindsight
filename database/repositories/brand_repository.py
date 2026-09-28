"""
Repository for Brand entity persistence and retrieval.
"""

from __future__ import annotations

from typing import List, Optional
from database.models import BrandRecord
from database.repositories.base import BaseRepository


class BrandRepository(BaseRepository):
    def create(self, brand: BrandRecord) -> BrandRecord:
        with self.db.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO brands (id, name, identity, target_audience, voice_tone, communication_style, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name=excluded.name,
                    identity=excluded.identity,
                    target_audience=excluded.target_audience,
                    voice_tone=excluded.voice_tone,
                    communication_style=excluded.communication_style;
                """,
                (
                    brand.id,
                    brand.name,
                    brand.identity,
                    brand.target_audience,
                    brand.voice_tone,
                    brand.communication_style,
                    brand.created_at,
                ),
            )
        return brand

    def get_by_id(self, brand_id: str) -> Optional[BrandRecord]:
        with self.db.get_connection() as conn:
            cursor = conn.execute("SELECT * FROM brands WHERE id = ?", (brand_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return BrandRecord(
                id=row["id"],
                name=row["name"],
                identity=row["identity"],
                target_audience=row["target_audience"],
                voice_tone=row["voice_tone"],
                communication_style=row["communication_style"],
                created_at=row["created_at"],
            )

    def list_all(self) -> List[BrandRecord]:
        with self.db.get_connection() as conn:
            cursor = conn.execute("SELECT * FROM brands ORDER BY created_at DESC")
            return [
                BrandRecord(
                    id=row["id"],
                    name=row["name"],
                    identity=row["identity"],
                    target_audience=row["target_audience"],
                    voice_tone=row["voice_tone"],
                    communication_style=row["communication_style"],
                    created_at=row["created_at"],
                )
                for row in cursor.fetchall()
            ]
