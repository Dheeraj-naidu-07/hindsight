"""
Repository for Strategy records persistence and retrieval.
"""

from __future__ import annotations

from typing import List, Optional
from database.models import StrategyRecord
from database.repositories.base import BaseRepository


class StrategyRepository(BaseRepository):
    def create(self, strategy: StrategyRecord) -> StrategyRecord:
        with self.db.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO strategies (
                    id, brand_id, objective, target_audience,
                    recommended_platforms_json, content_themes_json,
                    recommended_formats_json, posting_recommendations_json,
                    rationale, supporting_evidence_json, recalled_memories_json,
                    confidence_notes, experiments_json, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    objective=excluded.objective,
                    target_audience=excluded.target_audience,
                    recommended_platforms_json=excluded.recommended_platforms_json,
                    content_themes_json=excluded.content_themes_json,
                    recommended_formats_json=excluded.recommended_formats_json,
                    posting_recommendations_json=excluded.posting_recommendations_json,
                    rationale=excluded.rationale,
                    supporting_evidence_json=excluded.supporting_evidence_json,
                    recalled_memories_json=excluded.recalled_memories_json,
                    confidence_notes=excluded.confidence_notes,
                    experiments_json=excluded.experiments_json;
                """,
                (
                    strategy.id,
                    strategy.brand_id,
                    strategy.objective,
                    strategy.target_audience,
                    strategy.recommended_platforms_json,
                    strategy.content_themes_json,
                    strategy.recommended_formats_json,
                    strategy.posting_recommendations_json,
                    strategy.rationale,
                    strategy.supporting_evidence_json,
                    strategy.recalled_memories_json,
                    strategy.confidence_notes,
                    strategy.experiments_json,
                    strategy.created_at,
                ),
            )
        return strategy

    def get_by_id(self, strategy_id: str) -> Optional[StrategyRecord]:
        with self.db.get_connection() as conn:
            cursor = conn.execute("SELECT * FROM strategies WHERE id = ?", (strategy_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return StrategyRecord(
                id=row["id"],
                brand_id=row["brand_id"],
                objective=row["objective"],
                target_audience=row["target_audience"],
                recommended_platforms_json=row["recommended_platforms_json"],
                content_themes_json=row["content_themes_json"],
                recommended_formats_json=row["recommended_formats_json"],
                posting_recommendations_json=row["posting_recommendations_json"],
                rationale=row["rationale"],
                supporting_evidence_json=row["supporting_evidence_json"],
                recalled_memories_json=row["recalled_memories_json"],
                confidence_notes=row["confidence_notes"],
                experiments_json=row["experiments_json"],
                created_at=row["created_at"],
            )

    def list_by_brand(self, brand_id: str, limit: int = 50) -> List[StrategyRecord]:
        with self.db.get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM strategies WHERE brand_id = ? ORDER BY created_at DESC LIMIT ?",
                (brand_id, limit),
            )
            return [
                StrategyRecord(
                    id=row["id"],
                    brand_id=row["brand_id"],
                    objective=row["objective"],
                    target_audience=row["target_audience"],
                    recommended_platforms_json=row["recommended_platforms_json"],
                    content_themes_json=row["content_themes_json"],
                    recommended_formats_json=row["recommended_formats_json"],
                    posting_recommendations_json=row["posting_recommendations_json"],
                    rationale=row["rationale"],
                    supporting_evidence_json=row["supporting_evidence_json"],
                    recalled_memories_json=row["recalled_memories_json"],
                    confidence_notes=row["confidence_notes"],
                    experiments_json=row["experiments_json"],
                    created_at=row["created_at"],
                )
                for row in cursor.fetchall()
            ]
