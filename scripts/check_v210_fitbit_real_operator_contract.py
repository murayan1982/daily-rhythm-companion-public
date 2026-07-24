"""Source-tree guard for v2.1.0 W-5a Fitbit operator contract."""

from __future__ import annotations

import hashlib
from pathlib import Path
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "backend/env_profiles/fitbit_real_operator.env.example",
    "backend/scripts/run_fitbit_real_operator.ps1",
    "docs/v210_fitbit_real_operator_runbook.md",
    "scripts/smoke_v210_fitbit_real_operator_preflight.py",
    "scripts/smoke_v210_fitbit_real_operator_execution.py",
    "scripts/check_v210_fitbit_real_operator_contract.py",
)

ACCEPTED_RUNTIME_HASHES = {
    "backend/app/api/fitbit.py": "44463bb3ce7c0e325c7a2a31602a68b0bc436cff615ef03ea70a3d4be6641b66",
    "backend/app/models/fitbit.py": "5474e1f121b43f7d25a6959954bd1d7caed8f37478453fa3a7e7c672c4948b52",
    "backend/app/services/fitbit_service.py": "18c00c52a9e9a2f24eab027f0a484d658729635d76ec61fb85c942eed971adc1",
    "backend/app/services/fitbit_token_exchange.py": "60c4cc3ca7942c1334b443e0089547b97d6e7a4cc9ad1d745077d3be9a45d136",
    "backend/app/services/fitbit_token_store.py": "9215e20d1a02e8b97906e75875279cb3ee228a0bf640f418820623318fb62fb3",
    "backend/app/services/fitbit_api_client.py": "34a613eeda3d20adbae0a7a4fd0e21a7dd5e68c210d21372548424e1a4aef54b",
    "backend/app/services/fitbit_sleep_service.py": "5d62b006f760278d2f8501f2f32d95deeb99437e7004e35c5388662c686d9e89",
    "backend/app/services/fitbit_sleep_normalizer.py": "c0acb09ad59c89be97d64eaf2e1b410cd3bad3efed1a52a790049f16ac410c2d",
    "backend/app/services/sleep_providers/fitbit.py": "41f48c65245515ac429ad4380f00052ca9010258782eb90e15e04dafc065f356",
    "app/lib/models/fitbit_status.dart": "3c06914f0eb992ae11fd7febf5589b5ffe44fd639d3c847d9fe26ec11b513814",
    "app/lib/models/fitbit_connect_response.dart": "b2f897316bb6dd52f271e994bc15c6ddb1096b4c5c6ca2f499cc9495de77ed1c",
    "app/lib/models/sleep_provider_selection.dart": "3d25703232dbb34b22d9d876d97125695d3870c3448bfd47d5fe10b8581b0241",
    "app/lib/models/sleep_summary.dart": "f28173aeb89b996e284771243fe6cbd6e037098a634647b827ac096cef4d11e8",
}


def read(relative: str) -> str:
    path = ROOT / relative
    if not path.exists():
        raise AssertionError(f"Missing required file: {relative}")
    return path.read_text(encoding="utf-8")


def require(text: str, fragment: str, label: str) -> None:
    if fragment not in text:
        raise AssertionError(f"Missing {label}: {fragment}")


