from __future__ import annotations

from dataclasses import dataclass


TEXT_CHAT_STATUS = "completed"
VOICE_INPUT_STATUS = "boundary-evidence-recorded"
VOICE_OUTPUT_STATUS = "boundary-evidence-recorded"
MOTION_STATUS = "boundary-ready"


@dataclass(frozen=True)
class FrameworkFw40CapabilityCoverageAfterVoiceOutputInput:
    """Public-safe evidence input after the Day41 voice output boundary record.

    The input stores status labels and booleans only. It must not include raw
    audio, generated audio files, audio URLs, transcript bodies, text bodies,
    prompt bodies, response bodies, provider payloads, API key values,
    authorization headers, private paths, raw LAN IPs, raw screenshots,
    microphone captures, playback artifacts, or provider error payloads.
    """

    text_chat_smartphone_web_completed: bool
    voice_input_boundary_recorded: bool
    voice_output_boundary_recorded: bool
    voice_input_configured_runtime_verified: bool
    voice_output_configured_runtime_verified: bool
    motion_boundary_ready: bool
    public_safe_evidence_only: bool


@dataclass(frozen=True)
class FrameworkFw40CapabilityCoverageAfterVoiceOutputResult:
    """Rendered v1.9.0 FW4.0.0 coverage after voice output evidence."""

    status: str
    text_chat_status: str
    voice_input_status: str
    voice_output_status: str
    voice_input_configured_runtime_verified: bool
    voice_output_configured_runtime_verified: bool
    motion_status: str
    evidence_recorded_count: int
    remaining_boundary_evidence_count: int
    configured_runtime_verified_count: int
    public_safe_evidence_only: bool
    next_capability_focus: str
    safe_summary: str


def evaluate_v190_fw40_capability_coverage_after_voice_output(
    evidence: FrameworkFw40CapabilityCoverageAfterVoiceOutputInput,
) -> FrameworkFw40CapabilityCoverageAfterVoiceOutputResult:
    """Evaluate the v1.9.0 FW4.0.0 coverage snapshot after Day41."""

    text_chat_status = TEXT_CHAT_STATUS if evidence.text_chat_smartphone_web_completed else "incomplete"
    voice_input_status = VOICE_INPUT_STATUS if evidence.voice_input_boundary_recorded else "boundary-ready"
    voice_output_status = VOICE_OUTPUT_STATUS if evidence.voice_output_boundary_recorded else "boundary-ready"
    motion_status = MOTION_STATUS if evidence.motion_boundary_ready else "incomplete"

    evidence_recorded_count = sum(
        [
            evidence.text_chat_smartphone_web_completed,
            evidence.voice_input_boundary_recorded,
            evidence.voice_output_boundary_recorded,
        ]
    )
    configured_runtime_verified_count = sum(
        [
            evidence.text_chat_smartphone_web_completed,
            evidence.voice_input_configured_runtime_verified,
            evidence.voice_output_configured_runtime_verified,
        ]
    )
    remaining_boundary_evidence_count = sum([evidence.motion_boundary_ready])

    ready = (
        evidence.text_chat_smartphone_web_completed
        and evidence.voice_input_boundary_recorded
        and evidence.voice_output_boundary_recorded
        and not evidence.voice_input_configured_runtime_verified
        and not evidence.voice_output_configured_runtime_verified
        and evidence.motion_boundary_ready
        and evidence.public_safe_evidence_only
    )
    status = (
        "text-chat-voice-input-and-voice-output-boundary-evidence-complete-motion-boundary-pending"
        if ready
        else "needs-capability-coverage-review-after-voice-output"
    )
    next_capability_focus = "live2d_vts_motion" if ready else "review-fw40-capability-coverage"
    safe_summary = (
        "v1.9.0 FW4.0.0 capability coverage after voice output: LLM/text-chat smartphone Web proof is complete, STT/voice input and TTS/voice output smartphone Web boundary evidence are recorded without configured STT/TTS runtime execution, and Live2D/VTS motion boundary evidence remains pending."
        if ready
        else "v1.9.0 FW4.0.0 capability coverage after voice output needs review before moving to the motion boundary."
    )
    return FrameworkFw40CapabilityCoverageAfterVoiceOutputResult(
        status=status,
        text_chat_status=text_chat_status,
        voice_input_status=voice_input_status,
        voice_output_status=voice_output_status,
        voice_input_configured_runtime_verified=evidence.voice_input_configured_runtime_verified,
        voice_output_configured_runtime_verified=evidence.voice_output_configured_runtime_verified,
        motion_status=motion_status,
        evidence_recorded_count=evidence_recorded_count,
        remaining_boundary_evidence_count=remaining_boundary_evidence_count,
        configured_runtime_verified_count=configured_runtime_verified_count,
        public_safe_evidence_only=evidence.public_safe_evidence_only,
        next_capability_focus=next_capability_focus,
        safe_summary=safe_summary,
    )


def build_v190_fw40_capability_coverage_after_voice_output_input() -> FrameworkFw40CapabilityCoverageAfterVoiceOutputInput:
    """Build the public-safe Day42 coverage input from recorded evidence status."""

    return FrameworkFw40CapabilityCoverageAfterVoiceOutputInput(
        text_chat_smartphone_web_completed=True,
        voice_input_boundary_recorded=True,
        voice_output_boundary_recorded=True,
        voice_input_configured_runtime_verified=False,
        voice_output_configured_runtime_verified=False,
        motion_boundary_ready=True,
        public_safe_evidence_only=True,
    )


def render_v190_fw40_capability_coverage_after_voice_output(
    result: FrameworkFw40CapabilityCoverageAfterVoiceOutputResult,
) -> list[str]:
    """Render public-safe v1.9.0 FW4.0.0 coverage-after-voice-output lines."""

    prefix = "v190_fw40_capability_coverage_after_voice_output_"
    return [
        prefix + "status: " + result.status,
        prefix + "llm_text_chat_status: " + result.text_chat_status,
        prefix + "stt_voice_input_status: " + result.voice_input_status,
        prefix + "tts_voice_output_status: " + result.voice_output_status,
        prefix
        + "stt_voice_input_configured_runtime_verified: "
        + str(result.voice_input_configured_runtime_verified),
        prefix
        + "tts_voice_output_configured_runtime_verified: "
        + str(result.voice_output_configured_runtime_verified),
        prefix + "live2d_vts_motion_status: " + result.motion_status,
        prefix + "evidence_recorded_count: " + str(result.evidence_recorded_count),
        prefix
        + "remaining_boundary_evidence_count: "
        + str(result.remaining_boundary_evidence_count),
        prefix
        + "configured_runtime_verified_count: "
        + str(result.configured_runtime_verified_count),
        prefix + "public_safe_evidence_only: " + str(result.public_safe_evidence_only),
        prefix + "next_focus: " + result.next_capability_focus,
        prefix + "safe_summary: " + result.safe_summary,
    ]
