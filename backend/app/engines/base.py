from abc import ABC, abstractmethod

from app.models.advice import AdviceRequest, AdviceResponse


class ConversationEngine(ABC):
    """
    Base interface for conversation engines.

    App APIs should depend on this interface instead of depending directly
    on a specific implementation such as MockConversationEngine.
    """

    @abstractmethod
    def create_advice(self, request: AdviceRequest) -> AdviceResponse:
        """Create daily advice from character, sleep, and mood context."""
        raise NotImplementedError