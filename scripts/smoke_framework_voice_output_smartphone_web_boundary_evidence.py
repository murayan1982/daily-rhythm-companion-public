"""Day40 smoke for TTS / voice output smartphone Web boundary evidence.

Default source-tree mode checks that the guarded voice output API and Flutter Web
UI surfaces exist. Manual mode records public-safe booleans from a smartphone Web
operator check. Neither mode imports AI Character Framework audio modules,
synthesizes speech, generates audio files, plays audio, calls TTS providers, or
stores text/audio/provider payload bodies.
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

EXPECTED_STATUS_MARKER = "voice_output_smartphone_web_boundary_evidence_status"

from app.services.framework_voice_output_smartphone_web_boundary_evidence import (
    evaluate_manual_voice_output_smartphone_web_boundary_evidence,
    evaluate_voice_output_source_tree_boundary_evidence,
    render_voice_output_smartphone_web_boundary_evidence,
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
                "Public-safe voice output evidence contained forbidden pattern: "
                + pattern
            )


def _build_source_tree_evidence():
    api = _read("backend/app/api/voice_output_demo.py")
    service = _read("backend/app/services/voice_output_demo_service.py")
    model = _read("backend/app/models/voice_output_demo.py")
    client = _read("app/lib/services/backend_api_client.dart")
    screen = _read("app/lib/screens/home_screen.dart")

    return evaluate_voice_output_source_tree_boundary_evidence(
        status_route_present='@router.get("/demo/voice-output/status"' in api,
        request_route_present='@router.post("/demo/voice-output"' in api,
        api_client_route_present="$baseUrl/demo/voice-output" in client,
        flutter_section_visible="Voice Output / TTS Demo" in screen,
        flutter_button_visible="Voice output demoを試す" in screen,
        flutter_no_audio_copy_visible="音声再生や音声ファイル生成はまだ行わず" in screen,
        request_contract_metadata_only=(
            "text_content" in model
            and "voice_profile_id" in model
            and "audio_format" in model
            and "audio_url" in model
        ),
        synthesis_blocked=(
            "does not import FW audio code" in service
            and "synthesize text" in service
        ),
        audio_generation_blocked=(
            "generate audio" in service
            and "accepted=False" in service
            and "audio_url=None" in service
            and "audio_format=None" in service
        ),
        audio_playback_not_used="play sound" in service,
    )


def _build_manual_evidence(args: argparse.Namespace):
    return evaluate_manual_voice_output_smartphone_web_boundary_evidence(
        backend_status_ok=args.backend_status_ok,
        api_base_url_visible=args.api_base_url_visible,
        voice_output_section_visible=args.voice_output_section_visible,
        voice_output_button_visible=args.voice_output_button_visible,
        voice_output_request_sent=args.voice_output_request_sent,
        voice_output_response_visible=args.voice_output_response_visible,
        capability_status_visible=args.capability_status_visible,
        checks_visible=args.checks_visible,
        synthesis_blocked=args.synthesis_blocked,
        audio_generation_blocked=args.audio_generation_blocked,
        audio_playback_not_used=args.audio_playback_not_used,
        generated_audio_absent=args.generated_audio_absent,
        audio_url_hidden_or_absent=args.audio_url_hidden_or_absent,
        text_body_hidden_or_placeholder=args.text_body_hidden_or_placeholder,
        provider_call_not_made=args.provider_call_not_made,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Render public-safe Day40 voice output smartphone Web boundary evidence."
    )
    parser.add_argument("--record-manual-ui-evidence", action="store_true")
    parser.add_argument("--backend-status-ok", action="store_true")
    parser.add_argument("--api-base-url-visible", action="store_true")
    parser.add_argument("--voice-output-section-visible", action="store_true")
    parser.add_argument("--voice-output-button-visible", action="store_true")
    parser.add_argument("--voice-output-request-sent", action="store_true")
    parser.add_argument("--voice-output-response-visible", action="store_true")
    parser.add_argument("--capability-status-visible", action="store_true")
    parser.add_argument("--checks-visible", action="store_true")
    parser.add_argument("--synthesis-blocked", action="store_true")
    parser.add_argument("--audio-generation-blocked", action="store_true")
    parser.add_argument("--audio-playback-not-used", action="store_true")
    parser.add_argument("--generated-audio-absent", action="store_true")
    parser.add_argument("--audio-url-hidden-or-absent", action="store_true")
    parser.add_argument("--text-body-hidden-or-placeholder", action="store_true")
    parser.add_argument("--provider-call-not-made", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    evidence = (
        _build_manual_evidence(args)
        if args.record_manual_ui_evidence
        else _build_source_tree_evidence()
    )
    rendered_lines = render_voice_output_smartphone_web_boundary_evidence(evidence)
    rendered = "\n".join(rendered_lines)
    _assert_public_safe(rendered)

    label = "configured" if args.record_manual_ui_evidence else "source-tree"
    print(f"[smoke-framework-voice-output-smartphone-web-boundary-evidence-{label}] RESULT")
    print(rendered)
    if evidence.status != "verified":
        raise SystemExit(1)
    print(
        "Voice output smartphone Web boundary evidence was rendered without synthesized audio, generated audio files, audio URLs, provider payloads, API key values, private paths, raw LAN IPs, audio playback, or TTS provider calls."
    )


if __name__ == "__main__":
    main()
