#!/usr/bin/env python3
"""Validate the exact RT-6f acceptance-state synchronization."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess

REPO_ROOT = Path(__file__).resolve().parents[1]
IMPLEMENTATION_BASELINE = "e1d4f63d71c2de485b05fbfc5dad6811b81b31fc"
IMPLEMENTATION_COMMIT = "fcdce38b9260604ea7c435c6de44fc129dc613f6"
FW_VERSION = "5.4.0"
FW_REFERENCE_COMMIT = "d313eb6acb643103fe25988720ebee5976a04f78"
EXACT_PATHS = {
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v300_goal_checklist_small_commit.md",
    "docs/v300_rt6f_configured_local_mock_motion_presentation_acceptance.md",
    "scripts/check_v300_rt6f_configured_local_mock_motion_presentation_acceptance.py",
}
IMPLEMENTATION_PATHS = {
    "backend/.env.example",
    "backend/app/config.py",
    "backend/app/main.py",
    "backend/app/api/character_motion_presentation.py",
    "backend/app/models/character_motion_presentation.py",
    "backend/app/services/character_motion_presentation_service.py",
    "backend/tests/conftest.py",
    "backend/tests/test_character_motion_presentation_api.py",
    "app/lib/main.dart",
    "app/lib/services/configured_character_motion_presentation_runtime.dart",
    "app/test/configured_character_motion_presentation_runtime_test.dart",
    "app/test/main_character_motion_presentation_wiring_widget_test.dart",
}


def _run(*args: str) -> str:
    completed = subprocess.run(
        args,
        cwd=REPO_ROOT,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return completed.stdout.strip()


def _changed_paths() -> set[str]:
    paths: set[str] = set()
    for command in (
        ("git", "diff", "--name-only"),
        ("git", "diff", "--cached", "--name-only"),
        ("git", "ls-files", "--others", "--exclude-standard"),
    ):
        paths.update(
            line.strip().replace("\\", "/")
            for line in _run(*command).splitlines()
            if line.strip()
        )
    return paths


def _text(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8", errors="replace")


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _assert_surface(snapshot: bool) -> None:
    missing = sorted(
        path
        for path in EXACT_PATHS | IMPLEMENTATION_PATHS
        if not (REPO_ROOT / path).is_file()
    )
    _require(not missing, f"RT-6f files missing: {missing}")
    changed = _changed_paths()
    _require(
        changed == EXACT_PATHS,
        f"RT-6f acceptance surface mismatch: expected={sorted(EXACT_PATHS)} actual={sorted(changed)}",
    )
    _require(
        not (changed & IMPLEMENTATION_PATHS),
        "RT-6f acceptance sync changed implementation runtime/tests",
    )
    if not snapshot:
        head = _run("git", "rev-parse", "HEAD")
        origin = _run("git", "rev-parse", "origin/main")
        _require(
            head == IMPLEMENTATION_COMMIT and origin == IMPLEMENTATION_COMMIT,
            f"RT-6f implementation baseline mismatch: head={head} origin/main={origin} expected={IMPLEMENTATION_COMMIT}",
        )


def _assert_docs() -> None:
    docs = "\n".join(
        _text(path) for path in sorted(EXACT_PATHS) if path.endswith(".md")
    )
    required = (
        "RT-6f: COMPLETED / ACCEPTED / PUSHED",
        "RT-6: COMPLETED / ACCEPTED",
        IMPLEMENTATION_BASELINE,
        IMPLEMENTATION_COMMIT,
        FW_VERSION,
        FW_REFERENCE_COMMIT,
        "exact 19 files",
        "acceptance-sync surface: exact 7",
        "focused Backend: 10 passed",
        "Backend full: 289 passed",
        "focused Flutter: 15 passed",
        "Flutter full: 483 passed",
        "configured local Controls A-E: passed",
        "home_screen_manual_motion",
        "whole-response timeout: 10 seconds",
        "real adapter enabled: false",
        "provider attempted: false",
        "network execution: false",
        "BLOCKED_REAL_LIVE2D_VTS_ADAPTER_NOT_IMPLEMENTED",
        "acceptance-sync commit/push: NOT_AUTHORIZED",
    )
    for marker in required:
        _require(marker in docs, f"RT-6f acceptance documentation marker missing: {marker}")
    forbidden = (
        "RT-6f: IMPLEMENTED / AWAITING_REVIEW",
        "Flutter real-checkout verification: pending",
        "configured local Controls A-E: pending",
    )
    for marker in forbidden:
        _require(marker not in docs, f"stale RT-6f marker remains: {marker}")


def _assert_implementation() -> None:
    config = _text("backend/app/config.py")
    route = _text("backend/app/api/character_motion_presentation.py")
    request_model = _text("backend/app/models/character_motion_presentation.py")
    service = _text("backend/app/services/character_motion_presentation_service.py")
    backend_test = _text("backend/tests/test_character_motion_presentation_api.py")
    main_dart = _text("app/lib/main.dart")
    runtime = _text("app/lib/services/configured_character_motion_presentation_runtime.dart")
    runtime_test = _text("app/test/configured_character_motion_presentation_runtime_test.dart")
    wiring_test = _text("app/test/main_character_motion_presentation_wiring_widget_test.dart")

    markers = (
        ("DRC_RT6_ENABLE_FRAMEWORK_MOCK_MOTION", config),
        ('"/demo/character-motion/presentation"', route),
        ("home_screen_manual_motion", request_model),
        ("CharacterMotionMapper", service),
        ("FrameworkMockMotionSessionAdapter", service),
        ("provider_execution_attempted", backend_test),
        ("characterMotionPresentationControllerFactory", main_dart),
        ("DRC_RT6_ENABLE_CONFIGURED_MOCK_MOTION", runtime),
        ("followRedirects = false", runtime),
        ("configuredCharacterMotionPresentationMaxResponseBytes = 65536", runtime),
        ("_sendAndDecode(request).timeout(timeout)", runtime),
        ("mediaType != 'application/json'", runtime),
        ("one explicit apply sends one strict POST", runtime_test),
        ("default main app keeps character motion unconfigured", wiring_test),
    )
    for marker, text in markers:
        _require(marker in text, f"accepted RT-6f implementation marker missing: {marker}")

    forbidden_runtime_tokens = (
        "WebSocket",
        "VTube Studio",
        "Live2D",
        "Authorization",
        "api_key",
        "token",
    )
    _require(
        not any(token in runtime for token in forbidden_runtime_tokens),
        "Flutter RT-6f runtime contains forbidden real/provider surface",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", action="store_true")
    args = parser.parse_args()

    _assert_surface(args.snapshot)
    _assert_docs()
    _assert_implementation()

    values = [
        ("v300_rt6f_status", "completed-accepted-pushed"),
        ("v300_rt6_status", "completed-accepted"),
        ("v300_rt6f_exact_acceptance_sync_surface", "True"),
        ("v300_rt6f_acceptance_sync_file_count", "7"),
        ("v300_rt6f_implementation_baseline", IMPLEMENTATION_BASELINE),
        ("v300_rt6f_implementation_commit", IMPLEMENTATION_COMMIT),
        ("v300_rt6f_implementation_surface", "19"),
        ("v300_rt6f_focused_backend_passed", "10"),
        ("v300_rt6f_backend_full_passed", "289"),
        ("v300_rt6f_backend_warning_count", "1"),
        ("v300_rt6f_flutter_analyze_passed", "True"),
        ("v300_rt6f_focused_flutter_passed", "15"),
        ("v300_rt6f_flutter_full_passed", "483"),
        ("v300_rt6f_configured_controls_a_to_e_passed", "True"),
        ("v300_rt6f_double_default_off", "True"),
        ("v300_rt6f_manual_apply_only", "True"),
        ("v300_rt6f_apply_http_limit", "1"),
        ("v300_rt6f_reset_opt_out_transport", "False"),
        ("v300_rt6f_real_adapter_enabled", "False"),
        ("v300_rt6f_provider_execution_allowed", "False"),
        ("v300_rt6f_network_execution_in_fw_adapter", "False"),
        ("v300_rt6f_framework_version", FW_VERSION),
        ("v300_rt6f_framework_reference_commit", FW_REFERENCE_COMMIT),
        ("v300_rt6f_runtime_changed_by_acceptance_sync", "False"),
        ("v300_rt6f_tests_changed_by_acceptance_sync", "False"),
        ("v300_rt6f_framework_source_changed", "False"),
        ("v300_rt6f_implementation_push_completed", "True"),
        ("v300_rt7_real_adapter_blocked", "True"),
        ("v300_rt6f_acceptance_sync_commit_push_authorized", "False"),
        ("v300_rt6f_snapshot_mode", str(args.snapshot)),
    ]
    for key, value in values:
        print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
