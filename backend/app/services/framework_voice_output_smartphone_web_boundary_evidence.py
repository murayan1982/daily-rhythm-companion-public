from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class VoiceOutputSmartphoneWebBoundaryEvidence:
    """Public-safe TTS / voice output smartphone Web boundary evidence.

    The evidence stores only booleans, status labels, and next-step labels. It
    must not store synthesized audio, audio URLs, text bodies, provider payloads,
    API key values, authorization headers, private paths, raw LAN IPs, raw
    screenshots, raw provider error payloads, or generated audio artifacts.
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
    synthesis_blocked: bool
    audio_generation_blocked: bool
    audio_playback_not_used: bool
    generated_audio_absent: bool
    audio_url_hidden_or_absent: bool
    text_body_hidden_or_placeholder: bool
    provider_call_not_made: bool
    public_safe_evidence_only: bool
    next_step: str
    safe_summary: str


def evaluate_voice_output_source_tree_boundary_evidence(
    *,
    status_route_present: bool,
    request_route_present: bool,
    api_client_route_present: bool,
    flutter_section_visible: bool,
    flutter_button_visible: bool,
    flutter_no_audio_copy_visible: bool,
    request_contract_metadata_only: bool,
    synthesis_blocked: bool,
    audio_generation_blocked: bool,
    audio_playback_not_used: bool,
) -> VoiceOutputSmartphoneWebBoundaryEvidence:
    """Evaluate source-tree TTS / voice output boundary evidence.

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
            flutter_no_audio_copy_visible,
            request_contract_metadata_only,
            synthesis_blocked,
            audio_generation_blocked,
            audio_playback_not_used,
        ]
    )
    return VoiceOutputSmartphoneWebBoundaryEvidence(
        status="verified" if verified else "needs-review",
        mode="source-tree-boundary",
        source_mode="voice_output_demo_boundary",
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
        synthesis_blocked=synthesis_blocked,
        audio_generation_blocked=audio_generation_blocked,
        audio_playback_not_used=audio_playback_not_used,
        generated_audio_absent=True,
        audio_url_hidden_or_absent=True,
        text_body_hidden_or_placeholder=True,
        provider_call_not_made=True,
        public_safe_evidence_only=True,
        next_step="record-manual-smartphone-web-voice-output-boundary-evidence",
        safe_summary=(
            "Source-tree evidence verifies that the DRC backend and smartphone Web UI expose a guarded TTS / voice output demo boundary. No synthesis, generated audio file, audio playback, audio URL, TTS provider, or FW voice output runtime is used."
        ),
    )


def evaluate_manual_voice_output_smartphone_web_boundary_evidence(
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
) -> VoiceOutputSmartphoneWebBoundaryEvidence:
    """Evaluate manual smartphone Web TTS / voice output boundary evidence."""

    verified = all(
        [
            backend_status_ok,
            api_base_url_visible,
            voice_output_section_visible,
            voice_output_button_visible,
            voice_output_request_sent,
            voice_output_response_visible,
            capability_status_visible,
            checks_visible,
            synthesis_blocked,
            audio_generation_blocked,
            audio_playback_not_used,
            generated_audio_absent,
            audio_url_hidden_or_absent,
            text_body_hidden_or_placeholder,
            provider_call_not_made,
        ]
    )
    return VoiceOutputSmartphoneWebBoundaryEvidence(
        status="verified" if verified else "needs-review",
        mode="manual-smartphone-web-ui-boundary",
        source_mode="voice_output_demo_boundary",
        backend_status_ok=backend_status_ok,
        api_base_url_visible=api_base_url_visible,
        status_route_present=True,
        request_route_present=True,
        api_client_route_present=True,
        flutter_section_visible=voice_output_section_visible,
        flutter_button_visible=voice_output_button_visible,
        request_contract_metadata_only=True,
        request_sent=voice_output_request_sent,
        response_visible=voice_output_response_visible,
        capability_status_visible=capability_status_visible,
        checks_visible=checks_visible,
        synthesis_blocked=synthesis_blocked,
        audio_generation_blocked=audio_generation_blocked,
        audio_playback_not_used=audio_playback_not_used,
        generated_audio_absent=generated_audio_absent,
        audio_url_hidden_or_absent=audio_url_hidden_or_absent,
        text_body_hidden_or_placeholder=text_body_hidden_or_placeholder,
        provider_call_not_made=provider_call_not_made,
        public_safe_evidence_only=True,
        next_step="record-v190-voice-output-smartphone-web-boundary-evidence",
        safe_summary=(
            "Manual smartphone Web evidence verifies that the DRC UI can reach the guarded TTS / voice output demo request boundary through the actual backend API while synthesis remains blocked and public-safe."
        ),
    )


def render_voice_output_smartphone_web_boundary_evidence(
    evidence: VoiceOutputSmartphoneWebBoundaryEvidence,
) -> list[str]:
    """Render public-safe TTS / voice output boundary evidence lines."""

    prefix = "voice_output_smartphone_web_boundary_"
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
        prefix + "synthesis_blocked: " + str(evidence.synthesis_blocked),
        prefix + "audio_generation_blocked: " + str(evidence.audio_generation_blocked),
        prefix + "audio_playback_not_used: " + str(evidence.audio_playback_not_used),
        prefix + "generated_audio_absent: " + str(evidence.generated_audio_absent),
        prefix + "audio_url_hidden_or_absent: " + str(evidence.audio_url_hidden_or_absent),
        prefix + "text_body_hidden_or_placeholder: " + str(evidence.text_body_hidden_or_placeholder),
        prefix + "provider_call_not_made: " + str(evidence.provider_call_not_made),
        prefix + "public_safe_evidence_only: " + str(evidence.public_safe_evidence_only),
        prefix + "next_step: " + evidence.next_step,
        prefix + "safe_summary: " + evidence.safe_summary,
    ]
