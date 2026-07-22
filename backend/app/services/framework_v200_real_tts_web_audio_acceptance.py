"""v2.0.0 real TTS Web audio output acceptance gate.

This module combines the marker-only Day54, Day65, and Day77 evidence
validators for the second v2.0.0 real Web execution requirement. It deliberately
avoids provider SDK imports, AI Character Framework calls, backend requests,
browser automation, audio synthesis, audio playback, screenshot inspection, and
release artifact creation.

A successful validation means only that a private operator has supplied public-
safe markers for an already-completed real Web TTS run. The validators must not
be pointed at raw provider payloads, raw audio files, screenshots, private
synthesis text, token files, browser storage dumps, or local evidence folders.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from backend.app.services.framework_v200_real_tts_web_audio_execution_evidence import (
    validate_v200_real_tts_web_audio_execution_operator_evidence,
)
from backend.app.services.framework_v200_real_tts_web_audio_output_evidence import (
    validate_v200_real_tts_web_audio_operator_evidence,
)
from backend.app.services.framework_v200_real_tts_web_audio_screenshot_evidence import (
    validate_v200_real_tts_web_audio_screenshot_evidence,
)


@dataclass(frozen=True)
class V200RealTtsWebAudioAcceptanceContract:
    """Public-safe contract for the final D-3 TTS acceptance gate."""

    status: str
    requirement_key: str
    required_sources: tuple[str, ...]
    required_validation_status: str
    screenshot_required: bool
    web_ui_execution_required: bool
    actual_drc_backend_api_required: bool
    real_tts_provider_audio_required: bool
    framework_voice_output_boundary_required: bool
    api_only_counts_as_success: bool
    source_tree_only_counts_as_success: bool
    command_output_only_counts_as_success: bool
    mock_safe_default: bool
    next_focus: str


@dataclass(frozen=True)
class V200RealTtsWebAudioAcceptanceValidation:
    """Combined validation result for D-3 real TTS Web audio evidence."""

    status: str
    accepted_sources: tuple[str, ...]
    missing_sources: tuple[str, ...]
    missing_markers: tuple[str, ...]
    public_safe: bool
    screenshot_reference_public_safe: bool
    forbidden_success_states_absent: bool
    requirement_satisfied: bool


def build_v200_real_tts_web_audio_acceptance_contract() -> V200RealTtsWebAudioAcceptanceContract:
    """Build the source-tree safe D-3 acceptance contract."""

    return V200RealTtsWebAudioAcceptanceContract(
        status="real-tts-web-audio-acceptance-gate-ready",
        requirement_key="real_tts_web_audio_output",
        required_sources=(
            "day54_output_evidence",
            "day65_execution_evidence",
            "day77_screenshot_evidence",
        ),
        required_validation_status="accepted",
        screenshot_required=True,
        web_ui_execution_required=True,
        actual_drc_backend_api_required=True,
        real_tts_provider_audio_required=True,
        framework_voice_output_boundary_required=True,
        api_only_counts_as_success=False,
        source_tree_only_counts_as_success=False,
        command_output_only_counts_as_success=False,
        mock_safe_default=True,
        next_focus=(
            "Accept real_tts_web_audio_output in the v2.0.0 checklist only after "
            "private Day54, Day65, and Day77 marker-only evidence all validate."
        ),
    )


def render_v200_real_tts_web_audio_acceptance_contract(
    contract: V200RealTtsWebAudioAcceptanceContract,
) -> str:
    """Render the D-3 acceptance contract as deterministic public-safe text."""

    return "\n".join(
        [
            f"v200_real_tts_web_audio_acceptance_status: {contract.status}",
            f"v200_real_tts_web_audio_acceptance_requirement_key: {contract.requirement_key}",
            "v200_real_tts_web_audio_acceptance_required_sources: "
            + ",".join(contract.required_sources),
            "v200_real_tts_web_audio_acceptance_required_validation_status: "
            + contract.required_validation_status,
            "v200_real_tts_web_audio_acceptance_screenshot_required: "
            f"{contract.screenshot_required}",
            "v200_real_tts_web_audio_acceptance_web_ui_execution_required: "
            f"{contract.web_ui_execution_required}",
            "v200_real_tts_web_audio_acceptance_actual_drc_backend_api_required: "
            f"{contract.actual_drc_backend_api_required}",
            "v200_real_tts_web_audio_acceptance_real_tts_provider_audio_required: "
            f"{contract.real_tts_provider_audio_required}",
            "v200_real_tts_web_audio_acceptance_framework_voice_output_boundary_required: "
            f"{contract.framework_voice_output_boundary_required}",
            "v200_real_tts_web_audio_acceptance_api_only_counts_as_success: "
            f"{contract.api_only_counts_as_success}",
            "v200_real_tts_web_audio_acceptance_source_tree_only_counts_as_success: "
            f"{contract.source_tree_only_counts_as_success}",
            "v200_real_tts_web_audio_acceptance_command_output_only_counts_as_success: "
            f"{contract.command_output_only_counts_as_success}",
            f"v200_real_tts_web_audio_acceptance_mock_safe_default: {contract.mock_safe_default}",
            "v200_real_tts_web_audio_acceptance_default_provider_status: not-called",
            "v200_real_tts_web_audio_acceptance_default_backend_status: not-started",
            "v200_real_tts_web_audio_acceptance_default_browser_status: not-opened",
            "v200_real_tts_web_audio_acceptance_default_audio_playback_status: not-started",
            "v200_real_tts_web_audio_acceptance_default_screenshot_status: not-inspected",
            "v200_real_tts_web_audio_acceptance_next_focus: " + contract.next_focus,
        ]
    )


def validate_v200_real_tts_web_audio_acceptance(
    *,
    day54_output_evidence: Mapping[str, object],
    day65_execution_evidence: Mapping[str, object],
    day77_screenshot_evidence: Mapping[str, object],
) -> V200RealTtsWebAudioAcceptanceValidation:
    """Validate combined D-3 evidence without inspecting private artifacts."""

    accepted_sources: list[str] = []
    missing_sources: list[str] = []
    missing_markers: list[str] = []

    day54_validation = validate_v200_real_tts_web_audio_operator_evidence(
        day54_output_evidence
    )
    if day54_validation.status == "accepted":
        accepted_sources.append("day54_output_evidence")
    else:
        missing_sources.append("day54_output_evidence")
        missing_markers.extend(
            f"day54_output_evidence.{marker}"
            for marker in day54_validation.missing_markers
        )

    day65_validation = validate_v200_real_tts_web_audio_execution_operator_evidence(
        day65_execution_evidence
    )
    if day65_validation.status == "accepted":
        accepted_sources.append("day65_execution_evidence")
    else:
        missing_sources.append("day65_execution_evidence")
        missing_markers.extend(
            f"day65_execution_evidence.{marker}"
            for marker in day65_validation.missing_markers
        )

    day77_validation = validate_v200_real_tts_web_audio_screenshot_evidence(
        day77_screenshot_evidence
    )
    if day77_validation.status == "accepted":
        accepted_sources.append("day77_screenshot_evidence")
    else:
        missing_sources.append("day77_screenshot_evidence")
        missing_markers.extend(
            f"day77_screenshot_evidence.{marker}"
            for marker in day77_validation.missing_markers
        )

    public_safe = (
        day54_validation.public_safe
        and day65_validation.public_safe
        and day77_validation.public_safe
    )
    screenshot_reference_public_safe = day77_validation.screenshot_reference_public_safe
    forbidden_success_states_absent = (
        day65_validation.forbidden_success_states_absent
        and day77_validation.forbidden_success_states_absent
    )
    status = (
        "accepted"
        if not missing_sources
        and not missing_markers
        and public_safe
        and screenshot_reference_public_safe
        and forbidden_success_states_absent
        else "incomplete"
    )

    return V200RealTtsWebAudioAcceptanceValidation(
        status=status,
        accepted_sources=tuple(accepted_sources),
        missing_sources=tuple(missing_sources),
        missing_markers=tuple(missing_markers),
        public_safe=public_safe,
        screenshot_reference_public_safe=screenshot_reference_public_safe,
        forbidden_success_states_absent=forbidden_success_states_absent,
        requirement_satisfied=status == "accepted",
    )


def render_v200_real_tts_web_audio_acceptance_validation(
    validation: V200RealTtsWebAudioAcceptanceValidation,
) -> str:
    """Render combined D-3 validation as deterministic public-safe text."""

    return "\n".join(
        [
            f"v200_real_tts_web_audio_acceptance_validation_status: {validation.status}",
            "v200_real_tts_web_audio_acceptance_accepted_sources: "
            + ",".join(validation.accepted_sources),
            "v200_real_tts_web_audio_acceptance_missing_sources: "
            + ",".join(validation.missing_sources),
            "v200_real_tts_web_audio_acceptance_missing_markers: "
            + ",".join(validation.missing_markers),
            f"v200_real_tts_web_audio_acceptance_public_safe: {validation.public_safe}",
            "v200_real_tts_web_audio_acceptance_screenshot_reference_public_safe: "
            f"{validation.screenshot_reference_public_safe}",
            "v200_real_tts_web_audio_acceptance_forbidden_success_states_absent: "
            f"{validation.forbidden_success_states_absent}",
            "v200_real_tts_web_audio_acceptance_requirement_satisfied: "
            f"{validation.requirement_satisfied}",
        ]
    )
