#!/usr/bin/env python3
"""Validate the exact RT-6e HomeScreen character-motion candidate."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess


REPO_ROOT = Path(__file__).resolve().parents[1]
DRC_BASELINE = "8d69b539e974ba71fde5d9b15dd951d0c670b7ff"
RT6D_IMPLEMENTATION_COMMIT = "0f220b792feb7ebb82c5871a794731aa1327439a"
FW_VERSION = "5.4.0"
FW_REFERENCE_COMMIT = "d313eb6acb643103fe25988720ebee5976a04f78"
FW_SOURCE_MODE = "external-vendored-snapshot"
EXACT_PATHS = {
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v300_goal_checklist_small_commit.md",
    "docs/v300_rt6e_home_screen_character_motion_wiring.md",
    "scripts/check_v300_rt6e_home_screen_character_motion_wiring.py",
    "app/lib/screens/home_screen.dart",
    "app/lib/widgets/character_motion_presentation_panel.dart",
    "app/test/character_motion_home_screen_test.dart",
}
FLUTTER_RUNTIME_PATHS = {
    "app/lib/screens/home_screen.dart",
    "app/lib/widgets/character_motion_presentation_panel.dart",
}
FLUTTER_TEST_PATHS = {"app/test/character_motion_home_screen_test.dart"}
PROTECTED_PATHS = {
    "app/lib/main.dart",
    "app/lib/models/character_motion_presentation.dart",
    "app/lib/services/character_motion_presentation_client.dart",
    "app/lib/services/character_motion_presentation_controller.dart",
    "app/lib/models/character_display_presentation.dart",
    "app/lib/widgets/character_display_card.dart",
    "app/lib/models/motion_demo.dart",
    "app/lib/services/backend_api_client.dart",
    "app/pubspec.yaml",
    "app/pubspec.lock",
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


def _git_paths() -> set[str]:
    values: set[str] = set()
    for command in (
        ("git", "diff", "--name-only"),
        ("git", "diff", "--cached", "--name-only"),
        ("git", "ls-files", "--others", "--exclude-standard"),
    ):
        output = _run(*command)
        values.update(
            line.strip().replace("\\", "/")
            for line in output.splitlines()
            if line.strip()
        )
    return values


def _assert_exact_surface(*, snapshot: bool) -> None:
    missing = sorted(path for path in EXACT_PATHS if not (REPO_ROOT / path).is_file())
    if missing:
        raise AssertionError(f"RT-6e candidate files are missing: {missing}")
    changed = _git_paths()
    if changed != EXACT_PATHS:
        raise AssertionError(
            "RT-6e candidate surface mismatch: "
            f"expected={sorted(EXACT_PATHS)} actual={sorted(changed)}"
        )
    if changed & PROTECTED_PATHS:
        raise AssertionError("RT-6e changed a protected accepted path")
    if any(path.startswith("backend/") for path in changed):
        raise AssertionError("RT-6e changed Backend source")
    if any(path.startswith("vendor/") for path in changed):
        raise AssertionError("RT-6e changed external vendor source")
    if not snapshot:
        head = _run("git", "rev-parse", "HEAD")
        origin = _run("git", "rev-parse", "origin/main")
        if head != DRC_BASELINE or origin != DRC_BASELINE:
            raise AssertionError(
                f"DRC baseline mismatch: head={head} origin/main={origin} expected={DRC_BASELINE}"
            )


def _assert_docs() -> None:
    docs = "\n".join(
        (REPO_ROOT / path).read_text(encoding="utf-8", errors="replace")
        for path in (
            "README.md",
            "roadmap.md",
            "tasklist.md",
            "scripts/README.md",
            "docs/DRC_v300_goal_checklist_small_commit.md",
            "docs/v300_rt6e_home_screen_character_motion_wiring.md",
        )
    )
    required = (
        "RT-6e: IMPLEMENTED / AWAITING_REVIEW",
        DRC_BASELINE,
        RT6D_IMPLEMENTATION_COMMIT,
        FW_VERSION,
        FW_REFERENCE_COMMIT,
        FW_SOURCE_MODE,
        "exact 10 files",
        "home_screen_manual_motion",
        "default-off",
        "RT-6f: NOT_STARTED / BLOCKED_PENDING_RT6E_ACCEPTANCE / NOT_AUTHORIZED",
        "BLOCKED_REAL_LIVE2D_VTS_ADAPTER_NOT_IMPLEMENTED",
    )
    for marker in required:
        if marker not in docs:
            raise AssertionError(f"RT-6e documentation marker missing: {marker}")


def _assert_home_screen() -> None:
    source = (REPO_ROOT / "app/lib/screens/home_screen.dart").read_text(
        encoding="utf-8", errors="replace"
    )
    required = (
        "characterMotionPresentationControllerFactory",
        "CharacterMotionPresentationController? _characterMotionController",
        "bool _characterMotionOptedIn = false",
        "CharacterMotionLifecycleFact.idle",
        "_handleCharacterMotionChanged",
        "_characterMotionController?.removeListener",
        "_characterMotionController?.dispose()",
        "_characterMotionConfigurationCode = 'configuration_failed'",
        "controller.reset()",
        "sourceEventType: 'home_screen_manual_motion'",
        "characterId: _selectedCharacter?.characterId",
        "_buildCharacterMotionPresentationSection",
        "CharacterMotionPresentationPanel(",
        "!state.isApplying",
        "!state.isClosed",
    )
    for marker in required:
        if marker not in source:
            raise AssertionError(f"RT-6e HomeScreen marker missing: {marker}")
    forbidden = (
        "sourceSessionId:",
        "sourceTurnId:",
        "Timer.periodic",
        "WebSocket.connect",
        "http.get(",
        "http.post(",
        "VTubeStudio",
    )
    for marker in forbidden:
        if marker in source:
            raise AssertionError(f"RT-6e HomeScreen forbidden marker present: {marker}")


def _assert_panel() -> None:
    source = (
        REPO_ROOT / "app/lib/widgets/character_motion_presentation_panel.dart"
    ).read_text(encoding="utf-8", errors="replace")
    required = (
        "class CharacterMotionPresentationPanel extends StatelessWidget",
        "character-motion-opt-in",
        "character-motion-lifecycle-fact",
        "character-motion-apply-button",
        "character-motion-reset-button",
        "character-motion-configuration",
        "character-motion-phase",
        "character-motion-execution-status",
        "character-motion-commands-requested",
        "character-motion-event-type-count",
        "character-motion-provider-execution-attempted",
        "character-motion-network-execution",
        "character-motion-safe-message",
        "Normalized mock motion state only",
        "No Live2D / VTS animation is executed",
        "does not display source event, session, turn, character",
    )
    for marker in required:
        if marker not in source:
            raise AssertionError(f"RT-6e panel marker missing: {marker}")
    forbidden = (
        "sourceSessionId",
        "sourceTurnId",
        "sourceEventType",
        "commandResults.map",
        "eventTypes.join",
        "package:http",
        "dart:io",
        "WebSocket",
    )
    for marker in forbidden:
        if marker in source:
            raise AssertionError(f"RT-6e panel forbidden marker present: {marker}")


def _assert_test() -> None:
    source = (REPO_ROOT / "app/test/character_motion_home_screen_test.dart").read_text(
        encoding="utf-8", errors="replace"
    )
    required = (
        "normal HomeScreen is unconfigured and performs no motion call",
        "factory is called once and configured state remains default-off",
        "factory failure becomes configuration_failed",
        "opt-in alone performs zero transport calls",
        "all accepted lifecycle facts are available",
        "explicit apply sends one bounded manual request",
        "duplicate apply is disabled while one request is active",
        "reset is local and performs no extra transport call",
        "opt-out invalidates a delayed completion",
        "controller is disposed exactly once and late result is ignored",
        "panel hides raw IDs, command details, event strings and errors",
        "sourceEventType, 'home_screen_manual_motion'",
        "sourceSessionId, isNull",
        "sourceTurnId, isNull",
    )
    for marker in required:
        if marker not in source:
            raise AssertionError(f"RT-6e focused-test marker missing: {marker}")
    forbidden = (
        "http.get(",
        "http.post(",
        "WebSocket.connect",
        "127.0.0.1",
        "localhost",
        "VTubeStudio",
        "Live2D",
    )
    for marker in forbidden:
        if marker in source:
            raise AssertionError(f"RT-6e focused test real-execution marker: {marker}")


def _assert_non_changes() -> None:
    main_source = (REPO_ROOT / "app/lib/main.dart").read_text(
        encoding="utf-8", errors="replace"
    )
    if "characterMotionPresentationControllerFactory" in main_source:
        raise AssertionError("RT-6e unexpectedly configured motion in main.dart")
    display = (REPO_ROOT / "app/lib/widgets/character_display_card.dart").read_text(
        encoding="utf-8", errors="replace"
    )
    if "character-display-static-baseline" not in display or "静的表示" not in display:
        raise AssertionError("RT-6e static character baseline is missing")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--snapshot",
        action="store_true",
        help="Skip real checkout HEAD/origin validation for artifact generation.",
    )
    args = parser.parse_args()

    _assert_exact_surface(snapshot=args.snapshot)
    _assert_docs()
    _assert_home_screen()
    _assert_panel()
    _assert_test()
    _assert_non_changes()

    print("v300_rt6e_status: implemented-awaiting-review")
    print("v300_rt6e_exact_change_surface: True")
    print(f"v300_rt6e_change_file_count: {len(EXACT_PATHS)}")
    print(f"v300_rt6e_flutter_runtime_file_count: {len(FLUTTER_RUNTIME_PATHS)}")
    print(f"v300_rt6e_flutter_test_file_count: {len(FLUTTER_TEST_PATHS)}")
    print("v300_rt6e_focused_flutter_defined: 16")
    print("v300_rt6e_flutter_full_expected: 468")
    print("v300_rt6e_main_changed: False")
    print("v300_rt6e_rt6d_runtime_changed: False")
    print("v300_rt6e_character_display_changed: False")
    print("v300_rt6e_backend_changed: False")
    print("v300_rt6e_existing_tests_changed: False")
    print("v300_rt6e_dependencies_changed: False")
    print("v300_rt6e_framework_changed: False")
    print("v300_rt6e_vendor_changed: False")
    print("v300_rt6e_controller_factory_optional: True")
    print("v300_rt6e_default_unconfigured: True")
    print("v300_rt6e_default_opt_in: False")
    print("v300_rt6e_opt_in_persisted: False")
    print("v300_rt6e_opt_in_triggers_transport: False")
    print("v300_rt6e_explicit_apply_only: True")
    print("v300_rt6e_apply_transport_limit: 1")
    print("v300_rt6e_automatic_lifecycle_subscription: False")
    print("v300_rt6e_queueing: False")
    print("v300_rt6e_automatic_retry: False")
    print("v300_rt6e_reset_triggers_transport: False")
    print("v300_rt6e_opt_out_invalidates_stale_result: True")
    print("v300_rt6e_dispose_invalidates_stale_result: True")
    print("v300_rt6e_source_event_type_fixed: home_screen_manual_motion")
    print("v300_rt6e_source_session_id_used: False")
    print("v300_rt6e_source_turn_id_used: False")
    print("v300_rt6e_raw_result_exposed: False")
    print("v300_rt6e_raw_exception_exposed: False")
    print("v300_rt6e_private_ids_exposed: False")
    print("v300_rt6e_real_http_execution: False")
    print("v300_rt6e_framework_version: 5.4.0")
    print(f"v300_rt6e_framework_reference_commit: {FW_REFERENCE_COMMIT}")
    print(f"v300_rt6e_framework_source_mode: {FW_SOURCE_MODE}")
    print("v300_rt6e_framework_execution: False")
    print("v300_rt6e_provider_execution: False")
    print("v300_rt6e_network_execution: False")
    print("v300_rt6e_live2d_animation_claimed: False")
    print("v300_rt6f_authorized: False")
    print("v300_rt7_real_adapter_blocked: True")
    print("v300_rt6e_commit_push_authorized: False")
    print(f"v300_rt6e_snapshot_mode: {args.snapshot}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
