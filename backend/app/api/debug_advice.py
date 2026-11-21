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
from app.services.debug_advice_voice_store import DebugAdviceVoiceStore
from app.services.framework_text_chat_drc_live_reply import (
    FrameworkTextChatDrcLiveReplyService,
)
from app.services.mina_voice_output import MINA_VOICE_OUTPUT_MODE
from app.services.voice_output_demo_service import VoiceOutputDemoService


class SyntheticSleepSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    total_sleep_minutes: int = Field(strict=True, ge=0, le=1440)


DebugCharacterId = Literal["gentle_mina", "cheerful_sora", "cool_rei"]


class DebugAdviceRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    mood: Literal["energetic", "normal", "tired"]
    character_id: DebugCharacterId
    sleep_summary: SyntheticSleepSummary | None = None


class DebugAdviceResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    message: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=240)]
    expression_tag: MotionExpressionId


class DebugMinaAdviceRequest(DebugAdviceRequest):
    character_id: Literal["gentle_mina"]


class DebugMinaAdviceResponse(DebugAdviceResponse):
    voice_ref: str


class DebugCharacterAdviceResponse(DebugAdviceResponse):
    voice_ref: str | None


class DebugMinaVoiceRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    voice_ref: str = Field(min_length=32, max_length=32, pattern=r"^[A-Za-z0-9_-]+$")


class DebugCharacterVoiceRequest(DebugMinaVoiceRequest):
    character_id: DebugCharacterId


class DebugMinaVoiceResponse(BaseModel):
    accepted: bool
    audio_ready: bool
    audio_format: str | None
    audio_url: str | None


router = APIRouter(prefix="/debug")
config = load_config()
characters = {preset.character_id: preset for preset in CharacterService().list_presets()}
provider_lock = Lock()
advice_voice = DebugAdviceVoiceStore()


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
        voice_ref=advice_voice.issue(request.character_id, advice.message),
    )


@router.post("/mina/voice", response_model=DebugMinaVoiceResponse)
def create_debug_mina_voice(request: DebugMinaVoiceRequest) -> DebugMinaVoiceResponse:
    return _play_advice("gentle_mina", request.voice_ref, legacy_mina=True)


@router.post("/character/ai-advice", response_model=DebugCharacterAdviceResponse)
def create_debug_character_advice(
    request: DebugAdviceRequest,
    response: Response,
    provider: Annotated[FrameworkTextChatDrcLiveReplyService, Depends(get_debug_advice_provider)],
) -> DebugCharacterAdviceResponse:
    advice = create_debug_advice(request, provider)
    service = VoiceOutputDemoService(load_config())
    voice_ref = (
        advice_voice.issue(request.character_id, advice.message)
        if service.generated_voice_available(request.character_id)
        else None
    )
    response.headers["Cache-Control"] = "no-store"
    return DebugCharacterAdviceResponse(
        message=advice.message, expression_tag=advice.expression_tag, voice_ref=voice_ref
    )


@router.post("/character/voice", response_model=DebugMinaVoiceResponse)
def create_debug_character_voice(
    request: DebugCharacterVoiceRequest,
) -> DebugMinaVoiceResponse:
    return _play_advice(request.character_id, request.voice_ref)


def _play_advice(
    character_id: str, ref: str, *, legacy_mina: bool = False
) -> DebugMinaVoiceResponse:
    if not config.debug_ai_advice_enabled:
        raise HTTPException(status_code=503, detail="Debug AI advice is disabled.")
    voice_config = load_config()
    if voice_config.voice_output_adapter_mode.strip().lower() != MINA_VOICE_OUTPUT_MODE:
        detail = "Debug Mina voice is disabled." if legacy_mina else "Debug character voice is disabled."
        raise HTTPException(status_code=503, detail=detail)
    message = advice_voice.resolve(ref, character_id)
    if message is None:
        detail = (
            "Mina advice reference is unavailable."
            if legacy_mina
            else "Character advice reference is unavailable."
        )
        raise HTTPException(status_code=404, detail=detail)
    result = VoiceOutputDemoService(voice_config).submit_generated_voice(character_id, message)
    return DebugMinaVoiceResponse(
        accepted=bool(result and result.audio_ready),
        audio_ready=bool(result and result.audio_ready),
        audio_format=result.audio_format if result else None,
        audio_url=result.audio_url if result else None,
    )
