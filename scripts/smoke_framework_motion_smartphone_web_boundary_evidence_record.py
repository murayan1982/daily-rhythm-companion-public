r"""Day44 smoke for recording v1.9.0 Live2D / VTS motion Web evidence.

Default mode is source-tree only. It does not start Flutter, open a browser,
call the backend, import AI Character Framework motion modules, connect to
VTube Studio, load Live2D runtime dependencies, dispatch motion, or store
motion/VTS/Live2D payload bodies. It verifies that Day43 manual smartphone Web
evidence can be represented as a public-safe v1.9.0 record.

Manual recording mode accepts booleans from an operator-run smartphone Web check:

    python scripts\smoke_framework_motion_smartphone_web_boundary_evidence_record.py ^
      --record-manual-ui-evidence ^
      --backend-status-ok ^
      --api-base-url-visible ^
      --motion-section-visible ^
      --motion-button-visible ^
      --motion-request-sent ^
      --motion-response-visible ^
      --capability-status-visible ^
      --checks-visible ^
      --motion-send-blocked ^
      --vts-connection-not-used ^
      --live2d-runtime-not-loaded ^
      --motion-payload-hidden-or-absent

The script never accepts or prints motion payload bodies, VTS WebSocket
payloads, Live2D runtime state, provider payloads, API key values, private
paths, raw LAN IPs, raw screenshots, or provider error payloads.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.services.framework_motion_smartphone_web_boundary_evidence import (
    evaluate_manual_motion_smartphone_web_boundary_evidence,
)
from app.services.framework_motion_smartphone_web_boundary_evidence_record import (
    MotionSmartphoneWebBoundaryEvidenceRecordInput,
    evaluate_motion_smartphone_web_boundary_evidence_record,
    render_motion_smartphone_web_boundary_evidence_record,
)


def _assert_public_safe(text: str) -> None:
    forbidden_patterns = [
        r"sk-[A-Za-z0-9_\-]{12,}",
        r"AIza[0-9A-Za-z_\-]{20,}",
        r"xai-[A-Za-z0-9_\-]{12,}",
        r"Bearer\s+[A-Za-z0-9_\-\.]{12,}",
        r"Authorization:\s*Bearer",
        r"refresh_token\s*[:=]\s*['\"][^'\"]+",
        r"access_token\s*[:=]\s*['\"][^'\"]+",
        r"client_secret\s*[:=]\s*['\"][^'\"]+",
        r"[A-Za-z]:\\Users\\",
        r"192\.168\.\d+\.\d+",
        r"10\.\d+\.\d+\.\d+",
        r"172\.(1[6-9]|2\d|3[0-1])\.\d+\.\d+",
    ]
    for pattern in forbidden_patterns:
        if re.search(pattern, text, flags=re.IGNORECASE):
            raise AssertionError(
                "Public-safe motion boundary record contained forbidden pattern: "
                + pattern
            )


def _build_record_input(
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
    evidence_mode: str,
) -> MotionSmartphoneWebBoundaryEvidenceRecordInput:
    evidence = evaluate_manual_motion_smartphone_web_boundary_evidence(
        backend_status_ok=backend_status_ok,
        api_base_url_visible=api_base_url_visible,
        motion_section_visible=motion_section_visible,
        motion_button_visible=motion_button_visible,
        motion_request_sent=motion_request_sent,
        motion_response_visible=motion_response_visible,
        capability_status_visible=capability_status_visible,
        checks_visible=checks_visible,
        motion_send_blocked=motion_send_blocked,
        vts_connection_not_used=vts_connection_not_used,
        live2d_runtime_not_loaded=live2d_runtime_not_loaded,
        motion_payload_hidden_or_absent=motion_payload_hidden_or_absent,
    )
    return MotionSmartphoneWebBoundaryEvidenceRecordInput(
        evidence_status=evidence.status,
        evidence_mode=evidence_mode,
        source_mode=evidence.source_mode,
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
    )


def _render_and_validate(record_input: MotionSmartphoneWebBoundaryEvidenceRecordInput) -> str:
    record = evaluate_motion_smartphone_web_boundary_evidence_record(record_input)
    rendered = "\n".join(render_motion_smartphone_web_boundary_evidence_record(record))
    _assert_public_safe(rendered)
    return rendered


def _run_source_tree_smoke() -> None:
    rendered = _render_and_validate(
        _build_record_input(
            backend_status_ok=True,
            api_base_url_visible=True,
            motion_section_visible=True,
            motion_button_visible=True,
            motion_request_sent=True,
            motion_response_visible=True,
            capability_status_visible=True,
            checks_visible=True,
            motion_send_blocked=True,
            vts_connection_not_used=True,
            live2d_runtime_not_loaded=True,
            motion_payload_hidden_or_absent=True,
            evidence_mode="source-tree-synthetic-smartphone-web-motion-boundary-record",
        )
    )
    required = [
        "v190_motion_smartphone_web_boundary_record_status: recorded",
        "v190_motion_smartphone_web_boundary_record_from_evidence_status: verified",
        "v190_motion_smartphone_web_boundary_record_source_mode: motion_demo_boundary",
        "v190_motion_smartphone_web_boundary_record_backend_status_ok: True",
        "v190_motion_smartphone_web_boundary_record_request_sent: True",
        "v190_motion_smartphone_web_boundary_record_response_visible: True",
        "v190_motion_smartphone_web_boundary_record_motion_send_blocked: True",
        "v190_motion_smartphone_web_boundary_record_vts_connection_not_used: True",
        "v190_motion_smartphone_web_boundary_record_live2d_runtime_not_loaded: True",
        "v190_motion_smartphone_web_boundary_record_motion_payload_hidden_or_absent: True",
        "v190_motion_smartphone_web_boundary_record_next_step: update-fw40-capability-coverage-after-motion-boundary-evidence",
    ]
    for needle in required:
        if needle not in rendered:
            raise AssertionError(f"Missing source-tree motion record marker: {needle}")
    print("[smoke-framework-motion-smartphone-web-boundary-evidence-record] OK")


def _run_manual_recording(args: argparse.Namespace) -> None:
    rendered = _render_and_validate(
        _build_record_input(
            backend_status_ok=args.backend_status_ok,
            api_base_url_visible=args.api_base_url_visible,
            motion_section_visible=args.motion_section_visible,
            motion_button_visible=args.motion_button_visible,
            motion_request_sent=args.motion_request_sent,
            motion_response_visible=args.motion_response_visible,
            capability_status_visible=args.capability_status_visible,
            checks_visible=args.checks_visible,
            motion_send_blocked=args.motion_send_blocked,
            vts_connection_not_used=args.vts_connection_not_used,
            live2d_runtime_not_loaded=args.live2d_runtime_not_loaded,
            motion_payload_hidden_or_absent=args.motion_payload_hidden_or_absent,
            evidence_mode="manual-smartphone-web-ui-motion-boundary-record",
        )
    )
    print("[smoke-framework-motion-smartphone-web-boundary-evidence-record-configured] RESULT")
    print(rendered)
    print(
        "v1.9.0 Live2D / VTS motion smartphone Web boundary record was rendered without motion payload bodies, VTS WebSocket payloads, Live2D runtime state, provider payloads, API key values, private paths, raw LAN IPs, raw screenshots, VTS connections, Live2D runtime loading, or motion dispatch."
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--record-manual-ui-evidence", action="store_true")
    parser.add_argument("--backend-status-ok", action="store_true")
    parser.add_argument("--api-base-url-visible", action="store_true")
    parser.add_argument("--motion-section-visible", action="store_true")
    parser.add_argument("--motion-button-visible", action="store_true")
    parser.add_argument("--motion-request-sent", action="store_true")
    parser.add_argument("--motion-response-visible", action="store_true")
    parser.add_argument("--capability-status-visible", action="store_true")
    parser.add_argument("--checks-visible", action="store_true")
    parser.add_argument("--motion-send-blocked", action="store_true")
    parser.add_argument("--vts-connection-not-used", action="store_true")
    parser.add_argument("--live2d-runtime-not-loaded", action="store_true")
    parser.add_argument("--motion-payload-hidden-or-absent", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.record_manual_ui_evidence:
        _run_manual_recording(args)
        return
    _run_source_tree_smoke()


if __name__ == "__main__":
    main()
