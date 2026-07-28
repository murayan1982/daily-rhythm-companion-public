from __future__ import annotations

from typing import NoReturn

from fastapi import APIRouter, HTTPException, Request, status

from app.config import AppConfig, load_config
from app.models.voice_input_demo import (
    VoiceInputDemoRequest,
    VoiceInputDemoRequestResponse,
    VoiceInputDemoStatusResponse,
    VoiceInputFakeHandoffRequest,
    VoiceInputFakeHandoffResponse,
    VoiceInputStagingProblem,
    VoiceInputStagingUploadResponse,
)
from app.services.voice_input_demo_service import VoiceInputDemoService
from app.services.framework_voice_input_fake_handoff import (
    FrameworkVoiceInputFakeHandoffAdapter,
    FrameworkVoiceInputFakeHandoffError,
    FrameworkVoiceInputFakeHandoffRequest as ServiceFakeHandoffRequest,
)
from app.services.voice_input_staging_store import (
    VoiceInputStagingError,
    VoiceInputStagingStore,
)

router = APIRouter()

_MAX_CAPTURE_DURATION_MS = 15000
_EXPECTED_SAMPLE_RATE_HZ = 16000
_EXPECTED_CHANNEL_COUNT = 1


@router.get("/demo/voice-input/status", response_model=VoiceInputDemoStatusResponse)
def get_voice_input_demo_status():
    """Return the guarded v0.34.0 voice input demo boundary status."""

    return VoiceInputDemoService(load_config()).build_status()


@router.post("/demo/voice-input", response_model=VoiceInputDemoRequestResponse)
def create_voice_input_demo_request(request: VoiceInputDemoRequest):
    """Accept a metadata-only voice input demo request.

    This endpoint is intentionally a safe contract placeholder. It does not
    process audio yet; it returns the current capability status and a clear
    not-started result for the future Flutter voice trigger flow.
    """

    return VoiceInputDemoService(load_config()).submit_request(request)


