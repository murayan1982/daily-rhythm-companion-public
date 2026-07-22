"""v2.0.0 Day65 real TTS Web audio output execution evidence acceptance.

This module validates marker-only evidence for the second v2.0.0 real execution
requirement. It deliberately avoids provider SDK imports, AI Character
Framework voice output calls, backend requests, browser automation, audio
synthesis, audio playback, audio artifact inspection, and release artifact
creation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class V200RealTtsWebAudioExecutionEvidenceItem:
    """One required Day65 execution evidence marker."""

    key: str
    status: str
    description: str


@dataclass(frozen=True)
class V200RealTtsWebAudioExecutionEvidenceResult:
    """Public-safe Day65 execution evidence contract."""

    status: str
    requirement_key: str
    evidence_items: tuple[V200RealTtsWebAudioExecutionEvidenceItem, ...]
    required_operator_markers: tuple[str, ...]
    public_safe_omissions: tuple[str, ...]
    forbidden_success_states: tuple[str, ...]
    operator_run_required: bool
    mock_safe_default: bool
    next_focus: str


@dataclass(frozen=True)
class V200RealTtsWebAudioExecutionEvidenceValidation:
    """Validation result for a marker-only Day65 evidence summary."""

    status: str
    accepted_markers: tuple[str, ...]
    missing_markers: tuple[str, ...]
    public_safe: bool
    forbidden_success_states_absent: bool


def build_v200_real_tts_web_audio_execution_evidence_contract() -> V200RealTtsWebAudioExecutionEvidenceResult:
    """Build the Day65 real TTS Web audio execution evidence contract.

    The returned structure is static and source-tree safe. It must not call a
    TTS provider, AI Character Framework, DRC backend, browser, Flutter, audio
    device, file-system audio artifact, or release packaging command.
    """

    evidence_items = (
        V200RealTtsWebAudioExecutionEvidenceItem(
            key="explicit_operator_opt_in",
            status="required",
            description=(
                "A prepared operator must explicitly enable the configured real "
                "TTS run; normal checks must remain credential-free."
            ),
        ),
        V200RealTtsWebAudioExecutionEvidenceItem(
            key="framework_voice_output_boundary_used",
            status="required",
            description=(
                "The configured run must use the AI Character Framework voice "
                "output boundary instead of DRC-owned provider-specific TTS code."
            ),
        ),
        V200RealTtsWebAudioExecutionEvidenceItem(
            key="neutral_voice_contract_used",
            status="required",
            description=(
                "DRC must pass neutral request fields such as voice_profile_id, "
                "text, requested_audio_format, character_id, and utterance_purpose."
            ),
        ),
        V200RealTtsWebAudioExecutionEvidenceItem(
            key="real_provider_synthesis_confirmed",
            status="required",
            description=(
                "The operator must confirm a configured real TTS provider "
                "synthesized audio without publishing raw provider payloads."
            ),
        ),
        V200RealTtsWebAudioExecutionEvidenceItem(
            key="safe_backend_audio_contract_confirmed",
            status="required",
            description=(
                "The generated voice must be exposed to the Web UI through a "
                "safe backend contract that does not leak provider internals."
            ),
        ),
        V200RealTtsWebAudioExecutionEvidenceItem(
            key="smartphone_web_audio_audibly_confirmed",
            status="required",
            description=(
                "The operator must confirm the smartphone Web UI audibly plays "
                "the generated voice."
            ),
        ),
        V200RealTtsWebAudioExecutionEvidenceItem(
            key="fallback_or_skip_not_counted",
            status="required",
            description=(
                "Mock, fallback, skipped, unavailable, synthesis failure, and "
                "playback failure states must not count as real TTS success."
            ),
        ),
        V200RealTtsWebAudioExecutionEvidenceItem(
            key="public_safe_evidence_recorded",
            status="required",
            description=(
                "Shared evidence must be marker-only and omit secrets, private "
                "text bodies, provider payloads, generated audio artifacts, raw "
                "audio URLs, LAN IPs, private paths, screenshots, and browser storage."
            ),
        ),
    )

    return V200RealTtsWebAudioExecutionEvidenceResult(
        status="operator-execution-evidence-contract-ready",
        requirement_key="real_tts_web_audio_output",
        evidence_items=evidence_items,
        required_operator_markers=(
            "explicit_operator_opt_in_enabled",
            "framework_voice_output_boundary_used",
            "neutral_voice_contract_used",
            "real_provider_synthesis_confirmed",
            "safe_backend_audio_contract_confirmed",
            "smartphone_web_audio_audibly_confirmed",
            "fallback_or_skip_not_counted",
            "public_safe_evidence_recorded",
        ),
        public_safe_omissions=(
            "api_keys",
            "private_text_bodies",
            "provider_voice_ids",
            "raw_provider_payloads",
            "raw_provider_errors_with_private_payloads",
            "generated_audio_artifacts",
            "raw_audio_urls",
            "raw_lan_ips",
            "private_paths",
            "raw_screenshots",
            "browser_storage_dumps",
        ),
        forbidden_success_states=(
            "mock_voice_output_counted_as_success",
            "framework_fallback_counted_as_success",
            "provider_unavailable_counted_as_success",
            "synthesis_failed_counted_as_success",
            "playback_failed_counted_as_success",
            "skipped_counted_as_success",
            "unavailable_counted_as_success",
            "error_counted_as_success",
        ),
        operator_run_required=True,
        mock_safe_default=True,
        next_focus="real-google-health-sleep-data-execution-evidence",
    )


def render_v200_real_tts_web_audio_execution_evidence(
    result: V200RealTtsWebAudioExecutionEvidenceResult,
) -> str:
    """Render public-safe Day65 execution evidence markers."""

    lines = [
        "v200_real_tts_web_audio_execution_evidence_status: " + result.status,
        "v200_real_tts_web_audio_execution_requirement_key: " + result.requirement_key,
        "v200_real_tts_web_audio_execution_operator_run_required: "
        + str(result.operator_run_required),
        "v200_real_tts_web_audio_execution_mock_safe_default: "
        + str(result.mock_safe_default),
        "v200_real_tts_web_audio_execution_required_operator_markers: "
        + ",".join(result.required_operator_markers),
        "v200_real_tts_web_audio_execution_public_safe_omissions: "
        + ",".join(result.public_safe_omissions),
        "v200_real_tts_web_audio_execution_forbidden_success_states: "
        + ",".join(result.forbidden_success_states),
    ]

    for item in result.evidence_items:
        lines.append(f"v200_real_tts_web_audio_execution_evidence_{item.key}: {item.status}")

    lines.extend(
        [
            "v200_real_tts_web_audio_execution_default_provider_call_status: not-called",
            "v200_real_tts_web_audio_execution_default_framework_voice_output_status: not-called",
            "v200_real_tts_web_audio_execution_default_backend_status: not-started",
            "v200_real_tts_web_audio_execution_default_browser_status: not-opened",
            "v200_real_tts_web_audio_execution_default_audio_generation_status: not-called",
            "v200_real_tts_web_audio_execution_default_audio_playback_status: not-started",
            "v200_real_tts_web_audio_execution_default_audio_artifact_status: not-created",
            "v200_real_tts_web_audio_execution_default_audio_url_status: not-recorded",
            "v200_real_tts_web_audio_execution_public_evidence_body_policy: marker-only-no-private-text-no-audio-artifact",
            "v200_real_tts_web_audio_execution_next_focus: " + result.next_focus,
        ]
    )

    return "\n".join(lines)


def validate_v200_real_tts_web_audio_execution_operator_evidence(
    evidence: Mapping[str, object],
) -> V200RealTtsWebAudioExecutionEvidenceValidation:
    """Validate marker-only Day65 operator evidence.

    This helper checks booleans only. It must not be pointed at raw provider
    payloads, private synthesis text, screenshots, audio files, audio URLs,
    token files, browser storage dumps, generated artifacts, or release work
    folders.
    """

    contract = build_v200_real_tts_web_audio_execution_evidence_contract()
    accepted: list[str] = []
    missing: list[str] = []

    for marker in contract.required_operator_markers:
        if evidence.get(marker) is True:
            accepted.append(marker)
        else:
            missing.append(marker)

    forbidden_publication_flags = (
        "api_keys_included",
        "private_text_bodies_included",
        "provider_voice_ids_included",
        "raw_provider_payloads_included",
        "raw_provider_errors_with_private_payloads_included",
        "generated_audio_artifacts_included",
        "audio_artifacts_committed",
        "raw_audio_urls_included",
        "raw_lan_ips_included",
        "private_paths_included",
        "raw_screenshots_included",
        "browser_storage_dumps_included",
    )
    public_safe = not any(evidence.get(flag) is True for flag in forbidden_publication_flags)
    forbidden_success_states_absent = not any(
        evidence.get(flag) is True for flag in contract.forbidden_success_states
    )

    status = (
        "accepted"
        if not missing and public_safe and forbidden_success_states_absent
        else "incomplete-or-unsafe"
    )

    return V200RealTtsWebAudioExecutionEvidenceValidation(
        status=status,
        accepted_markers=tuple(accepted),
        missing_markers=tuple(missing),
        public_safe=public_safe,
        forbidden_success_states_absent=forbidden_success_states_absent,
    )
