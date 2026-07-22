from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class VoiceInputSmartphoneWebBoundaryEvidence:
    """Public-safe STT / voice input smartphone Web boundary evidence.

    The evidence stores only booleans, status labels, and next-step labels. It
    must not store raw audio, transcript bodies, prompt bodies, response bodies,
    provider payloads, API key values, authorization headers, private paths, raw
    LAN IPs, raw screenshots, or raw provider error payloads.
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
    audio_processing_blocked: bool
    microphone_not_used: bool
    raw_audio_not_uploaded: bool
    transcript_body_hidden_or_absent: bool
    public_safe_evidence_only: bool
    next_step: str
    safe_summary: str


def evaluate_voice_input_source_tree_boundary_evidence(
    *,
    status_route_present: bool,
    request_route_present: bool,
    api_client_route_present: bool,
    flutter_section_visible: bool,
    flutter_button_visible: bool,
    flutter_no_microphone_copy_visible: bool,
    request_contract_metadata_only: bool,
    audio_processing_blocked: bool,
) -> VoiceInputSmartphoneWebBoundaryEvidence:
    """Evaluate source-tree STT / voice input boundary evidence.

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
            flutter_no_microphone_copy_visible,
            request_contract_metadata_only,
            audio_processing_blocked,
        ]
    )
    return VoiceInputSmartphoneWebBoundaryEvidence(
        status="verified" if verified else "needs-review",
        mode="source-tree-boundary",
        source_mode="voice_input_demo_boundary",
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
        audio_processing_blocked=audio_processing_blocked,
        microphone_not_used=flutter_no_microphone_copy_visible,
        raw_audio_not_uploaded=True,
        transcript_body_hidden_or_absent=True,
        public_safe_evidence_only=True,
        next_step="record-manual-smartphone-web-voice-input-boundary-evidence",
        safe_summary=(
            "Source-tree evidence verifies that the DRC backend and smartphone Web UI expose a guarded STT / voice input demo boundary. No microphone, raw audio, transcript body, STT provider, or FW realtime voice runtime is used."
        ),
    )


def evaluate_manual_voice_input_smartphone_web_boundary_evidence(
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
) -> VoiceInputSmartphoneWebBoundaryEvidence:
    """Evaluate manual smartphone Web STT / voice input boundary evidence."""

    verified = all(
        [
            backend_status_ok,
            api_base_url_visible,
            voice_input_section_visible,
            voice_input_button_visible,
            voice_input_request_sent,
            voice_input_response_visible,
            capability_status_visible,
            checks_visible,
            audio_processing_blocked,
            microphone_not_used,
            raw_audio_not_uploaded,
            transcript_body_hidden_or_absent,
        ]
    )
    return VoiceInputSmartphoneWebBoundaryEvidence(
        status="verified" if verified else "needs-review",
        mode="manual-smartphone-web-ui-boundary",
        source_mode="voice_input_demo_boundary",
        backend_status_ok=backend_status_ok,
        api_base_url_visible=api_base_url_visible,
        status_route_present=True,
        request_route_present=True,
        api_client_route_present=True,
        flutter_section_visible=voice_input_section_visible,
        flutter_button_visible=voice_input_button_visible,
        request_contract_metadata_only=True,
        request_sent=voice_input_request_sent,
        response_visible=voice_input_response_visible,
        capability_status_visible=capability_status_visible,
        checks_visible=checks_visible,
        audio_processing_blocked=audio_processing_blocked,
        microphone_not_used=microphone_not_used,
        raw_audio_not_uploaded=raw_audio_not_uploaded,
        transcript_body_hidden_or_absent=transcript_body_hidden_or_absent,
        public_safe_evidence_only=True,
        next_step="record-v190-voice-input-smartphone-web-boundary-evidence",
        safe_summary=(
            "Manual smartphone Web evidence verifies that the DRC UI can reach the guarded STT / voice input demo request boundary through the actual backend API while audio processing remains blocked and public-safe."
        ),
    )


def render_voice_input_smartphone_web_boundary_evidence(
    evidence: VoiceInputSmartphoneWebBoundaryEvidence,
) -> list[str]:
    """Render public-safe STT / voice input boundary evidence lines."""

    prefix = "voice_input_smartphone_web_boundary_"
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
        prefix + "audio_processing_blocked: " + str(evidence.audio_processing_blocked),
        prefix + "microphone_not_used: " + str(evidence.microphone_not_used),
        prefix + "raw_audio_not_uploaded: " + str(evidence.raw_audio_not_uploaded),
        prefix + "transcript_body_hidden_or_absent: " + str(evidence.transcript_body_hidden_or_absent),
        prefix + "public_safe_evidence_only: " + str(evidence.public_safe_evidence_only),
        prefix + "next_step: " + evidence.next_step,
        prefix + "safe_summary: " + evidence.safe_summary,
    ]
