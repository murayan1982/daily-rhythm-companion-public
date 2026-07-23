"""Run the current-main v2.0.x aggregate maintenance readiness gate.

The portable default is credential-free and does not require Flutter. Pass
``--with-flutter`` for the local full developer gate used for M-8 acceptance.
Historical release-evidence validators and release artifact work are excluded.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
HISTORICAL_HASHES = {
    "docs/DRC_v200_goal_checklist_small_commit.md": (
        "4c043837986c626c6fc44e4f84f73b019b2c8c21da7531a3f029554006b7eb63"
    ),
    "release_notes/v2.0.0.md": (
        "d2e13041ae51b9fef330a01a0d9124ccbfb6fb0850a0c2a29966baf96be3417b"
    ),
}
TERMINAL_MAINTENANCE_CHECK = "scripts/check_v20x_fitbit_current_state_contract.py"


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


def snapshot_local_data() -> tuple[tuple[str, int, int], ...] | None:
    local_data = ROOT / "backend/local_data"
    if not local_data.exists():
        return None
    entries: list[tuple[str, int, int]] = []
    for path in sorted(local_data.rglob("*")):
        stat = path.lstat()
        entries.append(
            (
                path.relative_to(local_data).as_posix(),
                stat.st_size,
                stat.st_mtime_ns,
            )
        )
    return tuple(entries)


def assert_historical_hashes() -> None:
    for relative, expected in HISTORICAL_HASHES.items():
        normalized = (
            (ROOT / relative)
            .read_bytes()
            .replace(b"\r\n", b"\n")
            .replace(b"\r", b"\n")
        )
        actual = sha256(normalized).hexdigest()
        if actual != expected:
            raise AssertionError(
                f"Historical release record changed: {relative}: {actual} != {expected}"
            )


def run(command: list[str], *, cwd: Path = ROOT) -> None:
    subprocess.run(command, cwd=cwd, check=True)


def verify_contract() -> None:
    checklist = read("docs/DRC_v20x_maintenance_checklist.md")
    require(
        checklist,
        "Current small commit: none (M-8 accepted; M-9 planned)",
        "M-8 accepted state",
    )
    m7 = checklist.split("## M-7", 1)[1].split("## M-8", 1)[0]
    require(m7, "Status: COMPLETED / ACCEPTED", "M-7 accepted state")
    m8 = checklist.split("## M-8", 1)[1].split("\n## M-9 — Patch release", 1)[0]
    require(m8, "Status: COMPLETED / ACCEPTED", "M-8 accepted state")
    require(m8, "M-8 was accepted on 2026-07-23", "M-8 acceptance record")
    require(m8, "M-9 remains PLANNED", "M-9 non-advancement")
    m9 = checklist.split("\n## M-9 — Patch release", 1)[1].split("# Future-version boundary", 1)[0]
    require(m9, "Status: PLANNED", "M-9 planned state")
    reject(m9, "Status: COMPLETED", "M-9 early completion")

    documentation = read("docs/v20x_maintenance_readiness.md")
    for needle in (
        "Status: COMPLETED / ACCEPTED",
        "M-8 was accepted on 2026-07-23",
        "python scripts\\check_v20x_maintenance_readiness.py --with-flutter",
        "Historical v2.0.0 validators remain available",
        "M-9 may become CURRENT only after",
        "builds one fixed ZIP",
        "verifies that same ZIP without rebuilding it",
        "M-9 remains PLANNED",
    ):
        require(documentation, needle, "M-8 documentation")

    script_readme = read("scripts/README.md")
    require(
        script_readme,
        r"python scripts\check_v20x_maintenance_readiness.py --with-flutter",
        "scripts README aggregate command",
    )

    if TERMINAL_MAINTENANCE_CHECK != "scripts/check_v20x_fitbit_current_state_contract.py":
        raise AssertionError("M-8 must aggregate through the accepted M-7 terminal check")
    if any(fragment in TERMINAL_MAINTENANCE_CHECK for fragment in ("v200", "release", "smoke")):
        raise AssertionError("Historical release validators must not be aggregate children")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--with-flutter",
        action="store_true",
        help="also run flutter test from app/",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    local_data_before = snapshot_local_data()

    verify_contract()
    assert_historical_hashes()

    run([sys.executable, "-m", "compileall", "-q", "backend", "scripts"])
    run([sys.executable, str(ROOT / TERMINAL_MAINTENANCE_CHECK)])
    run([sys.executable, "-m", "pytest", "-q", "backend/tests"])

    if args.with_flutter:
        flutter = shutil.which("flutter")
        if flutter is None:
            raise AssertionError("flutter executable is required for --with-flutter")
        run([flutter, "test"], cwd=ROOT / "app")

    if snapshot_local_data() != local_data_before:
        raise AssertionError(
            "Normal M-8 checks must not create or modify backend/local_data"
        )

    print("v20x_maintenance_readiness_status: m8-completed-accepted")
    print("v20x_maintenance_readiness_m1_through_m7_aggregated: True")
    print("v20x_maintenance_readiness_historical_release_validators_invoked: False")
    print("v20x_maintenance_readiness_backend_pytest_required: True")
    print(f"v20x_maintenance_readiness_flutter_executed: {args.with_flutter}")
    print("v20x_maintenance_readiness_m9_entry_contract_defined: True")
    print("v20x_maintenance_readiness_release_created: False")
    print("[v20x-maintenance-readiness-check] OK")


if __name__ == "__main__":
    main()
