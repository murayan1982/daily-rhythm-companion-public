#!/usr/bin/env python3
"""Validate the exact RT-7a real-motion adapter readiness candidate."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
DRC_BASELINE = "c3c78316fd2bcd4f9939dcaadc32134a704374cf"
FW_VERSION = "5.4.0"
FW_REFERENCE_COMMIT = "d313eb6acb643103fe25988720ebee5976a04f78"

EXACT_PATHS = {
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v300_goal_checklist_small_commit.md",
    "docs/v300_rt7a_real_motion_adapter_readiness.md",
    "scripts/check_v300_rt7a_real_motion_adapter_readiness.py",
}

PROTECTED_RT6_PATHS = {
    "backend/app/api/character_motion_presentation.py",
    "backend/app/models/character_motion.py",
    "backend/app/models/character_motion_adapter.py",
    "backend/app/models/character_motion_presentation.py",
    "backend/app/services/character_motion_mapper.py",
    "backend/app/services/framework_mock_motion_session_adapter.py",
    "backend/app/services/character_motion_presentation_service.py",
    "backend/tests/test_character_motion_mapper.py",
    "backend/tests/test_framework_mock_motion_session_adapter.py",
    "backend/tests/test_character_motion_presentation_api.py",
    "app/lib/main.dart",
    "app/lib/models/character_motion_presentation.dart",
    "app/lib/services/character_motion_presentation_client.dart",
    "app/lib/services/character_motion_presentation_controller.dart",
    "app/lib/services/configured_character_motion_presentation_runtime.dart",
    "app/lib/screens/home_screen.dart",
    "app/lib/widgets/character_motion_presentation_panel.dart",
    "app/test/character_motion_home_screen_test.dart",
    "app/test/character_motion_presentation_client_test.dart",
    "app/test/character_motion_presentation_controller_test.dart",
    "app/test/configured_character_motion_presentation_runtime_test.dart",
    "app/test/main_character_motion_presentation_wiring_widget_test.dart",
}

SENSITIVE_PATTERNS = (
    r"(?i)sk-[a-z0-9_-]{12,}",
    r"(?i)bearer\s+[a-z0-9._~+/-]{12,}",
    r"(?i)(api[_-]?key|access[_-]?token|refresh[_-]?token|client[_-]?secret)\s*[:=]\s*['\"][^<][^'\"]{7,}",
    r"(?i)(?:^|\s)[a-z]:\\(?:users|work|home)\\",
    r"/(?:home|users)/[^/\s]+/",
    r"\b(?:10|127|169\.254|172\.(?:1[6-9]|2\d|3[01])|192\.168)\.\d{1,3}\.\d{1,3}\b",
)


def run(*args: str, cwd: Path = ROOT, capture: bool = False) -> str:
    completed = subprocess.run(
        list(args),
        cwd=cwd,
        check=True,
        text=True,
        encoding="utf-8",
        errors="surrogateescape",
        capture_output=capture,
    )
    return completed.stdout.rstrip("\r\n") if capture else ""


def read(relative: str, *, root: Path = ROOT) -> str:
    return (root / relative).read_text(encoding="utf-8", errors="replace")


def require(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise AssertionError(f"Missing {label}: {needle!r}")


def forbid(text: str, needle: str, label: str) -> None:
    if needle in text:
        raise AssertionError(f"Unexpected {label}: {needle!r}")


def changed_paths() -> set[str]:
    paths: set[str] = set()
    for command in (
        ("git", "diff", "--name-only"),
        ("git", "diff", "--cached", "--name-only"),
        ("git", "ls-files", "--others", "--exclude-standard"),
    ):
        output = run(*command, capture=True)
        paths.update(
            line.strip().replace("\\", "/")
            for line in output.splitlines()
            if line.strip()
        )
    return paths


def resolve_framework_root() -> Path:
    candidates: list[Path] = []
    for name in ("FRAMEWORK_ROOT", "FRAMEWORK_PROJECT_ROOT"):
        value = os.environ.get(name, "").strip()
        if value:
            candidates.append(Path(value).expanduser())
    candidates.extend(
        (
            ROOT.parent.parent / "AI-Character-Framework" / "Development",
            ROOT.parent / "AI-Character-Framework" / "Development",
            ROOT.parent / "ai-character-framework",
        )
    )
    for candidate in candidates:
        resolved = candidate.resolve()
        if (resolved / "framework" / "__init__.py").is_file():
            return resolved
    raise AssertionError("Set FRAMEWORK_ROOT to the clean FW v5.4.0 checkout.")


def assert_surface(*, snapshot: bool) -> Path | None:
    missing = sorted(path for path in EXACT_PATHS if not (ROOT / path).is_file())
    if missing:
        raise AssertionError(f"RT-7a files missing: {missing}")

    changed = changed_paths()
    if changed != EXACT_PATHS:
        raise AssertionError(
            "RT-7a exact surface mismatch: "
            f"expected={sorted(EXACT_PATHS)} actual={sorted(changed)}"
        )
    if changed & PROTECTED_RT6_PATHS:
        raise AssertionError("RT-7a changed accepted RT-6 runtime/tests")

    if snapshot:
        return None

    head = run("git", "rev-parse", "HEAD", capture=True)
    origin = run("git", "rev-parse", "origin/main", capture=True)
    if head != DRC_BASELINE or origin != DRC_BASELINE:
        raise AssertionError(
            f"Unexpected DRC baseline: head={head} origin/main={origin} expected={DRC_BASELINE}"
        )

    fw_root = resolve_framework_root()
    fw_head = run("git", "rev-parse", "HEAD", cwd=fw_root, capture=True)
    if fw_head != FW_REFERENCE_COMMIT:
        raise AssertionError(
            f"Unexpected FW HEAD: {fw_head}; expected {FW_REFERENCE_COMMIT}"
        )
    if run(
        "git",
        "status",
        "--porcelain",
        "--untracked-files=all",
        cwd=fw_root,
        capture=True,
    ):
        raise AssertionError("FW working tree is not clean.")
    return fw_root


def assert_docs() -> None:
    sources = {
        "README": read("README.md"),
        "roadmap": read("roadmap.md"),
        "tasklist": read("tasklist.md"),
        "scripts README": read("scripts/README.md"),
        "checklist": read("docs/DRC_v300_goal_checklist_small_commit.md"),
        "contract": read("docs/v300_rt7a_real_motion_adapter_readiness.md"),
    }
    combined = "\n".join(sources.values())

    required = (
        "RT-7a: IMPLEMENTED / AWAITING_REVIEW",
        "RT-7: CURRENT / NOT_COMPLETED",
        "BLOCKED_FRAMEWORK_REAL_MOTION_ADAPTER_RELEASE_REQUIRED",
        DRC_BASELINE,
        FW_VERSION,
        FW_REFERENCE_COMMIT,
        "exact 7 documentation/static-gate files",
        "real_adapter_supported=false",
        "not_implemented",
        "create_motion_session()",
        "DRC-owned VTS/provider bypass",
        "Framework internal/provider import",
        "VTS WebSocket",
        "token",
        "private model",
        "DRC runtime changed: false",
        "Framework source changed: false",
        "real motion executed: false",
        "commit/push: NOT_AUTHORIZED",
    )
    for marker in required:
        require(combined, marker, f"RT-7a marker {marker}")

    for relative in sorted(EXACT_PATHS):
        require(combined, relative, f"exact path {relative}")

    forbidden = (
        "RT-7a: COMPLETED / ACCEPTED",
        "RT-7a implementation commit:",
        "real adapter execution: true",
        "VTS WebSocket opened: true",
        "commit/push: AUTHORIZED",
    )
    for marker in forbidden:
        forbid(combined, marker, f"premature RT-7a marker {marker}")


def assert_drc_rt6_frozen() -> None:
    for path in PROTECTED_RT6_PATHS:
        if not (ROOT / path).is_file():
            raise AssertionError(f"Accepted RT-6 path missing: {path}")

    adapter = read("backend/app/services/framework_mock_motion_session_adapter.py")
    route = read("backend/app/api/character_motion_presentation.py")
    runtime = read("app/lib/services/configured_character_motion_presentation_runtime.dart")

    for marker in (
        "create_motion_session",
        'adapter="mock"',
        "real_adapter_enabled=False",
        "allow_provider_execution=False",
    ):
        require(adapter, marker, f"accepted mock adapter marker {marker}")
    require(route, '"/demo/character-motion/presentation"', "accepted presentation route")
    require(runtime, "DRC_RT6_ENABLE_CONFIGURED_MOCK_MOTION", "accepted Flutter mock flag")


def assert_framework_boundary(fw_root: Path | None) -> None:
    if fw_root is None:
        return

    public_init = read("framework/__init__.py", root=fw_root)
    motion = read("framework/motion.py", root=fw_root)
    session = read("framework/motion_session.py", root=fw_root)

    for marker in (
        "MotionAdapterStatus",
        "MotionCapability",
        "MotionRequest",
        "MotionResult",
        "MotionSession",
        "MotionSessionInfo",
        "create_motion_session",
    ):
        require(public_init, marker, f"FW root-public export {marker}")

    for marker in (
        'NOT_IMPLEMENTED = "not_implemented"',
        'TOKEN_MISSING = "token_missing"',
        'RUNTIME_NOT_INSTALLED = "runtime_not_installed"',
        'MODEL_NOT_SELECTED = "model_not_selected"',
        "supports_real_adapter: bool = False",
    ):
        require(motion, marker, f"FW motion contract marker {marker}")

    for marker in (
        "real_adapter_supported=capability.supports_real_adapter",
        'adapter not in {"mock", "live2d", "vts", "vtube_studio"}',
        "Real motion adapter is not implemented yet.",
        "This skeleton performs no real Live2D or VTS operation.",
        "result = MotionResult.not_implemented",
    ):
        require(session, marker, f"FW mock-safe session marker {marker}")


def assert_changed_content_safe() -> None:
    diff = run(
        "git",
        "diff",
        "HEAD",
        "--unified=0",
        "--",
        *sorted(EXACT_PATHS),
        capture=True,
    )
    added = "\n".join(
        line[1:]
        for line in diff.splitlines()
        if line.startswith("+") and not line.startswith("+++")
    )
    for pattern in SENSITIVE_PATTERNS:
        if re.search(pattern, added):
            raise AssertionError(f"Sensitive-looking value in RT-7a candidate: {pattern}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", action="store_true")
    args = parser.parse_args()

    fw_root = assert_surface(snapshot=args.snapshot)
    assert_docs()
    assert_drc_rt6_frozen()
    assert_framework_boundary(fw_root)
    assert_changed_content_safe()

    values = (
        ("v300_rt7a_status", "implemented-awaiting-review"),
        (
            "v300_rt7_status",
            "current-not-completed-blocked-framework-real-motion-adapter-release-required",
        ),
        ("v300_rt7a_exact_change_surface", "True"),
        ("v300_rt7a_change_file_count", "7"),
        ("v300_rt7a_drc_baseline", DRC_BASELINE),
        ("v300_rt7a_framework_version", FW_VERSION),
        ("v300_rt7a_framework_reference_commit", FW_REFERENCE_COMMIT),
        ("v300_rt7a_rt6_runtime_changed", "False"),
        ("v300_rt7a_backend_runtime_changed", "False"),
        ("v300_rt7a_flutter_runtime_changed", "False"),
        ("v300_rt7a_existing_tests_changed", "False"),
        ("v300_rt7a_framework_source_changed", "False"),
        ("v300_rt7a_vts_connection_opened", "False"),
        ("v300_rt7a_token_read", "False"),
        ("v300_rt7a_private_model_loaded", "False"),
        ("v300_rt7a_real_motion_executed", "False"),
        ("v300_rt7a_drc_provider_bypass_allowed", "False"),
        ("v300_rt7a_framework_update_required", "True"),
        ("v300_rt7a_commit_push_authorized", "False"),
        ("v300_rt7a_snapshot_mode", str(args.snapshot)),
    )
    for key, value in values:
        print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
