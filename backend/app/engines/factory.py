from app.config import AppConfig
from app.engines.base import ConversationEngine
from app.engines.framework_engine import FrameworkConversationEngine
from app.engines.mock_engine import MockConversationEngine


def create_conversation_engine(config: AppConfig) -> ConversationEngine:
    """
    Create the configured conversation engine.

    Supported engines:
    - mock: deterministic development engine
    - framework: adapter boundary for the AI Character Conversation Framework
    """

    if config.conversation_engine == "mock":
        return MockConversationEngine()

    if config.conversation_engine == "framework":
        return FrameworkConversationEngine(config=config)

    raise ValueError(
        f"Unsupported conversation engine: {config.conversation_engine}"
    )