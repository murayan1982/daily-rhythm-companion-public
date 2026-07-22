"""Day37 smoke for STT / voice input smartphone Web boundary evidence.

Default source-tree mode checks that the guarded voice input API and Flutter Web
UI surfaces exist. Manual mode records public-safe booleans from a smartphone Web
operator check. Neither mode imports AI Character Framework, opens microphones,
reads or uploads audio, calls STT providers, creates realtime voice sessions, or
stores transcript bodies.
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

from app.services.framework_voice_input_smartphone_web_boundary_evidence import (
    evaluate_manual_voice_input_smartphone_web_boundary_evidence,
    evaluate_voice_input_source_tree_boundary_evidence,
    render_voice_input_smartphone_web_boundary_evidence,
)


def _read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


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
                "Public-safe voice input evidence contained forbidden pattern: "
                + pattern
            )


def _build_source_tree_evidence():
    api = _read("backend/app/api/voice_input_demo.py")
    service = _read("backend/app/services/voice_input_demo_service.py")
    model = _read("backend/app/models/voice_input_demo.py")
    client = _read("app/lib/services/backend_api_client.dart")
    screen = _read("app/lib/screens/home_screen.dart")

    return evaluate_voice_input_source_tree_boundary_evidence(
        status_route_present='@router.get("/demo/voice-input/status"' in api,
        request_route_present='@router.post("/demo/voice-input"' in api,
        api_client_route_present="$baseUrl/demo/voice-input" in client,
        flutter_section_visible="Voice Input Demo" in screen,
        flutter_button_visible="Voice input demoを試す" in screen,
        flutter_no_microphone_copy_visible="録音やマイク権限はまだ使わず" in screen,
        request_contract_metadata_only=(
            "raw audio bytes" in model
            and "audio_reference" in model
            and "sample_rate_hz" in model
            and "duration_ms" in model
        ),
        audio_processing_blocked=(
            "does not import FW audio code" in service
            and "open a" in service
            and "microphone" in service
            and "attempt speech recognition" in service
            and "accepted=False" in service
            and "transcript=None" in service
        ),
    )


def _build_manual_evidence(args: argparse.Namespace):
    return evaluate_manual_voice_input_smartphone_web_boundary_evidence(
        backend_status_ok=args.backend_status_ok,
        api_base_url_visible=args.api_base_url_visible,
        voice_input_section_visible=args.voice_input_section_visible,
        voice_input_button_visible=args.voice_input_button_visible,
        voice_input_request_sent=args.voice_input_request_sent,
        voice_input_response_visible=args.voice_input_response_visible,
        capability_status_visible=args.capability_status_visible,
        checks_visible=args.checks_visible,
        audio_processing_blocked=args.audio_processing_blocked,
        microphone_not_used=args.microphone_not_used,
        raw_audio_not_uploaded=args.raw_audio_not_uploaded,
        transcript_body_hidden_or_absent=args.transcript_body_hidden_or_absent,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Render public-safe Day37 voice input smartphone Web boundary evidence."
    )
    parser.add_argument("--record-manual-ui-evidence", action="store_true")
    parser.add_argument("--backend-status-ok", action="store_true")
    parser.add_argument("--api-base-url-visible", action="store_true")
    parser.add_argument("--voice-input-section-visible", action="store_true")
    parser.add_argument("--voice-input-button-visible", action="store_true")
    parser.add_argument("--voice-input-request-sent", action="store_true")
    parser.add_argument("--voice-input-response-visible", action="store_true")
    parser.add_argument("--capability-status-visible", action="store_true")
    parser.add_argument("--checks-visible", action="store_true")
    parser.add_argument("--audio-processing-blocked", action="store_true")
    parser.add_argument("--microphone-not-used", action="store_true")
    parser.add_argument("--raw-audio-not-uploaded", action="store_true")
    parser.add_argument("--transcript-body-hidden-or-absent", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    evidence = (
        _build_manual_evidence(args)
        if args.record_manual_ui_evidence
        else _build_source_tree_evidence()
    )
    rendered_lines = render_voice_input_smartphone_web_boundary_evidence(evidence)
    rendered = "\n".join(rendered_lines)
    _assert_public_safe(rendered)

    label = "configured" if args.record_manual_ui_evidence else "source-tree"
    print(f"[smoke-framework-voice-input-smartphone-web-boundary-evidence-{label}] RESULT")
    print(rendered)
    if evidence.status != "verified":
        raise SystemExit(1)
    print(
        "Voice input smartphone Web boundary evidence was rendered without raw audio, transcript bodies, provider payloads, API key values, private paths, raw LAN IPs, microphone access, or STT provider calls."
    )


if __name__ == "__main__":
    main()
