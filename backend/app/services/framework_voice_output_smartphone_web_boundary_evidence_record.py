from __future__ import annotations

from dataclasses import dataclass


EXPECTED_VOICE_OUTPUT_EVIDENCE_STATUS = "verified"
EXPECTED_VOICE_OUTPUT_SOURCE_MODE = "voice_output_demo_boundary"


@dataclass(frozen=True)
class VoiceOutputSmartphoneWebBoundaryEvidenceRecordInput:
    """Public-safe input for the v1.9.0 voice output smartphone Web record.

    The record stores booleans, source labels, and status markers only. It must
    not store synthesized audio, generated audio files, audio URLs, text bodies,
    provider payloads, API key values, authorization headers, private paths, raw
    LAN IPs, raw screenshots, raw provider error payloads, or playback artifacts.
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
    synthesis_blocked: bool
    audio_generation_blocked: bool
    audio_playback_not_used: bool
    generated_audio_absent: bool
    audio_url_hidden_or_absent: bool
    text_body_hidden_or_placeholder: bool
    provider_call_not_made: bool
    public_safe_evidence_only: bool


@dataclass(frozen=True)
class VoiceOutputSmartphoneWebBoundaryEvidenceRecordResult:
    """Rendered v1.9.0 voice output smartphone Web boundary evidence record."""

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


def evaluate_voice_output_smartphone_web_boundary_evidence_record(
    evidence: VoiceOutputSmartphoneWebBoundaryEvidenceRecordInput,
) -> VoiceOutputSmartphoneWebBoundaryEvidenceRecordResult:
    """Evaluate whether voice output smartphone Web evidence is ready to record."""

    source_mode_matches = evidence.source_mode == EXPECTED_VOICE_OUTPUT_SOURCE_MODE
    required_flags = (
        evidence.evidence_status == EXPECTED_VOICE_OUTPUT_EVIDENCE_STATUS,
        source_mode_matches,
        evidence.backend_status_ok,
        evidence.api_base_url_visible,
        evidence.request_sent,
        evidence.response_visible,
        evidence.capability_status_visible,
        evidence.checks_visible,
        evidence.synthesis_blocked,
        evidence.audio_generation_blocked,
        evidence.audio_playback_not_used,
        evidence.generated_audio_absent,
        evidence.audio_url_hidden_or_absent,
        evidence.text_body_hidden_or_placeholder,
        evidence.provider_call_not_made,
        evidence.public_safe_evidence_only,
    )
    recorded = all(required_flags)
    return VoiceOutputSmartphoneWebBoundaryEvidenceRecordResult(
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
        synthesis_blocked=evidence.synthesis_blocked,
        audio_generation_blocked=evidence.audio_generation_blocked,
        audio_playback_not_used=evidence.audio_playback_not_used,
        generated_audio_absent=evidence.generated_audio_absent,
        audio_url_hidden_or_absent=evidence.audio_url_hidden_or_absent,
        text_body_hidden_or_placeholder=evidence.text_body_hidden_or_placeholder,
        provider_call_not_made=evidence.provider_call_not_made,
        public_safe_evidence_only=evidence.public_safe_evidence_only,
        next_step=(
            "update-fw40-capability-coverage-after-voice-output-boundary-evidence"
            if recorded
            else "complete-v190-voice-output-smartphone-web-boundary-evidence-record"
        ),
        safe_summary=(
            "v1.9.0 voice output smartphone Web boundary evidence is recorded: "
            "the guarded DRC voice output demo boundary was visible and reachable "
            "through the actual backend API while synthesis, audio generation, "
            "playback, and provider calls stayed blocked and evidence remained "
            "public-safe."
            if recorded
            else "v1.9.0 voice output smartphone Web boundary evidence is incomplete; rerun the public-safe checklist."
        ),
    )


def render_voice_output_smartphone_web_boundary_evidence_record(
    result: VoiceOutputSmartphoneWebBoundaryEvidenceRecordResult,
) -> list[str]:
    """Render public-safe voice output boundary record lines."""

    prefix = "v190_voice_output_smartphone_web_boundary_record_"
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
        prefix + "synthesis_blocked: " + str(result.synthesis_blocked),
        prefix + "audio_generation_blocked: " + str(result.audio_generation_blocked),
        prefix + "audio_playback_not_used: " + str(result.audio_playback_not_used),
        prefix + "generated_audio_absent: " + str(result.generated_audio_absent),
        prefix + "audio_url_hidden_or_absent: " + str(result.audio_url_hidden_or_absent),
        prefix + "text_body_hidden_or_placeholder: " + str(result.text_body_hidden_or_placeholder),
        prefix + "provider_call_not_made: " + str(result.provider_call_not_made),
        prefix + "public_safe_evidence_only: " + str(result.public_safe_evidence_only),
        prefix + "next_step: " + result.next_step,
        prefix + "safe_summary: " + result.safe_summary,
    ]
