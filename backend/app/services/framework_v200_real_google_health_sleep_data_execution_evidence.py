"""v2.0.0 Day66 real Google Health sleep-data execution evidence acceptance.

This module validates marker-only evidence for the third v2.0.0 real execution
requirement. It deliberately avoids Google API client imports, OAuth/token
reads, backend calls, browser automation, raw health payload parsing, health-data
artifact creation, and release artifact creation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class V200RealGoogleHealthSleepDataExecutionEvidenceItem:
    """One required Day66 execution evidence marker."""

    key: str
    status: str
    description: str


@dataclass(frozen=True)
class V200RealGoogleHealthSleepDataExecutionEvidenceResult:
    """Public-safe Day66 execution evidence contract."""

    status: str
    requirement_key: str
    evidence_items: tuple[V200RealGoogleHealthSleepDataExecutionEvidenceItem, ...]
    required_operator_markers: tuple[str, ...]
    public_safe_omissions: tuple[str, ...]
    forbidden_success_states: tuple[str, ...]
    operator_run_required: bool
    mock_safe_default: bool
    next_focus: str


@dataclass(frozen=True)
class V200RealGoogleHealthSleepDataExecutionEvidenceValidation:
    """Validation result for a marker-only Day66 evidence summary."""

    status: str
    accepted_markers: tuple[str, ...]
    missing_markers: tuple[str, ...]
    public_safe: bool
    forbidden_success_states_absent: bool


def build_v200_real_google_health_sleep_data_execution_evidence_contract() -> V200RealGoogleHealthSleepDataExecutionEvidenceResult:
    """Build the Day66 real Google Health sleep-data execution evidence contract.

    The returned structure is static and source-tree safe. It must not inspect
    Google credentials, read OAuth tokens, call Google Health APIs, call the DRC
    backend, open a browser, parse raw health payloads, write local evidence
    artifacts, or create release packages.
    """

    evidence_items = (
        V200RealGoogleHealthSleepDataExecutionEvidenceItem(
            key="explicit_operator_opt_in",
            status="required",
            description=(
                "A prepared operator must explicitly enable the configured real "
                "Google Health run; normal checks must remain credential-free."
            ),
        ),
        V200RealGoogleHealthSleepDataExecutionEvidenceItem(
            key="google_health_real_api_gate_enabled",
            status="required",
            description=(
                "The real Google Health API gate must be enabled before any "
                "OAuth token use or provider API request is allowed."
            ),
        ),
        V200RealGoogleHealthSleepDataExecutionEvidenceItem(
            key="oauth_connection_available",
            status="required",
            description=(
                "The configured OAuth connection must be available without "
                "publishing access tokens, refresh tokens, authorization headers, "
                "client secrets, or token files."
            ),
        ),
        V200RealGoogleHealthSleepDataExecutionEvidenceItem(
            key="real_google_health_api_request_confirmed",
            status="required",
            description=(
                "The operator must confirm that the configured real Google Health "
                "API path was used instead of mock, fixture, or fallback data."
            ),
        ),
        V200RealGoogleHealthSleepDataExecutionEvidenceItem(
            key="real_sleep_data_fetch_succeeded",
            status="required",
            description=(
                "The configured run must confirm that real sleep data was fetched "
                "from Google Health."
            ),
        ),
        V200RealGoogleHealthSleepDataExecutionEvidenceItem(
            key="sleep_summary_normalized",
            status="required",
            description=(
                "The fetched sleep data must be normalized into the public "
                "SleepSummary contract without exposing raw provider payloads or "
                "precise personal sleep timestamps."
            ),
        ),
        V200RealGoogleHealthSleepDataExecutionEvidenceItem(
            key="backend_sleep_summary_real_data_confirmed",
            status="required",
            description=(
                "The backend sleep summary path must report real-data source fields "
                "through the safe public response contract."
            ),
        ),
        V200RealGoogleHealthSleepDataExecutionEvidenceItem(
            key="smartphone_web_sleep_summary_real_source_confirmed",
            status="required",
            description=(
                "The smartphone Web UI must visibly confirm the real sleep summary "
                "source or equivalent public-safe real-data indicator."
            ),
        ),
        V200RealGoogleHealthSleepDataExecutionEvidenceItem(
            key="fallback_or_skip_not_counted",
            status="required",
            description=(
                "Mock, fixture, fallback, skipped, unavailable, failed, or error "
                "states must not be counted as real Google Health execution success."
            ),
        ),
        V200RealGoogleHealthSleepDataExecutionEvidenceItem(
            key="public_safe_evidence_recorded",
            status="required",
            description=(
                "Shared evidence must be marker-only and must omit secrets, raw "
                "health data, precise personal timestamps, raw LAN IPs, private "
                "paths, screenshots, and browser storage dumps."
            ),
        ),
    )

    return V200RealGoogleHealthSleepDataExecutionEvidenceResult(
        status="operator-execution-evidence-contract-ready",
        requirement_key="real_google_health_sleep_data",
        evidence_items=evidence_items,
        required_operator_markers=(
            "explicit_operator_opt_in_enabled",
            "google_health_real_api_gate_enabled",
            "oauth_connection_available",
            "real_google_health_api_request_confirmed",
            "real_sleep_data_fetch_succeeded",
            "sleep_summary_normalized_to_public_contract",
            "backend_sleep_summary_real_data_confirmed",
            "smartphone_web_sleep_summary_real_source_confirmed",
            "fallback_or_skip_not_counted",
            "public_safe_evidence_recorded",
        ),
        public_safe_omissions=(
            "client_secrets",
            "access_tokens",
            "refresh_tokens",
            "authorization_headers",
            "raw_google_health_payloads",
            "raw_sleep_events",
            "precise_personal_sleep_timestamps",
            "raw_lan_ips",
            "private_paths",
            "raw_screenshots",
            "browser_storage_dumps",
            "local_token_files",
        ),
        forbidden_success_states=(
            "mock_data",
            "fixture_data",
            "fallback_data",
            "simulated_data",
            "skipped",
            "unavailable",
            "oauth_missing",
            "token_invalid",
            "api_failed",
            "normalization_failed",
            "backend_not_called",
            "web_ui_not_confirmed",
            "error",
        ),
        operator_run_required=True,
        mock_safe_default=True,
        next_focus="image-asset-intake-and-web-display-execution-evidence",
    )


def render_v200_real_google_health_sleep_data_execution_evidence(
    result: V200RealGoogleHealthSleepDataExecutionEvidenceResult,
) -> str:
    """Render public-safe Day66 execution evidence markers."""

    lines = [
        "v200_real_google_health_sleep_data_execution_evidence_status: " + result.status,
        "v200_real_google_health_sleep_data_execution_requirement_key: "
        + result.requirement_key,
        "v200_real_google_health_sleep_data_execution_operator_run_required: "
        + str(result.operator_run_required),
        "v200_real_google_health_sleep_data_execution_mock_safe_default: "
        + str(result.mock_safe_default),
        "v200_real_google_health_sleep_data_execution_required_operator_markers: "
        + ",".join(result.required_operator_markers),
        "v200_real_google_health_sleep_data_execution_public_safe_omissions: "
        + ",".join(result.public_safe_omissions),
        "v200_real_google_health_sleep_data_execution_forbidden_success_states: "
        + ",".join(result.forbidden_success_states),
    ]

    for item in result.evidence_items:
        lines.append(
            f"v200_real_google_health_sleep_data_execution_evidence_{item.key}: {item.status}"
        )

    lines.extend(
        [
            "v200_real_google_health_sleep_data_execution_default_google_api_status: not-called",
            "v200_real_google_health_sleep_data_execution_default_oauth_status: not-started",
            "v200_real_google_health_sleep_data_execution_default_token_read_status: not-read",
            "v200_real_google_health_sleep_data_execution_default_backend_call_status: not-called",
            "v200_real_google_health_sleep_data_execution_default_browser_status: not-opened",
            "v200_real_google_health_sleep_data_execution_default_raw_payload_status: not-recorded",
            "v200_real_google_health_sleep_data_execution_default_health_data_artifact_status: not-created",
            "v200_real_google_health_sleep_data_execution_public_evidence_body_policy: marker-only-no-raw-health-data",
            "v200_real_google_health_sleep_data_execution_next_focus: " + result.next_focus,
        ]
    )

    return "\n".join(lines)


def validate_v200_real_google_health_sleep_data_execution_operator_evidence(
    evidence: Mapping[str, object],
) -> V200RealGoogleHealthSleepDataExecutionEvidenceValidation:
    """Validate a redacted Day66 operator evidence shape.

    This helper checks marker booleans only. It must not be used with raw Google
    Health payloads, token files, screenshots, browser storage dumps, logs, or
    local health-data artifacts.
    """

    contract = build_v200_real_google_health_sleep_data_execution_evidence_contract()
    accepted: list[str] = []
    missing: list[str] = []

    for marker in contract.required_operator_markers:
        if evidence.get(marker) is True:
            accepted.append(marker)
        else:
            missing.append(marker)

    forbidden_publication_flags = (
        "client_secrets_included",
        "access_tokens_included",
        "refresh_tokens_included",
        "authorization_headers_included",
        "raw_google_health_payloads_included",
        "raw_sleep_events_included",
        "precise_personal_sleep_timestamps_included",
        "raw_lan_ips_included",
        "private_paths_included",
        "raw_screenshots_included",
        "browser_storage_dumps_included",
        "local_token_files_included",
    )
    public_safe = all(evidence.get(flag) is not True for flag in forbidden_publication_flags)

    forbidden_success_state_flags = tuple(
        f"{state}_counted_as_success" for state in contract.forbidden_success_states
    )
    forbidden_success_states_absent = all(
        evidence.get(flag) is not True for flag in forbidden_success_state_flags
    )

    status = (
        "accepted"
        if not missing and public_safe and forbidden_success_states_absent
        else "incomplete-or-unsafe"
    )
    return V200RealGoogleHealthSleepDataExecutionEvidenceValidation(
        status=status,
        accepted_markers=tuple(accepted),
        missing_markers=tuple(missing),
        public_safe=public_safe,
        forbidden_success_states_absent=forbidden_success_states_absent,
    )
