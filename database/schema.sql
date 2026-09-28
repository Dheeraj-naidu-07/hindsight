-- Schema definition for Content Strategy Agent application database.
-- Application records live here; reusable experiences and memory live in Hindsight.

CREATE TABLE IF NOT EXISTS brands (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    identity TEXT NOT NULL,
    target_audience TEXT NOT NULL,
    voice_tone TEXT NOT NULL,
    communication_style TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS content_items (
    id TEXT PRIMARY KEY,
    brand_id TEXT NOT NULL,
    platform TEXT NOT NULL,
    content_id TEXT NOT NULL,
    topic TEXT,
    content_type TEXT NOT NULL,
    title TEXT,
    url TEXT,
    published_at TEXT NOT NULL,
    metadata_json TEXT DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_content_brand_platform ON content_items(brand_id, platform);
CREATE INDEX IF NOT EXISTS idx_content_topic ON content_items(topic);

CREATE TABLE IF NOT EXISTS content_performances (
    id TEXT PRIMARY KEY,
    content_item_id TEXT NOT NULL,
    views INTEGER,
    engagements INTEGER NOT NULL DEFAULT 0,
    engagement_rate REAL,
    likes INTEGER,
    comments INTEGER,
    shares INTEGER,
    saves INTEGER,
    measured_at TEXT NOT NULL,
    source TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_performance_content_id ON content_performances(content_item_id);

CREATE TABLE IF NOT EXISTS strategies (
    id TEXT PRIMARY KEY,
    brand_id TEXT NOT NULL,
    objective TEXT NOT NULL,
    target_audience TEXT NOT NULL,
    recommended_platforms_json TEXT NOT NULL,
    content_themes_json TEXT NOT NULL,
    recommended_formats_json TEXT NOT NULL,
    posting_recommendations_json TEXT NOT NULL,
    rationale TEXT NOT NULL,
    supporting_evidence_json TEXT NOT NULL,
    recalled_memories_json TEXT NOT NULL,
    confidence_notes TEXT,
    experiments_json TEXT DEFAULT '[]',
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_strategies_brand_id ON strategies(brand_id);

CREATE TABLE IF NOT EXISTS strategy_outcomes (
    id TEXT PRIMARY KEY,
    strategy_id TEXT NOT NULL,
    actual_metrics_json TEXT NOT NULL,
    expected_metrics_json TEXT NOT NULL,
    observed_difference TEXT NOT NULL,
    reusable_lesson TEXT NOT NULL,
    hindsight_memory_id TEXT,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_outcomes_strategy_id ON strategy_outcomes(strategy_id);
