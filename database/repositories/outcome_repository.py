"""
Repository for Strategy Outcome and Post-Mortem Analysis Records.
"""

from __future__ import annotations

from typing import List, Optional
from database.models import StrategyOutcomeRecord
from database.repositories.base import BaseRepository


class OutcomeRepository(BaseRepository):
    def create(self, outcome: StrategyOutcomeRecord) -> StrategyOutcomeRecord:
        with self.db.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO strategy_outcomes (
                    id, strategy_id, actual_metrics_json, expected_metrics_json,
                    observed_difference, reusable_lesson, hindsight_memory_id, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    actual_metrics_json=excluded.actual_metrics_json,
                    expected_metrics_json=excluded.expected_metrics_json,
                    observed_difference=excluded.observed_difference,
                    reusable_lesson=excluded.reusable_lesson,
                    hindsight_memory_id=excluded.hindsight_memory_id;
                """,
                (
                    outcome.id,
                    outcome.strategy_id,
                    outcome.actual_metrics_json,
                    outcome.expected_metrics_json,
                    outcome.observed_difference,
                    outcome.reusable_lesson,
                    outcome.hindsight_memory_id,
                    outcome.created_at,
                ),
            )
        return outcome

    def get_by_strategy_id(self, strategy_id: str) -> Optional[StrategyOutcomeRecord]:
        with self.db.get_connection() as conn:
            cursor = conn.execute("SELECT * FROM strategy_outcomes WHERE strategy_id = ?", (strategy_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return StrategyOutcomeRecord(
                id=row["id"],
                strategy_id=row["strategy_id"],
                actual_metrics_json=row["actual_metrics_json"],
                expected_metrics_json=row["expected_metrics_json"],
                observed_difference=row["observed_difference"],
                reusable_lesson=row["reusable_lesson"],
                hindsight_memory_id=row["hindsight_memory_id"],
                created_at=row["created_at"],
            )

    def list_all(self, limit: int = 50) -> List[StrategyOutcomeRecord]:
        with self.db.get_connection() as conn:
            cursor = conn.execute("SELECT * FROM strategy_outcomes ORDER BY created_at DESC LIMIT ?", (limit,))
            return [
                StrategyOutcomeRecord(
                    id=row["id"],
                    strategy_id=row["strategy_id"],
                    actual_metrics_json=row["actual_metrics_json"],
                    expected_metrics_json=row["expected_metrics_json"],
                    observed_difference=row["observed_difference"],
                    reusable_lesson=row["reusable_lesson"],
                    hindsight_memory_id=row["hindsight_memory_id"],
                    created_at=row["created_at"],
                )
                for row in cursor.fetchall()
            ]
