from app.models.sleep import SleepSummary
from app.services.sleep_providers.base import SleepProvider


class MockSleepProvider(SleepProvider):
    """Deterministic sleep provider for local development and tests."""

    def get_sleep_summary(self) -> SleepSummary:
        return SleepSummary(
            date="2026-04-28",
            total_sleep_minutes=372,
            efficiency=86,
            deep_sleep_minutes=52,
            rem_sleep_minutes=78,
            awake_minutes=31,
            source="mock",
            available=True,
            message="Mock sleep summary is available.",
        )