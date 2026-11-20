from threading import Lock
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, ValidationError

from app.config import load_config
from app.models.advice import AdviceRequest
from app.models.character import CharacterContext
from app.models.motion_demo import MotionExpressionId
from app.models.sleep import SleepSummary
from app.services.advice_prompt_builder import build_advice_prompt
from app.services.character_service import CharacterService
from app.services.framework_text_chat_drc_live_reply import (
    FrameworkTextChatDrcLiveReplyService,
)


class SyntheticSleepSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    total_sleep_minutes: int = Field(strict=True, ge=0, le=1440)


class DebugAdviceRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    mood: Literal["energetic", "normal", "tired"]
    character_id: Literal["gentle_mina", "cheerful_sora", "cool_rei"]
    sleep_summary: SyntheticSleepSummary | None = None


class DebugAdviceResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    message: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=240)]
    expression_tag: MotionExpressionId


router = APIRouter(prefix="/debug")
config = load_config()
characters = {preset.character_id: preset for preset in CharacterService().list_presets()}
provider_lock = Lock()


def get_debug_advice_provider() -> FrameworkTextChatDrcLiveReplyService:
    if not config.debug_ai_advice_enabled:
        raise HTTPException(status_code=503, detail="Debug AI advice is disabled.")
    return FrameworkTextChatDrcLiveReplyService(config)


@router.post("/ai-advice", response_model=DebugAdviceResponse)
def create_debug_advice(
    request: DebugAdviceRequest,
    provider: Annotated[FrameworkTextChatDrcLiveReplyService, Depends(get_debug_advice_provider)],
) -> DebugAdviceResponse:
    character = CharacterContext.model_validate(
        characters[request.character_id], from_attributes=True
    )
    sleep = request.sleep_summary
    prompt = build_advice_prompt(
        AdviceRequest(
            character=character,
            mood=request.mood,
            sleep=SleepSummary(
                date="not supplied",
                total_sleep_minutes=sleep.total_sleep_minutes if sleep else 0,
                available=sleep is not None,
            ),
        )
    )
    expression_tags = ", ".join(tag.value for tag in MotionExpressionId)
    prompt += (
        "\n\nThis is a development request using synthetic input. "
        "Return only a JSON object with exactly two fields. "
        '"message" must be one or two short Japanese sentences, at most 240 characters. '
        f'"expression_tag" must be one of: {expression_tags}. '
        "Use the character's voice and choose a tag that fits the message. "
        "Do not wrap the JSON in Markdown."
    )

    try:
        # The existing adapter uses a fresh session and temporarily changes the
        # working directory. Serialize calls made by this development route.
        with provider_lock:
            result = provider.reply(prompt=prompt)
    except Exception:
        raise HTTPException(status_code=502, detail="AI advice generation failed.") from None

    if result.status.startswith("blocked-"):
        raise HTTPException(status_code=503, detail="AI advice provider is unavailable.")
    if result.status != "responded":
        raise HTTPException(status_code=502, detail="AI advice generation failed.")

    try:
        return DebugAdviceResponse.model_validate_json(result.reply_text)
    except ValidationError:
        raise HTTPException(status_code=502, detail="Invalid AI advice response.") from None
