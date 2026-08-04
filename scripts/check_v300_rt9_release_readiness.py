#!/usr/bin/env python3
"""RT-9b v3.0.0 candidate metadata and aggregate readiness gate.

Default mode is credential-free, provider-free, network-free, private-manifest-
free, artifact-free, tag-free, and publication-free. Explicit full Windows mode
adds Flutter tests/builds and read-only strict validation of one ignored RT-8
aggregate manifest. No mode builds a fixed ZIP or publishes a release.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import importlib.util
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
RT9A_COMMIT = "0e4af7603f60c56f0240271fbb2590d72a189a65"
RT8_ACCEPTANCE_COMMIT = "4c3b724a0c42e0d078c876c02b07a04d4c71e24d"
EXPECTED_BACKEND_VERSION = "3.0.0"
EXPECTED_FLUTTER_VERSION = "3.0.0+4"
EXPECTED_BACKEND_TESTS = 417
EXPECTED_FLUTTER_TESTS = 500
HISTORICAL_V300_GATE_COUNT = 63
OFFICIAL_ORIGIN = re.compile(
    r"^(?:https://github\.com/|git@github\.com:)"
    r"murayan1982/daily-rhythm-companion-public(?:\.git)?$"
)
SURFACE = {
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v300_goal_checklist_small_commit.md",
    "docs/v300_rt9_release_readiness_current_behavior_inventory.md",
    "docs/v300_rt9_release_readiness.md",
    "docs/v300_release_record.md",
    "release_notes/v3.0.0.md",
    "scripts/check_v300_rt9_release_readiness.py",
    "scripts/check_v20x_application_version_metadata.py",
    "backend/app/version.py",
    "app/pubspec.yaml",
}
TOP = (
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v300_goal_checklist_small_commit.md",
)
PROTECTED_HASHES = {
    "docs/DRC_v200_goal_checklist_small_commit.md": "4c043837986c626c6fc44e4f84f73b019b2c8c21da7531a3f029554006b7eb63",
    "docs/DRC_v20x_maintenance_checklist.md": "02e6e2e49a54a5c1360ee5d95d6bed2314ab42aec5dce911f3ed72867c4d46f2",
    "docs/v20x_patch_release.md": "eb6ae9770a4611a463ddb227a1dd8ce8816ee310cddaed327a02404a34a7935d",
    "docs/v201_patch_release_record.md": "9b724a6c5c7ffffdb3e699ad010ff75148ec4549b6cf2d940b44e62e161140bd",
    "docs/DRC_v210_goal_checklist_small_commit.md": "a953165821c38b2671affcdbb0bc427233dabf5c00320d7c7f19ee939a688018",
    "docs/v210_release_record.md": "de7e83b9cd9d21bbd61805a0a09c0039c90b7a85ce9f25512e760fd0bcb562a1",
    "release_notes/v2.0.0.md": "d2e13041ae51b9fef330a01a0d9124ccbfb6fb0850a0c2a29966baf96be3417b",
    "release_notes/v2.0.1.md": "1e90c85e51ef848b64bddaa73f1f40c659457935e30831027310ea95fc94656b",
    "release_notes/v2.1.0.md": "0507586860e2e4fa057c3cf5e61b8c6f9be43453c28edc50088223bb80f6bf86",
    "build_v200_final_fixed_release_zip_from_head.ps1": "4a4439341b0ad00d56b50038993631fcb48fb417cd0f0648dc3abc5e72d3b360",
    "build_v201_fixed_release_zip_from_head.ps1": "89d3fe3e39484b36272d9c8ec8499276ffe305ec844a87cca5d90fef8931ab1b",
    "build_v210_fixed_release_zip_from_head.ps1": "434011e1ed8680a1619db845c8eda9d462d78956ed0d1d1e734c06f18c6d2f6d",
    "scripts/check_v20x_patch_release.py": "e4eefc408abcbccc2651c1113ae8264269cce1d77525067173e0a06a7ef685cf",
    "scripts/check_v210_release_readiness.py": "31056738993481889d1cb4fe492fe25f474087e7fa031cdde82d6529a3ace96f",
    "scripts/check_v210_fixed_release_zip.py": "3fc73ffda276b45f034a8314b6af66c0176c5f715eff7dd63b632f48624c6a2a",
    "build_release.bat": "1e939e31187b58efe7c5987fd763dba733ff706ad864a14cf945e641a9f23c1a",
    "scripts/check_release_package.py": "57d6e4a6fae67bbc2e8c9e9b5c710f4d951866ad4007606075c244c6a29d212b",
    ".gitignore": "bd7d15c32d4a8a061ae009358c6603b277a2b73bdab56089c5c6e5a7ec2b5de0",
    "scripts/validate_v300_rt8_private_operator_manifest.py": "4ea2e587f21e182c6a505a1a92d1062731221834a6480474cc40b8362e944725",
    "scripts/run_v300_rt8e_private_aggregate_cleanup.py": "e3ebf3538e96e82c45c0ffde9e1c0aebb628e7b54d6eb6f521766890b6682e1b",
    "backend/tests/test_v300_rt8e_private_aggregate_cleanup.py": "030f12f9e34a277d08aad0d49079d863cf704eee71898d333b35da5ef49f756a",
    "scripts/check_v300_rt9_release_readiness_current_behavior_inventory.py": "32d1380592164aa812ae7bfb84bd272e26861905f6c7630a5cc7d989469a9704",
}
ABSENT_RT9C = (
    "build_v300_fixed_release_zip_from_head.ps1",
    "scripts/check_v300_fixed_release_zip.py",
    "docs/v300_fixed_release_zip.md",
)
SENSITIVE = (
    re.compile(r"(?i)sk-[a-z0-9_-]{12,}"),
    re.compile(r"(?i)xai-[a-z0-9_-]{12,}"),
    re.compile(r"(?i)bearer\s+[a-z0-9._~+/-]{12,}"),
    re.compile(r"(?i)(?:api[_-]?key|access[_-]?token|refresh[_-]?token|client[_-]?secret)\s*[:=]"),
    re.compile(r"(?i)\b[a-z]:\\(?:users|work|home)\\"),
    re.compile(r"/(?:home|users)/[^/\s]+/"),
    re.compile(r"\b(?:10|169\.254|172\.(?:1[6-9]|2\d|3[01])|192\.168)\.\d{1,3}\.\d{1,3}\b"),
)


def fail(message: str) -> None:
    raise SystemExit("v300_rt9b_gate_error: " + message)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def git(*args: str) -> str:
    completed = subprocess.run(
        ["git", *args], cwd=ROOT, check=False, text=True,
        encoding="utf-8", errors="surrogateescape",
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    if completed.returncode:
        fail(completed.stderr.strip() or "git command failed")
    return completed.stdout.strip()


def git_ok(*args: str) -> bool:
    return subprocess.run(
        ["git", *args], cwd=ROOT, check=False,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    ).returncode == 0


def paths(value: str) -> set[str]:
    return {line.strip().replace("\\", "/") for line in value.splitlines() if line.strip()}


def working_changes() -> set[str]:
    result = paths(git("diff", "--name-only"))
    result |= paths(git("diff", "--cached", "--name-only"))
    result |= paths(git("ls-files", "--others", "--exclude-standard"))
    return result


def read(relative: str) -> str:
    path = ROOT / relative
    require(path.is_file(), "missing " + relative)
    return path.read_text(encoding="utf-8")


def normalized_hash(relative: str) -> str:
    data = (ROOT / relative).read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return sha256(data).hexdigest()


def subprocess_command(command: list[str]) -> list[str]:
    """Return a CreateProcess-safe command for the current platform.

    On Windows, ``shutil.which("flutter")`` resolves to ``flutter.bat``.
    Batch files are not native Win32 executables and therefore must be invoked
    through the command processor rather than passed directly to CreateProcess.
    """
    if os.name != "nt" or Path(command[0]).suffix.lower() not in {".bat", ".cmd"}:
        return command
    command_processor = os.environ.get("COMSPEC") or shutil.which("cmd.exe")
    require(command_processor is not None, "Windows command processor required")
    return [
        command_processor,
        "/d",
        "/s",
        "/c",
        subprocess.list2cmdline(command),
    ]


def run_capture(command: list[str], *, cwd: Path = ROOT) -> str:
    completed = subprocess.run(
        subprocess_command(command), cwd=cwd, check=False, text=True,
        encoding="utf-8", errors="replace",
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    )
    print(completed.stdout, end="")
    if completed.returncode:
        fail("command failed: " + " ".join(command))
    return completed.stdout


def snapshot_tree(relative: str) -> str | None:
    root = ROOT / relative
    if not root.exists():
        return None
    digest = sha256()
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root).as_posix().encode("utf-8", errors="surrogateescape")
        stat = path.lstat()
        digest.update(rel + b"\0" + str(stat.st_mode).encode() + b"\0" + str(stat.st_size).encode() + b"\0" + str(stat.st_mtime_ns).encode() + b"\n")
    return digest.hexdigest()


def determine_source_mode() -> tuple[str, str]:
    require(git("branch", "--show-current") == "main", "branch must be main")
    head = git("rev-parse", "HEAD")
    origin = git("rev-parse", "origin/main")
    require(git_ok("cat-file", "-e", RT9A_COMMIT + "^{commit}"), "RT-9a commit missing")
    require(git_ok("merge-base", "--is-ancestor", RT8_ACCEPTANCE_COMMIT, RT9A_COMMIT), "RT-8 acceptance ancestry")
    origin_url = git("remote", "get-url", "origin")
    require(OFFICIAL_ORIGIN.fullmatch(origin_url) is not None, "official origin")
    changes = working_changes()
    if head == RT9A_COMMIT and origin == RT9A_COMMIT and changes == SURFACE:
        return "candidate", head
    if head == origin and not changes and git_ok("merge-base", "--is-ancestor", RT9A_COMMIT, head):
        committed_surface = paths(git("diff", "--name-only", RT9A_COMMIT + ".." + head))
        require(committed_surface == SURFACE, "committed exact surface " + repr(sorted(committed_surface)))
        return "committed", head
    fail("source state is neither exact candidate nor clean committed RT-9b source")


def markers(relative: str, *values: str) -> None:
    text = read(relative)
    for value in values:
        require(value in text, f"{relative} missing {value}")


def verify_contract(mode: str) -> None:
    common = (
        "RT-9: CURRENT / NOT_COMPLETED",
        "RT-9a: COMPLETED / ACCEPTED / PUSHED",
        "RT-9a commit: " + RT9A_COMMIT,
        "RT-9b: IMPLEMENTED / AWAITING_REVIEW",
        "RT-9b baseline: " + RT9A_COMMIT,
        "RT-9b surface: exact 13 files",
        "Backend candidate metadata: 3.0.0",
        "Flutter candidate metadata: 3.0.0+4",
        "v3.0.0 fixed ZIP: NOT_BUILT",
        "DRC_v3.0.0 annotated tag: NOT_CREATED",
        "GitHub Release: NOT_CREATED",
    )
    for relative in TOP:
        markers(relative, *common)
    markers("README.md", "Current v3.0.0 candidate metadata: Backend 3.0.0 / Flutter 3.0.0+4 (**NOT_RELEASED**)")
    markers("backend/app/version.py", 'APP_VERSION = "3.0.0"')
    markers("app/pubspec.yaml", "version: 3.0.0+4")
    markers(
        "scripts/check_v20x_application_version_metadata.py",
        '"3.0.0": "4"',
        'for forbidden in ("3.0.0", "2.1.0", "2.0.1", "2.0.0+1", "0.15.0")',
    )
    markers(
        "docs/v300_rt9_release_readiness.md",
        "Status: IMPLEMENTED / AWAITING_REVIEW",
        "Backend candidate version: 3.0.0",
        "Flutter candidate version: 3.0.0+4",
        "python scripts\\check_v300_rt9_release_readiness.py",
        "--with-flutter",
        "--with-builds",
        "--rt8-manifest-json",
        "Flutter Android debug APK build",
        "accepted baseline: 417 passed",
        "accepted baseline: 500 passed",
        "## Exact RT-9b surface",
        "## Stop rule",
    )
    markers(
        "docs/v300_release_record.md",
        "Status: PREPARED / NOT_RELEASED",
        "release source HEAD: NOT_RECORDED",
        "fixed ZIP basename: NOT_BUILT",
        "fixed ZIP SHA-256: NOT_RECORDED",
        "fixed ZIP builder invocation count: 0",
        "explicit final operator approval: NOT_RECEIVED",
        "annotated tag publication: NOT_CREATED",
        "GitHub Release publication: NOT_CREATED",
        "post-publication SHA-256 verification: NOT_COMPLETED",
    )
    markers(
        "release_notes/v3.0.0.md",
        "Status: RELEASE CANDIDATE / NOT_RELEASED",
        "Release tag: `DRC_v3.0.0` — NOT_CREATED",
        "GitHub Release: NOT_CREATED",
        "Fixed release ZIP: NOT_BUILT",
        "Backend semantic version: `3.0.0`",
        "Flutter package version: `3.0.0+4`",
        "Bundled AI Character Framework",
    )
    for relative in ABSENT_RT9C:
        require(not (ROOT / relative).exists(), "early RT-9c file " + relative)
    release_root = ROOT / "release"
    if release_root.exists():
        require(not any(release_root.glob("DailyRhythmCompanion_v3.0.0_*.zip")), "early v3 fixed ZIP")
    require(not git("tag", "--list", "DRC_v3.0.0"), "early DRC_v3.0.0 tag")
    checks = sorted((ROOT / "scripts").glob("check_v300_*.py"))
    historical = [p for p in checks if p.name != "check_v300_rt9_release_readiness.py"]
    require(len(historical) == HISTORICAL_V300_GATE_COUNT, "historical v300 gate count")
    require(len(checks) == HISTORICAL_V300_GATE_COUNT + 1, "v300 gate count including RT-9b")
    for relative, expected in PROTECTED_HASHES.items():
        require(normalized_hash(relative) == expected, "protected hash changed " + relative)
    builder = read("build_release.bat")
    for value in ('"%ROOT_DIR%release"', '"%ROOT_DIR%vendor"', '"%ROOT_DIR%backend\\local_data"', '"%ROOT_DIR%operator_evidence"', '"*.zip"'):
        require(value in builder, "package denylist marker " + value)
    if mode == "candidate":
        for relative in SURFACE:
            if git_ok("ls-files", "--error-unmatch", "--", relative):
                diff = git("diff", "--unified=0", "HEAD", "--", relative)
                added = "\n".join(
                    line[1:]
                    for line in diff.splitlines()
                    if line.startswith("+") and not line.startswith("+++")
                )
            else:
                added = read(relative)
            for pattern in SENSITIVE:
                require(pattern.search(added) is None, "private-looking value in " + relative)


def load_validator():
    path = ROOT / "scripts/validate_v300_rt8_private_operator_manifest.py"
    spec = importlib.util.spec_from_file_location("v300_rt8_validator_for_rt9b", path)
    require(spec is not None and spec.loader is not None, "validator import spec")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_rt8_manifest(path: Path, mode: str, head: str) -> None:
    validator = load_validator()
    target = path if path.is_absolute() else ROOT / path
    raw = validator.validate_private_manifest_path(target, root=ROOT)
    before = raw
    data = validator.load_json_bytes(raw)
    validator.validate_manifest_data(data, "aggregate")
    for key in ("pc_windows_candidate_source_head", "android_candidate_source_head"):
        candidate = str(data[key])
        require(git_ok("cat-file", "-e", candidate + "^{commit}"), "RT-8 candidate commit missing")
        require(git_ok("merge-base", "--is-ancestor", candidate, head), "RT-8 candidate not ancestor")
    if mode == "committed":
        validator.verify_git_state(data, "aggregate", RT9A_COMMIT)
    after = target.read_bytes()
    require(before == after, "RT-8 aggregate manifest modified")


def parse_count(output: str, pattern: str, expected: int, label: str) -> None:
    matches = [int(value) for value in re.findall(pattern, output)]
    require(expected in matches, f"{label} expected {expected}, saw {matches}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--with-flutter", action="store_true")
    parser.add_argument("--with-builds", action="store_true")
    parser.add_argument("--rt8-manifest-json", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    require(not args.with_builds or args.with_flutter, "--with-builds requires --with-flutter")
    require(not args.with_builds or args.rt8_manifest_json is not None, "--with-builds requires --rt8-manifest-json")
    require(args.rt8_manifest_json is None or args.with_builds, "--rt8-manifest-json requires --with-builds")
    mode, head = determine_source_mode()
    verify_contract(mode)
    snapshots_before = {name: snapshot_tree(name) for name in ("backend/local_data", "release", "vendor")}

    run_capture([sys.executable, "-m", "compileall", "-q", "backend", "scripts"])
    run_capture([sys.executable, "scripts/check_v20x_application_version_metadata.py"])
    maintenance = run_capture([sys.executable, "scripts/check_v20x_maintenance_readiness.py"])
    parse_count(maintenance, r"(\d+) passed", EXPECTED_BACKEND_TESTS, "Backend tests")

    manifest_read = False
    if args.rt8_manifest_json is not None:
        validate_rt8_manifest(args.rt8_manifest_json, mode, head)
        manifest_read = True

    flutter_executed = False
    builds_executed = False
    if args.with_flutter:
        if os.name == "nt":
            flutter = (
                shutil.which("flutter.bat")
                or shutil.which("flutter.cmd")
                or shutil.which("flutter")
            )
        else:
            flutter = shutil.which("flutter")
        require(flutter is not None, "flutter executable required")
        run_capture([flutter, "analyze"], cwd=ROOT / "app")
        flutter_test = run_capture([flutter, "test"], cwd=ROOT / "app")
        parse_count(flutter_test, r"\+(\d+): All tests passed!", EXPECTED_FLUTTER_TESTS, "Flutter tests")
        flutter_executed = True
        if args.with_builds:
            run_capture([flutter, "build", "web"], cwd=ROOT / "app")
            run_capture([flutter, "build", "windows"], cwd=ROOT / "app")
            run_capture([flutter, "build", "apk", "--debug"], cwd=ROOT / "app")
            builds_executed = True

    snapshots_after = {name: snapshot_tree(name) for name in snapshots_before}
    require(snapshots_before == snapshots_after, "private/generated protected directory changed")
    require(determine_source_mode()[0] == mode, "source state changed during gate")

    print("v300_rt9_status: current-not-completed")
    print("v300_rt9a_status: completed-accepted-pushed")
    print("v300_rt9b_status: implemented-awaiting-review")
    print("v300_rt9b_source_mode:", mode)
    print("v300_rt9b_baseline:", RT9A_COMMIT)
    print("v300_rt9b_exact_implementation_surface: True")
    print("v300_rt9b_implementation_change_file_count:", len(SURFACE))
    print("v300_rt9b_backend_version_metadata:", EXPECTED_BACKEND_VERSION)
    print("v300_rt9b_flutter_version_metadata:", EXPECTED_FLUTTER_VERSION)
    print("v300_rt9b_historical_v300_gate_count:", HISTORICAL_V300_GATE_COUNT)
    print("v300_rt9b_backend_test_baseline:", EXPECTED_BACKEND_TESTS)
    print("v300_rt9b_flutter_test_baseline:", EXPECTED_FLUTTER_TESTS)
    print("v300_rt9b_private_manifest_read:", manifest_read)
    print("v300_rt9b_private_manifest_modified: False")
    print("v300_rt9b_flutter_executed:", flutter_executed)
    print("v300_rt9b_builds_executed:", builds_executed)
    print("v300_rt9b_provider_network_configured_execution: False")
    print("v300_rt9b_fixed_zip_built: False")
    print("v300_rt9b_tag_created: False")
    print("v300_rt9b_github_release_created: False")
    print("v300_rt9b_commit_push_authorized: False")
    print("v300_rt9c_authorized: False")
    print("v300_release_ready: False")


if __name__ == "__main__":
    main()
