"""Source-tree guard for accepted W-5b2 Google Health real operator verification.

This check reads Public source and documentation only. It does not read ignored
operator env files, credentials, tokens, screenshots, or private evidence; start
backend/Web processes; open OAuth; or make a provider request.
"""

from __future__ import annotations

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]


def read(relative: str) -> str:
    path = ROOT / relative
    if not path.is_file():
        raise AssertionError(f"Missing required file: {relative}")
    return path.read_text(encoding="utf-8")


def require(text: str, fragment: str, label: str) -> None:
    if fragment not in text:
        raise AssertionError(f"Missing {label}: {fragment}")


def assert_public_safe(relative: str, text: str) -> None:
    patterns = (
        r"Bearer\s+[A-Za-z0-9._\-]{12,}",
        r"AIza[0-9A-Za-z_\-]{20,}",
        r"(?i)client_secret\s*=\s*[^<\s]",
        r"(?i)(?:access_token|refresh_token)\s*=\s*[A-Za-z0-9._\-]{12,}",
        r"[A-Za-z]:\\Users\\[^<\r\n]+",
        r"(?:192\.168|10\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01]))\.\d{1,3}\.\d{1,3}",
        r"\b\d{1,2}:\d{2}\b",
        r"(?i)\.(?:png|jpe?g|webp)\b",
    )
    for pattern in patterns:
        if re.search(pattern, text):
            raise AssertionError(f"Sensitive-looking value in {relative}: {pattern}")


def main() -> None:
    doc = read("docs/v210_google_health_real_operator_verification.md")
    checklist = read("docs/DRC_v210_goal_checklist_small_commit.md")
    tasklist = read("tasklist.md")
    readme = read("README.md")
    roadmap = read("roadmap.md")
    scripts_readme = read("scripts/README.md")

    required_doc_markers = (
        "Status: COMPLETED / ACCEPTED",
        "operator_env_validation=accepted",
        "operator_private_files_git_ignored=True",
        "credentials_file_exists=True",
        "token_file_exists=True",
        "actual_run_checkpoint=passed",
        "initial_preflight_status=needs_token_refresh",
        "token_refresh_succeeded=True",
        "post_refresh_preflight_status=ready_for_real_api",
        "ready_for_real_api_request=True",
        "real_http_attempted=True",
        "google_health_http_status=200",
        "google_health_source_status=ok",
        "safe_to_use_sleep_summary=True",
        "backend_sleep_summary_source=google_health",
        "backend_sleep_summary_available=True",
        "backend_sleep_summary_is_real_data=True",
        "backend_sleep_summary_positive_duration=True",
        "pc_web_display=True",
        "smartphone_web_display=True",
        "data_source_label=Google Health",
        "data_kind_label=実データ",
        "availability_label=取得済み",
        "normalized_sleep_summary_visible=True",
        "raw_screenshot_committed=False",
        "fitbit_origin_provenance=operator-confirmed",
        "fitbit_origin_device_model=Fitbit Versa 2",
        "backend_pytest=100 passed",
        "flutter_test=57 passed",
        "diff_review=passed",
        "operator_approval=passed",
        "release_records_changed=False",
    )
    for marker in required_doc_markers:
        require(doc, marker, "W-5b2 public-safe marker")

    for text, fragment, label in (
        (checklist, "Current small commit: C-1a", "checklist current commit"),
        (checklist, "W-5b2  COMPLETED / ACCEPTED", "checklist W-5b2 state"),
        (checklist, "W-5  COMPLETED / ACCEPTED", "checklist parent state"),
        (checklist, "Status: COMPLETED / ACCEPTED", "checklist execution record"),
        (tasklist, "W-5b2 — Configured Google Health API operator verification", "tasklist W-5b2"),
        (tasklist, "W-5b2と親W-5は2026-07-24にCOMPLETED / ACCEPTED", "tasklist acceptance status"),
        (readme, "W-5 is completed and accepted", "README acceptance status"),
        (roadmap, "W-5b2 and parent W-5 are completed and accepted", "roadmap acceptance status"),
        (scripts_readme, "check_v210_google_health_real_operator_verification.py", "scripts README command"),
    ):
        require(text, fragment, label)

    require(checklist, "C-1  CURRENT / NOT_COMPLETED", "C-1 current state")
    for phase in ("T-1", "V-1", "R-1"):
        require(checklist, f"{phase}  PLANNED", f"{phase} planned state")

    for relative, text in (
        ("docs/v210_google_health_real_operator_verification.md", doc),
        ("docs/DRC_v210_goal_checklist_small_commit.md", checklist),
        ("tasklist.md", tasklist),
        ("README.md", readme),
        ("roadmap.md", roadmap),
        ("scripts/README.md", scripts_readme),
    ):
        assert_public_safe(relative, text)

    print("v210_google_health_real_operator_verification_status: completed-accepted")
    print("v210_google_health_real_operator_verification_completed_small_commit: W-5b2")
    print("v210_google_health_real_operator_verification_current_small_commit: C-1a")
    print("v210_google_health_real_operator_verification_parent_phase: W-5-completed-accepted")
    print("v210_google_health_real_operator_verification_operator_env_validation: accepted")
    print("v210_google_health_real_operator_verification_token_refresh: succeeded")
    print("v210_google_health_real_operator_verification_real_http_attempted: true")
    print("v210_google_health_real_operator_verification_http_status: 200")
    print("v210_google_health_real_operator_verification_normalized_summary: confirmed")
    print("v210_google_health_real_operator_verification_pc_web_display: true")
    print("v210_google_health_real_operator_verification_smartphone_web_display: true")
    print("v210_google_health_real_operator_verification_fitbit_origin_provenance: operator-confirmed")
    print("v210_google_health_real_operator_verification_fitbit_origin_device_model: Fitbit Versa 2")
    print("v210_google_health_real_operator_verification_raw_screenshot_committed: false")
    print("v210_google_health_real_operator_verification_release_records_changed: false")
    print("[v210-google-health-real-operator-verification-check] OK")


if __name__ == "__main__":
    main()
