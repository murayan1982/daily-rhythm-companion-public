from fastapi import APIRouter, HTTPException

from app.models.chat import (
    ChatMessageRequest,
    ChatMessageResponse,
    ChatSessionCreateRequest,
    ChatSessionProblem,
    ChatSessionResponse,
)
from app.services.post_advice_chat_service import (
    CHAT_PROBLEM_TURN_LIMIT,
    PostAdviceChatService,
)


router = APIRouter(prefix="/chat", tags=["post-advice-chat"])

_chat_service = PostAdviceChatService()


@router.post("/sessions", response_model=ChatSessionResponse)
def create_chat_session(request: ChatSessionCreateRequest) -> ChatSessionResponse:
    """Start a mock-safe optional chat session after an advice result."""

    return _chat_service.create_session(request)


@router.get("/sessions/{session_id}", response_model=ChatSessionResponse)
def get_chat_session(session_id: str) -> ChatSessionResponse:
    """Return the current state of a post-advice chat session."""

    result = _chat_service.get_session_result(session_id)
    if result.session is None:
        _raise_chat_problem(result.problem)
    return result.session


@router.post(
    "/sessions/{session_id}/messages",
    response_model=ChatMessageResponse,
)
def add_chat_message(
    session_id: str,
    request: ChatMessageRequest,
) -> ChatMessageResponse:
    """Add a user message and return a mock-safe character response."""

    result = _chat_service.add_message_result(session_id=session_id, request=request)
    if result.response is None:
        _raise_chat_problem(result.problem)
    return result.response


def _raise_chat_problem(problem: ChatSessionProblem | None) -> None:
    problem = problem or ChatSessionProblem(
        code="session_not_found",
        message="Chat session not found",
        user_message="この会話を見つけられませんでした。新しい会話を始めてください。",
    )
    status_code = 409 if problem.code == CHAT_PROBLEM_TURN_LIMIT else 404
    raise HTTPException(status_code=status_code, detail=problem.model_dump())
