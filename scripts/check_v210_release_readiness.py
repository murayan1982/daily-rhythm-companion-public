"""Run the accepted R-1b gate plus the current R-1c source contract.

The portable default is credential-free and artifact-free. It runs the accepted
R-1b source/test baseline, the current R-1c validator contract, and Backend pytest. ``--with-flutter`` adds the full
Flutter test suite. ``--with-builds`` additionally requires Web and Windows
builds and reproduces the accepted R-1b gate on the Windows release host.
No mode builds a release ZIP or creates a tag/GitHub Release.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_BACKEND_VERSION = "2.1.0"
EXPECTED_FLUTTER_VERSION = "2.1.0+3"
EXPECTED_BACKEND_TESTS = 110
EXPECTED_FLUTTER_TESTS = 103
V20X_COMPATIBILITY_GATE = "scripts/check_v20x_maintenance_readiness.py"

AGGREGATE_CHECKS = (
    "scripts/check_v210_character_display_current_behavior_inventory.py",
    "scripts/check_v210_character_display_home_integration.py",
    "scripts/check_v210_character_display_state.py",
    "scripts/check_v210_final_smartphone_web_evidence.py",
    "scripts/check_v210_fitbit_current_behavior_inventory.py",
    "scripts/check_v210_fitbit_real_operator_contract.py",
    "scripts/check_v210_fitbit_real_sleep_normalization.py",
    "scripts/check_v210_fitbit_token_status_reconnect.py",
    "scripts/check_v210_flutter_sleep_provider_source_ui.py",
    "scripts/check_v210_google_health_migration_audit.py",
    "scripts/check_v210_google_health_real_operator_verification.py",
    "scripts/check_v210_post_advice_chat_backend_lifecycle.py",
    "scripts/check_v210_post_advice_chat_current_behavior_inventory.py",
    "scripts/check_v210_post_advice_chat_flutter_lifecycle.py",
    "scripts/check_v210_release_readiness_current_behavior_inventory.py",
    "scripts/check_v210_sleep_provider_selection_source_labels.py",
    "scripts/check_v210_tts_player_controller.py",
    "scripts/check_v210_tts_player_current_behavior_inventory.py",
    "scripts/check_v210_tts_player_home_integration.py",
)

PROTECTED_HISTORICAL_HASHES = {
    "docs/DRC_v200_goal_checklist_small_commit.md": "4c043837986c626c6fc44e4f84f73b019b2c8c21da7531a3f029554006b7eb63",
    "release_notes/v2.0.0.md": "d2e13041ae51b9fef330a01a0d9124ccbfb6fb0850a0c2a29966baf96be3417b",
    "docs/DRC_v20x_maintenance_checklist.md": "02e6e2e49a54a5c1360ee5d95d6bed2314ab42aec5dce911f3ed72867c4d46f2",
    "docs/v20x_patch_release.md": "eb6ae9770a4611a463ddb227a1dd8ce8816ee310cddaed327a02404a34a7935d",
    "docs/v201_patch_release_record.md": "9b724a6c5c7ffffdb3e699ad010ff75148ec4549b6cf2d940b44e62e161140bd",
    "release_notes/v2.0.1.md": "1e90c85e51ef848b64bddaa73f1f40c659457935e30831027310ea95fc94656b",
    "build_v200_final_fixed_release_zip_from_head.ps1": "4a4439341b0ad00d56b50038993631fcb48fb417cd0f0648dc3abc5e72d3b360",
    "build_v201_fixed_release_zip_from_head.ps1": "89d3fe3e39484b36272d9c8ec8499276ffe305ec844a87cca5d90fef8931ab1b",
    "scripts/check_v20x_patch_release.py": "e4eefc408abcbccc2651c1113ae8264269cce1d77525067173e0a06a7ef685cf",
}

PROTECTED_GENERIC_PACKAGE_HASHES = {
    "build_release.bat": "1e939e31187b58efe7c5987fd763dba733ff706ad864a14cf945e641a9f23c1a",
    "scripts/check_release_package.py": "56b5550b2d7145c3bfc4d9ff4370499df261c9f629ba551820588d859fbcff50",
    ".gitignore": "740b4903072fef306fba8880bc9f8d57ac2055ed38168314b6834ce0eec0c8a3",
}

R1D_FILES_MUST_NOT_EXIST = (
    "build_v210_fixed_release_zip_from_head.ps1",
    "scripts/check_v210_fixed_release_zip.py",
)

PUBLIC_SAFE_FILES = (
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v210_goal_checklist_small_commit.md",
    "docs/v210_release_readiness_current_behavior_inventory.md",
    "docs/v210_release_readiness.md",
    "docs/v210_final_smartphone_web_evidence.md",
    "docs/operator_evidence_templates/v210_final_smartphone_web_evidence_r1c.example.json",
    "docs/v210_release_record.md",
    "release_notes/v2.1.0.md",
)


def read(relative: str) -> str:
    path = ROOT / relative
    if not path.is_file():
        raise AssertionError(f"Missing required file: {relative}")
    return path.read_text(encoding="utf-8")


def require(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise AssertionError(f"Missing {label}: {needle!r}")


def forbid(text: str, needle: str, label: str) -> None:
    if needle in text:
        raise AssertionError(f"Unexpected {label}: {needle!r}")


def normalized_hash(relative: str) -> str:
    data = (ROOT / relative).read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return sha256(data).hexdigest()


def assert_hashes(expected: dict[str, str], label: str) -> None:
    for relative, digest in expected.items():
        actual = normalized_hash(relative)
        if actual != digest:
            raise AssertionError(f"{label} changed: {relative}: {actual} != {digest}")


def snapshot_tree(relative: str) -> tuple[tuple[str, int, int], ...] | None:
    root = ROOT / relative
    if not root.exists():
        return None
    entries: list[tuple[str, int, int]] = []
    for path in sorted(root.rglob("*")):
        stat = path.lstat()
        entries.append((path.relative_to(root).as_posix(), stat.st_size, stat.st_mtime_ns))
    return tuple(entries)


def assert_no_sensitive_values(relative: str, text: str) -> None:
    patterns = (
        r"sk-[A-Za-z0-9_\-]{12,}",
        r"xai-[A-Za-z0-9_\-]{12,}",
        r"AIza[0-9A-Za-z_\-]{20,}",
        r"Bearer\s+[A-Za-z0-9_\-.]{16,}",
        r"[A-Za-z]:\\Users\\[^<\r\n]+",
        r"\b(?:10\.\d+\.\d+\.\d+|192\.168\.\d+\.\d+|172\.(?:1[6-9]|2\d|3[0-1])\.\d+\.\d+)\b",
    )
    for pattern in patterns:
        if re.search(pattern, text, flags=re.IGNORECASE):
            raise AssertionError(f"Sensitive-looking value in {relative}: {pattern}")


def run(command: list[str], *, cwd: Path = ROOT) -> None:
    subprocess.run(command, cwd=cwd, check=True)


def run_capture(command: list[str], *, cwd: Path = ROOT) -> str:
    completed = subprocess.run(
        command,
        cwd=cwd,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    print(completed.stdout, end="")
    return completed.stdout


def verify_contract() -> None:
    checklist = read("docs/DRC_v210_goal_checklist_small_commit.md")
    readme = read("README.md")
    roadmap = read("roadmap.md")
    tasklist = read("tasklist.md")
    scripts_readme = read("scripts/README.md")
    inventory = read("docs/v210_release_readiness_current_behavior_inventory.md")
    readiness = read("docs/v210_release_readiness.md")
    evidence_doc = read("docs/v210_final_smartphone_web_evidence.md")
    release_record = read("docs/v210_release_record.md")
    release_notes = read("release_notes/v2.1.0.md")

    for source, label in (
        (checklist, "checklist"),
        (readme, "README"),
        (roadmap, "roadmap"),
        (tasklist, "tasklist"),
        (scripts_readme, "scripts README"),
        (inventory, "R-1a inventory"),
        (readiness, "R-1b readiness"),
        (evidence_doc, "R-1c evidence contract"),
    ):
        require(source, "R-1a", f"{label} R-1a marker")
        require(source, "COMPLETED / ACCEPTED", f"{label} R-1a accepted marker")
        require(source, "R-1b", f"{label} R-1b marker")
        require(source, "COMPLETED / ACCEPTED", f"{label} R-1b accepted marker")
        require(source, "R-1c", f"{label} R-1c marker")
        require(source, "CURRENT / NOT_COMPLETED", f"{label} R-1c current marker")
        require(source, "IMPLEMENTED / NOT_ACCEPTED", f"{label} R-1c implementation marker")

    require(checklist, "Current small commit: R-1c", "current small commit")
    require(checklist, "Current implementation state: IMPLEMENTED / NOT_ACCEPTED", "R-1c implementation state")
    require(checklist, "R-1  CURRENT / NOT_COMPLETED", "parent R-1 state")
    require(checklist, "R-1a  COMPLETED / ACCEPTED", "R-1a accepted state")
    require(checklist, "R-1b  COMPLETED / ACCEPTED", "R-1b accepted state")
    require(checklist, "R-1c  CURRENT / NOT_COMPLETED", "R-1c current state")
    require(checklist, "R-1e  PLANNED", "R-1e planned state")

    backend_version = read("backend/app/version.py")
    require(backend_version, f'APP_VERSION = "{EXPECTED_BACKEND_VERSION}"', "Backend candidate version")
    if len(re.findall(r"^APP_VERSION\s*=", backend_version, flags=re.MULTILINE)) != 1:
        raise AssertionError("backend/app/version.py must define APP_VERSION exactly once")

    pubspec = read("app/pubspec.yaml")
    require(pubspec, f"version: {EXPECTED_FLUTTER_VERSION}", "Flutter candidate version")

    require(readiness, "expected accepted baseline: 110 passed", "Backend test requirement")
    require(readiness, "expected accepted baseline: 103 passed", "Flutter test requirement")
    require(readiness, "flutter build web", "Web build requirement")
    require(readiness, "flutter build windows", "Windows build requirement")
    require(readiness, "does not invoke build_release.bat", "artifact-free boundary")
    require(readiness, "accepted R-1b record of 18 / 18 checks", "accepted R-1b check count")
    require(readiness, "nineteenth child check", "current R-1c aggregate count")
    require(evidence_doc, "Status: IMPLEMENTED / NOT_ACCEPTED", "R-1c evidence status")

    for child in AGGREGATE_CHECKS:
        if not (ROOT / child).is_file():
            raise AssertionError(f"Missing aggregate child check: {child}")
        require(readiness, Path(child).name, "documented aggregate child")
    if tuple(sorted(AGGREGATE_CHECKS)) != AGGREGATE_CHECKS:
        raise AssertionError("Aggregate checks must remain sorted")
    if "scripts/check_v210_release_readiness.py" in AGGREGATE_CHECKS:
        raise AssertionError("Aggregate gate must not invoke itself")
    if not (ROOT / V20X_COMPATIBILITY_GATE).is_file():
        raise AssertionError(f"Missing v2.0.x compatibility gate: {V20X_COMPATIBILITY_GATE}")
    require(readiness, Path(V20X_COMPATIBILITY_GATE).name, "v2.0.x compatibility gate")

    for marker in (
        "Status: RELEASE CANDIDATE / NOT_RELEASED",
        "Backend semantic version: `2.1.0`",
        "Flutter package version: `2.1.0+3`",
        "Release tag: `DRC_v2.1.0` — NOT_CREATED",
    ):
        require(release_notes, marker, "candidate release notes")

    for marker in (
        "Status: PREPARED / NOT_RELEASED",
        "source HEAD: NOT_RECORDED",
        "fixed ZIP basename: NOT_BUILT",
        "fixed ZIP SHA-256: NOT_RECORDED",
        "explicit final operator approval: NOT_RECEIVED",
        "annotated tag publication: NOT_CREATED",
        "GitHub Release publication: NOT_CREATED",
    ):
        require(release_record, marker, "unfilled release record")

    forbid(release_record, "Status: RELEASED", "early released state")
    forbid(release_notes, "Status: RELEASED", "early release-notes state")

    for relative in R1D_FILES_MUST_NOT_EXIST:
        if (ROOT / relative).exists():
            raise AssertionError(f"R-1b must not create R-1d implementation: {relative}")

    assert_hashes(PROTECTED_HISTORICAL_HASHES, "Protected historical release record")
    assert_hashes(PROTECTED_GENERIC_PACKAGE_HASHES, "Protected generic package boundary")

    for relative in PUBLIC_SAFE_FILES:
        assert_no_sensitive_values(relative, read(relative))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--with-flutter",
        action="store_true",
        help="also run the full Flutter test suite",
    )
    parser.add_argument(
        "--with-builds",
        action="store_true",
        help="also run Flutter Web and Windows release builds (requires --with-flutter on Windows)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.with_builds and not args.with_flutter:
        raise AssertionError("--with-builds requires --with-flutter")
    if args.with_builds and os.name != "nt":
        raise AssertionError("--with-builds must run on the Windows release host")

    local_data_before = snapshot_tree("backend/local_data")
    release_before = snapshot_tree("release")

    verify_contract()
    run([sys.executable, "-m", "compileall", "-q", "backend", "scripts"])
    for child in AGGREGATE_CHECKS:
        run([sys.executable, child])
    run([sys.executable, V20X_COMPATIBILITY_GATE])
    pytest_output = run_capture(
        [sys.executable, "-m", "pytest", "-q", "backend/tests"]
    )
    passed_matches = re.findall(r"(\d+) passed", pytest_output)
    if not passed_matches or int(passed_matches[-1]) != EXPECTED_BACKEND_TESTS:
        raise AssertionError(
            f"Backend test count mismatch: {passed_matches[-1] if passed_matches else 'missing'} "
            f"!= {EXPECTED_BACKEND_TESTS}"
        )

    flutter_executed = False
    web_build_executed = False
    windows_build_executed = False
    if args.with_flutter:
        flutter = shutil.which("flutter")
        if flutter is None:
            raise AssertionError("flutter executable is required for --with-flutter")
        flutter_output = run_capture(
            [flutter, "test", "--reporter", "compact"], cwd=ROOT / "app"
        )
        plain_flutter_output = re.sub(r"\x1b\[[0-9;?]*[ -/]*[@-~]", "", flutter_output)
        flutter_matches = re.findall(
            r"\+(\d+)(?:\s+-\d+)?:\s+All tests passed!",
            plain_flutter_output.replace("\r", "\n"),
        )
        if not flutter_matches or int(flutter_matches[-1]) != EXPECTED_FLUTTER_TESTS:
            raise AssertionError(
                f"Flutter test count mismatch: "
                f"{flutter_matches[-1] if flutter_matches else 'missing'} "
                f"!= {EXPECTED_FLUTTER_TESTS}"
            )
        flutter_executed = True
        if args.with_builds:
            run([flutter, "build", "web"], cwd=ROOT / "app")
            web_build_executed = True
            run([flutter, "build", "windows"], cwd=ROOT / "app")
            windows_build_executed = True

    if snapshot_tree("backend/local_data") != local_data_before:
        raise AssertionError("R-1b gate must not create or modify backend/local_data")
    if snapshot_tree("release") != release_before:
        raise AssertionError("R-1b gate must not create or modify release artifacts")

    print("v210_release_readiness_status: completed-accepted")
    print("v210_release_readiness_completed_small_commit: R-1b")
    print("v210_release_readiness_current_small_commit: R-1c")
    print("v210_release_readiness_parent_phase: R-1-current-not-completed")
    print(f"v210_release_readiness_backend_version: {EXPECTED_BACKEND_VERSION}")
    print(f"v210_release_readiness_flutter_version: {EXPECTED_FLUTTER_VERSION}")
    print("v210_release_readiness_accepted_r1b_aggregate_checks: 18")
    print(f"v210_release_readiness_aggregate_checks: {len(AGGREGATE_CHECKS)}")
    print("v210_release_readiness_r1c_status: implemented-not-accepted")
    print("v210_release_readiness_v20x_compatibility_gate: true")
    print(f"v210_release_readiness_expected_backend_tests: {EXPECTED_BACKEND_TESTS}")
    print(f"v210_release_readiness_expected_flutter_tests: {EXPECTED_FLUTTER_TESTS}")
    print(f"v210_release_readiness_flutter_executed: {str(flutter_executed).lower()}")
    print(f"v210_release_readiness_web_build_executed: {str(web_build_executed).lower()}")
    print(f"v210_release_readiness_windows_build_executed: {str(windows_build_executed).lower()}")
    print("v210_release_readiness_fixed_zip_built: false")
    print("v210_release_readiness_tag_created: false")
    print("v210_release_readiness_github_release_created: false")
    print("[v210-release-readiness-check] OK")


if __name__ == "__main__":
    main()
