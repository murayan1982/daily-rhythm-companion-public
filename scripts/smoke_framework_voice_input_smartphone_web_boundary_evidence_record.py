r"""Day38 smoke for recording v1.9.0 voice input smartphone Web evidence.

Default mode is source-tree only. It does not start Flutter, open a browser,
call the backend, import AI Character Framework voice modules, create realtime
voice sessions, touch microphones, read or upload audio, call STT providers, or
store transcript bodies. It verifies that Day37 manual smartphone Web evidence
can be represented as a public-safe v1.9.0 record.

Manual recording mode accepts booleans from an operator-run smartphone Web check:

    python scripts\smoke_framework_voice_input_smartphone_web_boundary_evidence_record.py ^
      --record-manual-ui-evidence ^
      --backend-status-ok ^
      --api-base-url-visible ^
      --voice-input-section-visible ^
      --voice-input-button-visible ^
      --voice-input-request-sent ^
      --voice-input-response-visible ^
      --capability-status-visible ^
      --checks-visible ^
      --audio-processing-blocked ^
      --microphone-not-used ^
      --raw-audio-not-uploaded ^
      --transcript-body-hidden-or-absent

The script never accepts or prints raw audio, transcript bodies, provider
payloads, API key values, private paths, raw LAN IPs, or raw screenshots.
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
)
from app.services.framework_voice_input_smartphone_web_boundary_evidence_record import (
    VoiceInputSmartphoneWebBoundaryEvidenceRecordInput,
    evaluate_voice_input_smartphone_web_boundary_evidence_record,
    render_voice_input_smartphone_web_boundary_evidence_record,
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
                "Public-safe voice input boundary record contained forbidden pattern: "
                + pattern
            )


def _build_record_input(
    *,
    backend_status_ok: bool,
    api_base_url_visible: bool,
    voice_input_section_visible: bool,
    voice_input_button_visible: bool,
    voice_input_request_sent: bool,
    voice_input_response_visible: bool,
    capability_status_visible: bool,
    checks_visible: bool,
    audio_processing_blocked: bool,
    microphone_not_used: bool,
    raw_audio_not_uploaded: bool,
    transcript_body_hidden_or_absent: bool,
    evidence_mode: str,
) -> VoiceInputSmartphoneWebBoundaryEvidenceRecordInput:
    evidence = evaluate_manual_voice_input_smartphone_web_boundary_evidence(
        backend_status_ok=backend_status_ok,
        api_base_url_visible=api_base_url_visible,
        voice_input_section_visible=voice_input_section_visible,
        voice_input_button_visible=voice_input_button_visible,
        voice_input_request_sent=voice_input_request_sent,
        voice_input_response_visible=voice_input_response_visible,
        capability_status_visible=capability_status_visible,
        checks_visible=checks_visible,
        audio_processing_blocked=audio_processing_blocked,
        microphone_not_used=microphone_not_used,
        raw_audio_not_uploaded=raw_audio_not_uploaded,
        transcript_body_hidden_or_absent=transcript_body_hidden_or_absent,
    )
    return VoiceInputSmartphoneWebBoundaryEvidenceRecordInput(
        evidence_status=evidence.status,
        evidence_mode=evidence_mode,
        source_mode=evidence.source_mode,
        backend_status_ok=evidence.backend_status_ok,
        api_base_url_visible=evidence.api_base_url_visible,
        request_sent=evidence.request_sent,
        response_visible=evidence.response_visible,
        capability_status_visible=evidence.capability_status_visible,
        checks_visible=evidence.checks_visible,
        audio_processing_blocked=evidence.audio_processing_blocked,
        microphone_not_used=evidence.microphone_not_used,
        raw_audio_not_uploaded=evidence.raw_audio_not_uploaded,
        transcript_body_hidden_or_absent=evidence.transcript_body_hidden_or_absent,
        public_safe_evidence_only=evidence.public_safe_evidence_only,
    )


def _render_and_validate(record_input: VoiceInputSmartphoneWebBoundaryEvidenceRecordInput) -> str:
    record = evaluate_voice_input_smartphone_web_boundary_evidence_record(record_input)
    rendered = "\n".join(render_voice_input_smartphone_web_boundary_evidence_record(record))
    _assert_public_safe(rendered)
    return rendered


def _run_source_tree_smoke() -> None:
    rendered = _render_and_validate(
        _build_record_input(
            backend_status_ok=True,
            api_base_url_visible=True,
            voice_input_section_visible=True,
            voice_input_button_visible=True,
            voice_input_request_sent=True,
            voice_input_response_visible=True,
            capability_status_visible=True,
            checks_visible=True,
            audio_processing_blocked=True,
            microphone_not_used=True,
            raw_audio_not_uploaded=True,
            transcript_body_hidden_or_absent=True,
            evidence_mode="source-tree-synthetic-smartphone-web-voice-input-boundary-record",
        )
    )
    required = [
        "v190_voice_input_smartphone_web_boundary_record_status: recorded",
        "v190_voice_input_smartphone_web_boundary_record_from_evidence_status: verified",
        "v190_voice_input_smartphone_web_boundary_record_source_mode: voice_input_demo_boundary",
        "v190_voice_input_smartphone_web_boundary_record_backend_status_ok: True",
        "v190_voice_input_smartphone_web_boundary_record_request_sent: True",
        "v190_voice_input_smartphone_web_boundary_record_response_visible: True",
        "v190_voice_input_smartphone_web_boundary_record_audio_processing_blocked: True",
        "v190_voice_input_smartphone_web_boundary_record_raw_audio_not_uploaded: True",
        "v190_voice_input_smartphone_web_boundary_record_transcript_body_hidden_or_absent: True",
        "v190_voice_input_smartphone_web_boundary_record_next_step: update-fw40-capability-coverage-after-voice-input-boundary-evidence",
    ]
    for needle in required:
        if needle not in rendered:
            raise AssertionError(f"Missing source-tree voice input record marker: {needle}")
    print("[smoke-framework-voice-input-smartphone-web-boundary-evidence-record] OK")


def _run_manual_recording(args: argparse.Namespace) -> None:
    rendered = _render_and_validate(
        _build_record_input(
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
            evidence_mode="manual-smartphone-web-ui-voice-input-boundary-record",
        )
    )
    print("[smoke-framework-voice-input-smartphone-web-boundary-evidence-record-configured] RESULT")
    print(rendered)
    print(
        "v1.9.0 voice input smartphone Web boundary record was rendered without raw audio, transcript bodies, provider payloads, API key values, private paths, raw LAN IPs, raw screenshots, microphone access, or STT provider calls."
    )


def main() -> None:
    parser = argparse.ArgumentParser()
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
    args = parser.parse_args()

    if args.record_manual_ui_evidence:
        _run_manual_recording(args)
        return
    _run_source_tree_smoke()


if __name__ == "__main__":
    main()
