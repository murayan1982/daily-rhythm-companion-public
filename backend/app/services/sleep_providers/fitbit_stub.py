from app.models.sleep import SleepSummary
from app.services.sleep_providers.base import SleepProvider
from app.services.sleep_providers.wearable_stub import WearableStubSleepProvider


class FitbitStubSleepProvider(SleepProvider):
    """
    Deprecated compatibility alias for WearableStubSleepProvider.

    This provider name is kept temporarily so older local `.env` files using
    SLEEP_PROVIDER=fitbit_stub keep working during the provider rename.
    New local configuration should use:

    SLEEP_PROVIDER=wearable_stub
    """

    def __init__(self) -> None:
        self._delegate = WearableStubSleepProvider()

    def get_sleep_summary(self) -> SleepSummary:
        summary = self._delegate.get_sleep_summary()

        return summary.model_copy(
            update={
                "source": "fitbit_stub",
                "message": (
                    "Deprecated sleep provider alias 'fitbit_stub' is active. "
                    "Use SLEEP_PROVIDER=wearable_stub for new local setup."
                ),
            }
        )
