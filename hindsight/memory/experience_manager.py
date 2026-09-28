"""
Hindsight Experience Manager.
Coordinates storing synthesized strategic learnings into Hindsight memory banks,
enforcing deduplication and signal quality.
"""

from __future__ import annotations

import logging
from typing import Optional, Set
from hindsight.client.hindsight_client_wrapper import HindsightClientWrapper
from hindsight.schemas.memory_models import ReusableExperience

logger = logging.getLogger(__name__)


class ExperienceManager:
    """Manages writing and deduplicating strategic memories in Hindsight."""

    def __init__(self, client: Optional[HindsightClientWrapper] = None):
        self.client = client or HindsightClientWrapper()
        # In-memory tracking of retained fingerprints to prevent redundant writes
        self._stored_fingerprints: Set[str] = set()

    def remember_experience(self, experience: ReusableExperience) -> Optional[str]:
        """
        Store a reusable strategic experience in Hindsight.
        Deduplicates against previously recorded memories with identical fingerprints.
        """
        fingerprint = experience.generate_fingerprint()
        if fingerprint in self._stored_fingerprints:
            logger.info(
                f"Skipping duplicate experience write for fingerprint '{fingerprint}' "
                f"[{experience.platform}/{experience.content_type}]"
            )
            return None

        content = experience.to_hindsight_content()
        metadata = experience.to_hindsight_metadata()
        tags = list(experience.tags)
        if experience.platform not in tags:
            tags.append(experience.platform)
        if experience.content_type not in tags:
            tags.append(experience.content_type)
        if experience.topic and experience.topic not in tags:
            tags.append(experience.topic)

        memory_id = self.client.retain(
            bank_id=experience.bank_id,
            content=content,
            context=f"Outcome: {experience.observed_outcome}",
            metadata=metadata,
            tags=tags,
        )
        self._stored_fingerprints.add(fingerprint)
        logger.info(
            f"Stored experience in Hindsight bank '{experience.bank_id}' with ID '{memory_id}'"
        )
        return memory_id
