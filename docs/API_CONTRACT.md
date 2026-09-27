# Social Media Analytics Engine - API & Data Contract

This document provides the canonical specification for the data contracts, provider interfaces, and structured analytical output schemas produced by the **Social Media Analytics Engine** (data layer of the Content Strategy Agent).

---

## 1. Scope & System Boundary

The Social Media Analytics Engine is responsible exclusively for:
1. Connecting to platform APIs via official endpoints (YouTube Data v3 / Analytics, Instagram Graph API, Reddit API).
2. Normalizing diverse platform schemas into a strict, unified model (`NormalizedContent`).
3. Executing deterministic, pure-Python metric calculations and statistical aggregations.
4. Calculating historical account baselines and relative percentage differences.
5. Computing period-over-period comparisons (explicitly distinguishing percentage points from relative percentages).
6. Generating non-causal, data-driven observations with sample size and numerical evidence.
7. Auditing data quality, platform-inherent metric limitations, and sample size sufficiency.
8. Emitting a stable, validated JSON payload (`AnalyticsResult`).

Downstream layers (backend orchestration, LLM strategy, memory persistence via Hindsight, email notifications) consume `AnalyticsResult` directly.

---

## 2. Normalized Data Model (`NormalizedContent`)

All platform payloads are converted into this common normalized structure before analysis.

### Schema Fields
| Field | Type | Description | Nullability Rules |
| :--- | :--- | :--- | :--- |
| `platform` | `Literal["youtube", "instagram", "reddit"]` | Platform identifier | Required |
| `content_id` | `str` | Platform-specific unique ID | Required |
| `content_type` | `str` | Content format (`video`, `short`, `reel`, `post`, `carousel`, `submission`) | Required |
| `published_at` | `datetime` | UTC timestamp of publication | Required |
| `title` | `Optional[str]` | Title, headline, or caption snippet | Nullable |
| `url` | `Optional[str]` | Direct link to content item | Nullable |
| `views` | `Optional[int]` | Total video or play views | **0** = explicit 0; **null** = unavailable |
| `impressions` | `Optional[int]` | Total exposures | **0** = explicit 0; **null** = unavailable |
| `reach` | `Optional[int]` | Deduplicated unique accounts exposed | **0** = explicit 0; **null** = unavailable |
| `likes` | `Optional[int]` | Likes, upvotes, or net score | **0** = explicit 0; **null** = unavailable |
| `comments` | `Optional[int]` | Comments or direct replies | **0** = explicit 0; **null** = unavailable |
| `shares` | `Optional[int]` | Shares, reposts, or crossposts | **0** = explicit 0; **null** = unavailable |
| `saves` | `Optional[int]` | Saves or bookmarks | **0** = explicit 0; **null** = unavailable |
| `watch_time` | `Optional[float]` | Total watch time in seconds | Nullable |
| `average_view_duration`| `Optional[float]` | Average view duration in seconds | Nullable |
| `followers_gained` | `Optional[int]` | Attributed follower conversions | Nullable |
| `topic` | `Optional[str]` | Primary tag, category, or subreddit | Nullable |
| `platform_specific` | `Dict[str, Any]` | Preserved platform-native attributes | Required (dict) |

> **CRITICAL RULE**: `0` represents an explicit value reported by the platform. `null` represents that the metric is unavailable or unsupported. Unavailable metrics are **never** coerced to zero.

---

## 3. Metrics Specification & Exact Formulas

All calculations are performed deterministically in Python without LLM approximation.

### 3.1 Content Engagements
$$\text{Total Engagements} = \sum (\text{likes}, \text{comments}, \text{shares}, \text{saves})_{\text{available}}$$
*Missing (null) components are excluded; available components with value 0 are counted.*

### 3.2 Rate Calculations & Denominator Basis
Rate calculations use the best available denominator in order of priority:
1. `reach` (Unique audience exposed)
2. `impressions` (Total exposures)

$$\text{Engagement Rate} = \left(\frac{\text{Total Engagements}}{\text{Denominator}}\right) \times 100$$
$$\text{Like Rate} = \left(\frac{\text{likes}}{\text{Denominator}}\right) \times 100$$
$$\text{Comment Rate} = \left(\frac{\text{comments}}{\text{Denominator}}\right) \times 100$$
$$\text{Share Rate} = \left(\frac{\text{shares}}{\text{Denominator}}\right) \times 100$$
$$\text{Save Rate} = \left(\frac{\text{saves}}{\text{Denominator}}\right) \times 100$$
$$\text{View Rate} = \left(\frac{\text{views}}{\text{impressions}}\right) \times 100$$

