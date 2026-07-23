"""Verify the active post-v2.0.0 maintenance baseline.

This credential-free source-tree check preserves the immutable v2.0.0 records
and validates the current small-commit queue. It does not run external APIs,
build release artifacts, or modify the repository.
"""

from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

HISTORICAL_HASHES = {
    "docs/DRC_v200_goal_checklist_small_commit.md": (
        "4c043837986c626c6fc44e4f84f73b019b2c8c21da7531a3f029554006b7eb63"
    ),
    "release_notes/v2.0.0.md": (
        "d2e13041ae51b9fef330a01a0d9124ccbfb6fb0850a0c2a29966baf96be3417b"
    ),
}


def read(relative: str) -> str:
    path = ROOT / relative
    if not path.is_file():
        raise AssertionError(f"Missing required file: {relative}")
    return path.read_text(encoding="utf-8")


def require(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise AssertionError(f"Missing {label}: {needle!r}")


def reject(text: str, needle: str, label: str) -> None:
    if needle in text:
        raise AssertionError(f"Unexpected {label}: {needle!r}")


def section_between(text: str, start: str, end: str | None) -> str:
    if start not in text:
        raise AssertionError(f"Missing section: {start}")
    section = text.split(start, 1)[1]
    if end and end in section:
        section = section.split(end, 1)[0]
    return section


def assert_historical_hashes() -> None:
    for relative, expected in HISTORICAL_HASHES.items():
        path = ROOT / relative
        if not path.is_file():
            raise AssertionError(f"Missing historical release record: {relative}")
        normalized = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
        actual = sha256(normalized).hexdigest()
        if actual != expected:
            raise AssertionError(
                f"Historical release record changed: {relative}: {actual} != {expected}"
            )


def assert_no_obvious_secrets(relative: str, text: str) -> None:
    patterns = (
        r"sk-[A-Za-z0-9_\-]{12,}",
        r"xai-[A-Za-z0-9_\-]{12,}",
        r"AIza[0-9A-Za-z_\-]{20,}",
        r"Bearer\s+[A-Za-z0-9_\-.]{16,}",
        r"(?:access|refresh)_token\s*[:=]\s*['\"][^'\"]+",
        r"client_secret\s*[:=]\s*['\"][^'\"]+",
        r"[A-Za-z]:\\Users\\[^<\r\n]+",
        r"192\.168\.\d{1,3}\.\d{1,3}",
    )
    for pattern in patterns:
        if re.search(pattern, text, flags=re.IGNORECASE):
            raise AssertionError(f"Sensitive-looking value in {relative}: {pattern}")


def main() -> None:
    files = {
        "README.md": read("README.md"),
        "roadmap.md": read("roadmap.md"),
        "tasklist.md": read("tasklist.md"),
        "scripts/README.md": read("scripts/README.md"),
        "docs/post_v200_release_baseline.md": read("docs/post_v200_release_baseline.md"),
        "docs/DRC_v20x_maintenance_checklist.md": read("docs/DRC_v20x_maintenance_checklist.md"),
        "docs/public_private_development_policy.md": read("docs/public_private_development_policy.md"),
    }

    for relative in ("README.md", "roadmap.md", "tasklist.md", "scripts/README.md"):
        require(files[relative], "v2.0.0", f"{relative} released baseline")
        require(files[relative], "RELEASED", f"{relative} released status")
        require(files[relative], "docs/DRC_v20x_maintenance_checklist.md", f"{relative} active maintenance source")
        require(files[relative], "M-7", f"{relative} accepted M-7 state")

    require(files["README.md"], "Current released version: v2.0.1", "README released patch")
    require(files["roadmap.md"], "Status: Completed / released", "roadmap maintenance status")
    require(files["roadmap.md"], "M-1  COMPLETED", "roadmap M-1 completion")
    require(files["roadmap.md"], "M-2  COMPLETED", "roadmap M-2 completion")
    require(files["roadmap.md"], "M-3  COMPLETED", "roadmap M-3 completion")
    require(files["roadmap.md"], "M-4  COMPLETED", "roadmap M-4 completion")
    require(files["roadmap.md"], "M-5  COMPLETED", "roadmap M-5 completion")
    require(files["roadmap.md"], "M-6  COMPLETED", "roadmap M-6 completion")
    require(files["roadmap.md"], "M-7  COMPLETED", "roadmap M-7 completion")
    require(files["roadmap.md"], "M-8  COMPLETED", "roadmap M-8 completion")
    require(files["tasklist.md"], "M-5  COMPLETED", "task list M-5 completion")
    require(files["tasklist.md"], "M-6  COMPLETED", "task list M-6 completion")
    require(files["tasklist.md"], "M-7  COMPLETED", "task list M-7 completion")
    require(files["tasklist.md"], "M-8  COMPLETED", "task list M-8 completion")
    require(files["tasklist.md"], "Status: COMPLETED / ACCEPTED", "task list accepted state")
    require(files["scripts/README.md"], r"python scripts\check_v20x_maintenance_baseline.py", "scripts README baseline command")
    require(files["scripts/README.md"], r"python scripts\check_v20x_application_version_metadata.py", "scripts README M-2 command")
    require(files["scripts/README.md"], r"python scripts\check_v20x_backend_mock_safe_regression.py", "scripts README M-3 command")
    require(files["scripts/README.md"], r"python scripts\check_v20x_framework_fallback_voice_artifact_regression.py", "scripts README M-4 command")
    require(files["scripts/README.md"], r"python scripts\check_v20x_temporary_lifecycle_limits.py", "scripts README M-5 command")
    require(files["scripts/README.md"], r"python scripts\check_v20x_fitbit_current_state_contract.py", "scripts README M-7 command")
    require(files["scripts/README.md"], r"python scripts\check_v20x_maintenance_readiness.py", "scripts README M-8 command")

    checklist_text = files["docs/DRC_v20x_maintenance_checklist.md"]
    require(checklist_text, "Status: COMPLETED / ACCEPTED", "maintenance checklist status")
    require(checklist_text, "Current small commit: none (M-9 accepted; v2.0.1 released)", "maintenance current state")
    m1 = section_between(checklist_text, "# M-1", "# M-2")
    require(m1, "Status: COMPLETED", "M-1 completed status")
    m2 = section_between(checklist_text, "# M-2", "# M-3")
    require(m2, "Status: COMPLETED", "M-2 completed status")
    m3 = section_between(checklist_text, "# M-3", "# M-4")
    require(m3, "Status: COMPLETED", "M-3 completed status")
    m4 = section_between(checklist_text, "# M-4", "# M-5")
    require(m4, "Status: COMPLETED", "M-4 completed status")
    m5 = section_between(checklist_text, "# M-5", "# M-6")
    require(m5, "Status: COMPLETED", "M-5 completed status")
    require(m5, "M-5 was accepted on 2026-07-22", "M-5 acceptance record")
    m6 = section_between(checklist_text, "# M-6", "# Planned queue")
    require(m6, "Status: COMPLETED / ACCEPTED", "M-6 accepted status")
    require(m6, "M-6 was accepted on 2026-07-23", "M-6 acceptance record")
    m7 = section_between(checklist_text, "## M-7", "## M-8")
    require(m7, "Status: COMPLETED / ACCEPTED", "M-7 accepted status")
    require(m7, "M-7 was accepted on 2026-07-23", "M-7 acceptance record")
    m8 = section_between(checklist_text, "## M-8", "\n## M-9 — Patch release")
    require(m8, "Status: COMPLETED / ACCEPTED", "M-8 accepted status")
    require(m8, "M-8 was accepted on 2026-07-23", "M-8 acceptance record")
    m9 = section_between(checklist_text, "\n## M-9 — Patch release", "# Future-version boundary")
    require(m9, "Status: COMPLETED / ACCEPTED", "M-9 accepted status")
    require(m9, "M-9 was accepted on 2026-07-23", "M-9 acceptance record")

    baseline = files["docs/post_v200_release_baseline.md"]
    require(baseline, "DRC_v2.0.0", "baseline tag")
    require(baseline, "b32c7b8a64842480898fcc86ca7838625efb712f1429ab9fe7b33a4001ddc0c1", "baseline artifact hash")
    require(baseline, "Not accepted as real runtime", "baseline unfinished distinction")

    policy = files["docs/public_private_development_policy.md"]
    for needle in (
        "Mock-safe behavior remains the credential-free default",
        "Real external execution requires explicit opt-in",
        "Never move or rewrite a published release tag",
        "must not become an alternate source history",
    ):
        require(policy, needle, "Public/Private policy")

    assert_historical_hashes()
    for relative, text in files.items():
        assert_no_obvious_secrets(relative, text)

    print("v20x_maintenance_baseline_status: active")
    print("v20x_maintenance_baseline_released_version: v2.0.1")
    print("v20x_maintenance_baseline_patch_source_version: v2.0.1")
    print("v20x_maintenance_baseline_current_line: v2.0.x")
    print("v20x_maintenance_baseline_current_small_commit: none")
    print("v20x_maintenance_baseline_m1_completed: True")
    print("v20x_maintenance_baseline_m2_completed: True")
    print("v20x_maintenance_baseline_m3_completed: True")
    print("v20x_maintenance_baseline_m4_completed: True")
    print("v20x_maintenance_baseline_m5_completed: True")
    print("v20x_maintenance_baseline_m6_completed_accepted: True")
    print("v20x_maintenance_baseline_m7_completed_accepted: True")
    print("v20x_maintenance_baseline_m8_completed_accepted: True")
    print("v20x_maintenance_baseline_m9_completed_accepted: True")
    print("v20x_maintenance_baseline_historical_records_unchanged: True")
    print("[v20x-maintenance-baseline-check] OK")


if __name__ == "__main__":
    main()
