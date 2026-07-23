"""Validate the M-9 v2.0.1 patch-release preparation and fixed artifact.

Portable default mode validates the committed release contract and reruns the
credential-free aggregate maintenance gate. ``--source-tree`` adds the strict
Git topology gate required before the one-time fixed-ZIP build. ``--release-zip``
inspects and tests the supplied ZIP as-is and never invokes a release builder.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_BACKEND_VERSION = "2.0.1"
EXPECTED_FLUTTER_VERSION = "2.0.1+2"
OFFICIAL_ORIGIN = re.compile(
    r"^(?:https://github\.com/|git@github\.com:)"
    r"murayan1982/daily-rhythm-companion-public(?:\.git)?$"
)
HISTORICAL_HASHES = {
    "docs/DRC_v200_goal_checklist_small_commit.md": (
        "4c043837986c626c6fc44e4f84f73b019b2c8c21da7531a3f029554006b7eb63"
    ),
    "release_notes/v2.0.0.md": (
        "d2e13041ae51b9fef330a01a0d9124ccbfb6fb0850a0c2a29966baf96be3417b"
    ),
}
REQUIRED_PATCH_FILES = {
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v20x_maintenance_checklist.md",
    "docs/v20x_patch_release.md",
    "docs/v201_patch_release_record.md",
    "release_notes/v2.0.1.md",
    "build_v201_fixed_release_zip_from_head.ps1",
    "scripts/check_v20x_patch_release.py",
    "scripts/check_v20x_maintenance_readiness.py",
    "scripts/check_release_package.py",
    "backend/app/version.py",
    "app/pubspec.yaml",
}


def read(relative: str, *, root: Path = ROOT) -> str:
    path = root / relative
    if not path.is_file():
        raise AssertionError(f"Missing required file: {relative}")
    return path.read_text(encoding="utf-8")


def require(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise AssertionError(f"Missing {label}: {needle!r}")


def reject(text: str, needle: str, label: str) -> None:
    if needle in text:
        raise AssertionError(f"Unexpected {label}: {needle!r}")


def normalized_sha256(data: bytes) -> str:
    return sha256(data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run(command: list[str], *, cwd: Path = ROOT) -> None:
    subprocess.run(command, cwd=cwd, check=True)


def capture(command: list[str], *, cwd: Path = ROOT) -> str:
    completed = subprocess.run(
        command,
        cwd=cwd,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return completed.stdout.strip()


def snapshot_local_data(root: Path = ROOT) -> tuple[tuple[str, int, int], ...] | None:
    local_data = root / "backend/local_data"
    if not local_data.exists():
        return None
    entries: list[tuple[str, int, int]] = []
    for path in sorted(local_data.rglob("*")):
        stat = path.lstat()
        entries.append(
            (path.relative_to(local_data).as_posix(), stat.st_size, stat.st_mtime_ns)
        )
    return tuple(entries)


def assert_historical_files(*, root: Path = ROOT) -> None:
    for relative, expected in HISTORICAL_HASHES.items():
        path = root / relative
        if not path.is_file():
            raise AssertionError(f"Missing historical release record: {relative}")
        actual = normalized_sha256(path.read_bytes())
        if actual != expected:
            raise AssertionError(
                f"Historical release record changed: {relative}: {actual} != {expected}"
            )


def verify_contract(*, root: Path = ROOT) -> None:
    checklist = read("docs/DRC_v20x_maintenance_checklist.md", root=root)
    require(
        checklist,
        "Current small commit: M-9 (patch release preparation)",
        "active M-9 marker",
    )
    for number in range(1, 9):
        marker = f"M-{number}"
        if marker not in checklist:
            raise AssertionError(f"Missing maintenance task marker: {marker}")
    m8 = checklist.split("## M-8", 1)[1].split("\n## M-9 — Patch release", 1)[0]
    require(m8, "Status: COMPLETED / ACCEPTED", "M-8 accepted state")
    require(m8, "M-9 remains PLANNED", "M-8 historical non-advancement record")
    m9 = checklist.split("\n## M-9 — Patch release", 1)[1].split(
        "# Future-version boundary", 1
    )[0]
    require(m9, "Status: CURRENT / NOT_COMPLETED", "M-9 current state")
    require(m9, "release: prepare v2.0.1 fixed ZIP gate", "M-9 commit title")
    require(m9, "Do not create the fixed ZIP in this preparation commit", "M-9 stop rule")
    reject(m9, "Status: COMPLETED", "M-9 early completion")

    for relative in REQUIRED_PATCH_FILES:
        if not (root / relative).is_file():
            raise AssertionError(f"Missing M-9 release file: {relative}")

    for relative in ("README.md", "roadmap.md", "tasklist.md", "scripts/README.md"):
        text = read(relative, root=root)
        require(text, "M-9", f"{relative} M-9 status")
        require(text, "CURRENT", f"{relative} current state")
        require(text, "v2.0.1", f"{relative} patch version")

    release_policy = read("docs/v20x_patch_release.md", root=root)
    for needle in (
        "Status: CURRENT / NOT_COMPLETED",
        "--source-tree --with-flutter",
        "invokes build_release.bat release exactly once",
        "verify the same file",
        "does not verify, rebuild, tag, or publish the artifact",
        "Do not create `DRC_v2.0.1`",
    ):
        require(release_policy, needle, "M-9 release policy")

    release_record = read("docs/v201_patch_release_record.md", root=root)
    for needle in (
        "Status: PREPARED / NOT_RELEASED",
        "Release tag: NOT_CREATED",
        "Fixed release ZIP: NOT_BUILT",
        "Fixed release ZIP SHA-256: NOT_RECORDED",
        "The final ZIP SHA-256 is not embedded into the ZIP",
    ):
        require(release_record, needle, "v2.0.1 release record")

    release_notes = read("release_notes/v2.0.1.md", root=root)
    for needle in (
        "Status: PREPARED / NOT_RELEASED",
        "v2.0.1 is a maintenance and regression-hardening patch",
        "fixed release ZIP: not built",
        "annotated tag / GitHub Release: not created",
        "DRC_v2.0.0",
    ):
        require(release_notes, needle, "v2.0.1 release notes")
    reject(release_notes, "Status: RELEASED", "early v2.0.1 release claim")

    backend_version = read("backend/app/version.py", root=root)
    require(
        backend_version,
        f'APP_VERSION = "{EXPECTED_BACKEND_VERSION}"',
        "backend patch version",
    )
    flutter_pubspec = read("app/pubspec.yaml", root=root)
    require(
        flutter_pubspec,
        f"version: {EXPECTED_FLUTTER_VERSION}",
        "Flutter patch version",
    )

    builder = read("build_v201_fixed_release_zip_from_head.ps1", root=root)
    for needle in (
        '$buildInvocationCount = 0',
        'git status --porcelain --untracked-files=all',
        'refs/remotes/origin/main',
        'git worktree add --detach',
        'build_release.bat release',
        '$buildInvocationCount++',
        '$buildInvocationCount -ne 1',
        'Get-FileHash -LiteralPath $destinationPath -Algorithm SHA256',
        'verification_status: not-run',
        'next_action: verify-this-same-zip-without-rebuilding',
    ):
        require(builder, needle, "one-time fixed-ZIP builder contract")

    assert_historical_files(root=root)


def verify_git_source() -> tuple[str, str]:
    git_root = Path(capture(["git", "rev-parse", "--show-toplevel"])).resolve()
    if git_root != ROOT.resolve():
        raise AssertionError(f"Repository root mismatch: {git_root} != {ROOT.resolve()}")

    dirty = capture(["git", "status", "--porcelain", "--untracked-files=all"])
    if dirty:
        raise AssertionError(
            "Working tree contains tracked or untracked changes; commit or remove them first"
        )

    branch = capture(["git", "branch", "--show-current"])
    if branch != "main":
        raise AssertionError(f"Patch release source branch must be main, got {branch!r}")

    origin = capture(["git", "remote", "get-url", "origin"])
    if not OFFICIAL_ORIGIN.fullmatch(origin):
        raise AssertionError(f"Origin is not the official Public repository: {origin}")

    head = capture(["git", "rev-parse", "HEAD"])
    origin_main = capture(["git", "rev-parse", "refs/remotes/origin/main"])
    if head != origin_main:
        raise AssertionError(f"HEAD does not match origin/main: {head} != {origin_main}")

    root_commits = [
        line
        for line in capture(["git", "rev-list", "--max-parents=0", "HEAD"]).splitlines()
        if line
    ]
    if len(root_commits) != 1:
        raise AssertionError(
            f"Official Public repository must have one root commit, got {len(root_commits)}"
        )

    baseline_tags = capture(["git", "tag", "--list", "DRC_v2.0.0"])
    if baseline_tags != "DRC_v2.0.0":
        raise AssertionError("Annotated baseline tag DRC_v2.0.0 is required")
    baseline_type = capture(["git", "cat-file", "-t", "DRC_v2.0.0"])
    if baseline_type != "tag":
        raise AssertionError("DRC_v2.0.0 must remain an annotated tag")

    patch_tag = capture(["git", "tag", "--list", "DRC_v2.0.1"])
    if patch_tag:
        raise AssertionError("DRC_v2.0.1 already exists; refusing pre-release source gate")

    return head, origin_main


def run_aggregate(*, root: Path, with_flutter: bool) -> None:
    before = snapshot_local_data(root)
    command = [sys.executable, "scripts/check_v20x_maintenance_readiness.py"]
    if with_flutter:
        command.append("--with-flutter")
    run(command, cwd=root)
    if snapshot_local_data(root) != before:
        raise AssertionError("Release gate must not create or modify backend/local_data")


def _strip_package_root(name: str) -> str:
    parts = PurePosixPath(name.replace("\\", "/")).parts
    if parts and parts[0] == "DailyRhythmCompanion":
        return "/".join(parts[1:])
    return "/".join(parts)


def verify_release_zip(
    zip_path: Path,
    *,
    with_flutter: bool,
    expected_sha256: str | None,
    expected_source_head: str | None,
) -> tuple[str, int]:
    if not zip_path.is_file():
        raise AssertionError(f"Release ZIP not found: {zip_path}")

    before_stat = zip_path.stat()
    before_sha = file_sha256(zip_path)
    if expected_sha256 and before_sha.lower() != expected_sha256.lower():
        raise AssertionError(
            f"Release ZIP SHA-256 mismatch: {before_sha} != {expected_sha256.lower()}"
        )

    if expected_source_head:
        actual_head = capture(["git", "rev-parse", "HEAD"])
        if actual_head != expected_source_head:
            raise AssertionError(
                f"Current source HEAD does not match expected source HEAD: "
                f"{actual_head} != {expected_source_head}"
            )

    run([sys.executable, "scripts/check_release_package.py", str(zip_path)])

    with zipfile.ZipFile(zip_path) as package:
        bad_member = package.testzip()
        if bad_member is not None:
            raise AssertionError(f"ZIP CRC validation failed: {bad_member}")

        member_map: dict[str, str] = {}
        for original_name in package.namelist():
            normalized_name = original_name.replace("\\", "/")
            if normalized_name in member_map:
                raise AssertionError(
                    f"Duplicate normalized ZIP member: {normalized_name}"
                )
            member_map[normalized_name] = original_name

        file_names = list(member_map)
        roots = {PurePosixPath(name).parts[0] for name in file_names if name.strip("/")}
        if roots != {"DailyRhythmCompanion"}:
            raise AssertionError(f"Unexpected release ZIP package roots: {sorted(roots)}")

        normalized_files = {
            _strip_package_root(name)
            for name in file_names
            if name and not name.endswith("/")
        }
        missing = sorted(REQUIRED_PATCH_FILES - normalized_files)
        if missing:
            raise AssertionError(f"Release ZIP is missing M-9 files: {missing}")

        def package_bytes(relative: str) -> bytes:
            normalized_member = f"DailyRhythmCompanion/{relative}"
            original_member = member_map.get(normalized_member)
            if original_member is None:
                raise AssertionError(f"Missing ZIP member: {normalized_member}")
            return package.read(original_member)

        backend_version = package_bytes("backend/app/version.py").decode("utf-8")
        require(
            backend_version,
            f'APP_VERSION = "{EXPECTED_BACKEND_VERSION}"',
            "ZIP backend version",
        )
        flutter_pubspec = package_bytes("app/pubspec.yaml").decode("utf-8")
        require(
            flutter_pubspec,
            f"version: {EXPECTED_FLUTTER_VERSION}",
            "ZIP Flutter version",
        )
        zip_checklist = package_bytes(
            "docs/DRC_v20x_maintenance_checklist.md"
        ).decode("utf-8")
        require(
            zip_checklist,
            "Status: CURRENT / NOT_COMPLETED",
            "ZIP M-9 not-completed state",
        )
        zip_notes = package_bytes("release_notes/v2.0.1.md").decode("utf-8")
        require(
            zip_notes,
            "Status: PREPARED / NOT_RELEASED",
            "ZIP release-note preparation state",
        )
        for relative, expected in HISTORICAL_HASHES.items():
            actual = normalized_sha256(package_bytes(relative))
            if actual != expected:
                raise AssertionError(
                    f"Historical ZIP record changed: {relative}: {actual} != {expected}"
                )

    with tempfile.TemporaryDirectory(prefix="drc_v201_fixed_zip_") as temp_dir:
        extraction_root = Path(temp_dir)
        with zipfile.ZipFile(zip_path) as package:
            for info in package.infolist():
                normalized_name = info.filename.replace("\\", "/")
                pure_path = PurePosixPath(normalized_name)
                if pure_path.is_absolute() or ".." in pure_path.parts:
                    raise AssertionError(
                        f"Unsafe ZIP extraction member: {info.filename}"
                    )
                target = extraction_root.joinpath(*pure_path.parts)
                if info.is_dir() or normalized_name.endswith("/"):
                    target.mkdir(parents=True, exist_ok=True)
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                with package.open(info) as source, target.open("wb") as destination:
                    shutil.copyfileobj(source, destination)
        source_root = extraction_root / "DailyRhythmCompanion"
        verify_contract(root=source_root)
        run_aggregate(root=source_root, with_flutter=with_flutter)

    after_stat = zip_path.stat()
    after_sha = file_sha256(zip_path)
    if (
        after_stat.st_size != before_stat.st_size
        or after_stat.st_mtime_ns != before_stat.st_mtime_ns
        or after_sha != before_sha
    ):
        raise AssertionError("The supplied fixed ZIP changed during verification")

    return before_sha, before_stat.st_size


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source-tree",
        action="store_true",
        help="require clean official Public main with HEAD equal to origin/main",
    )
    parser.add_argument(
        "--release-zip",
        type=Path,
        help="verify this exact fixed release ZIP without rebuilding it",
    )
    parser.add_argument(
        "--expected-sha256",
        help="require the supplied release ZIP to match this SHA-256",
    )
    parser.add_argument(
        "--expected-source-head",
        help="require the current Git HEAD to match the builder-recorded source HEAD",
    )
    parser.add_argument(
        "--with-flutter",
        action="store_true",
        help="include Flutter test in source and extracted-ZIP gates",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    verify_contract()

    source_head = "not-required"
    origin_main = "not-required"
    if args.source_tree:
        source_head, origin_main = verify_git_source()
        run_aggregate(root=ROOT, with_flutter=args.with_flutter)
    elif args.release_zip is None:
        run_aggregate(root=ROOT, with_flutter=args.with_flutter)

    zip_sha = "not-run"
    zip_size: int | str = "not-run"
    if args.release_zip is not None:
        zip_sha, zip_size = verify_release_zip(
            args.release_zip.resolve(),
            with_flutter=args.with_flutter,
            expected_sha256=args.expected_sha256,
            expected_source_head=args.expected_source_head,
        )

    print("v20x_patch_release_status: m9-current-not-completed")
    print(f"v20x_patch_release_source_tree_gate: {args.source_tree}")
    print(f"v20x_patch_release_source_head: {source_head}")
    print(f"v20x_patch_release_origin_main_head: {origin_main}")
    print(f"v20x_patch_release_flutter_executed: {args.with_flutter}")
    print(f"v20x_patch_release_same_zip_verified: {args.release_zip is not None}")
    print(f"v20x_patch_release_zip_size_bytes: {zip_size}")
    print(f"v20x_patch_release_zip_sha256: {zip_sha}")
    print("v20x_patch_release_builder_invoked: False")
    print("v20x_patch_release_tag_created: False")
    print("v20x_patch_release_github_release_created: False")
    print("[v20x-patch-release-check] OK")


if __name__ == "__main__":
    main()
