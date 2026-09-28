"""
FastAPI Dependencies for dependency injection.
"""

from __future__ import annotations

from agent.orchestrator.agent_orchestrator import ContentStrategyAgentOrchestrator
from database.connection import DatabaseConnection, get_db
from database.repositories.brand_repository import BrandRepository
from database.repositories.content_repository import ContentRepository
from database.repositories.outcome_repository import OutcomeRepository
from database.repositories.strategy_repository import StrategyRepository
from hindsight.client.hindsight_client_wrapper import HindsightClientWrapper
from hindsight.memory.experience_manager import ExperienceManager
from hindsight.recall.experience_retriever import ExperienceRetriever
from learning.learning_service import LearningService
from services.analytics_service.service import AnalyticsService


def get_database_connection() -> DatabaseConnection:
    return get_db()


def get_brand_repository() -> BrandRepository:
    return BrandRepository(get_db())


def get_content_repository() -> ContentRepository:
    return ContentRepository(get_db())


def get_strategy_repository() -> StrategyRepository:
    return StrategyRepository(get_db())


def get_outcome_repository() -> OutcomeRepository:
    return OutcomeRepository(get_db())


def get_analytics_service() -> AnalyticsService:
    return AnalyticsService(content_repo=get_content_repository())


def get_hindsight_wrapper() -> HindsightClientWrapper:
    return HindsightClientWrapper()


def get_experience_manager() -> ExperienceManager:
    return ExperienceManager(client=get_hindsight_wrapper())


def get_experience_retriever() -> ExperienceRetriever:
    return ExperienceRetriever(client=get_hindsight_wrapper())


def get_orchestrator() -> ContentStrategyAgentOrchestrator:
    return ContentStrategyAgentOrchestrator(
        analytics_service=get_analytics_service(),
        brand_repo=get_brand_repository(),
        strategy_repo=get_strategy_repository(),
    )


def get_learning_service() -> LearningService:
    return LearningService(
        strategy_repo=get_strategy_repository(),
    )
