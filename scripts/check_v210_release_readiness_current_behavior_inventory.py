"""Validate the R-1a release/readiness current behavior inventory.

This source-tree-only check freezes the accepted pre-release implementation
surface without reading credentials, accessing providers, inspecting Git tags,
calling GitHub, building a ZIP, or modifying release artifacts.
"""

from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

PROTECTED_HISTORICAL_HASHES = {
    "docs/DRC_v200_goal_checklist_small_commit.md": "4c043837986c626c6fc44e4f84f73b019b2c8c21da7531a3f029554006b7eb63",
    "release_notes/v2.0.0.md": "d2e13041ae51b9fef330a01a0d9124ccbfb6fb0850a0c2a29966baf96be3417b",
    "docs/DRC_v20x_maintenance_checklist.md": "02e6e2e49a54a5c1360ee5d95d6bed2314ab42aec5dce911f3ed72867c4d46f2",
    "docs/v20x_patch_release.md": "eb6ae9770a4611a463ddb227a1dd8ce8816ee310cddaed327a02404a34a7935d",
    "docs/v201_patch_release_record.md": "9b724a6c5c7ffffdb3e699ad010ff75148ec4549b6cf2d940b44e62e161140bd",
    "release_notes/v2.0.1.md": "1e90c85e51ef848b64bddaa73f1f40c659457935e30831027310ea95fc94656b",
    "build_v200_final_fixed_release_zip_from_head.ps1": "4a4439341b0ad00d56b50038993631fcb48fb417cd0f0648dc3abc5e72d3b360",
}

R1A_RELEASE_SURFACE_HASHES = {
    "build_release.bat": "1e939e31187b58efe7c5987fd763dba733ff706ad864a14cf945e641a9f23c1a",
    "build_v201_fixed_release_zip_from_head.ps1": "89d3fe3e39484b36272d9c8ec8499276ffe305ec844a87cca5d90fef8931ab1b",
    "scripts/check_release_package.py": "56b5550b2d7145c3bfc4d9ff4370499df261c9f629ba551820588d859fbcff50",
    "scripts/check_v20x_maintenance_readiness.py": "ea27a4ee8b415317d7d1cedef3182d7365cbecaf86d68b5dd21d393c23e92160",
    "scripts/check_v20x_patch_release.py": "e4eefc408abcbccc2651c1113ae8264269cce1d77525067173e0a06a7ef685cf",
    "docs/v20x_maintenance_readiness.md": "980b7a5b84aaa1faca801ed79d7cc66cbea7d79b1dd913dced4e5f58d99dabd3",
    "backend/app/version.py": "ecc2c3e5218f0592bc95e03a59e7183f39fa84253331a492eb5d47eaddd2c2e3",
    "app/pubspec.yaml": "78ea66a2c1c4f96deced1063bf9f00369e7507c415e87d769a556b392dec4756",
    ".gitignore": "740b4903072fef306fba8880bc9f8d57ac2055ed38168314b6834ce0eec0c8a3",
}

MISSING_V210_RELEASE_FILES = (
    "build_v210_fixed_release_zip_from_head.ps1",
    "scripts/check_v210_release_readiness.py",
    "scripts/check_v210_fixed_release_zip.py",
    "docs/v210_release_readiness.md",
    "docs/v210_release_record.md",
    "release_notes/v2.1.0.md",
)


def read(relative: str) -> str:
    path = ROOT / relative
    if not path.is_file():
        raise AssertionError(f"Missing required file: {relative}")
    return path.read_text(encoding="utf-8")


def normalized_hash(relative: str) -> str:
    data = (ROOT / relative).read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return sha256(data).hexdigest()


