"""Validate the R-1d v2.1.0 one-time builder and exact same ZIP.

Default mode is source-only and artifact-free. ``--source-tree`` additionally
requires clean synchronized official Public main and runs the accepted v2.1.0
aggregate gate. ``--release-zip`` verifies one explicitly supplied fixed ZIP
without rebuilding it, then runs tests/builds from a safe temporary extraction.
No mode creates a tag or publishes a GitHub Release.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_BACKEND_VERSION = "2.1.0"
EXPECTED_FLUTTER_VERSION = "2.1.0+3"
EXPECTED_BACKEND_TESTS = 110
EXPECTED_FLUTTER_TESTS = 103
RELEASE_TAG = "DRC_v2.1.0"
ZIP_NAME_PATTERN = re.compile(
    r"^DailyRhythmCompanion_v2\.1\.0_\d{8}_\d{6}\.zip$"
)
OFFICIAL_ORIGIN = re.compile(
    r"^(?:https://github\.com/|git@github\.com:)"
    r"murayan1982/daily-rhythm-companion-public(?:\.git)?$"
)

REQUIRED_RELEASE_FILES = {
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "build_release.bat",
    "build_v210_fixed_release_zip_from_head.ps1",
    "scripts/check_release_package.py",
    "scripts/check_v210_fixed_release_zip.py",
    "scripts/check_v210_release_readiness.py",
    "scripts/check_v210_final_smartphone_web_evidence.py",
    "docs/DRC_v210_goal_checklist_small_commit.md",
    "docs/v210_release_readiness.md",
    "docs/v210_final_smartphone_web_evidence.md",
    "docs/v210_release_record.md",
    "release_notes/v2.1.0.md",
    "backend/app/version.py",
    "app/pubspec.yaml",
}

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
    "scripts/check_release_package.py": "57d6e4a6fae67bbc2e8c9e9b5c710f4d951866ad4007606075c244c6a29d212b",
    ".gitignore": "740b4903072fef306fba8880bc9f8d57ac2055ed38168314b6834ce0eec0c8a3",
}

PUBLIC_SAFE_FILES = (
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v210_goal_checklist_small_commit.md",
    "docs/v210_release_readiness_current_behavior_inventory.md",
    "docs/v210_release_readiness.md",
    "docs/v210_final_smartphone_web_evidence.md",
    "docs/v210_release_record.md",
    "release_notes/v2.1.0.md",
    "build_v210_fixed_release_zip_from_head.ps1",
    "scripts/check_v210_fixed_release_zip.py",
)


def read(relative: str, *, root: Path = ROOT) -> str:
    path = root / relative
    if not path.is_file():
        raise AssertionError(f"Missing required file: {relative}")
    return path.read_text(encoding="utf-8")


def require(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise AssertionError(f"Missing {label}: {needle!r}")


def forbid(text: str, needle: str, label: str) -> None:
    if needle in text:
        raise AssertionError(f"Unexpected {label}: {needle!r}")


def normalized_hash(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return sha256(data).hexdigest()


def file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


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


def assert_hashes(
    expected: dict[str, str],
    label: str,
    *,
    root: Path = ROOT,
) -> None:
    for relative, digest in expected.items():
        path = root / relative
        if not path.is_file():
            raise AssertionError(f"Missing {label}: {relative}")
        actual = normalized_hash(path)
        if actual != digest:
            raise AssertionError(f"{label} changed: {relative}: {actual} != {digest}")


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


def verify_contract(*, root: Path = ROOT) -> None:
    for relative in REQUIRED_RELEASE_FILES:
        if not (root / relative).is_file():
            raise AssertionError(f"Missing R-1d release file: {relative}")

    checklist = read("docs/DRC_v210_goal_checklist_small_commit.md", root=root)
    readme = read("README.md", root=root)
    roadmap = read("roadmap.md", root=root)
    tasklist = read("tasklist.md", root=root)
    scripts_readme = read("scripts/README.md", root=root)
    readiness = read("docs/v210_release_readiness.md", root=root)
    release_record = read("docs/v210_release_record.md", root=root)
    release_notes = read("release_notes/v2.1.0.md", root=root)

    for source, label in (
        (checklist, "checklist"),
        (readme, "README"),
        (roadmap, "roadmap"),
        (tasklist, "tasklist"),
        (scripts_readme, "scripts README"),
        (readiness, "release readiness"),
        (release_record, "release record"),
        (release_notes, "release notes"),
    ):
        require(source, "R-1c", f"{label} R-1c marker")
        require(source, "COMPLETED / ACCEPTED", f"{label} R-1c accepted state")
        require(source, "R-1d", f"{label} R-1d marker")
        require(source, "CURRENT / NOT_COMPLETED", f"{label} R-1d current state")
        require(source, "IMPLEMENTED / NOT_ACCEPTED", f"{label} R-1d implementation state")

    require(checklist, "Current small commit: R-1d", "current small commit")
    require(
        checklist,
        "Current implementation state: IMPLEMENTED / NOT_ACCEPTED",
        "R-1d implementation state",
    )
    require(checklist, "R-1e  PLANNED", "R-1e planned state")
    require(read("backend/app/version.py", root=root), 'APP_VERSION = "2.1.0"', "Backend version")
    require(read("app/pubspec.yaml", root=root), "version: 2.1.0+3", "Flutter version")

    for marker in (
        "Status: PREPARED / NOT_RELEASED",
        "source HEAD: NOT_RECORDED",
        "fixed ZIP basename: NOT_BUILT",
        "fixed ZIP size: NOT_RECORDED",
        "fixed ZIP SHA-256: NOT_RECORDED",
        "same-artifact verification: NOT_COMPLETED",
        "explicit final operator approval: NOT_RECEIVED",
        "annotated tag publication: NOT_CREATED",
        "GitHub Release publication: NOT_CREATED",
    ):
        require(release_record, marker, "unfilled R-1d release record")

    require(release_notes, "Status: RELEASE CANDIDATE / NOT_RELEASED", "candidate notes")
    require(release_notes, "Release tag: `DRC_v2.1.0` — NOT_CREATED", "unpublished tag")
    forbid(release_record, "Status: RELEASED", "early release record")
    forbid(release_notes, "Status: RELEASED", "early release notes")

    builder = read("build_v210_fixed_release_zip_from_head.ps1", root=root)
    for marker in (
        "$buildInvocationCount = 0",
        "[switch]$PreflightOnly",
        "function Get-RelativePathCompat",
        "git status --porcelain --untracked-files=all",
        "refs/remotes/origin/main",
        'foreach ($tagName in @("DRC_v2.0.0", "DRC_v2.0.1"))',
        'git tag --list "DRC_v2.1.0"',
        'Get-ChildItem -LiteralPath $outputFullDirectory',
        '-Filter "DailyRhythmCompanion_v2.1.0_*.zip"',
        "git worktree add --detach",
        "build_release.bat release",
        "$buildInvocationCount++",
        "$buildInvocationCount -ne 1",
        "DailyRhythmCompanion_v2.1.0_",
        "Get-FileHash -LiteralPath $destinationPath -Algorithm SHA256",
        "verification_status: not-run",
        "next_action: verify-this-same-zip-without-rebuilding",
        "v210_fixed_release_zip_preflight_status: passed-no-build",
    ):
        require(builder, marker, "one-time R-1d builder contract")

    forbid(
        builder,
        "[IO.Path]::GetRelativePath",
        "PowerShell 7-only relative-path API",
    )

    assert_hashes(PROTECTED_HISTORICAL_HASHES, "Protected historical release record", root=root)
    assert_hashes(PROTECTED_GENERIC_PACKAGE_HASHES, "Protected generic package boundary", root=root)

    for relative in PUBLIC_SAFE_FILES:
        assert_no_sensitive_values(relative, read(relative, root=root))


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
        raise AssertionError(f"Official release branch must be main, got {branch!r}")

    origin = capture(["git", "remote", "get-url", "origin"])
    if not OFFICIAL_ORIGIN.fullmatch(origin):
        raise AssertionError(f"Origin is not the official Public repository: {origin}")

    head = capture(["git", "rev-parse", "HEAD"])
    origin_main = capture(["git", "rev-parse", "refs/remotes/origin/main"])
    if head != origin_main:
        raise AssertionError(f"HEAD does not match origin/main: {head} != {origin_main}")

    roots = [
        line
        for line in capture(["git", "rev-list", "--max-parents=0", "HEAD"]).splitlines()
        if line
    ]
    if len(roots) != 1:
        raise AssertionError(f"Official Public repository must have one root commit, got {len(roots)}")

    for tag_name in ("DRC_v2.0.0", "DRC_v2.0.1"):
        if capture(["git", "tag", "--list", tag_name]) != tag_name:
            raise AssertionError(f"Annotated tag {tag_name} is required")
        if capture(["git", "cat-file", "-t", tag_name]) != "tag":
            raise AssertionError(f"{tag_name} must remain an annotated tag")

    if capture(["git", "tag", "--list", RELEASE_TAG]):
        raise AssertionError(f"{RELEASE_TAG} must not exist before R-1e approval")

    return head, origin_main


def parse_flutter_count(output: str) -> int:
    plain = re.sub(r"\x1b\[[0-9;?]*[ -/]*[@-~]", "", output)
    matches = re.findall(
        r"\+(\d+)(?:\s+-\d+)?:\s+All tests passed!",
        plain.replace("\r", "\n"),
    )
    if not matches:
        raise AssertionError("Flutter passed-test count was not found")
    return int(matches[-1])


def run_extracted_gates(
    source_root: Path,
    *,
    with_flutter: bool,
    with_builds: bool,
) -> None:
    run([sys.executable, "-m", "compileall", "-q", "backend", "scripts"], cwd=source_root)

    pytest_output = run_capture(
        [sys.executable, "-m", "pytest", "-q", "backend/tests"],
        cwd=source_root,
    )
    passed = re.findall(r"(\d+) passed", pytest_output)
    if not passed or int(passed[-1]) != EXPECTED_BACKEND_TESTS:
        raise AssertionError(
            f"Extracted ZIP Backend test count mismatch: "
            f"{passed[-1] if passed else 'missing'} != {EXPECTED_BACKEND_TESTS}"
        )

    if with_flutter:
        flutter = shutil.which("flutter")
        if flutter is None:
            raise AssertionError("flutter executable is required for --with-flutter")
        flutter_output = run_capture(
            [flutter, "test", "--reporter", "compact"],
            cwd=source_root / "app",
        )
        count = parse_flutter_count(flutter_output)
        if count != EXPECTED_FLUTTER_TESTS:
            raise AssertionError(
                f"Extracted ZIP Flutter test count mismatch: {count} != {EXPECTED_FLUTTER_TESTS}"
            )
        if with_builds:
            if os.name != "nt":
                raise AssertionError("--with-builds must run on the Windows release host")
            run([flutter, "build", "web"], cwd=source_root / "app")
            run([flutter, "build", "windows"], cwd=source_root / "app")


def _strip_package_root(name: str) -> str:
    parts = PurePosixPath(name.replace("\\", "/")).parts
    if parts and parts[0] == "DailyRhythmCompanion":
        return "/".join(parts[1:])
    return "/".join(parts)


def verify_release_zip(
    zip_path: Path,
    *,
    expected_sha256: str,
    expected_source_head: str,
    with_flutter: bool,
    with_builds: bool,
) -> tuple[str, int]:
    if not zip_path.is_file():
        raise AssertionError(f"Release ZIP not found: {zip_path}")
    if ZIP_NAME_PATTERN.fullmatch(zip_path.name) is None:
        raise AssertionError(f"Unexpected v2.1.0 fixed ZIP basename: {zip_path.name}")
    if re.fullmatch(r"[0-9a-f]{40}", expected_source_head) is None:
        raise AssertionError("--expected-source-head must be a lowercase 40-character commit SHA")
    if re.fullmatch(r"[0-9a-f]{64}", expected_sha256) is None:
        raise AssertionError("--expected-sha256 must be a lowercase 64-character SHA-256")

    head, origin_main = verify_git_source()
    if head != expected_source_head or origin_main != expected_source_head:
        raise AssertionError(
            f"Expected source HEAD mismatch: HEAD={head}, origin/main={origin_main}, "
            f"expected={expected_source_head}"
        )

    before_stat = zip_path.stat()
    before_sha = file_sha256(zip_path)
    if before_sha != expected_sha256:
        raise AssertionError(
            f"Release ZIP SHA-256 mismatch: {before_sha} != {expected_sha256}"
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
                raise AssertionError(f"Duplicate normalized ZIP member: {normalized_name}")
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
        missing = sorted(REQUIRED_RELEASE_FILES - normalized_files)
        if missing:
            raise AssertionError(f"Release ZIP is missing R-1d files: {missing}")

        def package_bytes(relative: str) -> bytes:
            normalized_member = f"DailyRhythmCompanion/{relative}"
            original_member = member_map.get(normalized_member)
            if original_member is None:
                raise AssertionError(f"Missing ZIP member: {normalized_member}")
            return package.read(original_member)

        require(
            package_bytes("backend/app/version.py").decode("utf-8"),
            'APP_VERSION = "2.1.0"',
            "ZIP Backend version",
        )
        require(
            package_bytes("app/pubspec.yaml").decode("utf-8"),
            "version: 2.1.0+3",
            "ZIP Flutter version",
        )
        zip_checklist = package_bytes(
            "docs/DRC_v210_goal_checklist_small_commit.md"
        ).decode("utf-8")
        require(zip_checklist, "Current small commit: R-1d", "ZIP R-1d current state")
        require(
            zip_checklist,
            "Current implementation state: IMPLEMENTED / NOT_ACCEPTED",
            "ZIP R-1d implementation state",
        )
        zip_record = package_bytes("docs/v210_release_record.md").decode("utf-8")
        require(zip_record, "Status: PREPARED / NOT_RELEASED", "ZIP release record")
        require(zip_record, "fixed ZIP basename: NOT_BUILT", "ZIP pre-artifact record")

        for relative, expected in PROTECTED_HISTORICAL_HASHES.items():
            actual = sha256(
                package_bytes(relative).replace(b"\r\n", b"\n").replace(b"\r", b"\n")
            ).hexdigest()
            if actual != expected:
                raise AssertionError(
                    f"Historical ZIP record changed: {relative}: {actual} != {expected}"
                )

    with tempfile.TemporaryDirectory(prefix="drc_v210_fixed_zip_") as temp_dir:
        extraction_root = Path(temp_dir)
        with zipfile.ZipFile(zip_path) as package:
            for info in package.infolist():
                normalized_name = info.filename.replace("\\", "/")
                pure_path = PurePosixPath(normalized_name)
                if pure_path.is_absolute() or ".." in pure_path.parts:
                    raise AssertionError(f"Unsafe ZIP extraction member: {info.filename}")
                target = extraction_root.joinpath(*pure_path.parts)
                if info.is_dir() or normalized_name.endswith("/"):
                    target.mkdir(parents=True, exist_ok=True)
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                with package.open(info) as source, target.open("wb") as destination:
                    shutil.copyfileobj(source, destination)

        source_root = extraction_root / "DailyRhythmCompanion"
        verify_contract(root=source_root)
        run_extracted_gates(
            source_root,
            with_flutter=with_flutter,
            with_builds=with_builds,
        )

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
        help="require clean synchronized official Public main and run the aggregate gate",
    )
    parser.add_argument(
        "--release-zip",
        type=Path,
        help="verify this exact fixed v2.1.0 ZIP without rebuilding it",
    )
    parser.add_argument(
        "--expected-sha256",
        help="require the supplied ZIP to match this lowercase SHA-256",
    )
    parser.add_argument(
        "--expected-source-head",
        help="require the supplied ZIP to match this exact committed Public source HEAD",
    )
    parser.add_argument(
        "--with-flutter",
        action="store_true",
        help="include the full Flutter test in source/extracted-ZIP gates",
    )
    parser.add_argument(
        "--with-builds",
        action="store_true",
        help="include Flutter Web and Windows builds; requires --with-flutter on Windows",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.with_builds and not args.with_flutter:
        raise AssertionError("--with-builds requires --with-flutter")
    if args.with_builds and os.name != "nt":
        raise AssertionError("--with-builds must run on the Windows release host")
    if args.release_zip is not None and (
        args.expected_sha256 is None or args.expected_source_head is None
    ):
        raise AssertionError(
            "--release-zip requires --expected-sha256 and --expected-source-head"
        )

    verify_contract()

    source_head = "not-run"
    origin_main = "not-run"
    source_tree_verified = False
    if args.source_tree:
        source_head, origin_main = verify_git_source()
        command = [sys.executable, "scripts/check_v210_release_readiness.py"]
        if args.with_flutter:
            command.append("--with-flutter")
        if args.with_builds:
            command.append("--with-builds")
        run(command)
        source_tree_verified = True

    zip_sha = "not-run"
    zip_size: int | str = "not-run"
    same_artifact_verified = False
    if args.release_zip is not None:
        zip_sha, zip_size = verify_release_zip(
            args.release_zip.resolve(),
            expected_sha256=args.expected_sha256,
            expected_source_head=args.expected_source_head,
            with_flutter=args.with_flutter,
            with_builds=args.with_builds,
        )
        source_head = args.expected_source_head
        origin_main = args.expected_source_head
        same_artifact_verified = True

    print("v210_fixed_release_zip_status: implemented-not-accepted")
    print("v210_fixed_release_zip_current_small_commit: R-1d")
    print("v210_fixed_release_zip_parent_phase: R-1-current-not-completed")
    print(f"v210_fixed_release_zip_source_tree_verified: {str(source_tree_verified).lower()}")
    print(f"v210_fixed_release_zip_source_head: {source_head}")
    print(f"v210_fixed_release_zip_origin_main_head: {origin_main}")
    print(f"v210_fixed_release_zip_same_artifact_verified: {str(same_artifact_verified).lower()}")
    print(f"v210_fixed_release_zip_size_bytes: {zip_size}")
    print(f"v210_fixed_release_zip_sha256: {zip_sha}")
    print(f"v210_fixed_release_zip_flutter_executed: {str(args.with_flutter).lower()}")
    print(f"v210_fixed_release_zip_builds_executed: {str(args.with_builds).lower()}")
    print("v210_fixed_release_zip_builder_invoked_by_verifier: false")
    print("v210_fixed_release_zip_tag_created: false")
    print("v210_fixed_release_zip_github_release_created: false")
    print("[v210-fixed-release-zip-check] OK")


if __name__ == "__main__":
    main()
