r"""Day41 smoke for recording v1.9.0 voice output smartphone Web evidence.

Default mode is source-tree only. It does not start Flutter, open a browser,
call the backend, import AI Character Framework audio modules, create sessions,
synthesize speech, generate audio files, play audio, call TTS providers, or
store text/audio/provider payload bodies. It verifies that Day40 manual
smartphone Web evidence can be represented as a public-safe v1.9.0 record.

Manual recording mode accepts booleans from an operator-run smartphone Web check:

    python scripts\smoke_framework_voice_output_smartphone_web_boundary_evidence_record.py ^
      --record-manual-ui-evidence ^
      --backend-status-ok ^
      --api-base-url-visible ^
      --voice-output-section-visible ^
      --voice-output-button-visible ^
      --voice-output-request-sent ^
      --voice-output-response-visible ^
      --capability-status-visible ^
      --checks-visible ^
      --synthesis-blocked ^
      --audio-generation-blocked ^
      --audio-playback-not-used ^
      --generated-audio-absent ^
      --audio-url-hidden-or-absent ^
      --text-body-hidden-or-placeholder ^
      --provider-call-not-made

The script never accepts or prints synthesized audio, generated audio files,
audio URLs, text bodies, provider payloads, API key values, private paths, raw
LAN IPs, raw screenshots, audio playback artifacts, or provider error payloads.
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

from app.services.framework_voice_output_smartphone_web_boundary_evidence import (
    evaluate_manual_voice_output_smartphone_web_boundary_evidence,
)
from app.services.framework_voice_output_smartphone_web_boundary_evidence_record import (
    VoiceOutputSmartphoneWebBoundaryEvidenceRecordInput,
    evaluate_voice_output_smartphone_web_boundary_evidence_record,
    render_voice_output_smartphone_web_boundary_evidence_record,
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
                "Public-safe voice output boundary record contained forbidden pattern: "
                + pattern
            )


def _build_record_input(
    *,
    backend_status_ok: bool,
    api_base_url_visible: bool,
    voice_output_section_visible: bool,
    voice_output_button_visible: bool,
    voice_output_request_sent: bool,
    voice_output_response_visible: bool,
    capability_status_visible: bool,
    checks_visible: bool,
    synthesis_blocked: bool,
    audio_generation_blocked: bool,
    audio_playback_not_used: bool,
    generated_audio_absent: bool,
    audio_url_hidden_or_absent: bool,
    text_body_hidden_or_placeholder: bool,
    provider_call_not_made: bool,
    evidence_mode: str,
) -> VoiceOutputSmartphoneWebBoundaryEvidenceRecordInput:
    evidence = evaluate_manual_voice_output_smartphone_web_boundary_evidence(
        backend_status_ok=backend_status_ok,
        api_base_url_visible=api_base_url_visible,
        voice_output_section_visible=voice_output_section_visible,
        voice_output_button_visible=voice_output_button_visible,
        voice_output_request_sent=voice_output_request_sent,
        voice_output_response_visible=voice_output_response_visible,
        capability_status_visible=capability_status_visible,
        checks_visible=checks_visible,
        synthesis_blocked=synthesis_blocked,
        audio_generation_blocked=audio_generation_blocked,
        audio_playback_not_used=audio_playback_not_used,
        generated_audio_absent=generated_audio_absent,
        audio_url_hidden_or_absent=audio_url_hidden_or_absent,
        text_body_hidden_or_placeholder=text_body_hidden_or_placeholder,
        provider_call_not_made=provider_call_not_made,
    )
    return VoiceOutputSmartphoneWebBoundaryEvidenceRecordInput(
        evidence_status=evidence.status,
        evidence_mode=evidence_mode,
        source_mode=evidence.source_mode,
        backend_status_ok=evidence.backend_status_ok,
        api_base_url_visible=evidence.api_base_url_visible,
        request_sent=evidence.request_sent,
        response_visible=evidence.response_visible,
        capability_status_visible=evidence.capability_status_visible,
        checks_visible=evidence.checks_visible,
        synthesis_blocked=evidence.synthesis_blocked,
        audio_generation_blocked=evidence.audio_generation_blocked,
        audio_playback_not_used=evidence.audio_playback_not_used,
        generated_audio_absent=evidence.generated_audio_absent,
        audio_url_hidden_or_absent=evidence.audio_url_hidden_or_absent,
        text_body_hidden_or_placeholder=evidence.text_body_hidden_or_placeholder,
        provider_call_not_made=evidence.provider_call_not_made,
        public_safe_evidence_only=evidence.public_safe_evidence_only,
    )


def _render_and_validate(record_input: VoiceOutputSmartphoneWebBoundaryEvidenceRecordInput) -> str:
    record = evaluate_voice_output_smartphone_web_boundary_evidence_record(record_input)
    rendered = "\n".join(render_voice_output_smartphone_web_boundary_evidence_record(record))
    _assert_public_safe(rendered)
    return rendered


def _run_source_tree_smoke() -> None:
    rendered = _render_and_validate(
        _build_record_input(
            backend_status_ok=True,
            api_base_url_visible=True,
            voice_output_section_visible=True,
            voice_output_button_visible=True,
            voice_output_request_sent=True,
            voice_output_response_visible=True,
            capability_status_visible=True,
            checks_visible=True,
            synthesis_blocked=True,
            audio_generation_blocked=True,
            audio_playback_not_used=True,
            generated_audio_absent=True,
            audio_url_hidden_or_absent=True,
            text_body_hidden_or_placeholder=True,
            provider_call_not_made=True,
            evidence_mode="source-tree-synthetic-smartphone-web-voice-output-boundary-record",
        )
    )
    required = [
        "v190_voice_output_smartphone_web_boundary_record_status: recorded",
        "v190_voice_output_smartphone_web_boundary_record_from_evidence_status: verified",
        "v190_voice_output_smartphone_web_boundary_record_source_mode: voice_output_demo_boundary",
        "v190_voice_output_smartphone_web_boundary_record_backend_status_ok: True",
        "v190_voice_output_smartphone_web_boundary_record_request_sent: True",
        "v190_voice_output_smartphone_web_boundary_record_response_visible: True",
        "v190_voice_output_smartphone_web_boundary_record_synthesis_blocked: True",
        "v190_voice_output_smartphone_web_boundary_record_audio_generation_blocked: True",
        "v190_voice_output_smartphone_web_boundary_record_generated_audio_absent: True",
        "v190_voice_output_smartphone_web_boundary_record_audio_url_hidden_or_absent: True",
        "v190_voice_output_smartphone_web_boundary_record_provider_call_not_made: True",
        "v190_voice_output_smartphone_web_boundary_record_next_step: update-fw40-capability-coverage-after-voice-output-boundary-evidence",
    ]
    for needle in required:
        if needle not in rendered:
            raise AssertionError(f"Missing source-tree voice output record marker: {needle}")
    print("[smoke-framework-voice-output-smartphone-web-boundary-evidence-record] OK")


def _run_manual_recording(args: argparse.Namespace) -> None:
    rendered = _render_and_validate(
        _build_record_input(
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
            evidence_mode="manual-smartphone-web-ui-voice-output-boundary-record",
        )
    )
    print("[smoke-framework-voice-output-smartphone-web-boundary-evidence-record-configured] RESULT")
    print(rendered)
    print(
        "v1.9.0 voice output smartphone Web boundary record was rendered without synthesized audio, generated audio files, audio URLs, text bodies, provider payloads, API key values, private paths, raw LAN IPs, raw screenshots, audio playback, or TTS provider calls."
    )


def main() -> None:
    parser = argparse.ArgumentParser()
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
    args = parser.parse_args()

    if args.record_manual_ui_evidence:
        _run_manual_recording(args)
        return
    _run_source_tree_smoke()


if __name__ == "__main__":
    main()
