"""Validate the accepted R-1a release/readiness inventory.

This source-tree-only check preserves the accepted R-1a snapshot while allowing
the accepted R-1b candidate metadata, accepted R-1c evidence record, accepted R-1d artifact record, and accepted R-1e publication record. It
never reads credentials, executes providers, builds a ZIP, or inspects tags.
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

R1A_FROZEN_RELEASE_SURFACE_HASHES = {
    "build_release.bat": "1e939e31187b58efe7c5987fd763dba733ff706ad864a14cf945e641a9f23c1a",
    "build_v201_fixed_release_zip_from_head.ps1": "89d3fe3e39484b36272d9c8ec8499276ffe305ec844a87cca5d90fef8931ab1b",
    "scripts/check_release_package.py": "57d6e4a6fae67bbc2e8c9e9b5c710f4d951866ad4007606075c244c6a29d212b",
    "scripts/check_v20x_maintenance_readiness.py": "ea27a4ee8b415317d7d1cedef3182d7365cbecaf86d68b5dd21d393c23e92160",
    "scripts/check_v20x_patch_release.py": "e4eefc408abcbccc2651c1113ae8264269cce1d77525067173e0a06a7ef685cf",
    "docs/v20x_maintenance_readiness.md": "980b7a5b84aaa1faca801ed79d7cc66cbea7d79b1dd913dced4e5f58d99dabd3",
    ".gitignore": "740b4903072fef306fba8880bc9f8d57ac2055ed38168314b6834ce0eec0c8a3",
}

REQUIRED_R1B_FILES = (
    "scripts/check_v210_release_readiness.py",
    "docs/v210_release_readiness.md",
    "docs/v210_release_record.md",
    "release_notes/v2.1.0.md",
)

REQUIRED_R1C_FILES = (
    "scripts/check_v210_final_smartphone_web_evidence.py",
    "docs/v210_final_smartphone_web_evidence.md",
    "docs/operator_evidence_templates/v210_final_smartphone_web_evidence_r1c.example.json",
)

REQUIRED_R1D_FILES = (
    "build_v210_fixed_release_zip_from_head.ps1",
    "scripts/check_v210_fixed_release_zip.py",
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
        require(source, "COMPLETED / ACCEPTED", f"{label} R-1a accepted state")
        require(source, "R-1b", f"{label} R-1b marker")
        require(source, "COMPLETED / ACCEPTED", f"{label} R-1b accepted state")
        require(source, "R-1c", f"{label} R-1c marker")
        require(source, "COMPLETED / ACCEPTED", f"{label} R-1c accepted state")
        require(source, "R-1d", f"{label} R-1d marker")
        require(source, "COMPLETED / ACCEPTED", f"{label} R-1d accepted state")
        require(source, "R-1e", f"{label} R-1e marker")
        require(source, "COMPLETED / ACCEPTED", f"{label} R-1e accepted state")

    require(checklist, "Current small commit: none", "completed small-commit state")
    require(checklist, "Current implementation state: COMPLETED / ACCEPTED", "R-1e implementation state")
    require(checklist, "R-1  COMPLETED / ACCEPTED", "parent R-1 state")
    require(checklist, "R-1a  COMPLETED / ACCEPTED", "R-1a accepted queue state")
    require(checklist, "R-1b  COMPLETED / ACCEPTED", "R-1b accepted queue state")
    require(checklist, "R-1c  COMPLETED / ACCEPTED", "R-1c accepted queue state")
    require(checklist, "R-1d  COMPLETED / ACCEPTED", "R-1d accepted queue state")
    require(checklist, "R-1e  COMPLETED / ACCEPTED", "R-1e accepted queue state")
    require(inventory, "Backend pytest: 110 passed", "R-1a Backend snapshot")
    require(inventory, "Flutter test: 103 passed", "R-1a Flutter snapshot")
    require(inventory, "backend APP_VERSION: 2.0.1", "R-1a Backend metadata snapshot")
    require(inventory, "Flutter package version: 2.0.1+2", "R-1a Flutter metadata snapshot")
    require(inventory, "implementation commit: dbc84db", "accepted R-1a implementation commit")
    require(inventory, "all check_v210_*.py: 18 / 18 passed", "accepted R-1a check count")
    require(inventory, "explicit operator approval: received", "R-1a operator acceptance")
    require(inventory, "Accepted R-1b candidate transition", "accepted R-1b transition marker")
    require(inventory, "Accepted R-1c evidence transition", "accepted R-1c transition marker")
    require(inventory, "Accepted R-1d artifact transition", "accepted R-1d transition marker")
    require(inventory, "accepted release source HEAD: 6e7af31f85eb6ee7887df3e184ac6a58142d6fec", "accepted R-1d source")
    require(inventory, "Accepted R-1e publication transition", "accepted R-1e transition marker")
    require(read("docs/v210_release_record.md"), "Status: RELEASED / ACCEPTED", "released v2.1.0 record")

    require(read("backend/app/version.py"), 'APP_VERSION = "2.1.0"', "active R-1b Backend candidate")
    require(read("app/pubspec.yaml"), "version: 2.1.0+3", "active R-1b Flutter candidate")

    for relative in REQUIRED_R1B_FILES:
        if not (ROOT / relative).is_file():
            raise AssertionError(f"Missing separately checked R-1b file: {relative}")
    for relative in REQUIRED_R1C_FILES:
        if not (ROOT / relative).is_file():
            raise AssertionError(f"Missing separately checked R-1c file: {relative}")
    for relative in REQUIRED_R1D_FILES:
        if not (ROOT / relative).is_file():
            raise AssertionError(f"Missing separately checked R-1d implementation: {relative}")

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

    assert_hashes(PROTECTED_HISTORICAL_HASHES, "Protected historical release record")
    assert_hashes(R1A_FROZEN_RELEASE_SURFACE_HASHES, "R-1a frozen release surface")

    for relative in (
        "README.md",
        "roadmap.md",
        "tasklist.md",
        "scripts/README.md",
        "docs/DRC_v210_goal_checklist_small_commit.md",
        "docs/v210_release_readiness_current_behavior_inventory.md",
        "docs/v210_release_readiness.md",
        "docs/v210_release_record.md",
        "release_notes/v2.1.0.md",
        "docs/v210_final_smartphone_web_evidence.md",
        "docs/operator_evidence_templates/v210_final_smartphone_web_evidence_r1c.example.json",
        "build_v210_fixed_release_zip_from_head.ps1",
        "scripts/check_v210_fixed_release_zip.py",
    ):
        assert_no_sensitive_values(relative, read(relative))

    print("v210_release_readiness_inventory_status: completed-accepted")
    print("v210_release_readiness_inventory_completed_small_commit: R-1a")
    print("v210_release_readiness_inventory_current_small_commit: none")
    print("v210_release_readiness_inventory_parent_phase: R-1-completed-accepted")
    print("v210_release_readiness_inventory_snapshot_backend_version: 2.0.1")
    print("v210_release_readiness_inventory_snapshot_flutter_version: 2.0.1+2")
    print("v210_release_readiness_inventory_active_backend_version: 2.1.0")
    print("v210_release_readiness_inventory_active_flutter_version: 2.1.0+3")
    print("v210_release_readiness_inventory_backend_tests: 110")
    print("v210_release_readiness_inventory_flutter_tests: 103")
    print("v210_release_readiness_inventory_generic_package_builder: true")
    print("v210_release_readiness_inventory_generic_package_checker: true")
    print("v210_release_readiness_inventory_v210_aggregate_gate: true")
    print("v210_release_readiness_inventory_r1c_validator: true")
    print("v210_release_readiness_inventory_final_smartphone_web_aggregate: true")
    print("v210_release_readiness_inventory_r1d_implementation: true")
    print("v210_release_readiness_inventory_r1d_completed_accepted: true")
    print("v210_release_readiness_inventory_fixed_zip_built: true")
    print("v210_release_readiness_inventory_tag_created: true")
    print("v210_release_readiness_inventory_github_release_created: true")
    print("[v210-release-readiness-current-behavior-inventory-check] OK")


if __name__ == "__main__":
    main()
