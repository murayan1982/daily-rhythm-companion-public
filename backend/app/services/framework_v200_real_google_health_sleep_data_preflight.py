"""v2.0.0 real Google Health sleep-data local env preflight contract.

Importing or rendering this module is source-tree safe. It must not read OAuth
credentials or token files, call Google Health, start the DRC backend, open
Flutter Web, inspect screenshots, or accept ``real_google_health_sleep_data``.

The optional env validation checks only KEY=VALUE markers from a dedicated,
ignored operator env file. Values are never rendered or persisted.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from app.config import (
    GOOGLE_HEALTH_API_BASE_URL,
    GOOGLE_HEALTH_SLEEP_API_PATH,
    GOOGLE_HEALTH_SLEEP_READONLY_SCOPE,
)


_TRUE_VALUES = {"1", "true", "yes", "on"}
_FALSE_VALUES = {"0", "false", "no", "off"}


@dataclass(frozen=True)
class V200RealGoogleHealthSleepDataPreflightCheck:
    """One public-safe checkpoint before a private configured run."""

    key: str
    status: str
    description: str


@dataclass(frozen=True)
class V200RealGoogleHealthSleepDataPreflightContract:
    """Static public-safe E-3 preflight contract."""

    status: str
    requirement_key: str
    commit_scope: str
    checks: tuple[V200RealGoogleHealthSleepDataPreflightCheck, ...]
    required_exact_values: Mapping[str, str]
    required_nonempty_keys: tuple[str, ...]
    required_true_keys: tuple[str, ...]
    required_false_keys: tuple[str, ...]
    required_scope: str
    recommended_project_access_keys: tuple[str, ...]
    forbidden_exact_keys: tuple[str, ...]
    forbidden_key_fragments: tuple[str, ...]
    required_repo_files: tuple[str, ...]
    required_gitignore_patterns: tuple[str, ...]
    required_commands: tuple[str, ...]
    env_location_policy: str
    private_value_policy: str
    acceptance_policy: str
    google_health_api_call_status: str
    oauth_token_read_status: str
    backend_start_status: str
    web_ui_execution_status: str
    screenshot_inspection_status: str
    operator_evidence_acceptance_status: str
    release_completion_status: str
    mock_safe_default: bool


@dataclass(frozen=True)
class V200RealGoogleHealthSleepDataPreflightEnvValidation:
    """Public-safe result of validating an ignored operator env file."""

    status: str
    accepted_keys: tuple[str, ...]
    missing_or_invalid_keys: tuple[str, ...]
    recommended_keys_present: tuple[str, ...]
    recommended_keys_missing: tuple[str, ...]
    forbidden_keys_present: tuple[str, ...]
    public_safe: bool


def build_v200_real_google_health_sleep_data_preflight_contract(
) -> V200RealGoogleHealthSleepDataPreflightContract:
    """Build the E-3 source-tree safe local env preflight contract."""

    checks = (
        V200RealGoogleHealthSleepDataPreflightCheck(
            key="dedicated_ignored_operator_env",
            status="required-before-private-run",
            description=(
                "Use a dedicated *.local.env file copied from the committed guarded "
                "Google Health example. Do not reuse a broad provider/LLM env file."
            ),
        ),
        V200RealGoogleHealthSleepDataPreflightCheck(
            key="google_health_only_runtime_profile",
            status="required-before-private-run",
            description=(
                "Keep CONVERSATION_ENGINE=mock and SLEEP_PROVIDER=google_health so the "
                "sleep evidence run does not accidentally call unrelated providers."
            ),
        ),
        V200RealGoogleHealthSleepDataPreflightCheck(
            key="three_gate_real_api_opt_in",
            status="required-before-private-run",
            description=(
                "Real API requests require ENABLE_REAL_API_REQUESTS, "
                "REAL_API_OPT_IN, and REAL_ENDPOINT_VERIFIED together."
            ),
        ),
        V200RealGoogleHealthSleepDataPreflightCheck(
            key="token_exchange_separated",
            status="required-before-private-run",
            description=(
                "Real token exchange stays disabled in the guarded request profile; "
                "token refresh may be enabled for the existing private token."
            ),
        ),
        V200RealGoogleHealthSleepDataPreflightCheck(
            key="official_sleep_endpoint_and_scope",
            status="required-before-private-run",
            description=(
                "Use the Google Health v4 sleep endpoint, readonly sleep scope, and "
                "filter query contract prepared by E-2."
            ),
        ),
        V200RealGoogleHealthSleepDataPreflightCheck(
            key="marker_only_public_output",
            status="required-before-private-run",
            description=(
                "Preflight output may contain key names and boolean markers only; "
                "credential paths, client IDs, tokens, raw health data, and private "
                "machine paths remain local."
            ),
        ),
    )

    return V200RealGoogleHealthSleepDataPreflightContract(
        status="real-google-health-sleep-data-preflight-ready",
        requirement_key="real_google_health_sleep_data",
        commit_scope="E-3 only",
        checks=checks,
        required_exact_values={
            "CONVERSATION_ENGINE": "mock",
            "SLEEP_PROVIDER": "google_health",
            "GOOGLE_HEALTH_REQUIRED_SLEEP_SCOPE": GOOGLE_HEALTH_SLEEP_READONLY_SCOPE,
            "GOOGLE_HEALTH_API_BASE_URL": GOOGLE_HEALTH_API_BASE_URL,
            "GOOGLE_HEALTH_SLEEP_API_PATH": GOOGLE_HEALTH_SLEEP_API_PATH,
            "GOOGLE_HEALTH_SLEEP_FILTER_QUERY_PARAM": "filter",
        },
        required_nonempty_keys=(
            "GOOGLE_HEALTH_CREDENTIALS_FILE",
            "GOOGLE_HEALTH_REDIRECT_URI",
            "GOOGLE_HEALTH_OAUTH_SCOPES",
        ),
        required_true_keys=(
            "GOOGLE_HEALTH_ENABLE_REAL_TOKEN_REFRESH",
            "GOOGLE_HEALTH_ENABLE_REAL_API_REQUESTS",
            "GOOGLE_HEALTH_REAL_API_OPT_IN",
            "GOOGLE_HEALTH_REAL_ENDPOINT_VERIFIED",
        ),
        required_false_keys=(
            "GOOGLE_HEALTH_ENABLE_REAL_TOKEN_EXCHANGE",
            "FITBIT_ENABLE_REAL_TOKEN_EXCHANGE",
        ),
        required_scope=GOOGLE_HEALTH_SLEEP_READONLY_SCOPE,
        recommended_project_access_keys=(
            "GOOGLE_HEALTH_EXPECTED_CLIENT_ID",
            "GOOGLE_HEALTH_CLOUD_API_ENABLED_CONFIRMED",
            "GOOGLE_HEALTH_OAUTH_CONSENT_SLEEP_SCOPE_CONFIRMED",
            "GOOGLE_HEALTH_OAUTH_TEST_USER_CONFIRMED",
            "GOOGLE_HEALTH_ENDPOINT_QUERY_CONFIRMED",
            "GOOGLE_HEALTH_DATA_ACCESS_SCOPE_CONFIRMED",
            "GOOGLE_HEALTH_OAUTH_PUBLISHING_STATUS_TESTING_CONFIRMED",
            "GOOGLE_HEALTH_OAUTH_USER_TYPE_EXTERNAL_CONFIRMED",
            "GOOGLE_HEALTH_TEST_USER_EMAIL_CONFIRMED",
        ),
        forbidden_exact_keys=(
            "OPENAI_API_KEY",
            "GEMINI_API_KEY",
            "GOOGLE_API_KEY",
            "XAI_API_KEY",
            "ELEVENLABS_API_KEY",
            "FITBIT_CLIENT_SECRET",
            "FRAMEWORK_ROOT",
            "FRAMEWORK_PROJECT_ROOT",
        ),
        forbidden_key_fragments=(
            "ACCESS_TOKEN",
            "REFRESH_TOKEN",
            "AUTHORIZATION_HEADER",
            "CLIENT_SECRET_VALUE",
            "OAUTH_CODE",
            "RAW_GOOGLE_HEALTH",
            "RAW_HEALTH_DATA",
            "RAW_PAYLOAD",
        ),
        required_repo_files=(
            "docs/v200_real_google_health_sleep_data_operator_runbook.md",
            "backend/env_profiles/google_health_real_api_guarded.env.example",
            "scripts/check_google_health_connection_checklist.py",
            "scripts/check_google_health_diagnostics.py",
            "scripts/check_google_health_self_check.py",
            "scripts/smoke_google_health_sleep_request_preview.py",
            "scripts/smoke_google_health_real_sleep_request.py",
            "scripts/smoke_v200_real_google_health_sleep_data_evidence.py",
            "scripts/smoke_framework_v200_real_google_health_sleep_data_execution_evidence.py",
            "scripts/smoke_framework_v200_real_google_health_web_sleep_screenshot_evidence.py",
        ),
        required_gitignore_patterns=(
            "*.local.env",
            "backend/env_profiles/*.local.env",
            "operator_evidence/",
            "credentials.json",
            "backend/local_data/",
        ),
        required_commands=(
            "python -m compileall -q backend scripts",
            "python scripts\\check_google_health_api_client_boundary.py",
            "python scripts\\check_google_health_session_boundary.py",
            "python scripts\\check_google_health_sleep_parser.py",
            "python scripts\\check_google_health_sleep_source_boundary.py",
            "python scripts\\check_google_health_runtime_guard.py",
            "python scripts\\check_google_health_connection_checklist.py",
            "python scripts\\check_google_health_diagnostics.py",
            "python scripts\\check_google_health_self_check.py",
            "python scripts\\smoke_framework_v200_real_google_health_sleep_data_preflight.py",
            "python scripts\\smoke_framework_v200_real_google_health_sleep_data_preflight.py --env-file .\\backend\\env_profiles\\google_health_real_api_operator.local.env",
        ),
        env_location_policy=(
            "copy the committed example to an ignored backend/env_profiles/*.local.env file"
        ),
        private_value_policy=(
            "do not print or commit credential paths, expected client IDs, OAuth tokens, "
            "authorization headers, raw health payloads, private paths, or LAN IPs"
        ),
        acceptance_policy=(
            "preflight cannot accept real_google_health_sleep_data; real backend/Web UI "
            "execution and screenshot evidence remain required"
        ),
        google_health_api_call_status="not-performed-by-this-commit",
        oauth_token_read_status="not-performed-by-this-commit",
        backend_start_status="not-performed-by-this-commit",
        web_ui_execution_status="not-performed-by-this-commit",
        screenshot_inspection_status="not-performed-by-this-commit",
        operator_evidence_acceptance_status="NOT_ACCEPTED",
        release_completion_status="NOT_RELEASED",
        mock_safe_default=True,
    )


def render_v200_real_google_health_sleep_data_preflight_contract(
    contract: V200RealGoogleHealthSleepDataPreflightContract,
) -> str:
    """Render deterministic marker-only contract text."""

    lines = [
        f"v200_real_google_health_sleep_data_preflight_status: {contract.status}",
        f"v200_real_google_health_sleep_data_preflight_requirement_key: {contract.requirement_key}",
        f"v200_real_google_health_sleep_data_preflight_commit_scope: {contract.commit_scope}",
        f"v200_real_google_health_sleep_data_preflight_mock_safe_default: {contract.mock_safe_default}",
        "v200_real_google_health_sleep_data_preflight_required_exact_keys: "
        + ",".join(contract.required_exact_values),
        "v200_real_google_health_sleep_data_preflight_required_nonempty_keys: "
        + ",".join(contract.required_nonempty_keys),
        "v200_real_google_health_sleep_data_preflight_required_true_keys: "
        + ",".join(contract.required_true_keys),
        "v200_real_google_health_sleep_data_preflight_required_false_keys: "
        + ",".join(contract.required_false_keys),
        "v200_real_google_health_sleep_data_preflight_recommended_project_access_keys: "
        + ",".join(contract.recommended_project_access_keys),
        "v200_real_google_health_sleep_data_preflight_required_repo_files: "
        + ",".join(contract.required_repo_files),
        "v200_real_google_health_sleep_data_preflight_required_gitignore_patterns: "
        + ",".join(contract.required_gitignore_patterns),
        "v200_real_google_health_sleep_data_preflight_required_commands: "
        + " | ".join(contract.required_commands),
        "v200_real_google_health_sleep_data_preflight_env_location_policy: "
        + contract.env_location_policy,
        "v200_real_google_health_sleep_data_preflight_private_value_policy: "
        + contract.private_value_policy,
        "v200_real_google_health_sleep_data_preflight_acceptance_policy: "
        + contract.acceptance_policy,
    ]

    for check in contract.checks:
        lines.append(
            f"v200_real_google_health_sleep_data_preflight_check_{check.key}: {check.status}"
        )

    lines.extend(
        [
            "v200_real_google_health_sleep_data_preflight_google_api_status: "
            + contract.google_health_api_call_status,
            "v200_real_google_health_sleep_data_preflight_oauth_token_read_status: "
            + contract.oauth_token_read_status,
            "v200_real_google_health_sleep_data_preflight_backend_start_status: "
            + contract.backend_start_status,
            "v200_real_google_health_sleep_data_preflight_web_ui_execution_status: "
            + contract.web_ui_execution_status,
            "v200_real_google_health_sleep_data_preflight_screenshot_inspection_status: "
            + contract.screenshot_inspection_status,
            "v200_real_google_health_sleep_data_preflight_operator_evidence_acceptance_status: "
            + contract.operator_evidence_acceptance_status,
            "v200_real_google_health_sleep_data_preflight_release_completion_status: "
            + contract.release_completion_status,
        ]
    )
    return "\n".join(lines)


def parse_env_file_without_expanding_values(path: Path) -> dict[str, str]:
    """Parse simple KEY=VALUE lines without expansion or value rendering."""

    parsed: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        parsed[key.strip()] = value.strip().strip('"').strip("'")
    return parsed


def validate_v200_real_google_health_sleep_data_preflight_env(
    env: Mapping[str, str],
) -> V200RealGoogleHealthSleepDataPreflightEnvValidation:
    """Validate marker shape without printing or persisting private values."""

    contract = build_v200_real_google_health_sleep_data_preflight_contract()
    accepted: list[str] = []
    missing_or_invalid: list[str] = []

    for key, expected in contract.required_exact_values.items():
        if str(env.get(key, "")).strip() == expected:
            accepted.append(key)
        else:
            missing_or_invalid.append(key)

    for key in contract.required_nonempty_keys:
        value = str(env.get(key, "")).strip()
        if value:
            accepted.append(key)
        else:
            missing_or_invalid.append(key)

    scopes = {
        part.strip()
        for part in str(env.get("GOOGLE_HEALTH_OAUTH_SCOPES", ""))
        .replace(",", " ")
        .split()
        if part.strip()
    }
    if contract.required_scope not in scopes:
        missing_or_invalid.append("GOOGLE_HEALTH_OAUTH_SCOPES_REQUIRED_SLEEP_SCOPE")
    else:
        accepted.append("GOOGLE_HEALTH_OAUTH_SCOPES_REQUIRED_SLEEP_SCOPE")

    for key in contract.required_true_keys:
        if str(env.get(key, "")).strip().lower() in _TRUE_VALUES:
            accepted.append(key)
        else:
            missing_or_invalid.append(key)

    for key in contract.required_false_keys:
        if str(env.get(key, "")).strip().lower() in _FALSE_VALUES:
            accepted.append(key)
        else:
            missing_or_invalid.append(key)

    recommended_present_list: list[str] = []
    for key in contract.recommended_project_access_keys:
        value = str(env.get(key, "")).strip()
        if key == "GOOGLE_HEALTH_EXPECTED_CLIENT_ID":
            confirmed = bool(value)
        else:
            confirmed = value.lower() in _TRUE_VALUES
        if confirmed:
            recommended_present_list.append(key)

    recommended_present = tuple(recommended_present_list)
    recommended_missing = tuple(
        key for key in contract.recommended_project_access_keys if key not in recommended_present
    )

    forbidden = set(key for key in env if key in contract.forbidden_exact_keys)
    for key in env:
        upper_key = key.upper()
        if any(fragment in upper_key for fragment in contract.forbidden_key_fragments):
            forbidden.add(key)

    forbidden_keys_present = tuple(sorted(forbidden))
    public_safe = not forbidden_keys_present
    status = "accepted" if not missing_or_invalid and public_safe else "incomplete-or-unsafe"

    return V200RealGoogleHealthSleepDataPreflightEnvValidation(
        status=status,
        accepted_keys=tuple(sorted(set(accepted))),
        missing_or_invalid_keys=tuple(sorted(set(missing_or_invalid))),
        recommended_keys_present=tuple(sorted(recommended_present)),
        recommended_keys_missing=tuple(sorted(recommended_missing)),
        forbidden_keys_present=forbidden_keys_present,
        public_safe=public_safe,
    )
