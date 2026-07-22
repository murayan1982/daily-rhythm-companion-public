from pydantic import BaseModel, Field

from app.models.demo_status import CapabilityStatus


class VoiceOutputDemoProbeCheck(BaseModel):
    """Single safe-readiness check for the voice output demo boundary."""

    name: str
    status: str
    message: str


class VoiceOutputDemoStatusResponse(BaseModel):
    """App-facing status for the voice output demo boundary."""

    engine: str
    mode: str
    adapter_mode: str
    real_tts_enabled: bool = False
    capability: CapabilityStatus
    checks: list[VoiceOutputDemoProbeCheck] = Field(default_factory=list)
    candidate_paths: list[str] = Field(default_factory=list)
    public_api_candidates: list[str] = Field(default_factory=list)


class VoiceOutputDemoRequest(BaseModel):
    """Guarded request for the voice output demo path.

    The request shape is intentionally provider-neutral. DRC may forward it to
    an AI Character Framework public voice output boundary only when explicit
    real TTS opt-in is enabled. Provider voice IDs, API keys, provider-specific
    parameters, and raw payload handling remain framework responsibilities.
    """

    output_mode: str = Field(
        default="tts",
        description="Requested output mode (for example, 'tts' or 'voice_synthesis').",
    )
    client_event_id: str | None = Field(
        default=None,
        description="Optional client-side event ID for request correlation.",
    )
    text_content: str | None = Field(
        default=None,
        description="Optional text content to synthesize through the FW boundary.",
    )
    character_id: str | None = Field(
        default=None,
        description="Optional DRC character ID associated with the requested voice output.",
    )
    voice_profile_id: str | None = Field(
        default=None,
        description="Optional neutral voice profile ID resolved by the framework.",
    )
    audio_format: str | None = Field(
        default=None,
        description="Optional requested audio format, such as 'wav' or 'mp3'.",
    )
    utterance_purpose: str | None = Field(
        default=None,
        description="Optional neutral purpose label, such as 'demo' or 'daily_advice'.",
    )


class VoiceOutputDemoRequestResponse(BaseModel):
    """Response to a guarded voice output demo request."""

    accepted: bool = False
    request_state: str = "not_started"
    engine: str
    mode: str
    adapter_mode: str
    real_tts_enabled: bool = False
    output_mode: str
    client_event_id: str | None = None
    text_content: str | None = None
    character_id: str | None = None
    voice_profile_id: str | None = None
    requested_audio_format: str | None = None
    utterance_purpose: str | None = None
    framework_call_state: str = "not_called"
    framework_api_name: str | None = None
    audio_url: str | None = None
    audio_artifact_ref: str | None = None
    audio_format: str | None = None
    audio_ready: bool = False
    audio_handoff_kind: str = "none"
    has_audio_handoff: bool = False
    is_generated: bool = False
    audio_playback_status: str = "not_started"
    evidence_status: str = "not_evidence"
    request_warnings: list[str] = Field(default_factory=list)
    runtime_notes: list[str] = Field(default_factory=list)
    message: str
    capability: CapabilityStatus
    checks: list[VoiceOutputDemoProbeCheck] = Field(default_factory=list)
    candidate_paths: list[str] = Field(default_factory=list)
    public_api_candidates: list[str] = Field(default_factory=list)
