from __future__ import annotations

from dataclasses import dataclass


TEXT_CHAT_STATUS = "completed"
VOICE_INPUT_STATUS = "boundary-evidence-recorded"
VOICE_OUTPUT_STATUS = "boundary-evidence-recorded"
MOTION_STATUS = "boundary-evidence-recorded"


@dataclass(frozen=True)
class FrameworkFw40CapabilityCoverageAfterMotionInput:
    """Public-safe evidence input after the Day44 motion boundary record.

    The input stores status labels and booleans only. It must not include raw
    audio, generated audio files, audio URLs, transcript bodies, text bodies,
    prompt bodies, response bodies, provider payloads, API key values,
    authorization headers, private paths, raw LAN IPs, raw screenshots,
    microphone captures, playback artifacts, motion payload bodies,
    VTS WebSocket payloads, Live2D runtime state, or provider error payloads.
    """

    text_chat_smartphone_web_completed: bool
    voice_input_boundary_recorded: bool
    voice_output_boundary_recorded: bool
    motion_boundary_recorded: bool
    text_chat_live_runtime_verified: bool
    voice_input_configured_runtime_verified: bool
    voice_output_configured_runtime_verified: bool
    motion_configured_runtime_verified: bool
    public_safe_evidence_only: bool


@dataclass(frozen=True)
class FrameworkFw40CapabilityCoverageAfterMotionResult:
    """Rendered v1.9.0 FW4.0.0 coverage after motion evidence."""

    status: str
    text_chat_status: str
    voice_input_status: str
    voice_output_status: str
    motion_status: str
    text_chat_live_runtime_verified: bool
    voice_input_configured_runtime_verified: bool
    voice_output_configured_runtime_verified: bool
    motion_configured_runtime_verified: bool
    evidence_recorded_count: int
    remaining_boundary_evidence_count: int
    configured_runtime_verified_count: int
    public_safe_evidence_only: bool
    next_focus: str
    safe_summary: str


def evaluate_v190_fw40_capability_coverage_after_motion(
    evidence: FrameworkFw40CapabilityCoverageAfterMotionInput,
) -> FrameworkFw40CapabilityCoverageAfterMotionResult:
    """Evaluate the v1.9.0 FW4.0.0 coverage snapshot after Day44."""

    text_chat_status = TEXT_CHAT_STATUS if evidence.text_chat_smartphone_web_completed else "incomplete"
    voice_input_status = VOICE_INPUT_STATUS if evidence.voice_input_boundary_recorded else "boundary-ready"
    voice_output_status = VOICE_OUTPUT_STATUS if evidence.voice_output_boundary_recorded else "boundary-ready"
    motion_status = MOTION_STATUS if evidence.motion_boundary_recorded else "boundary-ready"

    evidence_recorded_count = sum(
        [
            evidence.text_chat_smartphone_web_completed,
            evidence.voice_input_boundary_recorded,
            evidence.voice_output_boundary_recorded,
            evidence.motion_boundary_recorded,
        ]
    )
    configured_runtime_verified_count = sum(
        [
            evidence.text_chat_live_runtime_verified,
            evidence.voice_input_configured_runtime_verified,
            evidence.voice_output_configured_runtime_verified,
            evidence.motion_configured_runtime_verified,
        ]
    )
    remaining_boundary_evidence_count = 4 - evidence_recorded_count

    complete = (
        evidence.text_chat_smartphone_web_completed
        and evidence.voice_input_boundary_recorded
        and evidence.voice_output_boundary_recorded
        and evidence.motion_boundary_recorded
        and evidence.text_chat_live_runtime_verified
        and not evidence.voice_input_configured_runtime_verified
        and not evidence.voice_output_configured_runtime_verified
        and not evidence.motion_configured_runtime_verified
        and evidence.public_safe_evidence_only
    )
    status = (
        "fw40-smartphone-web-capability-evidence-complete"
        if complete
        else "needs-fw40-capability-coverage-review-after-motion"
    )
    next_focus = "v190-release-readiness" if complete else "review-fw40-capability-coverage"
    safe_summary = (
        "v1.9.0 FW4.0.0 capability coverage is complete for the public demo app: LLM/text-chat is verified through a live smartphone Web reply, and STT/voice input, TTS/voice output, and Live2D/VTS motion are recorded as smartphone Web boundary evidence without configured STT/TTS/motion runtime execution."
        if complete
        else "v1.9.0 FW4.0.0 capability coverage after motion evidence needs review before release readiness."
    )
    return FrameworkFw40CapabilityCoverageAfterMotionResult(
        status=status,
        text_chat_status=text_chat_status,
        voice_input_status=voice_input_status,
        voice_output_status=voice_output_status,
        motion_status=motion_status,
        text_chat_live_runtime_verified=evidence.text_chat_live_runtime_verified,
        voice_input_configured_runtime_verified=evidence.voice_input_configured_runtime_verified,
        voice_output_configured_runtime_verified=evidence.voice_output_configured_runtime_verified,
        motion_configured_runtime_verified=evidence.motion_configured_runtime_verified,
        evidence_recorded_count=evidence_recorded_count,
        remaining_boundary_evidence_count=remaining_boundary_evidence_count,
        configured_runtime_verified_count=configured_runtime_verified_count,
        public_safe_evidence_only=evidence.public_safe_evidence_only,
        next_focus=next_focus,
        safe_summary=safe_summary,
    )