def require(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise AssertionError(f"Missing {label}: {needle!r}")


def forbid(text: str, needle: str, label: str) -> None:
    if needle in text:
        raise AssertionError(f"Unexpected {label}: {needle!r}")


def assert_hashes(expected: dict[str, str], label: str) -> None:
    for relative, digest in expected.items():
        actual = normalized_hash(relative)
        if actual != digest:
            raise AssertionError(f"{label} changed: {relative}: {actual} != {digest}")


def assert_no_sensitive_values(relative: str, text: str) -> None:
    patterns = (
        r"sk-[A-Za-z0-9_\-]{12,}",
        r"xai-[A-Za-z0-9_\-]{12,}",
        r"AIza[0-9A-Za-z_\-]{20,}",
        r"Bearer\s+[A-Za-z0-9_\-.]{16,}",
        r"[A-Za-z]:\\Users\\[^<\r\n]+",
        r"192\.168\.\d{1,3}\.\d{1,3}",
    )
    for pattern in patterns:
        if re.search(pattern, text, flags=re.IGNORECASE):
            raise AssertionError(f"Sensitive-looking value in {relative}: {pattern}")


def main() -> None:
    inventory = read("docs/v210_release_readiness_current_behavior_inventory.md")
    checklist = read("docs/DRC_v210_goal_checklist_small_commit.md")
    readme = read("README.md")
    roadmap = read("roadmap.md")
    tasklist = read("tasklist.md")
    scripts_readme = read("scripts/README.md")

    for source, label in (
        (inventory, "inventory"),
        (checklist, "checklist"),
        (readme, "README"),
        (roadmap, "roadmap"),
        (tasklist, "tasklist"),
        (scripts_readme, "scripts README"),
    ):
        require(source, "R-1a", f"{label} R-1a marker")
        require(source, "IMPLEMENTED / NOT_ACCEPTED", f"{label} R-1a state")
        require(source, "R-1b", f"{label} R-1b marker")
        require(source, "PLANNED", f"{label} later-state marker")

    require(checklist, "Current small commit: R-1a", "current small commit")
    require(checklist, "R-1  CURRENT / NOT_COMPLETED", "parent R-1 state")
    require(checklist, "R-1a  CURRENT / NOT_COMPLETED", "R-1a queue state")
    require(checklist, "R-1e  PLANNED", "R-1e queue state")
    require(checklist, "V-1  COMPLETED / ACCEPTED", "accepted V-1 state")
    require(inventory, "Backend pytest: 110 passed", "Backend baseline")
    require(inventory, "Flutter test: 103 passed", "Flutter baseline")
    require(inventory, "W-5b2", "wearable smartphone evidence")
    require(inventory, "T-1c", "TTS smartphone evidence")
    require(inventory, "no final integrated smartphone Web evidence aggregate", "missing R-1 evidence")

    backend_version = read("backend/app/version.py")
    flutter_pubspec = read("app/pubspec.yaml")
    require(backend_version, 'APP_VERSION = "2.0.1"', "current backend version")
    require(flutter_pubspec, "version: 2.0.1+2", "current Flutter version")
    forbid(backend_version, 'APP_VERSION = "2.1.0"', "early backend release version")
    forbid(flutter_pubspec, "version: 2.1.0", "early Flutter release version")

    builder = read("build_release.bat")
    for marker in (
        "DENYLIST_PACKAGE_BUILDER_VERSION=v7-release-surface-cleanup",
        "DENYLIST_PACKAGE_BUILDER_HARDENING=v8-real-tts-secret-hygiene",
        "DENYLIST_PACKAGE_BUILDER_HARDENING=v9-committed-head-worktree-git-file",
        'set "RELEASE_DIR=%ROOT_DIR%release"',
        'set "PACKAGE_ROOT_NAME=DailyRhythmCompanion"',
        '"*.local.env"',
        '"operator_evidence"',
        '"*.zip"',
    ):
        require(builder, marker, "generic builder marker")

    package_check = read("scripts/check_release_package.py")
    for marker in (
        "BLOCKED_BASENAMES",
        "BLOCKED_PARTS",
        "SENSITIVE_TEXT_PATTERNS",
        "private Windows user path",
        "private LAN IP literal",
        "non-placeholder sensitive assignment",
        "[release-package-check] OK",
    ):
        require(package_check, marker, "generic package checker marker")

    v201_builder = read("build_v201_fixed_release_zip_from_head.ps1")
    for marker in (
        "official v2.0.1 fixed ZIP",
        'git status --porcelain --untracked-files=all',
        'refs/remotes/origin/main',
        'git worktree add --detach',
        'build_release.bat release',
        '$buildInvocationCount -ne 1',
        'Get-FileHash -LiteralPath $destinationPath -Algorithm SHA256',
        'verify-this-same-zip-without-rebuilding',
    ):
        require(v201_builder, marker, "historical v2.0.1 builder marker")

    v20x_release_check = read("scripts/check_v20x_patch_release.py")
    for marker in (
        'EXPECTED_BACKEND_VERSION = "2.0.1"',
        'EXPECTED_FLUTTER_VERSION = "2.0.1+2"',
        'DRC_v2.0.1',
        'RELEASE_SOURCE_HEAD',
        'RELEASE_ZIP_SHA256',
    ):
        require(v20x_release_check, marker, "historical v2.0.1 verifier marker")

    gitignore = read(".gitignore")
    for marker in ("operator_evidence/", "backend/local_data/", "release/"):
        require(gitignore, marker, "Git exclusion marker")

    for relative in MISSING_V210_RELEASE_FILES:
        if (ROOT / relative).exists():
            raise AssertionError(f"R-1a must not create v2.1.0 release implementation: {relative}")

    assert_hashes(PROTECTED_HISTORICAL_HASHES, "Protected historical release record")
    assert_hashes(R1A_RELEASE_SURFACE_HASHES, "R-1a release surface")

    for relative in (
        "README.md",
        "roadmap.md",
        "tasklist.md",
        "scripts/README.md",
        "docs/DRC_v210_goal_checklist_small_commit.md",
        "docs/v210_release_readiness_current_behavior_inventory.md",
    ):
        assert_no_sensitive_values(relative, read(relative))

    print("v210_release_readiness_inventory_status: implemented-not-accepted")
    print("v210_release_readiness_inventory_current_small_commit: R-1a")
    print("v210_release_readiness_inventory_parent_phase: R-1-current-not-completed")
    print("v210_release_readiness_inventory_backend_version: 2.0.1")
    print("v210_release_readiness_inventory_flutter_version: 2.0.1+2")
    print("v210_release_readiness_inventory_backend_tests: 110")
    print("v210_release_readiness_inventory_flutter_tests: 103")
    print("v210_release_readiness_inventory_generic_package_builder: true")
    print("v210_release_readiness_inventory_generic_package_checker: true")
    print("v210_release_readiness_inventory_v210_aggregate_gate: false")
    print("v210_release_readiness_inventory_final_smartphone_web_aggregate: false")
    print("v210_release_readiness_inventory_fixed_zip_built: false")
    print("v210_release_readiness_inventory_tag_created: false")
    print("v210_release_readiness_inventory_github_release_created: false")
    print("v210_release_readiness_inventory_runtime_changed: false")
    print("v210_release_readiness_inventory_release_records_changed: false")
    print("[v210-release-readiness-current-behavior-inventory-check] OK")


if __name__ == "__main__":
    main()
