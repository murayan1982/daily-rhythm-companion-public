"""v2.0.0 real TTS provider gate design checkpoint.

This module records the public-safe contract for the second v2.0.0
pre-release gate. It deliberately avoids provider SDK imports, backend
calls, audio generation, audio playback, or persistence of text/audio bodies.

DRC should request voice output through a neutral AI Character Framework
boundary. Provider-specific voice IDs, API keys, provider parameters,
endpoint selection, and provider payload handling stay framework-side.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class V200RealTtsProviderGateItem:
    key: str
    status: str
    description: str


@dataclass(frozen=True)
class V200RealTtsProviderGateResult:
    status: str
    requirement_key: str
    gate_items: tuple[V200RealTtsProviderGateItem, ...]
    neutral_contract_fields: tuple[str, ...]
    operator_run_required: bool
    mock_safe_default: bool
    next_focus: str


def build_v200_real_tts_provider_gate() -> V200RealTtsProviderGateResult:
    """Build the Day53 real TTS provider gate contract.

    The returned structure is intentionally static and safe to render from
    default checks. It does not inspect environment variables, connect to
    AI Character Framework, call ElevenLabs/OpenAI TTS, generate audio, or
    open a browser.
    """

    gate_items = (
        V200RealTtsProviderGateItem(
            key="explicit_operator_opt_in",
            status="required",
            description=(
                "Real TTS provider calls must require an explicit operator "
                "opt-in and must never happen during normal mock-safe checks."
            ),
        ),
        V200RealTtsProviderGateItem(
            key="framework_voice_output_boundary",
            status="required",
            description=(
                "DRC must request voice output through the AI Character "
                "Framework voice output boundary instead of embedding a "
                "provider-specific TTS implementation."
            ),
        ),
        V200RealTtsProviderGateItem(
            key="neutral_request_contract",
            status="required",
            description=(
                "The app-facing request must stay neutral: voice_profile_id, "
                "text, requested_audio_format, character_id, and "
                "utterance_purpose are acceptable app-level fields."
            ),
        ),
        V200RealTtsProviderGateItem(
            key="provider_specific_config_fw_owned",
            status="required",
            description=(
                "Provider voice IDs, API keys, endpoint parameters, and raw "
                "provider payload handling remain AI Character Framework "
                "responsibilities."
            ),
        ),
        V200RealTtsProviderGateItem(
            key="web_audio_output_evidence",
            status="required",
            description=(
                "A later operator run must confirm that generated audio can "
                "be exposed through a safe backend contract and output from Web."
            ),
        ),
        V200RealTtsProviderGateItem(
            key="public_safe_evidence",
            status="required",
            description=(
                "Evidence must not commit private text bodies, API keys, raw "
                "provider payloads, local paths, LAN IPs, audio artifacts, or "
                "raw screenshots."
            ),
        ),
    )

    return V200RealTtsProviderGateResult(
        status="provider-gate-contract-ready",
        requirement_key="real_tts_web_audio_output",
        gate_items=gate_items,
        neutral_contract_fields=(
            "voice_profile_id",
            "text",
            "requested_audio_format",
            "character_id",
            "utterance_purpose",
        ),
        operator_run_required=True,
        mock_safe_default=True,
        next_focus="configured-real-tts-web-voice-output-evidence",
    )


def render_v200_real_tts_provider_gate(
    result: V200RealTtsProviderGateResult,
) -> str:
    """Render public-safe Day53 evidence markers."""

    lines = [
        "v200_real_tts_provider_gate_status: " + result.status,
        "v200_real_tts_provider_requirement_key: " + result.requirement_key,
        "v200_real_tts_provider_operator_run_required: "
        + str(result.operator_run_required),
        "v200_real_tts_provider_mock_safe_default: "
        + str(result.mock_safe_default),
        "v200_real_tts_provider_neutral_contract_fields: "
        + ",".join(result.neutral_contract_fields),
        "v200_real_tts_provider_drc_provider_specific_implementation: forbidden",
        "v200_real_tts_provider_provider_specific_config_owner: ai-character-framework",
    ]

    for item in result.gate_items:
        lines.append(f"v200_real_tts_provider_gate_{item.key}: {item.status}")

    lines.extend(
        [
            "v200_real_tts_provider_default_provider_call_status: not-called",
            "v200_real_tts_provider_default_framework_call_status: not-called",
            "v200_real_tts_provider_default_backend_call_status: not-called",
            "v200_real_tts_provider_default_audio_generation_status: not-called",
            "v200_real_tts_provider_default_audio_playback_status: not-started",
            "v200_real_tts_provider_default_audio_artifact_status: not-created",
            "v200_real_tts_provider_public_safe_body_policy: no-private-text-or-provider-payload",
            "v200_real_tts_provider_next_focus: " + result.next_focus,
        ]
    )

    return "\n".join(lines)
