from __future__ import annotations

from dataclasses import dataclass


EXPECTED_MOTION_EVIDENCE_STATUS = "verified"
EXPECTED_MOTION_SOURCE_MODE = "motion_demo_boundary"


@dataclass(frozen=True)
class MotionSmartphoneWebBoundaryEvidenceRecordInput:
    """Public-safe input for the v1.9.0 Live2D / VTS motion Web record.

    The record stores booleans, source labels, and status markers only. It must
    not store motion payload bodies, VTS WebSocket payloads, Live2D runtime
    state, provider payloads, API key values, authorization headers, private
    paths, raw LAN IPs, raw screenshots, prompt/response bodies, transcript
    bodies, raw audio, generated audio, or raw provider error payloads.
    """

    evidence_status: str
    evidence_mode: str
    source_mode: str
    backend_status_ok: bool
    api_base_url_visible: bool
    request_sent: bool
    response_visible: bool
    capability_status_visible: bool
    checks_visible: bool
    motion_send_blocked: bool
    vts_connection_not_used: bool
    live2d_runtime_not_loaded: bool
    motion_payload_hidden_or_absent: bool
    public_safe_evidence_only: bool


@dataclass(frozen=True)
class MotionSmartphoneWebBoundaryEvidenceRecordResult:
    """Rendered v1.9.0 Live2D / VTS motion smartphone Web boundary record."""

    status: str
    evidence_status: str
    evidence_mode: str
    source_mode: str
    source_mode_matches: bool
    backend_status_ok: bool
    api_base_url_visible: bool
    request_sent: bool
    response_visible: bool
    capability_status_visible: bool
    checks_visible: bool
    motion_send_blocked: bool
    vts_connection_not_used: bool
    live2d_runtime_not_loaded: bool
    motion_payload_hidden_or_absent: bool
    public_safe_evidence_only: bool
    next_step: str
    safe_summary: str


def evaluate_motion_smartphone_web_boundary_evidence_record(
    evidence: MotionSmartphoneWebBoundaryEvidenceRecordInput,
) -> MotionSmartphoneWebBoundaryEvidenceRecordResult:
    """Evaluate whether Live2D / VTS motion smartphone Web evidence is recordable."""

    source_mode_matches = evidence.source_mode == EXPECTED_MOTION_SOURCE_MODE
    required_flags = (
        evidence.evidence_status == EXPECTED_MOTION_EVIDENCE_STATUS,
        source_mode_matches,
        evidence.backend_status_ok,
        evidence.api_base_url_visible,
        evidence.request_sent,
        evidence.response_visible,
        evidence.capability_status_visible,
        evidence.checks_visible,
        evidence.motion_send_blocked,
        evidence.vts_connection_not_used,
        evidence.live2d_runtime_not_loaded,
        evidence.motion_payload_hidden_or_absent,
        evidence.public_safe_evidence_only,
    )
    recorded = all(required_flags)
    return MotionSmartphoneWebBoundaryEvidenceRecordResult(
        status="recorded" if recorded else "incomplete",
        evidence_status=evidence.evidence_status,
        evidence_mode=evidence.evidence_mode,
        source_mode=evidence.source_mode,
        source_mode_matches=source_mode_matches,
        backend_status_ok=evidence.backend_status_ok,
        api_base_url_visible=evidence.api_base_url_visible,
        request_sent=evidence.request_sent,
        response_visible=evidence.response_visible,
        capability_status_visible=evidence.capability_status_visible,
        checks_visible=evidence.checks_visible,
        motion_send_blocked=evidence.motion_send_blocked,
        vts_connection_not_used=evidence.vts_connection_not_used,
        live2d_runtime_not_loaded=evidence.live2d_runtime_not_loaded,
        motion_payload_hidden_or_absent=evidence.motion_payload_hidden_or_absent,
        public_safe_evidence_only=evidence.public_safe_evidence_only,
        next_step=(
            "update-fw40-capability-coverage-after-motion-boundary-evidence"
            if recorded
            else "complete-v190-motion-smartphone-web-boundary-evidence-record"
        ),
        safe_summary=(
            "v1.9.0 Live2D / VTS motion smartphone Web boundary evidence is recorded: "
            "the guarded DRC motion demo boundary was visible and reachable through "
            "the actual backend API while motion dispatch, VTS connection, and Live2D "
            "runtime loading stayed blocked and evidence remained public-safe."
            if recorded
            else "v1.9.0 Live2D / VTS motion smartphone Web boundary evidence is incomplete; rerun the public-safe checklist."
        ),
    )


def render_motion_smartphone_web_boundary_evidence_record(
    result: MotionSmartphoneWebBoundaryEvidenceRecordResult,
) -> list[str]:
    """Render public-safe Live2D / VTS motion boundary record lines."""

    prefix = "v190_motion_smartphone_web_boundary_record_"
    return [
        prefix + "status: " + result.status,
        prefix + "from_evidence_status: " + result.evidence_status,
        prefix + "evidence_mode: " + result.evidence_mode,
        prefix + "source_mode: " + result.source_mode,
        prefix + "source_mode_matches: " + str(result.source_mode_matches),
        prefix + "backend_status_ok: " + str(result.backend_status_ok),
        prefix + "api_base_url_visible: " + str(result.api_base_url_visible),
        prefix + "request_sent: " + str(result.request_sent),
        prefix + "response_visible: " + str(result.response_visible),
        prefix + "capability_status_visible: " + str(result.capability_status_visible),
        prefix + "checks_visible: " + str(result.checks_visible),
        prefix + "motion_send_blocked: " + str(result.motion_send_blocked),
        prefix + "vts_connection_not_used: " + str(result.vts_connection_not_used),
        prefix + "live2d_runtime_not_loaded: " + str(result.live2d_runtime_not_loaded),
        prefix + "motion_payload_hidden_or_absent: " + str(result.motion_payload_hidden_or_absent),
        prefix + "public_safe_evidence_only: " + str(result.public_safe_evidence_only),
        prefix + "next_step: " + result.next_step,
        prefix + "safe_summary: " + result.safe_summary,
    ]
