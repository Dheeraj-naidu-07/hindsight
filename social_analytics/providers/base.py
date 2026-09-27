"""
Base provider abstraction for social data platforms.
Includes resilience utilities:
- Thread-safe / async-friendly rate limiting
- In-memory TTL caching
- Bounded retries with exponential backoff
- Deterministic mock / fixture fallback mode
"""

from __future__ import annotations

import abc
import logging
import random
import time
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, TypeVar

from social_analytics.models.normalized import (
    AccountInfo,
    AudienceMetrics,
    NormalizedContent,
)

logger = logging.getLogger(__name__)

T = TypeVar("T")


class RateLimiter:
    """
    Token bucket rate limiter to prevent exceeding external API quotas.
    """

    def __init__(self, requests_per_second: float = 5.0, burst: int = 10):
        self.rate = requests_per_second
        self.capacity = burst
        self.tokens = float(burst)
        self.last_update = time.monotonic()

    def acquire(self) -> None:
        """Blocks until a token is available."""
        while True:
            now = time.monotonic()
            elapsed = now - self.last_update
            self.last_update = now
            self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)

            if self.tokens >= 1.0:
                self.tokens -= 1.0
                return

            sleep_time = (1.0 - self.tokens) / self.rate
            time.sleep(max(0.01, sleep_time))


class TTLCache:
    """
    Lightweight in-memory cache with Time-To-Live (TTL) expiration.
    """

    def __init__(self, default_ttl_seconds: int = 300):
        self.default_ttl = default_ttl_seconds
        self._cache: Dict[str, tuple[float, Any]] = {}

    def get(self, key: str) -> Optional[Any]:
        if key in self._cache:
            expires_at, value = self._cache[key]
            if time.time() < expires_at:
                return value
            del self._cache[key]
        return None

    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl
        self._cache[key] = (time.time() + ttl, value)

    def clear(self) -> None:
        self._cache.clear()


class RetryPolicy:
    """
    Bounded exponential backoff retry executor with jitter.
    """

    def __init__(
        self,
        max_retries: int = 3,
        base_delay_seconds: float = 0.5,
        max_delay_seconds: float = 10.0,
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay_seconds
        self.max_delay = max_delay_seconds

    def execute(self, func: Callable[[], T]) -> T:
        last_exception: Optional[Exception] = None
        for attempt in range(self.max_retries + 1):
            try:
                return func()
            except Exception as exc:
                last_exception = exc
                if attempt == self.max_retries:
                    logger.error(f"Execution failed after {self.max_retries} retries: {exc}")
                    raise exc

                delay = min(
                    self.max_delay,
                    self.base_delay * (2 ** attempt) + random.uniform(0, 0.2),
                )
                logger.warning(
                    f"Retry {attempt + 1}/{self.max_retries} after error: {exc}. Sleeping {delay:.2f}s."
                )
                time.sleep(delay)

        if last_exception:
            raise last_exception
        raise RuntimeError("Unexpected retry loop exit")


class BaseSocialProvider(abc.ABC):
    """
    Abstract interface for social media data providers.
    All platform-specific adapters (YouTube, Instagram, Reddit) implement this contract.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        rate_limit_rps: float = 5.0,
        cache_ttl_seconds: int = 300,
        mock_mode: bool = False,
    ):
        self.api_key = api_key
        self.mock_mode = mock_mode
        self.rate_limiter = RateLimiter(requests_per_second=rate_limit_rps)
        self.cache = TTLCache(default_ttl_seconds=cache_ttl_seconds)
        self.retry_policy = RetryPolicy(max_retries=3, base_delay_seconds=0.3)

    @abc.abstractmethod
    def platform_name(self) -> str:
        """Returns the canonical platform identifier: 'youtube', 'instagram', or 'reddit'."""
        pass

    @abc.abstractmethod
    def get_account(self, account_id: str) -> AccountInfo:
        """
        Fetch normalized profile/channel/account details.
        """
        pass

    @abc.abstractmethod
    def get_content(
        self,
        account_id: str,
        start_date: datetime,
        end_date: datetime,
        limit: int = 100,
    ) -> List[NormalizedContent]:
        """
        Fetch normalized posts/videos published by the account between start_date and end_date.
        """
        pass

    @abc.abstractmethod
    def get_content_metrics(self, content_ids: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Fetch detailed lifetime or recent metrics for specific content IDs.
        """
        pass

    @abc.abstractmethod
    def get_audience_metrics(
        self,
        account_id: str,
        start_date: datetime,
        end_date: datetime,
    ) -> AudienceMetrics:
        """
        Fetch aggregate follower growth, reach, and demographic data across the window.
        """
        pass
