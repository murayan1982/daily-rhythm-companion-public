"""v2.0.0 real TTS Web audio output evidence checkpoint.

This module records the public-safe evidence contract for the second v2.0.0
pre-release requirement after the Day53 provider gate design. It deliberately
avoids provider SDK imports, framework voice output calls, backend calls,
audio generation, audio playback, browser automation, or audio artifact writes.

The actual configured run remains an operator-only step. Public evidence should
prove the shape of the run without committing API keys, provider payloads,
private text bodies, audio files, raw LAN IPs, private paths, or screenshots.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class V200RealTtsWebAudioEvidenceItem:
    key: str
    status: str
    description: str


@dataclass(frozen=True)
class V200RealTtsWebAudioEvidenceResult:
    status: str
    requirement_key: str
    evidence_items: tuple[V200RealTtsWebAudioEvidenceItem, ...]
    required_operator_markers: tuple[str, ...]
    public_safe_omissions: tuple[str, ...]
    operator_run_required: bool
    mock_safe_default: bool
    next_focus: str


@dataclass(frozen=True)
class V200RealTtsWebAudioOperatorEvidenceValidation:
    status: str
    accepted_markers: tuple[str, ...]
    missing_markers: tuple[str, ...]
    public_safe: bool


def build_v200_real_tts_web_audio_evidence_contract() -> V200RealTtsWebAudioEvidenceResult:
    """Build the Day54 real TTS Web audio evidence contract.

    The returned structure is static and source-tree safe. It does not inspect
    provider credentials, call AI Character Framework, generate audio, start
    Flutter, open a browser, or contact a running backend.
    """

    evidence_items = (
        V200RealTtsWebAudioEvidenceItem(
            key="explicit_operator_opt_in",
            status="required",
            description=(
                "The configured real TTS run must be manually enabled by an "
                "operator and must never run as part of normal checks."
            ),
        ),
        V200RealTtsWebAudioEvidenceItem(
            key="framework_voice_output_boundary_used",
            status="required",
            description=(
                "The DRC backend must request voice output through the neutral "
                "AI Character Framework voice output boundary prepared by Day53."
            ),
        ),
        V200RealTtsWebAudioEvidenceItem(
            key="provider_synthesis_confirmed",
            status="required",
            description=(
                "The configured provider synthesis must be confirmed without "
                "publishing provider-specific payloads or secret-bearing logs."
            ),
        ),
        V200RealTtsWebAudioEvidenceItem(
            key="safe_backend_audio_contract",
            status="required",
            description=(
                "Generated audio must be exposed to Web through a safe backend "
                "contract that avoids raw provider payload leakage."
            ),
        ),
        V200RealTtsWebAudioEvidenceItem(
            key="web_audio_output_audibly_confirmed",
            status="required",
            description=(
                "The operator must confirm that the Web UI can audibly output "
                "the generated voice."
            ),
        ),
        V200RealTtsWebAudioEvidenceItem(
            key="public_safe_evidence_recorded",
            status="required",
            description=(
                "Shared evidence must be marker-based and must omit private "
                "text, API keys, provider payloads, audio artifacts, local "
                "paths, raw LAN IPs, and screenshots."
            ),
        ),
    )

    return V200RealTtsWebAudioEvidenceResult(
        status="operator-evidence-contract-ready",
        requirement_key="real_tts_web_audio_output",
        evidence_items=evidence_items,
        required_operator_markers=(
            "explicit_operator_opt_in_enabled",
            "framework_voice_output_boundary_used",
            "provider_synthesis_confirmed",
            "safe_backend_audio_contract_confirmed",
            "web_audio_output_audibly_confirmed",
            "public_safe_evidence_recorded",
        ),
        public_safe_omissions=(
            "api_keys",
            "private_text_bodies",
            "raw_provider_payloads",
            "audio_artifacts",
            "raw_lan_ips",
            "private_paths",
            "raw_screenshots",
        ),
        operator_run_required=True,
        mock_safe_default=True,
        next_focus="real-google-health-sleep-data-evidence",
    )


def render_v200_real_tts_web_audio_evidence(
    result: V200RealTtsWebAudioEvidenceResult,
) -> str:
    """Render public-safe Day54 evidence markers."""

    lines = [
        "v200_real_tts_web_audio_evidence_status: " + result.status,
        "v200_real_tts_web_audio_requirement_key: " + result.requirement_key,
        "v200_real_tts_web_audio_operator_run_required: "
        + str(result.operator_run_required),
        "v200_real_tts_web_audio_mock_safe_default: "
        + str(result.mock_safe_default),
        "v200_real_tts_web_audio_required_operator_markers: "
        + ",".join(result.required_operator_markers),
        "v200_real_tts_web_audio_public_safe_omissions: "
        + ",".join(result.public_safe_omissions),
    ]

    for item in result.evidence_items:
        lines.append(f"v200_real_tts_web_audio_evidence_{item.key}: {item.status}")

    lines.extend(
        [
            "v200_real_tts_web_audio_default_provider_call_status: not-called",
            "v200_real_tts_web_audio_default_framework_call_status: not-called",
            "v200_real_tts_web_audio_default_backend_call_status: not-called",
            "v200_real_tts_web_audio_default_browser_status: not-opened",
            "v200_real_tts_web_audio_default_audio_generation_status: not-called",
            "v200_real_tts_web_audio_default_audio_playback_status: not-started",
            "v200_real_tts_web_audio_default_audio_artifact_status: not-created",
            "v200_real_tts_web_audio_public_evidence_body_policy: marker-only-no-private-text",
            "v200_real_tts_web_audio_next_focus: " + result.next_focus,
        ]
    )

    return "\n".join(lines)


def validate_v200_real_tts_web_audio_operator_evidence(
    evidence: Mapping[str, object],
) -> V200RealTtsWebAudioOperatorEvidenceValidation:
    """Validate a redacted operator evidence shape without reading artifacts.

    This helper is intentionally conservative. It checks public-safe marker
    booleans only and rejects evidence that appears to claim raw payload/audio
    publication. It should be used on a small redacted JSON summary, not on
    provider responses or screenshots.
    """

    contract = build_v200_real_tts_web_audio_evidence_contract()
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
        "raw_provider_payloads_included",
        "audio_artifacts_committed",
        "raw_lan_ips_included",
        "private_paths_included",
        "raw_screenshots_included",
    )
    public_safe = all(evidence.get(flag) is not True for flag in forbidden_publication_flags)

    status = "accepted" if not missing and public_safe else "incomplete-or-unsafe"
    return V200RealTtsWebAudioOperatorEvidenceValidation(
        status=status,
        accepted_markers=tuple(accepted),
        missing_markers=tuple(missing),
        public_safe=public_safe,
    )
