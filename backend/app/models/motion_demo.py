from pydantic import BaseModel, Field

from app.models.demo_status import CapabilityStatus


class MotionBoundaryProbeSummary(BaseModel):
    """No-import probe metadata for future framework/VTS/Live2D motion wiring."""

    framework_root: str | None = None
    framework_root_exists: bool = False
    candidate_paths: list[str] = Field(default_factory=list)
    public_api_candidates: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class MotionDemoStatusResponse(BaseModel):
    """App-facing status for the v0.36.0 Live2D/VTS motion demo boundary."""

    engine: str
    mode: str
    adapter_mode: str
    capability: CapabilityStatus
    supported_motion_events: list[str] = Field(default_factory=list)
    supported_character_ids: list[str] = Field(default_factory=list)
    supported_expression_ids: list[str] = Field(default_factory=list)
    framework_probe: MotionBoundaryProbeSummary | None = None


class MotionDemoRequest(BaseModel):
    """Metadata-only request for the guarded Live2D/VTS motion demo path.

    The request intentionally does not open a VTS WebSocket connection, import
    Live2D runtime dependencies, or send real motion events yet. v0.36 Day3
    makes the future request shape explicit while preserving a safe
    not-started/no-send contract.
    """

    motion_event: str = Field(
        default="idle",
        description="Requested motion event, such as 'greeting', 'thinking', or 'happy'.",
    )
    client_event_id: str | None = Field(
        default=None,
        description="Optional client-side event ID for request correlation.",
    )
    character_id: str | None = Field(
        default=None,
        description="Optional DRC character ID associated with the requested motion.",
    )
    expression_id: str | None = Field(
        default=None,
        description="Optional expression ID for lightweight avatar / future Live2D expression mapping.",
    )
    trigger_source: str | None = Field(
        default="manual",
        description="Optional source of the motion request, such as manual, advice, voice, or system.",
    )
    requested_adapter_mode: str | None = Field(
        default=None,
        description="Optional client-requested target adapter. This is echoed for diagnostics only.",
    )


class MotionDemoRequestResponse(BaseModel):
    """Response to a motion demo request.

    This is intentionally a safe placeholder. It does not connect to VTube
    Studio, load Live2D runtime code, or send motion/expression commands.
    """

    accepted: bool = False
    request_state: str = "not_started"
    engine: str
    mode: str
    adapter_mode: str
    motion_event: str
    client_event_id: str | None = None
    character_id: str | None = None
    expression_id: str | None = None
    trigger_source: str = "manual"
    requested_adapter_mode: str | None = None
    resolved_adapter_mode: str
    motion_sent: bool = False
    vts_connection_used: bool = False
    request_warnings: list[str] = Field(default_factory=list)
    message: str
    capability: CapabilityStatus
    supported_motion_events: list[str] = Field(default_factory=list)
    supported_character_ids: list[str] = Field(default_factory=list)
    supported_expression_ids: list[str] = Field(default_factory=list)
    framework_probe: MotionBoundaryProbeSummary | None = None
