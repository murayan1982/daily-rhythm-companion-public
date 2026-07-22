class ConversationEngineError(RuntimeError):
    """Base error for conversation engine failures."""


class FrameworkEngineError(ConversationEngineError):
    """Raised when the AI Character Framework engine fails."""