"""v2.0.0 real Google Health sleep data evidence checkpoint.

This module records the public-safe evidence contract for the third v2.0.0
pre-release requirement: retrieving real sleep data through the Google Health
API path. It deliberately avoids Google API client imports, OAuth/token reads,
backend calls, browser automation, raw health-data parsing, or artifact writes.

The actual configured run remains an operator-only step. Public evidence should
prove the shape of the run without committing client secrets, access tokens,
refresh tokens, authorization headers, raw Google Health payloads, raw sleep
events, precise personal sleep timestamps, raw LAN IPs, private paths, or
screenshots.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class V200RealGoogleHealthSleepEvidenceItem:
    key: str
    status: str
    description: str


@dataclass(frozen=True)
class V200RealGoogleHealthSleepEvidenceResult:
    status: str
    requirement_key: str
    evidence_items: tuple[V200RealGoogleHealthSleepEvidenceItem, ...]
    required_operator_markers: tuple[str, ...]
    public_safe_omissions: tuple[str, ...]
    operator_run_required: bool
    mock_safe_default: bool
    next_focus: str


@dataclass(frozen=True)
class V200RealGoogleHealthSleepOperatorEvidenceValidation:
    status: str
    accepted_markers: tuple[str, ...]
    missing_markers: tuple[str, ...]
    public_safe: bool


def build_v200_real_google_health_sleep_evidence_contract() -> V200RealGoogleHealthSleepEvidenceResult:
    """Build the Day55 real Google Health sleep-data evidence contract.

    The returned structure is static and source-tree safe. It does not inspect
    provider credentials, read OAuth tokens, call Google Health APIs, call the
    DRC backend, open a browser, normalize real health payloads, or write local
    evidence artifacts.
    """

    evidence_items = (
        V200RealGoogleHealthSleepEvidenceItem(
            key="explicit_operator_opt_in",
            status="required",
            description=(
                "The configured real Google Health run must be manually enabled "
                "by an operator and must never run as part of normal checks."
            ),
        ),
        V200RealGoogleHealthSleepEvidenceItem(
            key="google_health_real_api_gate_enabled",
            status="required",
            description=(
                "The real API gate must be explicitly enabled before token use "
                "or Google Health API requests are allowed."
            ),
        ),
        V200RealGoogleHealthSleepEvidenceItem(
            key="oauth_connection_available",
            status="required",
            description=(
                "A configured OAuth connection must be available without "
                "publishing access tokens, refresh tokens, or authorization headers."
            ),
        ),
        V200RealGoogleHealthSleepEvidenceItem(
            key="real_sleep_data_fetch_succeeded",
            status="required",
            description=(
                "The configured run must confirm that real sleep data was fetched "
                "from Google Health."
            ),
        ),
        V200RealGoogleHealthSleepEvidenceItem(
            key="sleep_summary_normalized",
            status="required",
            description=(
                "Fetched sleep data must be normalized into the public SleepSummary "
                "contract rather than exposed as a raw provider payload."
            ),
        ),
        V200RealGoogleHealthSleepEvidenceItem(
            key="backend_sleep_summary_confirmed",
            status="required",
            description=(
                "The operator must confirm the backend sleep summary path can report "
                "a real-data source through safe response fields."
            ),
        ),
        V200RealGoogleHealthSleepEvidenceItem(
            key="public_safe_evidence_recorded",
            status="required",
            description=(
                "Shared evidence must be marker-based and must omit secrets, raw "
                "health payloads, precise personal sleep timestamps, local paths, "
                "raw LAN IPs, and screenshots."
            ),
        ),
    )

    return V200RealGoogleHealthSleepEvidenceResult(
        status="operator-evidence-contract-ready",
        requirement_key="real_google_health_sleep_data",
        evidence_items=evidence_items,
        required_operator_markers=(
            "explicit_operator_opt_in_enabled",
            "google_health_real_api_gate_enabled",
            "oauth_connection_available",
            "real_sleep_data_fetch_succeeded",
            "sleep_summary_normalized_to_public_contract",
            "backend_sleep_summary_real_data_confirmed",
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
        ),
        operator_run_required=True,
        mock_safe_default=True,
        next_focus="web-image-display-evidence",
    )


def render_v200_real_google_health_sleep_evidence(
    result: V200RealGoogleHealthSleepEvidenceResult,
) -> str:
    """Render public-safe Day55 evidence markers."""

    lines = [
        "v200_real_google_health_sleep_evidence_status: " + result.status,
        "v200_real_google_health_sleep_requirement_key: " + result.requirement_key,
        "v200_real_google_health_sleep_operator_run_required: "
        + str(result.operator_run_required),
        "v200_real_google_health_sleep_mock_safe_default: "
        + str(result.mock_safe_default),
        "v200_real_google_health_sleep_required_operator_markers: "
        + ",".join(result.required_operator_markers),
        "v200_real_google_health_sleep_public_safe_omissions: "
        + ",".join(result.public_safe_omissions),
    ]

    for item in result.evidence_items:
        lines.append(f"v200_real_google_health_sleep_evidence_{item.key}: {item.status}")

    lines.extend(
        [
            "v200_real_google_health_sleep_default_google_api_status: not-called",
            "v200_real_google_health_sleep_default_oauth_status: not-started",
            "v200_real_google_health_sleep_default_token_read_status: not-read",
            "v200_real_google_health_sleep_default_backend_call_status: not-called",
            "v200_real_google_health_sleep_default_browser_status: not-opened",
            "v200_real_google_health_sleep_default_raw_payload_status: not-recorded",
            "v200_real_google_health_sleep_default_health_data_artifact_status: not-created",
            "v200_real_google_health_sleep_public_evidence_body_policy: marker-only-no-raw-health-data",
            "v200_real_google_health_sleep_next_focus: " + result.next_focus,
        ]
    )

    return "\n".join(lines)


def validate_v200_real_google_health_sleep_operator_evidence(
    evidence: Mapping[str, object],
) -> V200RealGoogleHealthSleepOperatorEvidenceValidation:
    """Validate a redacted Google Health operator evidence shape.

    This helper checks marker booleans only. It should be used on a small
    redacted JSON summary, not on raw Google Health payloads, token files,
    screenshots, browser storage, logs, or local health-data artifacts.
    """

    contract = build_v200_real_google_health_sleep_evidence_contract()
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
    )
    public_safe = all(evidence.get(flag) is not True for flag in forbidden_publication_flags)

    status = "accepted" if not missing and public_safe else "incomplete-or-unsafe"
    return V200RealGoogleHealthSleepOperatorEvidenceValidation(
        status=status,
        accepted_markers=tuple(accepted),
        missing_markers=tuple(missing),
        public_safe=public_safe,
    )
