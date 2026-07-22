from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


TEXT_CHAT_CAPABILITY_ID = "llm_text_chat"
VOICE_INPUT_CAPABILITY_ID = "stt_voice_input"
VOICE_OUTPUT_CAPABILITY_ID = "tts_voice_output"
MOTION_CAPABILITY_ID = "live2d_vts_motion"

COMPLETED = "completed"
BOUNDARY_READY = "boundary-ready"
PENDING = "pending-configured-smartphone-web-evidence"


@dataclass(frozen=True)
class FrameworkFw40CapabilityEvidence:
    """Public-safe per-capability coverage status for the v1.9.0 FW4.0.0 demo.

    The checkpoint stores capability IDs, status labels, and booleans only. It
    must not store prompt bodies, response bodies, raw provider payloads, API key
    values, authorization headers, private paths, raw LAN IPs, raw audio, or raw
    screenshots.
    """

    capability_id: str
    capability_label: str
    status: str
    backend_boundary_present: bool
    smartphone_web_surface_present: bool
    configured_runtime_verified: bool
    smartphone_web_evidence_verified: bool
    public_safe_evidence_only: bool
    next_step: str


@dataclass(frozen=True)
class FrameworkFw40CapabilityCoverageCheckpoint:
    """Rendered coverage checkpoint for v1.9.0 FW4.0.0 capability scope."""

    status: str
    text_chat_status: str
    voice_input_status: str
    voice_output_status: str
    motion_status: str
    completed_count: int
    boundary_ready_count: int
    pending_configured_evidence_count: int
    public_safe_evidence_only: bool
    next_capability_focus: str
    safe_summary: str


def build_v190_fw40_capability_evidence() -> list[FrameworkFw40CapabilityEvidence]:
    """Return the public-safe v1.9.0 FW4.0.0 capability evidence snapshot."""

    return [
        FrameworkFw40CapabilityEvidence(
            capability_id=TEXT_CHAT_CAPABILITY_ID,
            capability_label="LLM / text chat",
            status=COMPLETED,
            backend_boundary_present=True,
            smartphone_web_surface_present=True,
            configured_runtime_verified=True,
            smartphone_web_evidence_verified=True,
            public_safe_evidence_only=True,
            next_step="keep-as-v190-completed-proof-point",
        ),
        FrameworkFw40CapabilityEvidence(
            capability_id=VOICE_INPUT_CAPABILITY_ID,
            capability_label="STT / voice input boundary",
            status=BOUNDARY_READY,
            backend_boundary_present=True,
            smartphone_web_surface_present=True,
            configured_runtime_verified=False,
            smartphone_web_evidence_verified=False,
            public_safe_evidence_only=True,
            next_step="start-voice-input-smartphone-web-boundary-evidence",
        ),
        FrameworkFw40CapabilityEvidence(
            capability_id=VOICE_OUTPUT_CAPABILITY_ID,
            capability_label="TTS / voice output boundary",
            status=BOUNDARY_READY,
            backend_boundary_present=True,
            smartphone_web_surface_present=True,
            configured_runtime_verified=False,
            smartphone_web_evidence_verified=False,
            public_safe_evidence_only=True,
            next_step="start-voice-output-smartphone-web-boundary-evidence",
        ),
        FrameworkFw40CapabilityEvidence(
            capability_id=MOTION_CAPABILITY_ID,
            capability_label="Live2D / VTS motion boundary",
            status=BOUNDARY_READY,
            backend_boundary_present=True,
            smartphone_web_surface_present=True,
            configured_runtime_verified=False,
            smartphone_web_evidence_verified=False,
            public_safe_evidence_only=True,
            next_step="start-live2d-vts-motion-smartphone-web-boundary-evidence",
        ),
    ]


