"""Source-tree smoke for the E-5 Google Health actual run checkpoint.

Default mode does not read private env files, credentials, or OAuth tokens; call
Google Health; start backend/Web processes; open a browser; inspect screenshots;
read operator evidence; or create release artifacts.
"""

from __future__ import annotations

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.app.services.framework_v200_real_google_health_sleep_data_actual_run_checkpoint import (  # noqa: E402
    build_v200_real_google_health_actual_run_checkpoint_contract,
    render_v200_real_google_health_actual_run_checkpoint_contract,
)
from scripts.smoke_google_health_real_sleep_request import (  # noqa: E402
    SmokeFailure,
    _assert_backend_sleep_summary,
)


_REQUIRED_FILES = (
    "backend/scripts/run_google_health_real_api_operator.ps1",
    "backend/app/services/framework_v200_real_google_health_sleep_data_actual_run_checkpoint.py",
    "scripts/smoke_framework_v200_real_google_health_sleep_data_actual_run_checkpoint.py",
    "scripts/smoke_google_health_real_sleep_request.py",
    "docs/v200_real_google_health_sleep_data_operator_runbook.md",
    "docs/DRC_v200_goal_checklist_small_commit.md",
    "scripts/README.md",
)

_REQUIRED_DOC_FRAGMENTS_BY_PATH = {
    "docs/DRC_v200_goal_checklist_small_commit.md": (
        "Commit E-5 actual configured Google Health backend/Web run checkpoint progress",
        "smoke_framework_v200_real_google_health_sleep_data_actual_run_checkpoint.py",
        "run_google_health_real_api_operator.ps1",
        "DRC_SKIP_BACKEND_DOTENV=1",
        "backend_sleep_summary_source=google_health",
        "required_web_data_kind_label: 実データ",
        "real_google_health_sleep_data: NOT_ACCEPTED",
    ),
    "docs/v200_real_google_health_sleep_data_operator_runbook.md": (
        "## 5. E-5 actual configured backend/Web run checkpoint",
        "smoke_framework_v200_real_google_health_sleep_data_actual_run_checkpoint.py",
        "run_google_health_real_api_operator.ps1",
        "DRC_SKIP_BACKEND_DOTENV=1",
        "backend_sleep_summary_source=google_health",
        "data_kind_label=実データ",
        "real_google_health_sleep_data: NOT_ACCEPTED",
    ),
    "scripts/README.md": (
        "### v2.0.0 Commit E-5 actual Google Health backend/Web run checkpoint",
        "smoke_framework_v200_real_google_health_sleep_data_actual_run_checkpoint.py",
        "run_google_health_real_api_operator.ps1",
        "DRC_SKIP_BACKEND_DOTENV=1",
        "backend_sleep_summary_source=google_health",
        "data_kind_label=実データ",
        "real_google_health_sleep_data: NOT_ACCEPTED",
    ),
}


_FORBIDDEN_COMPLETION_SNIPPETS = (
    "real_google_health_api_call_status: performed-by-this-commit",
    "oauth_token_value_read_status: performed-by-this-commit",
    "backend_start_status: performed-by-this-commit",
    "backend_request_status: performed-by-this-commit",
    "normalized_sleep_summary_status: confirmed-by-this-commit",
    "browser_run_status: performed-by-this-commit",
    "web_ui_result_status: confirmed-by-this-commit",
    "screenshot_inspection_status: performed-by-this-commit",
    "marker_evidence_validation_status: performed-by-this-commit",
    "release_completion_status: RELEASED",
)

_SECRET_ASSIGNMENT_PATTERNS = (
    re.compile(r"(?i)(client_secret|access_token|refresh_token|authorization)\s*=\s*[^<\s][^\r\n]*"),
    re.compile(r"(?i)Bearer\s+[A-Za-z0-9._\-]{12,}"),
    re.compile(r"AIza[0-9A-Za-z_\-]{20,}"),
)