> **Denominator Safety**: If the denominator is `0` or `null`, the rate returns `null`. Rate calculations record their basis explicitly in `engagement_rate_basis`. Denominators are never silently mixed.

### 3.3 Account Aggregates
- **Average Engagement per Content**:
  $$\frac{\sum \text{Total Engagements}}{\text{Total Content Count}}$$
- **Median Views, Engagements, Engagement Rate, Shares, Comments**:
  $$\text{median}(X_{\text{non-null}})$$
  *Medians are used to insulate benchmarks against viral outliers.*
- **Posting Frequency**:
  $$\text{Posts per Day} = \frac{\text{Post Count}}{\text{Period Duration in Days}}$$
  $$\text{Posts per Week} = \text{Posts per Day} \times 7$$

### 3.4 Growth Metrics
- **Absolute Follower Growth**:
  $$\Delta_{\text{followers}} = \text{Followers}_{\text{end}} - \text{Followers}_{\text{start}}$$
- **Percentage Follower Growth**:
  $$\%_{\text{growth}} = \left(\frac{\text{Followers}_{\text{end}} - \text{Followers}_{\text{start}}}{\text{Followers}_{\text{start}}}\right) \times 100 \quad (\text{when } \text{Followers}_{\text{start}} > 0)$$

---

## 4. Baselines & Relative Differences

### Historical Account Baseline
Computed over a historical reference window:
- `median_views`
- `median_engagements`
- `median_engagement_rate`
- `median_shares`
- `median_comments`

### Item vs. Baseline Comparison
For each content item:
$$\text{Relative Difference (\%)} = \left(\frac{\text{Content Value} - \text{Historical Median}}{\text{Historical Median}}\right) \times 100$$

---

## 5. Period Comparison Methodology (pp vs %)

When comparing Current Period vs. Previous Period:
1. **For Rate Metrics** (e.g., Engagement Rate %):
   - **Percentage-Point Change**: $\text{Current Rate} - \text{Previous Rate}$ (in `pp`).
   - **Relative Change**: $\left(\frac{\text{Current Rate} - \text{Previous Rate}}{\text{Previous Rate}}\right) \times 100$ (in `\%`).
   *Example: 4.0% to 5.0% $\rightarrow$ $+1.0\text{ pp}$ and $+25.0\%$.*
2. **For Volume Metrics** (e.g., Views, Engagements, Followers):
   - **Absolute Change**: $\text{Current} - \text{Previous}$.
   - **Relative Change**: $\left(\frac{\text{Current} - \text{Previous}}{\text{Previous}}\right) \times 100$.

---

## 6. Deterministic Observations Format

Observations are factual, quantitative, and non-causal:
```json
{
  "type": "content_type_comparison",
  "observation": "Short format content had 116.8% higher median engagement rate than video format content.",
  "evidence": {
    "metric": "median_engagement_rate",
    "higher_format": "short",
    "lower_format": "video",
    "higher_value": 1.9351,
    "lower_value": 0.8924,
    "difference_percent": 116.8,
    "sample_sizes": {
      "short": 2,
      "video": 2
    }
  }
}
```

---

## 7. Data Quality Audit Schema

Every result provides data completeness metadata:
```json
{
  "source_platform": "youtube",
  "collection_timestamp": "2026-09-27T15:31:43Z",
  "analysis_period": {
    "start": "2026-09-01T00:00:00Z",
    "end": "2026-09-30T00:00:00Z",
    "duration_days": 29.0
  },
  "sample_size": 4,
  "insufficient_sample_size": true,
  "missing_metrics": [],
  "unavailable_metrics": ["reach", "saves", "profile_visits"],
  "data_quality_warnings": [
    "insufficient_sample_size: Sample size (4) is below statistical reliability threshold (5). Medians and rankings should be interpreted with caution."
  ]
}
```

---

## 8. Final JSON Contract (`AnalyticsResult`)

The top-level structure returned by the engine:
```json
{
  "account": { ... },
  "period": { ... },
  "content_summary": { ... },
  "growth": { ... },
  "baseline": { ... },
  "top_content": [ ... ],
  "bottom_content": [ ... ],
  "content_type_performance": { ... },
  "period_comparison": { ... },
  "observations": [ ... ],
  "platform_specific_metrics": { ... },
  "data_quality": { ... }
}
```
