from app.config import AppConfig
from app.models.sleep import SleepSummary
from app.services.sleep_providers.factory import create_sleep_provider


def get_sleep_summary(config: AppConfig) -> SleepSummary:
    """Return a sleep summary from the configured provider."""

    provider = create_sleep_provider(config)
    return provider.get_sleep_summary()