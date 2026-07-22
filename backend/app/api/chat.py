from fastapi import APIRouter, HTTPException

from app.models.chat import (
    ChatMessageRequest,
    ChatMessageResponse,
    ChatSessionCreateRequest,
    ChatSessionResponse,
)
from app.services.post_advice_chat_service import PostAdviceChatService


router = APIRouter(prefix="/chat", tags=["post-advice-chat"])

_chat_service = PostAdviceChatService()


@router.post("/sessions", response_model=ChatSessionResponse)
def create_chat_session(request: ChatSessionCreateRequest) -> ChatSessionResponse:
    """Start a mock-safe optional chat session after an advice result."""

    return _chat_service.create_session(request)


@router.get("/sessions/{session_id}", response_model=ChatSessionResponse)
def get_chat_session(session_id: str) -> ChatSessionResponse:
    """Return the current state of a post-advice chat session."""

    session = _chat_service.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Chat session not found")

    return session


@router.post(
    "/sessions/{session_id}/messages",
    response_model=ChatMessageResponse,
)
def add_chat_message(
    session_id: str,
    request: ChatMessageRequest,
) -> ChatMessageResponse:
    """Add a user message and return a mock-safe character response."""

    response = _chat_service.add_message(session_id=session_id, request=request)
    if response is None:
        raise HTTPException(status_code=404, detail="Chat session not found")

    return response
