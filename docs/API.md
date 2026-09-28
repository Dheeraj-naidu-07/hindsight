# Content Strategy Agent - REST API Reference

Base URL: `http://localhost:8000`

Interactive OpenAPI Documentation: `http://localhost:8000/docs`

---

## 1. System Health

### `GET /health`
Verifies backend operational status, SQLite connection, and Hindsight connectivity.

#### Response `200 OK`
```json
{
  "status": "ok",
  "version": "1.0.0",
  "database": "connected",
  "hindsight": "connected_server"
}
```

---

## 2. Strategy Generation & Retrieval

### `POST /api/v1/strategy/generate`
Executes end-to-end analytical pipeline, bounded Hindsight memory recall, LLM synthesis, and persists the strategy.

#### Request Body
```json
{
  "brand_id": "tech_brand_01",
  "platform": "youtube",
  "account_id": "UC_x5XG1OV2P6uZZ5FSM9Ttw",
  "objective": "Maximize authority and developer community engagement",
  "start_date": "2026-09-01T00:00:00Z",
  "end_date": "2026-09-30T00:00:00Z",
  "custom_brand_profile": {
    "brand_id": "tech_brand_01",
    "name": "CloudForge",
    "identity": "Developer tooling and distributed cloud systems",
    "target_audience": "Senior engineers and architects",
    "voice_preferences": {
      "tone": "Deeply technical, evidence-first",
      "communication_style": "Tutorials and post-mortems",
      "preferred_topics": ["Kubernetes", "Tracing", "Debugging"]
    }
  }
}
```

#### Response `200 OK`
```json
{
  "strategy": {
    "strategy_id": "strat_abc12345",
    "brand_id": "tech_brand_01",
    "objective": "Maximize authority and developer community engagement",
    "target_audience": "Senior engineers and architects",
    "recommended_platforms": ["youtube"],
    "content_themes": [
      {
        "topic": "Practical Debugging & Architecture Breakdowns",
        "priority": "high",
        "rationale": "Directly addresses empirical learning from Hindsight",
        "angle": "Step-by-step resolution of production bottlenecks",
        "is_gap_fill": false
      }
    ],
    "recommended_formats": [
      {
        "format_name": "short",
        "platform": "youtube",
        "recommended_cadence": "3x per week",
        "rationale": "Empirical medians confirm short formats yield 100%+ higher engagement rates"
      }
    ],
    "posting_recommendations": {
      "frequency_per_week": 4.0,
      "optimal_cadence_notes": "Post consistently during high-activity windows on youtube.",
      "platform_allocation": {"youtube": 1.0}
    },
    "rationale": "Strategy dynamically adapted based on persistent Hindsight learning...",
    "supporting_analytics": [
      {"observation": "Short format content had 116.8% higher median engagement rate than video format content."}
    ],
    "recalled_experiences": [
      {
        "memory_id": "mem_xyz789",
        "lesson": "Educational short-form technical content performed above baseline...",
        "context": "Tested on 10 posts",
        "influence_on_strategy": "Directly guided format selection to high-yield shorts."
      }
    ],
    "confidence_and_limitations": [
      "Sample size (4) is below statistical reliability threshold (5)."
    ],
    "suggested_experiments": [
      "Test tutorial hooks vs conceptual overviews"
    ],
    "created_at": "2026-09-27T16:00:00Z"
  },
  "analytics_snapshot": {
    "platform": "youtube",
    "sample_size": 4,
    "median_engagement_rate": 1.41,
    "basis": "impressions",
    "top_formats": ["short (median ER: 1.94%)"],
    "gaps_count": 1
  },
  "recalled_memories_count": 1
}
```

---

### `GET /api/v1/strategy/{strategy_id}`
Retrieves a previously generated strategy by ID.

#### Response `200 OK`
Returns the `ContentStrategy` JSON object.

---

### `GET /api/v1/strategy/history?brand_id={brand_id}&limit=20`
Lists historical strategies generated for a brand.

#### Response `200 OK`
Returns a list of `ContentStrategy` JSON objects ordered by `created_at DESC`.

---

## 3. Post-Execution Outcome & Learning

### `POST /api/v1/strategy/outcome`
Submits subsequent actual performance metrics for a strategy, runs the comparison engine, extracts reusable strategic lessons, and updates Hindsight memory.

#### Request Body
```json
{
  "strategy_id": "strat_abc12345",
  "analytics_result": {
    "...": "AnalyticsResult JSON payload from SocialMediaAnalyticsEngine"
  }
}
```

#### Response `201 Created`
```json
{
  "outcome": {
    "outcome_id": "out_98765",
    "strategy_id": "strat_abc12345",
    "brand_id": "tech_brand_01",
    "analysis_timestamp": "2026-09-27T16:30:00Z",
    "metric_comparisons": [
      {
        "metric": "median_engagement_rate",
        "expected_direction": "above_baseline",
        "actual_value": 1.94,
        "historical_baseline_value": 1.41,
        "relative_difference_percent": 37.6,
        "observation": "Account median ER was 1.94% vs historical baseline 1.41% (+37.6%)."
      }
    ],
    "observed_difference": "Account median ER was 1.94% vs historical baseline 1.41% (+37.6%). Format 'short' achieved median ER of 1.94% (+37.6% relative to account baseline).",
    "extracted_reusable_lesson": "Short, practical educational content on youtube consistently outperformed account baselines (+37.6% relative ER). Technical problem-solving topics drove higher audience engagement than broad conceptual or promotional themes.",
    "hindsight_memory_id": "mem_45678",
    "raw_analytics_summary": {
      "total_posts": 4,
      "median_er": 1.94,
      "er_basis": "impressions",
      "platform": "youtube"
    }
  },
  "reusable_lesson_stored": "Short, practical educational content on youtube consistently outperformed account baselines (+37.6% relative ER)...",
  "hindsight_memory_id": "mem_45678"
}
```

---

## 4. Memory Inspection

### `GET /api/v1/memory/{bank_id}?query={query}&platform={platform}`
Queries the persistent memories in a Hindsight memory bank.

#### Response `200 OK`
```json
{
  "bank_id": "tech_brand_01",
  "count": 1,
  "memories": [
    {
      "id": "mem_45678",
      "text": "Strategy Lesson [YOUTUBE - short on 'Debugging']: Short, practical educational content...",
      "context": "Context: Tested 'Targeted content execution'. Observed Result: Outperformed account baseline by +37.6% median ER.",
      "metadata": {
        "platform": "youtube",
        "content_type": "short",
        "topic": "Debugging"
      }
    }
  ]
}
```
