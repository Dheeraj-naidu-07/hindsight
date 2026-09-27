# Social Media Analytics Engine

Standalone data and analytics layer for the Content Strategy Agent.

## Quickstart

```python
from datetime import datetime, timezone
from social_analytics.providers import YouTubeProvider, InstagramProvider, RedditProvider
from social_analytics.engine import SocialMediaAnalyticsEngine

# Initialize provider (automatically falls back to deterministic mocks if API keys are unset)
provider = YouTubeProvider()
engine = SocialMediaAnalyticsEngine(provider)

# Run complete analysis
result = engine.run_analysis(
    account_id="UC_x5XG1OV2P6uZZ5FSM9Ttw",
    start_date=datetime(2026, 9, 1, tzinfo=timezone.utc),
    end_date=datetime(2026, 9, 30, tzinfo=timezone.utc),
)

# Output is a fully validated Pydantic model and serializable JSON dict
print(result.model_dump_json(indent=2))
```

## Running Tests

```bash
python3 -m pytest social_analytics/tests/ -v
```

See [docs/API_CONTRACT.md](../docs/API_CONTRACT.md) and [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md) for full specifications.
