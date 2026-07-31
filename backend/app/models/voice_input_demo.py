from typing import Any

from pydantic import BaseModel, Field

from app.models.demo_status import CapabilityStatus


class VoiceInputDemoProbeCheck(BaseModel):
    """Single safe-readiness check for the voice input demo boundary."""

    name: str
    status: str
    message: str


class VoiceInputDemoStatusResponse(BaseModel):
    """App-facing status for the v0.34.0 voice input demo boundary."""

    engine: str
    mode: str
    adapter_mode: str
    capability: CapabilityStatus
    checks: list[VoiceInputDemoProbeCheck] = Field(default_factory=list)
    candidate_paths: list[str] = Field(default_factory=list)
    public_api_candidates: list[str] = Field(default_factory=list)


class VoiceInputDemoRequest(BaseModel):
    """Metadata-only request for the guarded voice input demo path.

    The request intentionally does not contain raw audio bytes. Day3 only
    establishes the backend contract that a future Flutter voice button can
    call. The backend must not read local audio paths, open a microphone, or
    import FW audio modules from this model alone.
    """

    client_event_id: str | None = None
    input_mode: str = "demo_button"
    audio_format: str | None = None
    sample_rate_hz: int | None = Field(default=None, ge=0)
    duration_ms: int | None = Field(default=None, ge=0)
    text_hint: str | None = None
    audio_reference: str | None = None


class VoiceInputDemoRequestResponse(BaseModel):
    """Result of attempting to start a guarded voice input demo request."""

    accepted: bool
    request_state: str
    engine: str
    mode: str
    adapter_mode: str
    input_mode: str
    client_event_id: str | None = None
    capability: CapabilityStatus
    transcript: str | None = None
    message: str
    checks: list[VoiceInputDemoProbeCheck] = Field(default_factory=list)
    candidate_paths: list[str] = Field(default_factory=list)
    public_api_candidates: list[str] = Field(default_factory=list)


class VoiceInputStagingUploadResponse(BaseModel):
    """Path-free result for one guarded private Backend staging upload."""

    accepted: bool
    request_state: str
    staging_id: str
    audio_format: str
    media_type: str
    byte_count: int = Field(ge=1)
    sample_rate_hz: int = Field(ge=1)
    channel_count: int = Field(ge=1)
    duration_ms: int = Field(ge=1)
    expires_in_seconds: int = Field(ge=1)


class VoiceInputStagingProblem(BaseModel):
    """Public-safe error detail for the guarded staging upload boundary."""

    code: str
    message: str
    retryable: bool = False

class VoiceInputFakeHandoffRequest(BaseModel):
    """Safe metadata for one fake FW public-session handoff."""

    language: str | None = Field(default="ja-JP", max_length=32)
    duration_ms: int | None = Field(default=None, ge=1, le=15000)


class VoiceInputFakeHandoffResponse(BaseModel):
    """Path-free result from one single-use fake FW handoff."""

    accepted: bool
    request_state: str
    outcome: str
    transcript: str
    language: str | None = None
    duration_ms: int | None = Field(default=None, ge=0)
    public_error_code: str
    safe_message: str
    retryable: bool
    framework_api_name: str
    adapter_name: str
    fake_transcription_completed: bool
    staged_artifact_consumed: bool
    session_closed: bool
    audio_read: bool
    microphone_accessed: bool
    provider_execution_executed: bool
    stt_executed: bool

class VoiceInputOpenAIFakeExecutorRequest(BaseModel):
    """Safe metadata for one bounded FW OpenAI marked-fake execution."""

    language: str | None = Field(default="ja", max_length=32)
    duration_ms: int | None = Field(default=None, ge=1, le=15000)


class VoiceInputOpenAIFakeExecutorResponse(BaseModel):
    """Path-free result from one single-use bounded marked-fake execution."""

    accepted: bool
    request_state: str
    outcome: str
    transcript: str
    language: str | None = None
    duration_ms: int | None = Field(default=None, ge=0)
    public_error_code: str
    safe_message: str
    retryable: bool
    framework_api_name: str
    adapter_name: str
    executor_name: str
    fake_transcription_completed: bool
    fake_provider_protocol_call_executed: bool
    staged_artifact_consumed: bool
    audio_read: bool
    audio_bytes_read: int = Field(ge=0)
    microphone_accessed: bool
    provider_sdk_imported: bool
    provider_client_created: bool
    credential_values_read: bool
    real_provider_execution_executed: bool
    fake_stt_executed: bool
    real_stt_executed: bool


class VoiceInputRealTranscriptRequest(BaseModel):
    """Provider-neutral request for one single-use staged real transcript."""

    staging_id: Any = Field(repr=False)
    foreground_opt_in: bool
    language: str | None = Field(default="ja", max_length=32)
    duration_ms: int | None = Field(default=None, ge=1, le=15000)


class VoiceInputRealTranscriptResponse(BaseModel):
    """Minimal no-store final transcript response for the Flutter handoff."""

    accepted: bool
    request_state: str
    result_id: str = Field(pattern=r"^[0-9a-f]{32}$")
    text: str = Field(min_length=1, max_length=4096, repr=False)
    is_final: bool