def evaluate_v190_fw40_capability_coverage(
    evidence_items: Iterable[FrameworkFw40CapabilityEvidence],
) -> FrameworkFw40CapabilityCoverageCheckpoint:
    """Evaluate the current v1.9.0 FW4.0.0 capability coverage checkpoint."""

    items = list(evidence_items)
    by_id = {item.capability_id: item for item in items}

    required_ids = {
        TEXT_CHAT_CAPABILITY_ID,
        VOICE_INPUT_CAPABILITY_ID,
        VOICE_OUTPUT_CAPABILITY_ID,
        MOTION_CAPABILITY_ID,
    }
    missing_ids = required_ids.difference(by_id)
    if missing_ids:
        missing = ", ".join(sorted(missing_ids))
        raise ValueError("Missing FW4.0.0 capability evidence IDs: " + missing)

    text_chat = by_id[TEXT_CHAT_CAPABILITY_ID]
    voice_input = by_id[VOICE_INPUT_CAPABILITY_ID]
    voice_output = by_id[VOICE_OUTPUT_CAPABILITY_ID]
    motion = by_id[MOTION_CAPABILITY_ID]

    completed_count = sum(1 for item in items if item.status == COMPLETED)
    boundary_ready_count = sum(1 for item in items if item.status == BOUNDARY_READY)
    pending_configured_evidence_count = sum(
        1
        for item in items
        if item.backend_boundary_present
        and item.smartphone_web_surface_present
        and not item.configured_runtime_verified
    )
    public_safe_evidence_only = all(item.public_safe_evidence_only for item in items)

    status = (
        "text-chat-complete-boundary-capabilities-pending"
        if (
            text_chat.status == COMPLETED
            and voice_input.status == BOUNDARY_READY
            and voice_output.status == BOUNDARY_READY
            and motion.status == BOUNDARY_READY
            and public_safe_evidence_only
        )
        else "needs-capability-coverage-review"
    )
    next_capability_focus = (
        "stt_voice_input"
        if status == "text-chat-complete-boundary-capabilities-pending"
        else "review-fw40-capability-coverage"
    )
    safe_summary = (
        "v1.9.0 FW4.0.0 coverage checkpoint: LLM/text-chat smartphone Web proof is complete; STT, TTS, and Live2D/VTS remain guarded boundary capabilities that still need configured smartphone Web evidence."
        if status == "text-chat-complete-boundary-capabilities-pending"
        else "v1.9.0 FW4.0.0 coverage checkpoint needs review before moving to the next capability."
    )
    return FrameworkFw40CapabilityCoverageCheckpoint(
        status=status,
        text_chat_status=text_chat.status,
        voice_input_status=voice_input.status,
        voice_output_status=voice_output.status,
        motion_status=motion.status,
        completed_count=completed_count,
        boundary_ready_count=boundary_ready_count,
        pending_configured_evidence_count=pending_configured_evidence_count,
        public_safe_evidence_only=public_safe_evidence_only,
        next_capability_focus=next_capability_focus,
        safe_summary=safe_summary,
    )


def render_v190_fw40_capability_coverage(
    checkpoint: FrameworkFw40CapabilityCoverageCheckpoint,
) -> list[str]:
    """Render public-safe v1.9.0 FW4.0.0 capability coverage lines."""

    return [
        "v190_fw40_capability_coverage_status: " + checkpoint.status,
        "v190_fw40_capability_llm_text_chat_status: " + checkpoint.text_chat_status,
        "v190_fw40_capability_stt_voice_input_status: " + checkpoint.voice_input_status,
        "v190_fw40_capability_tts_voice_output_status: " + checkpoint.voice_output_status,
        "v190_fw40_capability_live2d_vts_motion_status: " + checkpoint.motion_status,
        "v190_fw40_capability_completed_count: " + str(checkpoint.completed_count),
        "v190_fw40_capability_boundary_ready_count: " + str(checkpoint.boundary_ready_count),
        "v190_fw40_capability_pending_configured_evidence_count: "
        + str(checkpoint.pending_configured_evidence_count),
        "v190_fw40_capability_public_safe_evidence_only: "
        + str(checkpoint.public_safe_evidence_only),
        "v190_fw40_capability_next_focus: " + checkpoint.next_capability_focus,
        "v190_fw40_capability_safe_summary: " + checkpoint.safe_summary,
    ]
