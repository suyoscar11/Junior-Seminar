from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import UTC, datetime


@dataclass(frozen=True)
class PublishResult:
    external_id: str
    published_at: str


class DemoConnector:
    """Deterministic connector used for demos and automated tests.

    Production connectors can implement the same publish method after OAuth and
    platform review. No credentials are required for the semester demonstration.
    """

    def __init__(self, platform: str):
        self.platform = platform

    def publish(self, post_id: int, caption: str) -> PublishResult:
        fingerprint = hashlib.sha256(f"{self.platform}:{post_id}:{caption}".encode()).hexdigest()[:12]
        return PublishResult(
            external_id=f"demo_{self.platform}_{fingerprint}",
            published_at=datetime.now(UTC).isoformat(),
        )


def connector_for(platform: str) -> DemoConnector:
    if platform not in {"instagram", "tiktok", "x"}:
        raise ValueError(f"Unsupported platform: {platform}")
    return DemoConnector(platform)

