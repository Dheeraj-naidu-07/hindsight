"""
Pytest global fixtures for Content Strategy Agent test suite.
"""

from __future__ import annotations

import os
import tempfile
import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient

from api.app import create_app
from database.connection import DatabaseConnection, reset_db_instance
from database.repositories.brand_repository import BrandRepository
from database.repositories.content_repository import ContentRepository
from database.repositories.outcome_repository import OutcomeRepository
from database.repositories.strategy_repository import StrategyRepository
from hindsight.client.hindsight_client_wrapper import HindsightClientWrapper
from hindsight.memory.experience_manager import ExperienceManager
from hindsight.recall.experience_retriever import ExperienceRetriever
from models.brand import BrandProfile, BrandVoicePreferences
from services.analytics_service.service import AnalyticsService
from social_analytics.engine.analytics_engine import SocialMediaAnalyticsEngine
from social_analytics.fixtures.youtube_fixtures import YOUTUBE_VIDEOS_FIXTURE
from social_analytics.models.output import AnalyticsResult
from social_analytics.providers.youtube import YouTubeProvider


@pytest.fixture
def temp_db():
    """Provides an isolated temporary database for each test."""
    reset_db_instance()
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        temp_path = f.name

    old_db_path = os.environ.get("DATABASE_PATH")
    os.environ["DATABASE_PATH"] = temp_path
    db = DatabaseConnection(db_path=temp_path)
    yield db

    reset_db_instance()
    if old_db_path is not None:
        os.environ["DATABASE_PATH"] = old_db_path
    else:
        os.environ.pop("DATABASE_PATH", None)

    if os.path.exists(temp_path):
        try:
            os.remove(temp_path)
        except OSError:
            pass


@pytest.fixture
def brand_repo(temp_db):
    return BrandRepository(temp_db)


@pytest.fixture
def content_repo(temp_db):
    return ContentRepository(temp_db)


@pytest.fixture
def strategy_repo(temp_db):
    return StrategyRepository(temp_db)


@pytest.fixture
def outcome_repo(temp_db):
    return OutcomeRepository(temp_db)


@pytest.fixture
def hindsight_wrapper():
    """Provides an in-memory isolated Hindsight wrapper."""
    return HindsightClientWrapper(force_mock=True)


@pytest.fixture
def experience_manager(hindsight_wrapper):
    return ExperienceManager(client=hindsight_wrapper)


@pytest.fixture
def experience_retriever(hindsight_wrapper):
    return ExperienceRetriever(client=hindsight_wrapper)


@pytest.fixture
def sample_brand():
    return BrandProfile(
        brand_id="test_tech_brand",
        name="TechForge Engineering",
        identity="Developer Tools, Cloud Architecture, and AI Infrastructure",
        target_audience="Backend Developers and Staff Engineers",
        voice_preferences=BrandVoicePreferences(
            tone="Deeply technical, evidence-first, code-focused",
            communication_style="Actionable tutorials and root-cause post-mortems",
            preferred_topics=["Microservices", "Debugging", "Distributed Systems", "AI Agents"],
        ),
    )


@pytest.fixture
def sample_analytics_result() -> AnalyticsResult:
    """Generate realistic AnalyticsResult from existing social_analytics YouTube provider."""
    provider = YouTubeProvider()
    engine = SocialMediaAnalyticsEngine(provider)
    result = engine.run_analysis(
        account_id="UC_x5XG1OV2P6uZZ5FSM9Ttw",
        start_date=datetime(2026, 9, 1, tzinfo=timezone.utc),
        end_date=datetime(2026, 9, 30, tzinfo=timezone.utc),
        previous_period_start=datetime(2026, 8, 1, tzinfo=timezone.utc),
        previous_period_end=datetime(2026, 8, 31, tzinfo=timezone.utc),
    )
    return result


@pytest.fixture
def test_client(temp_db, monkeypatch):
    """FastAPI TestClient with isolated DB and mock Hindsight."""
    monkeypatch.setenv("DATABASE_PATH", temp_db.db_path)
    monkeypatch.setenv("HINDSIGHT_MOCK_MODE", "true")
    monkeypatch.setenv("LLM_PROVIDER", "mock")
    app = create_app()
    return TestClient(app)