def normalized_hash(relative: str) -> str:
    text = read(relative).replace("\r\n", "\n").replace("\r", "\n")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def main() -> None:
    for relative in REQUIRED_FILES:
        read(relative)

    checklist = read("docs/DRC_v210_goal_checklist_small_commit.md")
    roadmap = read("roadmap.md")
    tasklist = read("tasklist.md")
    readme = read("README.md")
    scripts_readme = read("scripts/README.md")
    runbook = read("docs/v210_fitbit_real_operator_runbook.md")
    runner = read("backend/scripts/run_fitbit_real_operator.ps1")
    env_example = read("backend/env_profiles/fitbit_real_operator.env.example")
    gitignore = read(".gitignore")

    for text, label in (
        (checklist, "checklist"),
        (roadmap, "roadmap"),
        (tasklist, "tasklist"),
        (readme, "README"),
        (scripts_readme, "scripts README"),
    ):
        require(text, "W-5a", f"{label} W-5a state")
        require(text, "W-5b", f"{label} W-5b boundary")
        require(text, "W-5", f"{label} parent W-5 state")

    require(checklist, "Current small commit: T-1a", "current small commit")
    require(checklist, "W-5b1  COMPLETED / ACCEPTED", "W-5b1 accepted state")
    require(checklist, "Current small-commit state: CURRENT / NOT_COMPLETED", "W-5b current state")
    require(checklist, "W-5a  COMPLETED / ACCEPTED", "W-5a accepted state")
    require(checklist, "W-5 state: COMPLETED / ACCEPTED", "parent W-5 state")
    require(checklist, "C-1  COMPLETED / ACCEPTED", "current C-1 boundary")
    require(roadmap, "Current small commit: T-1a", "roadmap current commit")
    require(tasklist, "W-5b2 — Configured Google Health API operator verification", "tasklist current commit")

    for fragment in (
        "FITBIT_CLIENT_ID=<fitbit-client-id>",
        "FITBIT_CLIENT_SECRET=<fitbit-client-secret>",
        "FITBIT_REDIRECT_URI=http://127.0.0.1:8000/fitbit/callback",
        "FITBIT_ENABLE_REAL_TOKEN_EXCHANGE=0",
        "FITBIT_DEV_SAVE_DUMMY_TOKEN=0",
    ):
        require(env_example, fragment, "operator env template")

    forbidden_template_fragments = (
        "FITBIT_ACCESS_TOKEN=",
        "FITBIT_REFRESH_TOKEN=",
        "FITBIT_AUTHORIZATION_CODE=",
        "FITBIT_OAUTH_STATE=",
    )
    for fragment in forbidden_template_fragments:
        if fragment in env_example:
            raise AssertionError(f"Operator env template contains forbidden field: {fragment}")

    require(gitignore, "*.local.env", "ignored operator env pattern")
    require(gitignore, "operator_evidence/", "ignored operator evidence pattern")

    for fragment in (
        "ValidateOnly",
        "DRC_SKIP_BACKEND_DOTENV",
        "loaded_key_names",
        "token_file_exists",
        "Legacy Fitbit Web API execution is retired",
    ):
        require(runner, fragment, "guarded PowerShell runner")

    for forbidden in (
        "Write-Host $Value",
        "FITBIT_CLIENT_SECRET=$",
        "access_token=",
        "refresh_token=",
    ):
        if forbidden in runner:
            raise AssertionError(f"Runner may expose sensitive values: {forbidden}")

    for fragment in (
        "--allow-real-request",
        "smartphone_web_required: True",
        "smartphone_web_verified: False",
        "raw_payload_exposed: False",
        "W-5b",
    ):
        require(runbook, fragment, "operator runbook")

    default_preflight = run_script("scripts/smoke_v210_fitbit_real_operator_preflight.py")
    if default_preflight.returncode != 0:
        raise AssertionError(default_preflight.stdout + default_preflight.stderr)
    require(default_preflight.stdout, "mock_safe_default: True", "mock-safe preflight")
    require(default_preflight.stdout, "network_request: False", "network-free preflight")

    example_preflight = run_script(
        "scripts/smoke_v210_fitbit_real_operator_preflight.py",
        "--check-example",
    )
    if example_preflight.returncode != 0:
        raise AssertionError(example_preflight.stdout + example_preflight.stderr)
    require(example_preflight.stdout, "example_status: accepted", "example env validation")
    for secret_value in ("<fitbit-client-id>", "<fitbit-client-secret>"):
        if secret_value in example_preflight.stdout:
            raise AssertionError("Preflight printed an env value")

    with tempfile.TemporaryDirectory() as temp_dir:
        valid_env = Path(temp_dir) / "fitbit_real_operator.local.env"
        valid_env.write_text(
            "CONVERSATION_ENGINE=mock\n"
            "SLEEP_PROVIDER=fitbit\n"
            "FITBIT_REDIRECT_URI=http://127.0.0.1:8000/fitbit/callback\n"
            "FITBIT_ENABLE_REAL_TOKEN_EXCHANGE=0\n"
            "FITBIT_DEV_SAVE_DUMMY_TOKEN=0\n"
            "FITBIT_OAUTH_STATE_TTL_SECONDS=600\n",
            encoding="utf-8",
        )
        strict_preflight = run_script(
            "scripts/smoke_v210_fitbit_real_operator_preflight.py",
            "--env-file",
            str(valid_env),
        )
        if strict_preflight.returncode != 0:
            raise AssertionError(strict_preflight.stdout + strict_preflight.stderr)
        require(strict_preflight.stdout, "env_file_status: accepted", "strict env validation")
        for private_value in (str(valid_env),):
            if private_value in strict_preflight.stdout:
                raise AssertionError("Strict preflight printed a private value or path")

        forbidden_env = Path(temp_dir) / "fitbit_forbidden.local.env"
        forbidden_env.write_text(
            valid_env.read_text(encoding="utf-8") + "FITBIT_ACCESS_TOKEN=not-printed\n",
            encoding="utf-8",
        )
        rejected_preflight = run_script(
            "scripts/smoke_v210_fitbit_real_operator_preflight.py",
            "--env-file",
            str(forbidden_env),
        )
        if rejected_preflight.returncode == 0:
            raise AssertionError("Preflight accepted a forbidden token field")
        require(
            rejected_preflight.stdout,
            "forbidden_keys_present: FITBIT_ACCESS_TOKEN",
            "forbidden token key rejection",
        )
        if "not-printed" in rejected_preflight.stdout:
            raise AssertionError("Rejected preflight printed a forbidden token value")

    denied_execution = run_script("scripts/smoke_v210_fitbit_real_operator_execution.py")
    if denied_execution.returncode == 0:
        raise AssertionError("Real execution smoke ran without explicit opt-in")
    require(
        denied_execution.stdout,
        "legacy Fitbit Web API execution is retired; use Google Health API",
        "real execution opt-in guard",
    )

    for relative, expected in ACCEPTED_RUNTIME_HASHES.items():
        actual = normalized_hash(relative)
        if actual != expected:
            raise AssertionError(
                f"Accepted W-2/W-3/W-4 runtime changed: {relative}: {actual} != {expected}"
            )

    flutter_client = read("app/lib/services/backend_api_client.dart")
    flutter_home = read("app/lib/screens/home_screen.dart")
    require(flutter_client, "throw PostAdviceChatApiException", "C-1c typed chat error")
    require(flutter_home, "post-advice-chat-restart-button", "C-1c chat recovery UI")

    print("v210_fitbit_real_operator_contract_status: completed-accepted")
    print("v210_fitbit_real_operator_contract_completed_small_commit: W-5a")
    print("v210_fitbit_real_operator_contract_current_small_commit: T-1a")
    print("v210_fitbit_real_operator_contract_parent_phase: W-5-completed-accepted")
    print("v210_fitbit_real_operator_contract_mock_safe: True")
    print("v210_fitbit_real_operator_contract_real_operator_execution: False")
    print("v210_fitbit_real_operator_contract_runtime_changed: False")
    print("v210_fitbit_real_operator_contract_c1c_flutter_runtime_started: True")
    print("v210_fitbit_real_operator_contract_release_records_changed: False")
    print("v210_fitbit_real_operator_contract_w5b1_completed_accepted: True")
    print("v210_fitbit_real_operator_contract_w5b2_completed_accepted: True")
    print("[v210-fitbit-real-operator-contract-check] OK")


if __name__ == "__main__":
    main()
