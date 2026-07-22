"""v2.0.0 Day78 real Google Health Web sleep screenshot evidence capture.

The default contract is marker-only and public-safe. It does not call Google
Health, OAuth endpoints, the Daily Rhythm Companion backend, Flutter Web,
browsers, screenshot tools, release builders, GitHub, or the network.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping
import re


@dataclass(frozen=True)
class V200RealGoogleHealthWebSleepScreenshotEvidenceContract:
    """Public-safe contract for the Day78 Google Health sleep evidence item."""

    status: str
    capability: str
    required_true_markers: tuple[str, ...]
    required_false_markers: tuple[str, ...]
    forbidden_success_states: tuple[str, ...]
    public_safe_omissions: tuple[str, ...]
    screenshot_required: bool
    web_ui_execution_required: bool
    actual_drc_backend_api_required: bool
    real_google_health_api_required: bool
    normalized_sleep_summary_required: bool
    api_only_counts_as_success: bool
    source_tree_only_counts_as_success: bool
    command_output_only_counts_as_success: bool
    feeds_private_manifest_key: str


@dataclass(frozen=True)
class V200RealGoogleHealthWebSleepScreenshotEvidenceValidation:
    """Validation result for one private Day78 Google Health evidence item."""

    status: str
    missing_markers: tuple[str, ...]
    public_safe: bool
    screenshot_reference_public_safe: bool
    forbidden_success_states_absent: bool
    manifest_item_key: str


def build_v200_real_google_health_web_sleep_screenshot_evidence_contract() -> V200RealGoogleHealthWebSleepScreenshotEvidenceContract:
    """Build the Day78 real Google Health Web sleep evidence contract."""

    return V200RealGoogleHealthWebSleepScreenshotEvidenceContract(
        status="real-google-health-web-sleep-screenshot-evidence-validator-ready",
        capability="real_google_health_sleep_data",
        required_true_markers=(
            "actual_drc_backend_api_used",
            "web_ui_execution_confirmed",
            "web_execution_result_visible",
            "google_health_sleep_data_visible",
            "real_google_health_api_confirmed",
            "google_health_oauth_or_valid_token_confirmed",
            "normalized_sleep_summary_confirmed",
            "data_source_label_visible",
            "screenshot_captured",
            "screenshot_reference_recorded",
            "screenshot_private_storage_confirmed",
            "screenshot_public_safe_redaction_confirmed",
            "operator_review_accepted",
            "not_api_only",
            "not_source_tree_only",
            "not_command_output_only",
            "not_mock_only",
            "not_fallback",
            "not_skipped",
            "not_unavailable",
            "not_placeholder",
        ),
        required_false_markers=(
            "api_keys_included",
            "oauth_tokens_included",
            "refresh_tokens_included",
            "authorization_headers_included",
            "raw_google_health_payloads_included",
            "raw_sleep_data_exports_included",
            "raw_screenshot_files_included",
            "raw_lan_ips_included",
            "private_paths_included",
            "production_or_store_claims_included",
            "medical_claims_included",
        ),
        forbidden_success_states=(
            "api_only_success",
            "source_tree_only_success",
            "command_output_only_success",
            "web_ui_not_confirmed",
            "google_health_api_not_confirmed",
            "google_health_sleep_data_not_visible",
            "normalized_sleep_summary_not_confirmed",
            "screenshot_missing",
            "screenshot_reference_missing",
            "screenshot_not_reviewed",
            "raw_screenshot_committed",
            "raw_health_data_committed",
            "oauth_token_exposed",
            "authorization_header_exposed",
            "actual_drc_backend_api_not_used",
            "mock_only",
            "fallback_only",
            "skipped",
            "unavailable",
            "placeholder",
            "error",
        ),
        public_safe_omissions=(
            "api_keys",
            "oauth_tokens",
            "refresh_tokens",
            "authorization_headers",
            "raw_google_health_payloads",
            "raw_sleep_data_exports",
            "raw_screenshot_files",
            "raw_lan_ips",
            "private_paths",
            "production_claims",
            "app_store_claims",
            "medical_claims",
        ),
        screenshot_required=True,
        web_ui_execution_required=True,
        actual_drc_backend_api_required=True,
        real_google_health_api_required=True,
        normalized_sleep_summary_required=True,
        api_only_counts_as_success=False,
        source_tree_only_counts_as_success=False,
        command_output_only_counts_as_success=False,
        feeds_private_manifest_key="web_evidence.real_google_health_sleep_data",
    )


def render_v200_real_google_health_web_sleep_screenshot_evidence_contract(
    contract: V200RealGoogleHealthWebSleepScreenshotEvidenceContract,
) -> str:
    """Render the Day78 contract as deterministic public-safe text."""

    return "\n".join(
        [
            f"v200_real_google_health_web_sleep_screenshot_evidence_status: {contract.status}",
            f"v200_real_google_health_web_sleep_screenshot_evidence_capability: {contract.capability}",
            f"v200_real_google_health_web_sleep_screenshot_evidence_screenshot_required: {contract.screenshot_required}",
            f"v200_real_google_health_web_sleep_screenshot_evidence_web_ui_execution_required: {contract.web_ui_execution_required}",
            f"v200_real_google_health_web_sleep_screenshot_evidence_actual_drc_backend_api_required: {contract.actual_drc_backend_api_required}",
            f"v200_real_google_health_web_sleep_screenshot_evidence_real_google_health_api_required: {contract.real_google_health_api_required}",
            f"v200_real_google_health_web_sleep_screenshot_evidence_normalized_sleep_summary_required: {contract.normalized_sleep_summary_required}",
            f"v200_real_google_health_web_sleep_screenshot_evidence_api_only_counts_as_success: {contract.api_only_counts_as_success}",
            f"v200_real_google_health_web_sleep_screenshot_evidence_source_tree_only_counts_as_success: {contract.source_tree_only_counts_as_success}",
            f"v200_real_google_health_web_sleep_screenshot_evidence_command_output_only_counts_as_success: {contract.command_output_only_counts_as_success}",
            f"v200_real_google_health_web_sleep_screenshot_evidence_feeds_private_manifest_key: {contract.feeds_private_manifest_key}",
            "v200_real_google_health_web_sleep_screenshot_evidence_required_true_markers: " + ",".join(contract.required_true_markers),
            "v200_real_google_health_web_sleep_screenshot_evidence_required_false_markers: " + ",".join(contract.required_false_markers),
            "v200_real_google_health_web_sleep_screenshot_evidence_forbidden_success_states: " + ",".join(contract.forbidden_success_states),
            "v200_real_google_health_web_sleep_screenshot_evidence_public_safe_omissions: " + ",".join(contract.public_safe_omissions),
            "v200_real_google_health_web_sleep_screenshot_evidence_default_external_network_status: not-called",
            "v200_real_google_health_web_sleep_screenshot_evidence_default_backend_status: not-started",
            "v200_real_google_health_web_sleep_screenshot_evidence_default_browser_status: not-opened",
            "v200_real_google_health_web_sleep_screenshot_evidence_default_screenshot_status: not-inspected",
        ]
    )


def _is_public_safe_reference(value: object) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    unsafe_patterns = (
        r"[A-Za-z]:\\",
        r"/Users/",
        r"/home/[^/]+/",
        r"E:\\work\\",
        r"C:\\Users\\",
        r"192\.168\.\d+\.\d+",
        r"10\.\d+\.\d+\.\d+",
        r"172\.(1[6-9]|2\d|3[0-1])\.\d+\.\d+",
        r"sk-[A-Za-z0-9_\-]{12,}",
        r"AIza[0-9A-Za-z_\-]{20,}",
        r"xai-[A-Za-z0-9_\-]{12,}",
        r"Bearer\s+[A-Za-z0-9_\-\.]{12,}",
    )
    return not any(re.search(pattern, value, flags=re.IGNORECASE) for pattern in unsafe_patterns)


def validate_v200_real_google_health_web_sleep_screenshot_evidence(
    evidence: Mapping[str, object],
) -> V200RealGoogleHealthWebSleepScreenshotEvidenceValidation:
    """Validate one private Day78 real Google Health Web sleep evidence item."""

    contract = build_v200_real_google_health_web_sleep_screenshot_evidence_contract()
    missing: list[str] = []
    if evidence.get("status") != "accepted":
        missing.append("status=accepted")
    if evidence.get("capability") != contract.capability:
        missing.append(f"capability={contract.capability}")
    for marker in contract.required_true_markers:
        if evidence.get(marker) is not True:
            missing.append(marker)
    public_safe = True
    for marker in contract.required_false_markers:
        if evidence.get(marker) is not False:
            public_safe = False
            missing.append(marker + "=false")
    forbidden_absent = True
    for marker in contract.forbidden_success_states:
        if evidence.get(marker) is True:
            forbidden_absent = False
            missing.append(marker + "=false")
    screenshot_ref_safe = _is_public_safe_reference(evidence.get("screenshot_reference"))
    if not screenshot_ref_safe:
        missing.append("screenshot_reference_public_safe")
    status = "accepted" if not missing and public_safe and forbidden_absent and screenshot_ref_safe else "incomplete"
    return V200RealGoogleHealthWebSleepScreenshotEvidenceValidation(
        status=status,
        missing_markers=tuple(missing),
        public_safe=public_safe,
        screenshot_reference_public_safe=screenshot_ref_safe,
        forbidden_success_states_absent=forbidden_absent,
        manifest_item_key=contract.feeds_private_manifest_key,
    )


def render_v200_real_google_health_web_sleep_screenshot_evidence_validation(
    validation: V200RealGoogleHealthWebSleepScreenshotEvidenceValidation,
) -> str:
    """Render Day78 evidence validation as deterministic public-safe text."""

    return "\n".join(
        [
            f"v200_real_google_health_web_sleep_screenshot_evidence_validation_status: {validation.status}",
            f"v200_real_google_health_web_sleep_screenshot_evidence_manifest_item_key: {validation.manifest_item_key}",
            "v200_real_google_health_web_sleep_screenshot_evidence_missing_markers: " + ",".join(validation.missing_markers),
            f"v200_real_google_health_web_sleep_screenshot_evidence_public_safe: {validation.public_safe}",
            f"v200_real_google_health_web_sleep_screenshot_evidence_screenshot_reference_public_safe: {validation.screenshot_reference_public_safe}",
            f"v200_real_google_health_web_sleep_screenshot_evidence_forbidden_success_states_absent: {validation.forbidden_success_states_absent}",
        ]
    )
