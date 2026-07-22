"""v2.0.0 real Google Health sleep-data actual run checkpoint.

This module defines the source-tree safe E-5 handoff for the later private
configured Google Health backend/Web run. Building or rendering the contract
must not read credentials or OAuth tokens, call Google Health, start the DRC
backend, start Flutter Web, open a browser, inspect screenshots, read operator
evidence, or change v2.0.0 acceptance status.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class V200RealGoogleHealthActualRunStep:
    """One public-safe step in the private configured run sequence."""

    key: str
    status: str
    description: str


@dataclass(frozen=True)
class V200RealGoogleHealthActualRunCheckpointContract:
    """Static source-tree contract for the E-5 actual run handoff."""

    status: str
    requirement_key: str
    commit_scope: str
    checkpoint_steps: tuple[V200RealGoogleHealthActualRunStep, ...]
    required_source_tree_commands: tuple[str, ...]
    local_env_preflight_command: str
    backend_validate_only_command: str
    backend_start_command: str
    real_request_smoke_command: str
    flutter_web_start_command: str
    required_backend_result_markers: tuple[str, ...]
    required_web_ui_result_markers: tuple[str, ...]
    rejected_success_states: tuple[str, ...]
    required_operator_evidence_files: tuple[str, ...]
    required_marker_validation_commands: tuple[str, ...]
    required_docs: tuple[str, ...]
    required_gitignore_entries: tuple[str, ...]
    public_safe_omissions: tuple[str, ...]
    backend_env_loading_policy: str
    backend_dotenv_override_policy: str
    real_request_policy: str
    web_ui_policy: str
    screenshot_policy: str
    accepted_status_policy: str
    actual_local_preflight_status: str
    credentials_presence_status: str
    token_presence_status: str
    real_google_health_api_call_status: str
    oauth_token_value_read_status: str
    backend_start_status: str
    backend_request_status: str
    normalized_sleep_summary_status: str
    browser_run_status: str
    web_ui_result_status: str
    screenshot_inspection_status: str
    marker_evidence_validation_status: str
    operator_evidence_acceptance_status: str
    release_completion_status: str
    mock_safe_default: bool


def build_v200_real_google_health_actual_run_checkpoint_contract() -> (
    V200RealGoogleHealthActualRunCheckpointContract
):
    """Build the source-tree safe E-5 actual run checkpoint contract."""

    steps = (
        V200RealGoogleHealthActualRunStep(
            key="local_env_preflight_already_passed",
            status="required-before-private-run",
            description=(
                "The ignored Google Health operator env already produced accepted and "
                "public-safe preflight markers. E-5 records the next run sequence only."
            ),
        ),
        V200RealGoogleHealthActualRunStep(
            key="dedicated_backend_launcher_required",
            status="required-before-real-request",
            description=(
                "The actual backend must be started through the dedicated operator "
                "launcher so the validated env is loaded without printing values."
            ),
        ),
        V200RealGoogleHealthActualRunStep(
            key="backend_dotenv_override_disabled",
            status="required-before-real-request",
            description=(
                "The operator launcher must set DRC_SKIP_BACKEND_DOTENV=1 so a local "
                "backend/.env cannot silently override the validated operator profile."
            ),
        ),
        V200RealGoogleHealthActualRunStep(
            key="explicit_real_request_flag_required",
            status="required-for-google-api-call",
            description=(
                "The guarded real request smoke must still require --allow-real-request; "
                "source-tree checks and backend startup alone are not evidence."
            ),
        ),
        V200RealGoogleHealthActualRunStep(
            key="normalized_backend_sleep_summary_required",
            status="required-for-day55-and-day66",
            description=(
                "The actual /sleep/summary response must report source=google_health, "
                "available=True, is_real_data=True, and a positive normalized duration."
            ),
        ),
        V200RealGoogleHealthActualRunStep(
            key="smartphone_web_ui_required",
            status="required-for-day66-and-day78",
            description=(
                "Flutter Web must use DRC_BACKEND_API_BASE_URL and visibly show Google "
                "Health, real data, and retrieved status from the actual DRC backend."
            ),
        ),
        V200RealGoogleHealthActualRunStep(
            key="private_screenshot_required",
            status="required-for-day78",
            description=(
                "The Web result screenshot stays private; only an opaque public-safe "
                "reference and marker booleans may be recorded in operator evidence."
            ),
        ),
        V200RealGoogleHealthActualRunStep(
            key="day55_day66_day78_validation_required",
            status="required-before-later-acceptance-sync",
            description=(
                "All three marker-only validators must accept the private evidence before "
                "real_google_health_sleep_data may be synchronized as ACCEPTED."
            ),
        ),
    )

    return V200RealGoogleHealthActualRunCheckpointContract(
        status="real-google-health-sleep-data-actual-run-checkpoint-ready",
        requirement_key="real_google_health_sleep_data",
        commit_scope="E-5 only",
        checkpoint_steps=steps,
        required_source_tree_commands=(
            "python -m compileall -q backend scripts",
            "python scripts\\smoke_framework_v200_real_google_health_sleep_data_preflight.py",
            "python scripts\\check_google_health_runtime_guard.py",
            "python scripts\\check_google_health_sleep_parser.py",
            "python scripts\\check_google_health_sleep_source_boundary.py",
            "python scripts\\check_v200_real_google_health_sleep_data_day55.py",
            "python scripts\\check_v200_real_google_health_sleep_data_execution_day66.py",
            "python scripts\\check_v200_real_google_health_web_sleep_screenshot_day78.py",
            "python scripts\\smoke_framework_v200_real_google_health_sleep_data_actual_run_checkpoint.py",
        ),
        local_env_preflight_command=(
            "python scripts\\smoke_framework_v200_real_google_health_sleep_data_preflight.py "
            "--env-file .\\backend\\env_profiles\\google_health_real_api_operator.local.env"
        ),
        backend_validate_only_command=(
            "powershell -ExecutionPolicy Bypass -File "
            ".\\backend\\scripts\\run_google_health_real_api_operator.ps1 "
            "-EnvFile .\\backend\\env_profiles\\google_health_real_api_operator.local.env "
            "-ValidateOnly"
        ),
        backend_start_command=(
            "powershell -ExecutionPolicy Bypass -File "
            ".\\backend\\scripts\\run_google_health_real_api_operator.ps1 "
            "-EnvFile .\\backend\\env_profiles\\google_health_real_api_operator.local.env"
        ),
        real_request_smoke_command=(
            "python scripts\\smoke_google_health_real_sleep_request.py "
            "--base-url http://127.0.0.1:8000 --allow-real-request"
        ),
        flutter_web_start_command=(
            "cd app && flutter run -d chrome --web-hostname 0.0.0.0 --web-port 8080 "
            "--dart-define=DRC_BACKEND_API_BASE_URL=http://<PC_LAN_IP>:8000"
        ),
        required_backend_result_markers=(
            "real_http_attempted=True",
            "safe_to_use_sleep_summary=True",
            "backend_sleep_summary_source=google_health",
            "backend_sleep_summary_available=True",
            "backend_sleep_summary_is_real_data=True",
            "backend_sleep_summary_positive_duration=True",
        ),
        required_web_ui_result_markers=(
            "actual_drc_backend_api_used=True",
            "web_ui_execution_confirmed=True",
            "data_source_label=Google Health",
            "data_kind_label=実データ",
            "availability_label=取得済み",
            "normalized_sleep_summary_visible=True",
            "private_screenshot_reference_recorded=True",
        ),
        rejected_success_states=(
            "api_only",
            "source_tree_only",
            "command_output_only",
            "mock",
            "fixture",
            "fallback",
            "skipped",
            "unavailable",
            "oauth_missing",
            "token_invalid",
            "api_failed",
            "normalization_failed",
            "backend_not_called",
            "web_ui_not_confirmed",
            "screenshot_missing",
            "placeholder",
        ),
        required_operator_evidence_files=(
            "operator_evidence/200_real_google_health_sleep_data_day55.json",
            "operator_evidence/v200_real_google_health_sleep_data_day66.json",
            "operator_evidence/v200_real_google_health_web_sleep_screenshot_day78.json",
        ),
        required_marker_validation_commands=(
            "python scripts\\smoke_v200_real_google_health_sleep_data_evidence.py "
            "--operator-evidence-json .\\operator_evidence\\200_real_google_health_sleep_data_day55.json",
            "python scripts\\smoke_framework_v200_real_google_health_sleep_data_execution_evidence.py "
            "--operator-evidence-json .\\operator_evidence\\v200_real_google_health_sleep_data_day66.json",
            "python scripts\\smoke_framework_v200_real_google_health_web_sleep_screenshot_evidence.py "
            "--evidence-json .\\operator_evidence\\v200_real_google_health_web_sleep_screenshot_day78.json",
        ),
        required_docs=(
            "docs/v200_real_google_health_sleep_data_operator_runbook.md",
            "docs/v200_real_google_health_sleep_data_evidence.md",
            "docs/v200_real_google_health_sleep_data_execution_evidence.md",
            "docs/v200_real_google_health_web_sleep_screenshot_evidence_capture.md",
            "docs/DRC_v200_goal_checklist_small_commit.md",
            "scripts/README.md",
        ),
        required_gitignore_entries=(
            "*.local.env",
            "backend/env_profiles/*.local.env",
            "backend/local_data/",
            "credentials.json",
            "operator_evidence/",
            "_local/",
        ),
        public_safe_omissions=(
            "credential_contents",
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
        ),
        backend_env_loading_policy=(
            "load only the validated dedicated operator env into the backend process; "
            "print key names and boolean presence markers only"
        ),
        backend_dotenv_override_policy=(
            "set DRC_SKIP_BACKEND_DOTENV=1 so backend/.env cannot override the operator profile"
        ),
        real_request_policy=(
            "the guarded self-check plus backend summary sequence requires --allow-real-request and all three real API gates"
        ),
        web_ui_policy=(
            "Flutter Web must call the actual DRC backend through DRC_BACKEND_API_BASE_URL"
        ),
        screenshot_policy=(
            "raw screenshots stay private; only an opaque public-safe reference is recorded"
        ),
        accepted_status_policy=(
            "do not mark real_google_health_sleep_data ACCEPTED in E-5; later real execution, "
            "private evidence authoring, Day55/Day66/Day78 validation, and review are required"
        ),
        actual_local_preflight_status="PASSED-before-this-commit",
        credentials_presence_status="CONFIRMED-before-this-commit",
        token_presence_status="CONFIRMED-before-this-commit",
        real_google_health_api_call_status="not-performed-by-this-commit",
        oauth_token_value_read_status="not-performed-by-this-commit",
        backend_start_status="not-performed-by-this-commit",
        backend_request_status="not-performed-by-this-commit",
        normalized_sleep_summary_status="not-confirmed-by-this-commit",
        browser_run_status="not-performed-by-this-commit",
        web_ui_result_status="not-confirmed-by-this-commit",
        screenshot_inspection_status="not-performed-by-this-commit",
        marker_evidence_validation_status="not-performed-by-this-commit",
        operator_evidence_acceptance_status="NOT_ACCEPTED",
        release_completion_status="NOT_RELEASED",
        mock_safe_default=True,
    )


def render_v200_real_google_health_actual_run_checkpoint_contract(
    contract: V200RealGoogleHealthActualRunCheckpointContract,
) -> str:
    """Render deterministic public-safe E-5 checkpoint markers."""

    lines = [
        f"v200_real_google_health_actual_run_checkpoint_status: {contract.status}",
        f"v200_real_google_health_actual_run_checkpoint_requirement_key: {contract.requirement_key}",
        f"v200_real_google_health_actual_run_checkpoint_commit_scope: {contract.commit_scope}",
        "v200_real_google_health_actual_run_checkpoint_mock_safe_default: "
        + str(contract.mock_safe_default),
        "v200_real_google_health_actual_run_checkpoint_required_source_tree_commands: "
        + " | ".join(contract.required_source_tree_commands),
        "v200_real_google_health_actual_run_checkpoint_local_env_preflight_command: "
        + contract.local_env_preflight_command,
        "v200_real_google_health_actual_run_checkpoint_backend_validate_only_command: "
        + contract.backend_validate_only_command,
        "v200_real_google_health_actual_run_checkpoint_backend_start_command: "
        + contract.backend_start_command,
        "v200_real_google_health_actual_run_checkpoint_real_request_smoke_command: "
        + contract.real_request_smoke_command,
        "v200_real_google_health_actual_run_checkpoint_flutter_web_start_command: "
        + contract.flutter_web_start_command,
        "v200_real_google_health_actual_run_checkpoint_required_backend_result_markers: "
        + ",".join(contract.required_backend_result_markers),
        "v200_real_google_health_actual_run_checkpoint_required_web_ui_result_markers: "
        + ",".join(contract.required_web_ui_result_markers),
        "v200_real_google_health_actual_run_checkpoint_rejected_success_states: "
        + ",".join(contract.rejected_success_states),
        "v200_real_google_health_actual_run_checkpoint_required_operator_evidence_files: "
        + ",".join(contract.required_operator_evidence_files),
        "v200_real_google_health_actual_run_checkpoint_required_marker_validation_commands: "
        + " | ".join(contract.required_marker_validation_commands),
        "v200_real_google_health_actual_run_checkpoint_required_docs: "
        + ",".join(contract.required_docs),
        "v200_real_google_health_actual_run_checkpoint_required_gitignore_entries: "
        + ",".join(contract.required_gitignore_entries),
        "v200_real_google_health_actual_run_checkpoint_public_safe_omissions: "
        + ",".join(contract.public_safe_omissions),
        "v200_real_google_health_actual_run_checkpoint_backend_env_loading_policy: "
        + contract.backend_env_loading_policy,
        "v200_real_google_health_actual_run_checkpoint_backend_dotenv_override_policy: "
        + contract.backend_dotenv_override_policy,
        "v200_real_google_health_actual_run_checkpoint_real_request_policy: "
        + contract.real_request_policy,
        "v200_real_google_health_actual_run_checkpoint_web_ui_policy: "
        + contract.web_ui_policy,
        "v200_real_google_health_actual_run_checkpoint_screenshot_policy: "
        + contract.screenshot_policy,
        "v200_real_google_health_actual_run_checkpoint_accepted_status_policy: "
        + contract.accepted_status_policy,
    ]

    for step in contract.checkpoint_steps:
        lines.append(
            f"v200_real_google_health_actual_run_checkpoint_step_{step.key}: {step.status}"
        )

    lines.extend(
        [
            "v200_real_google_health_actual_run_checkpoint_actual_local_preflight_status: "
            + contract.actual_local_preflight_status,
            "v200_real_google_health_actual_run_checkpoint_credentials_presence_status: "
            + contract.credentials_presence_status,
            "v200_real_google_health_actual_run_checkpoint_token_presence_status: "
            + contract.token_presence_status,
            "v200_real_google_health_actual_run_checkpoint_real_google_health_api_call_status: "
            + contract.real_google_health_api_call_status,
            "v200_real_google_health_actual_run_checkpoint_oauth_token_value_read_status: "
            + contract.oauth_token_value_read_status,
            "v200_real_google_health_actual_run_checkpoint_backend_start_status: "
            + contract.backend_start_status,
            "v200_real_google_health_actual_run_checkpoint_backend_request_status: "
            + contract.backend_request_status,
            "v200_real_google_health_actual_run_checkpoint_normalized_sleep_summary_status: "
            + contract.normalized_sleep_summary_status,
            "v200_real_google_health_actual_run_checkpoint_browser_run_status: "
            + contract.browser_run_status,
            "v200_real_google_health_actual_run_checkpoint_web_ui_result_status: "
            + contract.web_ui_result_status,
            "v200_real_google_health_actual_run_checkpoint_screenshot_inspection_status: "
            + contract.screenshot_inspection_status,
            "v200_real_google_health_actual_run_checkpoint_marker_evidence_validation_status: "
            + contract.marker_evidence_validation_status,
            "v200_real_google_health_actual_run_checkpoint_operator_evidence_acceptance_status: "
            + contract.operator_evidence_acceptance_status,
            "v200_real_google_health_actual_run_checkpoint_release_completion_status: "
            + contract.release_completion_status,
        ]
    )

    return "\n".join(lines)
