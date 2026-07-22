"""Source-tree safe E-3 real Google Health local env preflight.

Default mode does not read OAuth credentials/tokens, call Google Health, start
backend/Web UI, inspect screenshots, or accept evidence. Optional ``--env-file``
reads only KEY=VALUE markers and renders key names/boolean status, never values.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.services.framework_v200_real_google_health_sleep_data_preflight import (  # noqa: E402
    build_v200_real_google_health_sleep_data_preflight_contract,
    parse_env_file_without_expanding_values,
    render_v200_real_google_health_sleep_data_preflight_contract,
    validate_v200_real_google_health_sleep_data_preflight_env,
)


_CHECKLIST_FILE = ROOT / "docs/DRC_v200_goal_checklist_small_commit.md"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Render or validate v2.0.0 real Google Health local env preflight markers."
    )
    parser.add_argument(
        "--env-file",
        type=Path,
        help="Optional ignored operator env file. Values are never printed.",
    )
    args = parser.parse_args()

    contract = build_v200_real_google_health_sleep_data_preflight_contract()
    print("[smoke-framework-v200-real-google-health-sleep-data-preflight] RESULT")
    print(render_v200_real_google_health_sleep_data_preflight_contract(contract))

    if contract.requirement_key != "real_google_health_sleep_data":
        return _error("wrong requirement key")
    if contract.commit_scope != "E-3 only":
        return _error("wrong commit scope")
    if contract.operator_evidence_acceptance_status != "NOT_ACCEPTED":
        return _error("preflight accepted operator evidence early")
    if contract.release_completion_status != "NOT_RELEASED":
        return _error("release status changed early")
    if not contract.mock_safe_default:
        return _error("default mode must remain mock-safe")

    if not _check_required_repo_files(contract.required_repo_files):
        return 1
    if not _check_gitignore(contract.required_gitignore_patterns):
        return 1
    if not _check_example_env():
        return 1
    if not _check_unsafe_env_rejected():
        return 1
    if not _check_connection_checklist_cli_contract():
        return 1
    if not _check_docs_and_source_of_truth():
        return 1

    if args.env_file is not None and not _validate_env_file(args.env_file):
        return 1

    print("[smoke-framework-v200-real-google-health-sleep-data-preflight] OK")
    print(
        "No Google Health request, OAuth/token read, backend/Web startup, screenshot "
        "inspection, operator evidence acceptance, fixed zip build, or tag creation was performed."
    )
    return 0


def _error(message: str) -> int:
    print(
        "[smoke-framework-v200-real-google-health-sleep-data-preflight] ERROR: "
        + message
    )
    return 1


def _check_required_repo_files(paths: tuple[str, ...]) -> bool:
    missing = [path for path in paths if not (ROOT / path).exists()]
    if missing:
        _error("missing required files: " + ",".join(missing))
        return False
    print("v200_real_google_health_sleep_data_preflight_required_repo_files: present")
    return True


def _check_gitignore(patterns: tuple[str, ...]) -> bool:
    text = (ROOT / ".gitignore").read_text(encoding="utf-8")
    missing = [pattern for pattern in patterns if pattern not in text]
    if missing:
        _error("missing .gitignore patterns: " + ",".join(missing))
        return False
    print("v200_real_google_health_sleep_data_preflight_gitignore_patterns: present")
    return True


def _check_example_env() -> bool:
    path = ROOT / "backend/env_profiles/google_health_real_api_guarded.env.example"
    validation = validate_v200_real_google_health_sleep_data_preflight_env(
        parse_env_file_without_expanding_values(path)
    )
    print(
        "v200_real_google_health_sleep_data_preflight_example_env_status: "
        + validation.status
    )
    print(
        "v200_real_google_health_sleep_data_preflight_example_env_accepted_keys: "
        + ",".join(validation.accepted_keys)
    )
    print(
        "v200_real_google_health_sleep_data_preflight_example_env_missing_or_invalid_keys: "
        + ",".join(validation.missing_or_invalid_keys)
    )
    print(
        "v200_real_google_health_sleep_data_preflight_example_env_forbidden_keys_present: "
        + ",".join(validation.forbidden_keys_present)
    )
    if validation.status != "accepted" or not validation.public_safe:
        _error("guarded env example does not satisfy the E-3 preflight")
        return False
    return True


def _check_unsafe_env_rejected() -> bool:
    path = ROOT / "backend/env_profiles/google_health_real_api_guarded.env.example"
    env = parse_env_file_without_expanding_values(path)
    env["GOOGLE_HEALTH_ACCESS_TOKEN"] = "<private-not-printed>"
    env["GEMINI_API_KEY"] = "<private-not-printed>"
    validation = validate_v200_real_google_health_sleep_data_preflight_env(env)
    expected = {"GOOGLE_HEALTH_ACCESS_TOKEN", "GEMINI_API_KEY"}
    actual = set(validation.forbidden_keys_present)
    print(
        "v200_real_google_health_sleep_data_preflight_unsafe_env_status: "
        + validation.status
    )
    print(
        "v200_real_google_health_sleep_data_preflight_unsafe_env_forbidden_keys: "
        + ",".join(validation.forbidden_keys_present)
    )
    if validation.status == "accepted" or not expected.issubset(actual):
        _error("unrelated/provider secret keys were not rejected")
        return False
    return True


def _check_connection_checklist_cli_contract() -> bool:
    env = dict(os.environ)
    env["DRC_SKIP_BACKEND_DOTENV"] = "1"
    for key in tuple(env):
        if key.startswith("GOOGLE_HEALTH_") or key in {"SLEEP_PROVIDER", "CONVERSATION_ENGINE"}:
            env.pop(key, None)
    with tempfile.TemporaryDirectory() as temp_dir:
        isolated_token_file = Path(temp_dir) / "google_health_tokens.json"
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts/check_google_health_connection_checklist.py"),
                "--token-file",
                str(isolated_token_file),
            ],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
    combined = result.stdout + result.stderr
    if "Traceback" in combined or "AttributeError" in combined:
        _error("connection checklist CLI still raises a stale model-field error")
        return False
    required = (
        "token_store_configured=True",
        "token_stored=False",
        "connection_checklist=python scripts\\check_google_health_connection_checklist.py",
        "[google-health-connection-checklist] WARN",
    )
    missing = [fragment for fragment in required if fragment not in combined]
    if missing:
        _error("connection checklist CLI output missing: " + ",".join(missing))
        return False
    print("v200_real_google_health_sleep_data_preflight_connection_checklist_cli: guarded")
    return True


def _check_docs_and_source_of_truth() -> bool:
    docs = (
        ROOT / "docs/v200_real_google_health_sleep_data_operator_runbook.md",
        ROOT / "scripts/README.md",
        _CHECKLIST_FILE,
    )
    required_fragments = (
        "smoke_framework_v200_real_google_health_sleep_data_preflight.py",
        "google_health_real_api_operator.local.env",
    )
    missing: list[str] = []
    for path in docs:
        text = path.read_text(encoding="utf-8")
        for fragment in required_fragments:
            if fragment not in text:
                missing.append(f"{path.relative_to(ROOT)}::{fragment}")
    if missing:
        _error("required docs/source-of-truth fragments missing: " + " | ".join(missing))
        return False

    checklist_text = _CHECKLIST_FILE.read_text(encoding="utf-8")
    section_start = checklist_text.find("### 2.3 Real Google Health sleep data evidence")
    section_end = checklist_text.find("### 2.4 Image asset generation and safe intake evidence", section_start)
    if section_start < 0 or section_end < 0:
        _error("real Google Health source-of-truth section is missing")
        return False
    section = checklist_text[section_start:section_end]
    if "real_google_health_sleep_data: ACCEPTED" not in section:
        _error("source of truth is not synchronized to accepted Google Health evidence")
        return False
    forbidden = (
        "release_completion_status: RELEASED",
        "Status: **RELEASED**",
    )
    for fragment in forbidden:
        if fragment in checklist_text:
            _error("release state advanced early: " + fragment)
            return False
    if "accepted_private_evidence_manifest: NOT_ACCEPTED" not in checklist_text:
        _error("accepted private evidence manifest advanced early")
        return False
    print("v200_real_google_health_sleep_data_preflight_source_of_truth: synchronized-accepted")
    return True


def _validate_env_file(path: Path) -> bool:
    try:
        env = parse_env_file_without_expanding_values(path)
    except OSError as exc:
        _error("could not read env file: " + exc.__class__.__name__)
        return False

    validation = validate_v200_real_google_health_sleep_data_preflight_env(env)
    print("v200_real_google_health_sleep_data_preflight_env_file_supplied: True")
    print(
        "v200_real_google_health_sleep_data_preflight_env_file_validation_status: "
        + validation.status
    )
    print(
        "v200_real_google_health_sleep_data_preflight_env_file_accepted_keys: "
        + ",".join(validation.accepted_keys)
    )
    print(
        "v200_real_google_health_sleep_data_preflight_env_file_missing_or_invalid_keys: "
        + ",".join(validation.missing_or_invalid_keys)
    )
    print(
        "v200_real_google_health_sleep_data_preflight_env_file_recommended_keys_present: "
        + ",".join(validation.recommended_keys_present)
    )
    print(
        "v200_real_google_health_sleep_data_preflight_env_file_recommended_keys_missing: "
        + ",".join(validation.recommended_keys_missing)
    )
    print(
        "v200_real_google_health_sleep_data_preflight_env_file_forbidden_keys_present: "
        + ",".join(validation.forbidden_keys_present)
    )
    print(
        "v200_real_google_health_sleep_data_preflight_env_file_public_safe: "
        + str(validation.public_safe)
    )
    if validation.status != "accepted":
        _error("operator env file is incomplete or unsafe")
        return False
    return True


if __name__ == "__main__":
    raise SystemExit(main())
