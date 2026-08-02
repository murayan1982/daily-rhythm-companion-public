#!/usr/bin/env python3
"""Validate the exact RT-7a acceptance-state synchronization."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
IMPLEMENTATION_BASELINE = "c3c78316fd2bcd4f9939dcaadc32134a704374cf"
IMPLEMENTATION_COMMIT = "efb139b2c0b6c7cc66912a229bd674b36df82dd7"
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
        list(args), cwd=cwd, check=True, text=True, encoding="utf-8",
        errors="surrogateescape", capture_output=capture,
    )
    return completed.stdout.rstrip("\r\n") if capture else ""


def read(relative: str, *, root: Path = ROOT) -> str:
    return (root / relative).read_text(encoding="utf-8", errors="replace")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def changed_paths() -> set[str]:
    paths: set[str] = set()
    for command in (
        ("git", "diff", "--name-only"),
        ("git", "diff", "--cached", "--name-only"),
        ("git", "ls-files", "--others", "--exclude-standard"),
    ):
        output = run(*command, capture=True)
        paths.update(line.strip().replace("\\", "/") for line in output.splitlines() if line.strip())
    return paths


def resolve_framework_root() -> Path:
    candidates: list[Path] = []
    for name in ("FRAMEWORK_ROOT", "FRAMEWORK_PROJECT_ROOT"):
        value = os.environ.get(name, "").strip()
        if value:
            candidates.append(Path(value).expanduser())
    candidates.extend((
        ROOT.parent.parent / "AI-Character-Framework" / "Development",
        ROOT.parent / "AI-Character-Framework" / "Development",
        ROOT.parent / "ai-character-framework",
    ))
    for candidate in candidates:
        resolved = candidate.resolve()
        if (resolved / "framework" / "__init__.py").is_file():
            return resolved
    raise AssertionError("Set FRAMEWORK_ROOT to the clean FW v5.4.0 checkout.")


def assert_surface(*, snapshot: bool) -> Path | None:
    missing = sorted(path for path in EXACT_PATHS | PROTECTED_RT6_PATHS if not (ROOT / path).is_file())
    require(not missing, f"RT-7a files missing: {missing}")
    changed = changed_paths()
    require(changed == EXACT_PATHS, f"RT-7a acceptance surface mismatch: expected={sorted(EXACT_PATHS)} actual={sorted(changed)}")
    require(not (changed & PROTECTED_RT6_PATHS), "RT-7a acceptance sync changed accepted RT-6 runtime/tests")
    if snapshot:
        return None
    head = run("git", "rev-parse", "HEAD", capture=True)
    origin = run("git", "rev-parse", "origin/main", capture=True)
    require(head == IMPLEMENTATION_COMMIT and origin == IMPLEMENTATION_COMMIT,
            f"RT-7a implementation baseline mismatch: head={head} origin/main={origin} expected={IMPLEMENTATION_COMMIT}")
    fw_root = resolve_framework_root()
    fw_head = run("git", "rev-parse", "HEAD", cwd=fw_root, capture=True)
    require(fw_head == FW_REFERENCE_COMMIT, f"Unexpected FW HEAD: {fw_head}; expected {FW_REFERENCE_COMMIT}")
    require(not run("git", "status", "--porcelain", "--untracked-files=all", cwd=fw_root, capture=True),
            "FW working tree is not clean.")
    return fw_root


def assert_docs() -> None:
    combined = "\n".join(read(path) for path in sorted(EXACT_PATHS) if path.endswith(".md"))
    required = (
        "RT-7a: COMPLETED / ACCEPTED / PUSHED",
        "RT-7: CURRENT / NOT_COMPLETED",
        "BLOCKED_FRAMEWORK_REAL_MOTION_ADAPTER_RELEASE_REQUIRED",
        IMPLEMENTATION_BASELINE,
        IMPLEMENTATION_COMMIT,
        FW_VERSION,
        FW_REFERENCE_COMMIT,
        "implementation surface: exact 7 documentation/static-gate files",
        "acceptance-sync surface: exact 7 documentation/static-gate files",
        "Backend full: 289 passed",
        "Flutter analyze: No issues found",
        "Flutter full: 483 passed",
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
        "implementation commit/push: COMPLETED",
        "acceptance-sync commit/push: NOT_AUTHORIZED",
    )
    for marker in required:
        require(marker in combined, f"RT-7a acceptance documentation marker missing: {marker}")
    forbidden = (
        "RT-7a: IMPLEMENTED / AWAITING_REVIEW",
        "Current implementation commit: none",
    )
    for marker in forbidden:
        require(marker not in combined, f"stale RT-7a candidate marker remains: {marker}")


def assert_drc_rt6_frozen() -> None:
    adapter = read("backend/app/services/framework_mock_motion_session_adapter.py")
    route = read("backend/app/api/character_motion_presentation.py")
    runtime = read("app/lib/services/configured_character_motion_presentation_runtime.dart")
    for marker in ("create_motion_session", 'adapter="mock"', "real_adapter_enabled=False", "allow_provider_execution=False"):
        require(marker in adapter, f"accepted mock adapter marker missing: {marker}")
    require('/demo/character-motion/presentation' in route, "accepted presentation route missing")
    require("DRC_RT6_ENABLE_CONFIGURED_MOCK_MOTION" in runtime, "accepted Flutter mock flag missing")


def assert_framework_boundary(fw_root: Path | None) -> None:
    if fw_root is None:
        return
    public_init = read("framework/__init__.py", root=fw_root)
    motion = read("framework/motion.py", root=fw_root)
    session = read("framework/motion_session.py", root=fw_root)
    for marker in ("MotionAdapterStatus", "MotionCapability", "MotionRequest", "MotionResult", "MotionSession", "MotionSessionInfo", "create_motion_session"):
        require(marker in public_init, f"FW root-public export missing: {marker}")
    for marker in ('NOT_IMPLEMENTED = "not_implemented"', 'TOKEN_MISSING = "token_missing"', 'RUNTIME_NOT_INSTALLED = "runtime_not_installed"', 'MODEL_NOT_SELECTED = "model_not_selected"', "supports_real_adapter: bool = False"):
        require(marker in motion, f"FW motion contract marker missing: {marker}")
    for marker in ("real_adapter_supported=capability.supports_real_adapter", 'adapter not in {"mock", "live2d", "vts", "vtube_studio"}', "Real motion adapter is not implemented yet.", "This skeleton performs no real Live2D or VTS operation.", "result = MotionResult.not_implemented"):
        require(marker in session, f"FW mock-safe session marker missing: {marker}")


def assert_changed_content_safe() -> None:
    diff = run("git", "diff", "HEAD", "--unified=0", "--", *sorted(EXACT_PATHS), capture=True)
    added = "\n".join(line[1:] for line in diff.splitlines() if line.startswith("+") and not line.startswith("+++"))
    for pattern in SENSITIVE_PATTERNS:
        require(re.search(pattern, added) is None, f"Sensitive-looking value in RT-7a acceptance sync: {pattern}")


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
        ("v300_rt7a_status", "completed-accepted-pushed"),
        ("v300_rt7_status", "current-not-completed-blocked-framework-real-motion-adapter-release-required"),
        ("v300_rt7a_exact_acceptance_sync_surface", "True"),
        ("v300_rt7a_acceptance_sync_file_count", "7"),
        ("v300_rt7a_implementation_baseline", IMPLEMENTATION_BASELINE),
        ("v300_rt7a_implementation_commit", IMPLEMENTATION_COMMIT),
        ("v300_rt7a_implementation_surface", "7"),
        ("v300_rt7a_backend_full_passed", "289"),
        ("v300_rt7a_backend_warning_count", "1"),
        ("v300_rt7a_flutter_analyze_passed", "True"),
        ("v300_rt7a_flutter_full_passed", "483"),
        ("v300_rt7a_rt6_runtime_changed_by_acceptance_sync", "False"),
        ("v300_rt7a_backend_runtime_changed_by_acceptance_sync", "False"),
        ("v300_rt7a_flutter_runtime_changed_by_acceptance_sync", "False"),
        ("v300_rt7a_existing_tests_changed_by_acceptance_sync", "False"),
        ("v300_rt7a_framework_source_changed", "False"),
        ("v300_rt7a_vts_connection_opened", "False"),
        ("v300_rt7a_token_read", "False"),
        ("v300_rt7a_private_model_loaded", "False"),
        ("v300_rt7a_real_motion_executed", "False"),
        ("v300_rt7a_drc_provider_bypass_allowed", "False"),
        ("v300_rt7a_framework_update_required", "True"),
        ("v300_rt7a_implementation_push_completed", "True"),
        ("v300_rt7a_acceptance_sync_commit_push_authorized", "False"),
        ("v300_rt7a_snapshot_mode", str(args.snapshot)),
    )
    for key, value in values:
        print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
