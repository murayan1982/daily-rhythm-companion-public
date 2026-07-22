"""Day43 smoke for Live2D / VTS motion smartphone Web boundary evidence.

Default source-tree mode checks that the guarded motion API and Flutter Web UI
surfaces exist. Manual mode records public-safe booleans from a smartphone Web
operator check. Neither mode imports AI Character Framework motion modules,
connects to VTube Studio, loads Live2D runtime dependencies, dispatches motion,
or stores motion payload bodies.
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
    evaluate_motion_source_tree_boundary_evidence,
    render_motion_smartphone_web_boundary_evidence,
)


def _read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def _assert_public_safe(text: str) -> None:
    forbidden_patterns = [
        r"sk-[A-Za-z0-9_-]{12,}",
        r"AIza[0-9A-Za-z_-]{20,}",
        r"xai-[A-Za-z0-9_-]{12,}",
        r"Bearer\s+[A-Za-z0-9_.-]{12,}",
        r"Authorization:\s*Bearer",
        r"refresh_token",
        r"access_token",
        r"client_secret",
        r"[A-Za-z]:\\Users\\",
        r"192\.168\.\d+\.\d+",
        r"10\.\d+\.\d+\.\d+",
        r"172\.(1[6-9]|2\d|3[0-1])\.\d+\.\d+",
    ]
    for pattern in forbidden_patterns:
        if re.search(pattern, text, flags=re.IGNORECASE):
            raise AssertionError(
                "Public-safe motion evidence contained forbidden pattern: " + pattern
            )


def _build_source_tree_evidence():
    api = _read("backend/app/api/motion_demo.py")
    service = _read("backend/app/services/motion_demo_service.py")
    model = _read("backend/app/models/motion_demo.py")
    client = _read("app/lib/services/backend_api_client.dart")
    screen = _read("app/lib/screens/home_screen.dart")

    return evaluate_motion_source_tree_boundary_evidence(
        status_route_present='@router.get("/demo/motion/status"' in api,
        request_route_present='@router.post("/demo/motion"' in api,
        api_client_route_present="$baseUrl/demo/motion" in client,
        flutter_section_visible="Motion Demo" in screen,
        flutter_button_visible="Motion demoを試す" in screen,
        flutter_simulator_copy_visible="軽量なペラ絵/表情差分 simulator" in screen,
        request_contract_metadata_only=(
            "motion_event" in model
            and "character_id" in model
            and "expression_id" in model
            and "requested_adapter_mode" in model
        ),
        motion_send_blocked=(
            "accepted=False" in service
            and "motion_sent=False" in service
            and "Motion demo request was received" in service
        ),
        vts_connection_not_used=(
            "vts_connection_used=False" in service
            and "VTube Studio / Live2D motion sending yet" in service
        ),
        live2d_runtime_not_loaded=(
            "does not open a VTS WebSocket connection" in model
            and "Live2D runtime dependencies" in model
        ),
    )


def _build_manual_evidence(args: argparse.Namespace):
    return evaluate_manual_motion_smartphone_web_boundary_evidence(
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
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Render public-safe Day43 Live2D / VTS motion smartphone Web boundary evidence."
    )
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
    evidence = (
        _build_manual_evidence(args)
        if args.record_manual_ui_evidence
        else _build_source_tree_evidence()
    )
    rendered_lines = render_motion_smartphone_web_boundary_evidence(evidence)
    rendered = "\n".join(rendered_lines)
    _assert_public_safe(rendered)

    label = "configured" if args.record_manual_ui_evidence else "source-tree"
    print(f"[smoke-framework-motion-smartphone-web-boundary-evidence-{label}] RESULT")
    print(rendered)
    if evidence.status != "verified":
        raise SystemExit(1)
    print(
        "Motion smartphone Web boundary evidence was rendered without VTS WebSocket payloads, Live2D runtime state, motion payload bodies, provider payloads, API key values, private paths, raw LAN IPs, screenshots, or motion dispatch."
    )


if __name__ == "__main__":
    main()