def main() -> int:
    contract = build_v200_real_google_health_actual_run_checkpoint_contract()
    print("[smoke-framework-v200-real-google-health-sleep-data-actual-run-checkpoint] RESULT")
    print(render_v200_real_google_health_actual_run_checkpoint_contract(contract))

    if contract.requirement_key != "real_google_health_sleep_data":
        return _error("wrong requirement key")
    if contract.operator_evidence_acceptance_status != "NOT_ACCEPTED":
        return _error("checkpoint accepted operator evidence early")
    if contract.release_completion_status != "NOT_RELEASED":
        return _error("release status changed early")
    if not contract.mock_safe_default:
        return _error("checkpoint must remain mock-safe")

    if not _check_non_execution_statuses(contract):
        return 1
    if not _check_required_files():
        return 1
    if not _check_command_contract(contract):
        return 1
    if not _check_launcher_contract():
        return 1
    if not _check_real_request_smoke_contract():
        return 1
    if not _check_backend_summary_runtime_contract():
        return 1
    if not _check_docs():
        return 1
    if not _check_gitignore(contract):
        return 1
    if not _check_public_files_for_secrets():
        return 1

    print("[smoke-framework-v200-real-google-health-sleep-data-actual-run-checkpoint] OK")
    print(
        "No private env read, credential/token read, Google Health request, backend/Web "
        "startup, browser action, screenshot inspection, operator evidence read, or "
        "release artifact creation was performed."
    )
    return 0


def _error(message: str) -> int:
    print(
        "[smoke-framework-v200-real-google-health-sleep-data-actual-run-checkpoint] "
        f"ERROR: {message}."
    )
    return 1


def _check_non_execution_statuses(contract) -> bool:
    expected = {
        "real_google_health_api_call_status": "not-performed-by-this-commit",
        "oauth_token_value_read_status": "not-performed-by-this-commit",
        "backend_start_status": "not-performed-by-this-commit",
        "backend_request_status": "not-performed-by-this-commit",
        "normalized_sleep_summary_status": "not-confirmed-by-this-commit",
        "browser_run_status": "not-performed-by-this-commit",
        "web_ui_result_status": "not-confirmed-by-this-commit",
        "screenshot_inspection_status": "not-performed-by-this-commit",
        "marker_evidence_validation_status": "not-performed-by-this-commit",
    }
    changed = [key for key, value in expected.items() if getattr(contract, key) != value]
    if changed:
        return not bool(_error("execution status changed early: " + ",".join(changed)))
    if contract.actual_local_preflight_status != "PASSED-before-this-commit":
        return not bool(_error("prior local preflight status is not PASSED"))
    if contract.credentials_presence_status != "CONFIRMED-before-this-commit":
        return not bool(_error("prior credentials presence is not confirmed"))
    if contract.token_presence_status != "CONFIRMED-before-this-commit":
        return not bool(_error("prior token presence is not confirmed"))
    print("v200_real_google_health_actual_run_checkpoint_non_execution_statuses: pass")
    return True


def _check_required_files() -> bool:
    missing = [path for path in _REQUIRED_FILES if not (ROOT / path).exists()]
    if missing:
        _error("missing required files: " + ",".join(missing))
        return False
    print("v200_real_google_health_actual_run_checkpoint_required_files: present")
    return True


def _check_command_contract(contract) -> bool:
    joined = "\n".join(
        contract.required_source_tree_commands
        + (
            contract.local_env_preflight_command,
            contract.backend_validate_only_command,
            contract.backend_start_command,
            contract.real_request_smoke_command,
            contract.flutter_web_start_command,
        )
        + contract.required_marker_validation_commands
    )
    required = (
        "run_google_health_real_api_operator.ps1",
        "-ValidateOnly",
        "smoke_google_health_real_sleep_request.py",
        "--allow-real-request",
        "DRC_BACKEND_API_BASE_URL=http://<PC_LAN_IP>:8000",
        "smoke_v200_real_google_health_sleep_data_evidence.py",
        "smoke_framework_v200_real_google_health_sleep_data_execution_evidence.py",
        "smoke_framework_v200_real_google_health_web_sleep_screenshot_evidence.py",
    )
    missing = [fragment for fragment in required if fragment not in joined]
    if missing:
        _error("required command fragments missing: " + ",".join(missing))
        return False
    if "DRC_API_BASE_URL=" in joined:
        _error("deprecated Flutter backend API define is present")
        return False
    print("v200_real_google_health_actual_run_checkpoint_commands: present")
    return True


