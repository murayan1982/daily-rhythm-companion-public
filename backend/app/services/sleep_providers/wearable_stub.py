from app.models.sleep import SleepSummary
from app.services.sleep_providers.base import SleepProvider


class WearableStubSleepProvider(SleepProvider):
    """
    Stub sleep provider for future wearable integrations.

    This does not call any real wearable or health API. It returns
    deterministic data so the app can test wearable-shaped sleep summaries
    without depending on external provider availability.
    """

    def get_sleep_summary(self) -> SleepSummary:
        return SleepSummary(
            date="2026-04-28",
            total_sleep_minutes=398,
            efficiency=89,
            deep_sleep_minutes=64,
            rem_sleep_minutes=92,
            awake_minutes=27,
            source="wearable_stub",
            available=True,
            message="Wearable stub sleep summary is available.",
        )