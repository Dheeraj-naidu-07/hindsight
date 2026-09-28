"""
Repository for Content Items and Performance Metrics.
"""

from __future__ import annotations

from typing import List, Optional, Tuple
from database.models import ContentItemRecord, ContentPerformanceRecord
from database.repositories.base import BaseRepository


class ContentRepository(BaseRepository):
    def save_content_item(self, item: ContentItemRecord) -> ContentItemRecord:
        with self.db.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO content_items (id, brand_id, platform, content_id, topic, content_type, title, url, published_at, metadata_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    topic=excluded.topic,
                    title=excluded.title,
                    url=excluded.url,
                    metadata_json=excluded.metadata_json;
                """,
                (
                    item.id,
                    item.brand_id,
                    item.platform,
                    item.content_id,
                    item.topic,
                    item.content_type,
                    item.title,
                    item.url,
                    item.published_at,
                    item.metadata_json,
                ),
            )
        return item

    def save_performance(self, perf: ContentPerformanceRecord) -> ContentPerformanceRecord:
        with self.db.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO content_performances (id, content_item_id, views, engagements, engagement_rate, likes, comments, shares, saves, measured_at, source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    views=excluded.views,
                    engagements=excluded.engagements,
                    engagement_rate=excluded.engagement_rate,
                    likes=excluded.likes,
                    comments=excluded.comments,
                    shares=excluded.shares,
                    saves=excluded.saves,
                    measured_at=excluded.measured_at;
                """,
                (
                    perf.id,
                    perf.content_item_id,
                    perf.views,
                    perf.engagements,
                    perf.engagement_rate,
                    perf.likes,
                    perf.comments,
                    perf.shares,
                    perf.saves,
                    perf.measured_at,
                    perf.source,
                ),
            )
        return perf

    def get_content_by_brand(self, brand_id: str, platform: Optional[str] = None) -> List[ContentItemRecord]:
        with self.db.get_connection() as conn:
            if platform:
                cursor = conn.execute(
                    "SELECT * FROM content_items WHERE brand_id = ? AND platform = ? ORDER BY published_at DESC",
                    (brand_id, platform),
                )
            else:
                cursor = conn.execute(
                    "SELECT * FROM content_items WHERE brand_id = ? ORDER BY published_at DESC",
                    (brand_id,),
                )
            return [
                ContentItemRecord(
                    id=row["id"],
                    brand_id=row["brand_id"],
                    platform=row["platform"],
                    content_id=row["content_id"],
                    topic=row["topic"],
                    content_type=row["content_type"],
                    title=row["title"],
                    url=row["url"],
                    published_at=row["published_at"],
                    metadata_json=row["metadata_json"],
                )
                for row in cursor.fetchall()
            ]

    def get_content_with_latest_performance(self, brand_id: str) -> List[Tuple[ContentItemRecord, Optional[ContentPerformanceRecord]]]:
        with self.db.get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT c.*, p.id as p_id, p.views, p.engagements, p.engagement_rate,
                       p.likes, p.comments, p.shares, p.saves, p.measured_at, p.source
                FROM content_items c
                LEFT JOIN content_performances p ON c.id = p.content_item_id
                WHERE c.brand_id = ?
                ORDER BY c.published_at DESC
                """,
                (brand_id,),
            )
            results = []
            for row in cursor.fetchall():
                c_item = ContentItemRecord(
                    id=row["id"],
                    brand_id=row["brand_id"],
                    platform=row["platform"],
                    content_id=row["content_id"],
                    topic=row["topic"],
                    content_type=row["content_type"],
                    title=row["title"],
                    url=row["url"],
                    published_at=row["published_at"],
                    metadata_json=row["metadata_json"],
                )
                perf = None
                if row["p_id"]:
                    perf = ContentPerformanceRecord(
                        id=row["p_id"],
                        content_item_id=row["id"],
                        views=row["views"],
                        engagements=row["engagements"],
                        engagement_rate=row["engagement_rate"],
                        likes=row["likes"],
                        comments=row["comments"],
                        shares=row["shares"],
                        saves=row["saves"],
                        measured_at=row["measured_at"],
                        source=row["source"],
                    )
                results.append((c_item, perf))
            return results
