from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MotionSmartphoneWebBoundaryEvidence:
    """Public-safe Live2D / VTS motion smartphone Web boundary evidence.

    The evidence stores only booleans, status labels, and next-step labels. It
    must not store motion payload bodies, VTS WebSocket payloads, Live2D runtime
    state, provider payloads, API key values, authorization headers, private
    paths, raw LAN IPs, raw screenshots, prompt/response bodies, transcript
    bodies, raw audio, generated audio, or raw provider error payloads.
    """

    status: str
    mode: str
    source_mode: str
    backend_status_ok: bool
    api_base_url_visible: bool
    status_route_present: bool
    request_route_present: bool
    api_client_route_present: bool
    flutter_section_visible: bool
    flutter_button_visible: bool
    request_contract_metadata_only: bool
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


def evaluate_motion_source_tree_boundary_evidence(
    *,
    status_route_present: bool,
    request_route_present: bool,
    api_client_route_present: bool,
    flutter_section_visible: bool,
    flutter_button_visible: bool,
    flutter_simulator_copy_visible: bool,
    request_contract_metadata_only: bool,
    motion_send_blocked: bool,
    vts_connection_not_used: bool,
    live2d_runtime_not_loaded: bool,
) -> MotionSmartphoneWebBoundaryEvidence:
    """Evaluate source-tree Live2D / VTS motion boundary evidence.

    Source-tree mode confirms that the DRC backend/API and smartphone Web UI
    surfaces exist, but it does not start Flutter or call the backend.
    """

    verified = all(
        [
            status_route_present,
            request_route_present,
            api_client_route_present,
            flutter_section_visible,
            flutter_button_visible,
            flutter_simulator_copy_visible,
            request_contract_metadata_only,
            motion_send_blocked,
            vts_connection_not_used,
            live2d_runtime_not_loaded,
        ]
    )
    return MotionSmartphoneWebBoundaryEvidence(
        status="verified" if verified else "needs-review",
        mode="source-tree-boundary",
        source_mode="motion_demo_boundary",
        backend_status_ok=False,
        api_base_url_visible=False,
        status_route_present=status_route_present,
        request_route_present=request_route_present,
        api_client_route_present=api_client_route_present,
        flutter_section_visible=flutter_section_visible,
        flutter_button_visible=flutter_button_visible,
        request_contract_metadata_only=request_contract_metadata_only,
        request_sent=False,
        response_visible=False,
        capability_status_visible=False,
        checks_visible=False,
        motion_send_blocked=motion_send_blocked,
        vts_connection_not_used=vts_connection_not_used,
        live2d_runtime_not_loaded=live2d_runtime_not_loaded,
        motion_payload_hidden_or_absent=True,
        public_safe_evidence_only=True,
        next_step="record-manual-smartphone-web-motion-boundary-evidence",
        safe_summary=(
            "Source-tree evidence verifies that the DRC backend and smartphone Web UI expose a guarded Live2D / VTS motion demo boundary. No VTS connection, Live2D runtime loading, motion dispatch, or motion payload recording is used."
        ),
    )


def evaluate_manual_motion_smartphone_web_boundary_evidence(
    *,
    backend_status_ok: bool,
    api_base_url_visible: bool,
    motion_section_visible: bool,
    motion_button_visible: bool,
    motion_request_sent: bool,
    motion_response_visible: bool,
    capability_status_visible: bool,
    checks_visible: bool,
    motion_send_blocked: bool,
    vts_connection_not_used: bool,
    live2d_runtime_not_loaded: bool,
    motion_payload_hidden_or_absent: bool,
) -> MotionSmartphoneWebBoundaryEvidence:
    """Evaluate manual smartphone Web Live2D / VTS motion boundary evidence."""

    verified = all(
        [
            backend_status_ok,
            api_base_url_visible,
            motion_section_visible,
            motion_button_visible,
            motion_request_sent,
            motion_response_visible,
            capability_status_visible,
            checks_visible,
            motion_send_blocked,
            vts_connection_not_used,
            live2d_runtime_not_loaded,
            motion_payload_hidden_or_absent,
        ]
    )
    return MotionSmartphoneWebBoundaryEvidence(
        status="verified" if verified else "needs-review",
        mode="manual-smartphone-web-ui-boundary",
        source_mode="motion_demo_boundary",
        backend_status_ok=backend_status_ok,
        api_base_url_visible=api_base_url_visible,
        status_route_present=True,
        request_route_present=True,
        api_client_route_present=True,
        flutter_section_visible=motion_section_visible,
        flutter_button_visible=motion_button_visible,
        request_contract_metadata_only=True,
        request_sent=motion_request_sent,
        response_visible=motion_response_visible,
        capability_status_visible=capability_status_visible,
        checks_visible=checks_visible,
        motion_send_blocked=motion_send_blocked,
        vts_connection_not_used=vts_connection_not_used,
        live2d_runtime_not_loaded=live2d_runtime_not_loaded,
        motion_payload_hidden_or_absent=motion_payload_hidden_or_absent,
        public_safe_evidence_only=True,
        next_step="record-v190-motion-smartphone-web-boundary-evidence",
        safe_summary=(
            "Manual smartphone Web evidence verifies that the DRC UI can reach the guarded Live2D / VTS motion demo request boundary through the actual backend API while motion dispatch remains blocked and public-safe."
        ),
    )


def render_motion_smartphone_web_boundary_evidence(
    evidence: MotionSmartphoneWebBoundaryEvidence,
) -> list[str]:
    """Render public-safe Live2D / VTS motion boundary evidence lines."""

    prefix = "motion_smartphone_web_boundary_"
    return [
        prefix + "evidence_status: " + evidence.status,
        prefix + "evidence_mode: " + evidence.mode,
        prefix + "source_mode: " + evidence.source_mode,
        prefix + "backend_status_ok: " + str(evidence.backend_status_ok),
        prefix + "api_base_url_visible: " + str(evidence.api_base_url_visible),
        prefix + "status_route_present: " + str(evidence.status_route_present),
        prefix + "request_route_present: " + str(evidence.request_route_present),
        prefix + "api_client_route_present: " + str(evidence.api_client_route_present),
        prefix + "flutter_section_visible: " + str(evidence.flutter_section_visible),
        prefix + "flutter_button_visible: " + str(evidence.flutter_button_visible),
        prefix + "request_contract_metadata_only: " + str(evidence.request_contract_metadata_only),
        prefix + "request_sent: " + str(evidence.request_sent),
        prefix + "response_visible: " + str(evidence.response_visible),
        prefix + "capability_status_visible: " + str(evidence.capability_status_visible),
        prefix + "checks_visible: " + str(evidence.checks_visible),
        prefix + "motion_send_blocked: " + str(evidence.motion_send_blocked),
        prefix + "vts_connection_not_used: " + str(evidence.vts_connection_not_used),
        prefix + "live2d_runtime_not_loaded: " + str(evidence.live2d_runtime_not_loaded),
        prefix + "motion_payload_hidden_or_absent: " + str(evidence.motion_payload_hidden_or_absent),
        prefix + "public_safe_evidence_only: " + str(evidence.public_safe_evidence_only),
        prefix + "next_step: " + evidence.next_step,
        prefix + "safe_summary: " + evidence.safe_summary,
    ]