def build_v190_fw40_capability_coverage_after_motion_input() -> FrameworkFw40CapabilityCoverageAfterMotionInput:
    """Build the public-safe Day45 coverage input from recorded evidence status."""

    return FrameworkFw40CapabilityCoverageAfterMotionInput(
        text_chat_smartphone_web_completed=True,
        voice_input_boundary_recorded=True,
        voice_output_boundary_recorded=True,
        motion_boundary_recorded=True,
        text_chat_live_runtime_verified=True,
        voice_input_configured_runtime_verified=False,
        voice_output_configured_runtime_verified=False,
        motion_configured_runtime_verified=False,
        public_safe_evidence_only=True,
    )


def render_v190_fw40_capability_coverage_after_motion(
    result: FrameworkFw40CapabilityCoverageAfterMotionResult,
) -> list[str]:
    """Render public-safe v1.9.0 FW4.0.0 coverage-after-motion lines."""

    prefix = "v190_fw40_capability_coverage_after_motion_"
    return [
        prefix + "status: " + result.status,
        prefix + "llm_text_chat_status: " + result.text_chat_status,
        prefix + "stt_voice_input_status: " + result.voice_input_status,
        prefix + "tts_voice_output_status: " + result.voice_output_status,
        prefix + "live2d_vts_motion_status: " + result.motion_status,
        prefix
        + "llm_text_chat_live_runtime_verified: "
        + str(result.text_chat_live_runtime_verified),
        prefix
        + "stt_voice_input_configured_runtime_verified: "
        + str(result.voice_input_configured_runtime_verified),
        prefix
        + "tts_voice_output_configured_runtime_verified: "
        + str(result.voice_output_configured_runtime_verified),
        prefix
        + "live2d_vts_motion_configured_runtime_verified: "
        + str(result.motion_configured_runtime_verified),
        prefix + "evidence_recorded_count: " + str(result.evidence_recorded_count),
        prefix
        + "remaining_boundary_evidence_count: "
        + str(result.remaining_boundary_evidence_count),
        prefix
        + "configured_runtime_verified_count: "
        + str(result.configured_runtime_verified_count),
        prefix + "public_safe_evidence_only: " + str(result.public_safe_evidence_only),
        prefix + "next_focus: " + result.next_focus,
        prefix + "safe_summary: " + result.safe_summary,
    ]
