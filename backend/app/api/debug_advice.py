from threading import Lock
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, ValidationError

from app.config import load_config
from app.models.advice import AdviceRequest
from app.models.character import CharacterContext
from app.models.motion_demo import MotionExpressionId
from app.models.sleep import SleepSummary
from app.services.advice_prompt_builder import build_advice_prompt
from app.services.character_service import CharacterService
from app.services.debug_mina_advice_store import DebugMinaAdviceStore
from app.services.framework_text_chat_drc_live_reply import (
    FrameworkTextChatDrcLiveReplyService,
)
from app.services.mina_voice_output import MINA_VOICE_OUTPUT_MODE
from app.services.voice_output_demo_service import VoiceOutputDemoService


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


class DebugMinaAdviceRequest(DebugAdviceRequest):
    character_id: Literal["gentle_mina"]


class DebugMinaAdviceResponse(DebugAdviceResponse):
    voice_ref: str


class DebugMinaVoiceRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    voice_ref: str = Field(min_length=32, max_length=32, pattern=r"^[A-Za-z0-9_-]+$")


class DebugMinaVoiceResponse(BaseModel):
    accepted: bool
    audio_ready: bool
    audio_format: str | None
    audio_url: str | None


router = APIRouter(prefix="/debug")
config = load_config()
characters = {preset.character_id: preset for preset in CharacterService().list_presets()}
provider_lock = Lock()
mina_advice = DebugMinaAdviceStore()


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


@router.post("/mina/ai-advice", response_model=DebugMinaAdviceResponse)
def create_debug_mina_advice(
    request: DebugMinaAdviceRequest,
    response: Response,
    provider: Annotated[FrameworkTextChatDrcLiveReplyService, Depends(get_debug_advice_provider)],
) -> DebugMinaAdviceResponse:
    advice = create_debug_advice(request, provider)
    response.headers["Cache-Control"] = "no-store"
    return DebugMinaAdviceResponse(
        message=advice.message,
        expression_tag=advice.expression_tag,
        voice_ref=mina_advice.issue(advice.message),
    )


@router.post("/mina/voice", response_model=DebugMinaVoiceResponse)
def create_debug_mina_voice(request: DebugMinaVoiceRequest) -> DebugMinaVoiceResponse:
    if not config.debug_ai_advice_enabled:
        raise HTTPException(status_code=503, detail="Debug AI advice is disabled.")
    voice_config = load_config()
    if voice_config.voice_output_adapter_mode.strip().lower() != MINA_VOICE_OUTPUT_MODE:
        raise HTTPException(status_code=503, detail="Debug Mina voice is disabled.")
    message = mina_advice.resolve(request.voice_ref)
    if message is None:
        raise HTTPException(status_code=404, detail="Mina advice reference is unavailable.")
    result = VoiceOutputDemoService(voice_config).submit_generated_mina(message)
    return DebugMinaVoiceResponse(
        accepted=result.accepted,
        audio_ready=result.audio_ready,
        audio_format=result.audio_format,
        audio_url=result.audio_url,
    )
