from __future__ import annotations

from dataclasses import dataclass


EXPECTED_VOICE_INPUT_EVIDENCE_STATUS = "verified"
EXPECTED_VOICE_INPUT_SOURCE_MODE = "voice_input_demo_boundary"


@dataclass(frozen=True)
class VoiceInputSmartphoneWebBoundaryEvidenceRecordInput:
    """Public-safe input for the v1.9.0 voice input smartphone Web record.

    The record stores booleans, source labels, and status markers only. It must
    not store raw audio, transcript bodies, prompt bodies, response bodies,
    provider payloads, API key values, authorization headers, private paths,
    raw LAN IPs, raw screenshots, or raw provider error payloads.
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
    audio_processing_blocked: bool
    microphone_not_used: bool
    raw_audio_not_uploaded: bool
    transcript_body_hidden_or_absent: bool
    public_safe_evidence_only: bool


@dataclass(frozen=True)
class VoiceInputSmartphoneWebBoundaryEvidenceRecordResult:
    """Rendered v1.9.0 voice input smartphone Web boundary evidence record."""

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
    audio_processing_blocked: bool
    microphone_not_used: bool
    raw_audio_not_uploaded: bool
    transcript_body_hidden_or_absent: bool
    public_safe_evidence_only: bool
    next_step: str
    safe_summary: str


def evaluate_voice_input_smartphone_web_boundary_evidence_record(
    evidence: VoiceInputSmartphoneWebBoundaryEvidenceRecordInput,
) -> VoiceInputSmartphoneWebBoundaryEvidenceRecordResult:
    """Evaluate whether voice input smartphone Web evidence is ready to record."""

    source_mode_matches = evidence.source_mode == EXPECTED_VOICE_INPUT_SOURCE_MODE
    required_flags = (
        evidence.evidence_status == EXPECTED_VOICE_INPUT_EVIDENCE_STATUS,
        source_mode_matches,
        evidence.backend_status_ok,
        evidence.api_base_url_visible,
        evidence.request_sent,
        evidence.response_visible,
        evidence.capability_status_visible,
        evidence.checks_visible,
        evidence.audio_processing_blocked,
        evidence.microphone_not_used,
        evidence.raw_audio_not_uploaded,
        evidence.transcript_body_hidden_or_absent,
        evidence.public_safe_evidence_only,
    )
    recorded = all(required_flags)
    return VoiceInputSmartphoneWebBoundaryEvidenceRecordResult(
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
        audio_processing_blocked=evidence.audio_processing_blocked,
        microphone_not_used=evidence.microphone_not_used,
        raw_audio_not_uploaded=evidence.raw_audio_not_uploaded,
        transcript_body_hidden_or_absent=evidence.transcript_body_hidden_or_absent,
        public_safe_evidence_only=evidence.public_safe_evidence_only,
        next_step=(
            "update-fw40-capability-coverage-after-voice-input-boundary-evidence"
            if recorded
            else "complete-v190-voice-input-smartphone-web-boundary-evidence-record"
        ),
        safe_summary=(
            "v1.9.0 voice input smartphone Web boundary evidence is recorded: "
            "the guarded DRC voice input demo boundary was visible and reachable "
            "through the actual backend API while audio processing stayed blocked "
            "and evidence remained public-safe."
            if recorded
            else "v1.9.0 voice input smartphone Web boundary evidence is incomplete; rerun the public-safe checklist."
        ),
    )


def render_voice_input_smartphone_web_boundary_evidence_record(
    result: VoiceInputSmartphoneWebBoundaryEvidenceRecordResult,
) -> list[str]:
    """Render public-safe voice input boundary record lines."""

    prefix = "v190_voice_input_smartphone_web_boundary_record_"
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
        prefix + "audio_processing_blocked: " + str(result.audio_processing_blocked),
        prefix + "microphone_not_used: " + str(result.microphone_not_used),
        prefix + "raw_audio_not_uploaded: " + str(result.raw_audio_not_uploaded),
        prefix + "transcript_body_hidden_or_absent: " + str(result.transcript_body_hidden_or_absent),
        prefix + "public_safe_evidence_only: " + str(result.public_safe_evidence_only),
        prefix + "next_step: " + result.next_step,
        prefix + "safe_summary: " + result.safe_summary,
    ]
