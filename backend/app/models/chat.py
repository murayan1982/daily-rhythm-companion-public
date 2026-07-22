from pydantic import BaseModel

from app.models.advice import AdviceSource
from app.models.character import CharacterContext
from app.models.report_handoff import ReportHandoffContext


class PostAdviceChatContext(BaseModel):
    """Context handed from an advice result into optional character chat."""

    character: CharacterContext
    advice_message: str
    mood: str | None = None
    advice_basis: str | None = None
    advice_source: AdviceSource | None = None
    report_handoff: ReportHandoffContext | None = None
    daily_record_id: str | None = None


class ChatMessage(BaseModel):
    """Single chat message in a post-advice chat session."""

    role: str
    content: str


class ChatSource(BaseModel):
    """App-facing metadata for post-advice chat responses."""

    engine: str
    mode: str
    drc_character_id: str
    drc_character_name: str
    framework_preset: str | None = None
    framework_character: str | None = None
    framework_character_source: str | None = None


class ChatSessionCreateRequest(BaseModel):
    """Request to start an optional chat after an advice result."""

    context: PostAdviceChatContext
    initial_user_message: str | None = None


class ChatSessionResponse(BaseModel):
    """Current state of a post-advice chat session."""

    session_id: str
    status: str
    source: ChatSource
    context: PostAdviceChatContext
    messages: list[ChatMessage]


class ChatMessageRequest(BaseModel):
    """User message sent to an existing post-advice chat session."""

    message: str


class ChatMessageResponse(BaseModel):
    """Assistant reply and updated session state."""

    session_id: str
    reply: ChatMessage
    source: ChatSource
    messages: list[ChatMessage]
