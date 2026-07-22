from app.config import AppConfig
from app.services.sleep_providers.base import SleepProvider
from app.services.sleep_providers.fitbit import FitbitSleepProvider
from app.services.sleep_providers.fitbit_stub import FitbitStubSleepProvider
from app.services.sleep_providers.google_health import GoogleHealthSleepProvider
from app.services.sleep_providers.mock import MockSleepProvider
from app.services.sleep_providers.wearable_stub import WearableStubSleepProvider

RECOMMENDED_SLEEP_PROVIDERS = ("mock", "wearable_stub", "google_health")
DEPRECATED_SLEEP_PROVIDER_ALIASES = {"fitbit_stub": "wearable_stub"}
LEGACY_SLEEP_PROVIDERS = ("fitbit",)
SUPPORTED_SLEEP_PROVIDERS = (
    *RECOMMENDED_SLEEP_PROVIDERS,
    *DEPRECATED_SLEEP_PROVIDER_ALIASES.keys(),
    *LEGACY_SLEEP_PROVIDERS,
)


def create_sleep_provider(config: AppConfig) -> SleepProvider:
    """
    Create the configured sleep provider.

    Public MVP configuration should prefer:
    - mock
    - wearable_stub

    fitbit_stub is kept as a temporary backward-compatible alias for older
    local configuration. fitbit is a legacy migration/reference provider and
    should not be presented as the recommended public integration path.
    """

    provider_name = config.sleep_provider.strip().lower()

    if provider_name == "mock":
        return MockSleepProvider()

    if provider_name == "wearable_stub":
        return WearableStubSleepProvider()

    if provider_name == "fitbit_stub":
        return FitbitStubSleepProvider()

    if provider_name == "fitbit":
        return FitbitSleepProvider()

    if provider_name == "google_health":
        return GoogleHealthSleepProvider(config)

    supported = ", ".join(SUPPORTED_SLEEP_PROVIDERS)
    raise ValueError(
        f"Unsupported sleep provider: {config.sleep_provider}. "
        f"Supported values: {supported}"
    )
