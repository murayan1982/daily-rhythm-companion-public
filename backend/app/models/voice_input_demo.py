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