def _check_launcher_contract() -> bool:
    text = (ROOT / "backend/scripts/run_google_health_real_api_operator.ps1").read_text(
        encoding="utf-8"
    )
    required = (
        "smoke_framework_v200_real_google_health_sleep_data_preflight.py",
        "DRC_SKIP_BACKEND_DOTENV",
        "GOOGLE_HEALTH_ENABLE_REAL_API_REQUESTS",
        "GOOGLE_HEALTH_REAL_API_OPT_IN",
        "GOOGLE_HEALTH_REAL_ENDPOINT_VERIFIED",
        "GOOGLE_HEALTH_ENABLE_REAL_TOKEN_EXCHANGE",
        "credentials_file_exists=True",
        "token_file_exists=True",
        "-m",
        "uvicorn",
        "app.main:app",
        "ValidateOnly",
    )
    missing = [fragment for fragment in required if fragment not in text]
    if missing:
        _error("operator launcher fragments missing: " + ",".join(missing))
        return False
    forbidden = (
        "Write-Host $Value",
        "Write-Output $Value",
        "client_secret=",
        "access_token=",
        "refresh_token=",
    )
    found = [fragment for fragment in forbidden if fragment in text]
    if found:
        _error("operator launcher may expose private values: " + ",".join(found))
        return False
    print("v200_real_google_health_actual_run_checkpoint_launcher: guarded")
    return True


def _check_real_request_smoke_contract() -> bool:
    text = (ROOT / "scripts/smoke_google_health_real_sleep_request.py").read_text(
        encoding="utf-8"
    )
    required = (
        '"/sleep/summary"',
        "backend_sleep_summary_source",
        "backend_sleep_summary_available",
        "backend_sleep_summary_is_real_data",
        "backend_sleep_summary_positive_duration",
        "--allow-real-request",
    )
    missing = [fragment for fragment in required if fragment not in text]
    if missing:
        _error("real request smoke does not verify backend handoff: " + ",".join(missing))
        return False
    print("v200_real_google_health_actual_run_checkpoint_real_request_smoke: guarded")
    return True



def _check_backend_summary_runtime_contract() -> bool:
    safe_summary = {
        "date": "redacted",
        "total_sleep_minutes": 1,
        "source": "google_health",
        "available": True,
        "is_real_data": True,
        "unavailable_reason": None,
    }
    _assert_backend_sleep_summary(safe_summary)

    rejected_summary = dict(safe_summary, source="mock", is_real_data=False)
    try:
        _assert_backend_sleep_summary(rejected_summary)
    except SmokeFailure:
        print("v200_real_google_health_actual_run_checkpoint_backend_summary_runtime: guarded")
        return True

    _error("backend summary runtime contract accepted mock data")
    return False

def _check_docs() -> bool:
    paths = tuple(ROOT / path for path in _REQUIRED_DOC_FRAGMENTS_BY_PATH)
    missing: list[str] = []
    for path in paths:
        relative = str(path.relative_to(ROOT)).replace("\\", "/")
        text = path.read_text(encoding="utf-8")
        for fragment in _REQUIRED_DOC_FRAGMENTS_BY_PATH[relative]:
            if fragment not in text:
                missing.append(f"{relative}::{fragment}")
        for forbidden in _FORBIDDEN_COMPLETION_SNIPPETS:
            if forbidden in text:
                missing.append(f"{relative}::forbidden::{forbidden}")
    if missing:
        _error("documentation checkpoint mismatch: " + " | ".join(missing))
        return False

    print("v200_real_google_health_actual_run_checkpoint_docs: docs-checklist-source-of-truth")
    return True


def _check_gitignore(contract) -> bool:
    text = (ROOT / ".gitignore").read_text(encoding="utf-8")
    missing = [entry for entry in contract.required_gitignore_entries if entry not in text]
    if missing:
        _error("gitignore entries missing: " + ",".join(missing))
        return False
    print("v200_real_google_health_actual_run_checkpoint_gitignore: protected")
    return True


def _check_public_files_for_secrets() -> bool:
    paths = (
        ROOT / "backend/scripts/run_google_health_real_api_operator.ps1",
        ROOT / "backend/app/services/framework_v200_real_google_health_sleep_data_actual_run_checkpoint.py",
        ROOT / "docs/v200_real_google_health_sleep_data_operator_runbook.md",
        ROOT / "scripts/README.md",
    )
    findings: list[str] = []
    for path in paths:
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in _SECRET_ASSIGNMENT_PATTERNS:
            if pattern.search(text):
                findings.append(str(path.relative_to(ROOT)))
                break
    if findings:
        _error("sensitive-looking assignments found: " + ",".join(findings))
        return False
    print("v200_real_google_health_actual_run_checkpoint_public_files: safe")
    return True


if __name__ == "__main__":
    raise SystemExit(main())