@router.post(
    "/demo/voice-input/staging",
    response_model=VoiceInputStagingUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def stage_voice_input_demo_audio(
    request: Request,
) -> VoiceInputStagingUploadResponse:
    """Stream one guarded WAV body into the private Backend staging store.

    The route accepts no multipart form, client path, capture ID, API key, or
    provider payload. It returns only a server-generated opaque staging ID and
    safe audio metadata. Framework import and STT remain outside this boundary.
    """

    config = load_config()
    _require_staging_upload_enabled(config)

    media_type = _normalized_media_type(request.headers.get("content-type"))
    if media_type != "audio/wav":
        _raise_staging_problem(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            "unsupported_media_type",
            "Voice-input staging requires Content-Type: audio/wav.",
        )

    audio_format = _required_header(request, "x-drc-audio-format")
    if audio_format.strip().lower().lstrip(".") != "wav":
        _raise_staging_problem(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            "unsupported_audio_format",
            "Voice-input staging accepts WAV audio only.",
        )

    sample_rate_hz = _required_positive_int_header(
        request,
        "x-drc-sample-rate-hz",
    )
    channel_count = _required_positive_int_header(
        request,
        "x-drc-channel-count",
    )
    duration_ms = _required_positive_int_header(
        request,
        "x-drc-duration-ms",
    )
    if sample_rate_hz != _EXPECTED_SAMPLE_RATE_HZ:
        _raise_staging_problem(
            status.HTTP_400_BAD_REQUEST,
            "unsupported_sample_rate",
            "Voice-input staging requires a 16000 Hz WAV artifact.",
        )
    if channel_count != _EXPECTED_CHANNEL_COUNT:
        _raise_staging_problem(
            status.HTTP_400_BAD_REQUEST,
            "unsupported_channel_count",
            "Voice-input staging requires a mono WAV artifact.",
        )
    if duration_ms > _MAX_CAPTURE_DURATION_MS:
        _raise_staging_problem(
            status.HTTP_400_BAD_REQUEST,
            "capture_duration_exceeded",
            "Voice-input staging accepts at most 15000 ms of audio.",
        )

    declared_length = _optional_content_length(request)
    if (
        declared_length is not None
        and declared_length > config.voice_input_staging_max_bytes
    ):
        _raise_staging_problem(
            413,
            "artifact_too_large",
            "Voice-input audio exceeded the configured staging byte limit.",
        )

    store = _create_voice_input_staging_store(config)
    try:
        artifact = await store.stage_async_chunks(
            request.stream(),
            audio_format="wav",
            media_type=media_type,
        )
    except VoiceInputStagingError as exc:
        _raise_store_error(exc)

    return VoiceInputStagingUploadResponse(
        accepted=True,
        request_state="staged",
        staging_id=artifact.staging_id,
        audio_format=artifact.audio_format,
        media_type=artifact.media_type,
        byte_count=artifact.byte_count,
        sample_rate_hz=sample_rate_hz,
        channel_count=channel_count,
        duration_ms=duration_ms,
        expires_in_seconds=config.voice_input_staging_ttl_seconds,
    )


@router.post(
    "/demo/voice-input/staging/{staging_id}/fake-handoff",
    response_model=VoiceInputFakeHandoffResponse,
)
def fake_transcribe_staged_voice_input(
    staging_id: str,
    request: VoiceInputFakeHandoffRequest,
) -> VoiceInputFakeHandoffResponse:
    """Consume one staged artifact through FW's public fake STT session.

    This route explicitly selects ``FakeVoiceInputProviderAdapter``. It passes
    the private Backend path only inside the single-use staging consume scope,
    returns no path or staging ID, closes the FW session, and performs no real
    provider execution or real STT.
    """

    config = load_config()
    _require_staging_upload_enabled(config)
    store = _create_voice_input_staging_store(config)
    adapter = _create_framework_voice_input_fake_handoff_adapter(config, store)

    try:
        result = adapter.transcribe_staged_artifact(
            ServiceFakeHandoffRequest(
                staging_id=staging_id,
                language=request.language,
                duration_ms=request.duration_ms,
                max_duration_ms=_MAX_CAPTURE_DURATION_MS,
            )
        )
    except FrameworkVoiceInputFakeHandoffError as exc:
        _raise_fake_handoff_error(exc)

    return VoiceInputFakeHandoffResponse(
        accepted=result.status == "completed",
        request_state=result.request_state,
        outcome=result.outcome,
        transcript=result.transcript,
        language=result.language,
        duration_ms=result.duration_ms,
        public_error_code=result.public_error_code,
        safe_message=result.safe_message,
        retryable=result.retryable,
        framework_api_name=result.framework_api_name,
        adapter_name=result.adapter_name,
        fake_transcription_completed=result.fake_transcription_completed,
        staged_artifact_consumed=result.staged_artifact_consumed,
        session_closed=result.session_closed,
        audio_read=result.audio_read,
        microphone_accessed=result.microphone_accessed,
        provider_execution_executed=result.provider_execution_executed,
        stt_executed=result.stt_executed,
    )


def _create_voice_input_staging_store(config: AppConfig) -> VoiceInputStagingStore:
    return VoiceInputStagingStore(config=config)


def _create_framework_voice_input_fake_handoff_adapter(
    config: AppConfig,
    store: VoiceInputStagingStore,
) -> FrameworkVoiceInputFakeHandoffAdapter:
    return FrameworkVoiceInputFakeHandoffAdapter(config, store)


def _require_staging_upload_enabled(config: AppConfig) -> None:
    if not config.voice_input_demo_enabled:
        _raise_staging_problem(
            status.HTTP_403_FORBIDDEN,
            "voice_input_staging_disabled",
            "Voice-input staging is disabled.",
        )
    if config.conversation_engine.strip().lower() != "framework":
        _raise_staging_problem(
            status.HTTP_409_CONFLICT,
            "voice_input_engine_not_framework",
            "Voice-input staging requires framework conversation mode.",
        )
    if config.voice_input_adapter_mode.strip().lower() != "framework":
        _raise_staging_problem(
            status.HTTP_409_CONFLICT,
            "voice_input_adapter_not_framework",
            "Voice-input staging requires the framework voice-input adapter mode.",
        )


def _normalized_media_type(value: str | None) -> str:
    return (value or "").strip().lower().split(";", 1)[0].strip()


def _required_header(request: Request, name: str) -> str:
    value = request.headers.get(name)
    if value is None or not value.strip():
        _raise_staging_problem(
            status.HTTP_400_BAD_REQUEST,
            "missing_audio_metadata",
            "Voice-input staging requires complete safe audio metadata headers.",
        )
    return value


def _required_positive_int_header(request: Request, name: str) -> int:
    value = _required_header(request, name)
    try:
        parsed = int(value.strip())
    except ValueError:
        parsed = 0
    if parsed <= 0:
        _raise_staging_problem(
            status.HTTP_400_BAD_REQUEST,
            "invalid_audio_metadata",
            "Voice-input staging received invalid safe audio metadata.",
        )
    return parsed


def _optional_content_length(request: Request) -> int | None:
    value = request.headers.get("content-length")
    if value is None or not value.strip():
        return None
    try:
        parsed = int(value.strip())
    except ValueError:
        _raise_staging_problem(
            status.HTTP_400_BAD_REQUEST,
            "invalid_content_length",
            "Voice-input staging received an invalid Content-Length header.",
        )
    if parsed < 0:
        _raise_staging_problem(
            status.HTTP_400_BAD_REQUEST,
            "invalid_content_length",
            "Voice-input staging received an invalid Content-Length header.",
        )
    return parsed


def _raise_fake_handoff_error(error: FrameworkVoiceInputFakeHandoffError) -> None:
    status_code = {
        "invalid_staging_id": status.HTTP_400_BAD_REQUEST,
        "artifact_not_found": status.HTTP_404_NOT_FOUND,
        "unexpected_fake_handoff_contract": status.HTTP_502_BAD_GATEWAY,
        "unsafe_fake_handoff_result": status.HTTP_502_BAD_GATEWAY,
    }.get(error.code, status.HTTP_503_SERVICE_UNAVAILABLE)
    _raise_staging_problem(
        status_code,
        error.code,
        str(error),
        retryable=error.retryable,
    )


def _raise_store_error(error: VoiceInputStagingError) -> None:
    status_code = {
        "unsupported_audio_format": status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        "unsupported_media_type": status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        "artifact_too_large": 413,
        "empty_audio": status.HTTP_400_BAD_REQUEST,
        "invalid_wav_header": status.HTTP_400_BAD_REQUEST,
        "invalid_audio_chunk": status.HTTP_400_BAD_REQUEST,
    }.get(error.code, status.HTTP_503_SERVICE_UNAVAILABLE)
    _raise_staging_problem(
        status_code,
        error.code,
        str(error),
        retryable=status_code >= 500,
    )


def _raise_staging_problem(
    status_code: int,
    code: str,
    message: str,
    *,
    retryable: bool = False,
) -> NoReturn:
    problem = VoiceInputStagingProblem(
        code=code,
        message=message,
        retryable=retryable,
    )
    raise HTTPException(status_code=status_code, detail=problem.model_dump())
