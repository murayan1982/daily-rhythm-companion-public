from __future__ import annotations

from app.config import AppConfig
from app.models.sleep import SleepSummary
from app.services.google_health_sleep_source import fetch_google_health_sleep_summary
from app.services.sleep_providers.base import SleepProvider


class GoogleHealthSleepProvider(SleepProvider):
    """
    Google Health sleep provider boundary.

    This provider delegates OAuth refresh and API request preparation to the
    Google Health source/session services. It returns only the app-facing
    SleepSummary shape and does not expose raw Google Health payloads.
    """

    def __init__(self, config: AppConfig):
        self._config = config

    def get_sleep_summary(self) -> SleepSummary:
        result = fetch_google_health_sleep_summary(config=self._config)
        return result.summary
