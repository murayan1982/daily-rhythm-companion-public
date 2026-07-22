from abc import ABC, abstractmethod

from app.models.sleep import SleepSummary


class SleepProvider(ABC):
    """Base interface for sleep summary providers."""

    @abstractmethod
    def get_sleep_summary(self) -> SleepSummary:
        """Return a sleep summary for the current app flow."""