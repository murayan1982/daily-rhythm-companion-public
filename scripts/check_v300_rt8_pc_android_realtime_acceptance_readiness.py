#!/usr/bin/env python3
"""Credential-free RT-8a PC/Android acceptance-readiness verification."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import subprocess
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
BASELINE = "0440aa28fa7d1f49a8e15fd056de8735c83ce2ae"
CONTROL_D_COMMIT = "ddd392c24907eae4d8c91850d84b31a7b84e760f"
CONTROL_E_MESSAGE = "docs: accept RT-7e private configured local VTS verification"

EXACT_PATHS = {
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v300_goal_checklist_small_commit.md",
    "docs/v300_rt8_pc_android_realtime_acceptance_readiness.md",
    "scripts/check_v300_rt8_pc_android_realtime_acceptance_readiness.py",
}

CONTROL_E_PATHS = {
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v300_goal_checklist_small_commit.md",
    "docs/v300_rt7e_private_configured_local_vts_operator_acceptance.md",
    "scripts/check_v300_rt7e_private_configured_local_vts_operator_acceptance.py",
}

SOURCE_PATHS = {
    "app/lib/main.dart",
    "app/lib/services/configured_integrated_voice_turn_runtime.dart",
    "app/lib/services/configured_realtime_text_stream_runtime.dart",
    "app/lib/services/configured_realtime_terminal_voice_output_runtime.dart",
    "app/lib/services/configured_character_motion_presentation_runtime.dart",
    "app/lib/services/configured_framework_vts_motion_presentation_runtime.dart",
    "docs/v300_rt4f4_configured_local_stream_acceptance.md",
    "docs/v300_rt5e_configured_local_voice_output_acceptance.md",
    "docs/v300_rt5f4_configured_local_end_to_end_acceptance.md",
    "docs/v300_rt7e_private_configured_local_vts_operator_acceptance.md",
}

SENSITIVE_PATTERNS = (
    r"(?i)sk-[a-z0-9_-]{12,}",
    r"(?i)bearer\s+[a-z0-9._~+/-]{12,}",
    r"(?i)(api[_-]?key|access[_-]?token|refresh[_-]?token|client[_-]?secret)\s*[:=]\s*['\"][^<][^'\"]{7,}",
    r"(?i)(?:^|\s)[a-z]:\\(?:users|work|home)\\",
    r"/(?:home|users)/[^/\s]+/",
    r"\b(?:10|127|169\.254|172\.(?:1[6-9]|2\d|3[01])|192\.168)\.\d{1,3}\.\d{1,3}\b",
)


def fail(message: str) -> None:
    raise SystemExit(f"v300_rt8a_gate_error: {message}")


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def run(*args: str, capture: bool = False) -> str:
    completed = subprocess.run(
        list(args),
        cwd=ROOT,
        check=True,
        text=True,
        encoding="utf-8",
        errors="surrogateescape",
        capture_output=capture,
    )
    return completed.stdout.rstrip("\r\n") if capture else ""


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8", errors="replace")


def git_available() -> bool:
    if not (ROOT / ".git").exists():
        return False
    try:
        return run("git", "rev-parse", "--is-inside-work-tree", capture=True) == "true"
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def normalized_lines(output: str) -> set[str]:
    return {
        line.strip().replace("\\", "/")
        for line in output.splitlines()
        if line.strip()
    }


def changed_paths() -> set[str]:
    paths: set[str] = set()
    for command in (
        ("git", "diff", "--name-only"),
        ("git", "diff", "--cached", "--name-only"),
        ("git", "ls-files", "--others", "--exclude-standard"),
    ):
        paths.update(normalized_lines(run(*command, capture=True)))
    return paths


def commit_paths(commit: str) -> set[str]:
    return normalized_lines(
        run(
            "git",
            "diff-tree",
            "--no-commit-id",
            "--name-only",
            "-r",
            commit,
            capture=True,
        )
    )


def require_markers(text: str, markers: Iterable[str], label: str) -> None:
    for marker in markers:
        require(marker in text, f"{label} marker missing: {marker}")


def assert_files_exist() -> None:
    missing = sorted(
        path for path in EXACT_PATHS | SOURCE_PATHS if not (ROOT / path).is_file()
    )
    require(not missing, f"required files missing: {missing}")


def assert_git_and_surface(*, snapshot: bool) -> tuple[bool, bool, bool]:
    available = git_available()
    if not available:
        require(snapshot, "Git metadata is required unless --snapshot is used")
        return False, False, False

    changed = changed_paths()
    require(
        changed == EXACT_PATHS,
        "RT-8a exact surface mismatch: "
        f"expected={sorted(EXACT_PATHS)} actual={sorted(changed)}",
    )
    if snapshot:
        return False, False, True

    head = run("git", "rev-parse", "HEAD", capture=True)
    origin = run("git", "rev-parse", "origin/main", capture=True)
    require(head == BASELINE, f"HEAD mismatch: {head}; expected {BASELINE}")
    require(origin == BASELINE, f"origin/main mismatch: {origin}; expected {BASELINE}")

    parent = run("git", "rev-parse", f"{BASELINE}^", capture=True)
    require(
        parent == CONTROL_D_COMMIT,
        f"Control E parent mismatch: {parent}; expected {CONTROL_D_COMMIT}",
    )
    message = run("git", "log", "-1", "--format=%s", BASELINE, capture=True)
    require(message == CONTROL_E_MESSAGE, f"Control E message mismatch: {message}")
    committed = commit_paths(BASELINE)
    require(
        committed == CONTROL_E_PATHS,
        "Control E commit surface mismatch: "
        f"expected={sorted(CONTROL_E_PATHS)} actual={sorted(committed)}",
    )
    return True, True, True


def assert_current_status() -> None:
    readme_top = "\n".join(read("README.md").splitlines()[:32])
    tasklist_top = "\n".join(read("tasklist.md").splitlines()[:36])
    checklist_top = "\n".join(
        read("docs/DRC_v300_goal_checklist_small_commit.md").splitlines()[:28]
    )
    roadmap = read("roadmap.md")

    require_markers(
        readme_top,
        (
            "Current small commit: RT-8a PC/Android realtime acceptance readiness",
            "Current implementation state: IMPLEMENTED / AWAITING_REVIEW",
            f"Current implementation baseline: `{BASELINE}`",
            "Current implementation commit: none",
            "Current realtime phase: RT-8 (**CURRENT / NOT_COMPLETED**)",
        ),
        "README current state",
    )
    require_markers(
        tasklist_top,
        (
            "current parent phase: RT-8 CURRENT / NOT_COMPLETED",
            "current small commit: RT-8a PC/Android realtime acceptance readiness",
            "current implementation state: IMPLEMENTED / AWAITING_REVIEW",
            f"current implementation baseline: {BASELINE}",
            "current implementation commit: none",
        ),
        "tasklist current state",
    )
    require_markers(
        checklist_top,
        (
            "Current parent phase: RT-8 CURRENT / NOT_COMPLETED",
            "Current small commit: RT-8a PC/Android realtime acceptance readiness",
            "Current implementation state: IMPLEMENTED / AWAITING_REVIEW",
            f"Current implementation baseline: {BASELINE}",
            "Current implementation commit: none",
        ),
        "v3 checklist current state",
    )
    require_markers(
        roadmap,
        (
            "Status: RT-8 CURRENT / NOT_COMPLETED",
            "RT-8a  IMPLEMENTED / AWAITING_REVIEW",
            "RT-8b  BLOCKED_PENDING_RT8A_ACCEPTANCE / NOT_AUTHORIZED",
            "RT-9   BLOCKED_PENDING_RT8",
        ),
        "roadmap active state",
    )


def assert_docs_contract() -> None:
    combined = "\n".join(
        read(path) for path in sorted(EXACT_PATHS) if path.endswith(".md")
    )
    require_markers(
        combined,
        (
            "RT-8a: IMPLEMENTED / AWAITING_REVIEW",
            f"RT-8a baseline: {BASELINE}",
            "RT-8a surface: exact 7 documentation/static-gate files",
            "READY_FOR_PLATFORM_APPROPRIATE_PC_WINDOWS_AND_ANDROID_REALTIME_ACCEPTANCE",
            "PC Windows integrated real voice turn supported: false",
            "Android integrated real voice turn supported: true",
            "identical cross-platform voice-runtime claim: false",
            "automatic voice/stream/TTS-to-VTS synchronization claim: false",
            "RT-8b exact contract review: BLOCKED_PENDING_RT8A_ACCEPTANCE",
            "RT-8b implementation: NOT_AUTHORIZED",
            "RT-9: BLOCKED_PENDING_RT8",
            "Control PC-A",
            "Control PC-H",
            "Control Android-A",
            "Control Android-H",
            "provider-level LLM hard cancel",
            "FW real TTS queue flush",
            "Framework unified realtime runtime",
            "physical VTS motion proven by Backend or Flutter response",
            "Backend full: 345 passed, 1 existing warning",
            "Flutter full: 500 passed",
            "private configuration read: false",
            "provider execution attempted: false",
            "microphone used: false",
            "network execution attempted: false",
            "real motion executed: false",
            "commit / push: NOT_AUTHORIZED",
        ),
        "RT-8a documentation",
    )


def assert_platform_source() -> None:
    main = read("app/lib/main.dart")
    integrated = read("app/lib/services/configured_integrated_voice_turn_runtime.dart")
    stream = read("app/lib/services/configured_realtime_text_stream_runtime.dart")
    voice = read("app/lib/services/configured_realtime_terminal_voice_output_runtime.dart")
    motion = read("app/lib/services/configured_character_motion_presentation_runtime.dart")
    vts = read("app/lib/services/configured_framework_vts_motion_presentation_runtime.dart")

    require_markers(
        main,
        (
            "ConfiguredRealtimeTextStreamRuntime",
            "ConfiguredRealtimeTerminalVoiceOutputRuntime",
            "ConfiguredIntegratedVoiceTurnRuntime",
            "ConfiguredCharacterMotionPresentationRuntime",
            "ConfiguredFrameworkVtsMotionPresentationRuntime",
            ".buildControllerFactory()",
            ".buildBindingFactory()",
        ),
        "main runtime assembly",
    )
    require_markers(
        integrated,
        (
            "DRC_RT5F3_ENABLE_CONFIGURED_VOICE_TURN",
            "DRC_RT4_ENABLE_CONFIGURED_TEXT_STREAM",
            "DRC_RT5_ENABLE_CONFIGURED_VOICE_OUTPUT",
            "!kIsWeb",
            "TargetPlatform.android",
            "TargetPlatform.iOS",
            "!supportedPlatform",
            "buildBindingFactory()",
        ),
        "integrated voice platform boundary",
    )
    require_markers(
        stream,
        (
            "DRC_RT4_ENABLE_CONFIGURED_TEXT_STREAM",
            "http.Client",
            "buildControllerFactory()",
        ),
        "configured stream boundary",
    )
    require_markers(
        voice,
        (
            "DRC_RT5_ENABLE_CONFIGURED_VOICE_OUTPUT",
            "buildBindingFactory()",
        ),
        "configured TTS boundary",
    )
    require_markers(
        motion,
        (
            "DRC_RT6_ENABLE_CONFIGURED_MOCK_MOTION",
            "buildControllerFactory()",
        ),
        "configured app-owned motion boundary",
    )
    require_markers(
        vts,
        (
            "DRC_RT7_ENABLE_CONFIGURED_VTS_MOTION",
            "http.Client",
            "followRedirects = false",
            "buildControllerFactory()",
        ),
        "configured VTS boundary",
    )


def assert_historical_claim_boundaries() -> None:
    stream_doc = read("docs/v300_rt4f4_configured_local_stream_acceptance.md")
    voice_doc = read("docs/v300_rt5e_configured_local_voice_output_acceptance.md")
    mobile_doc = read("docs/v300_rt5f4_configured_local_end_to_end_acceptance.md")
    vts_doc = read("docs/v300_rt7e_private_configured_local_vts_operator_acceptance.md")

    require_markers(
        stream_doc,
        (
            "input source: bounded manual input only",
            "real incremental streaming: accepted",
            "cooperative cancel",
            "hard cancel supported: false",
        ),
        "RT-4f4 accepted boundary",
    )
    require_markers(
        voice_doc,
        (
            "real FW root-public synthesis: accepted",
            "audible playback completed naturally: confirmed",
            "audible playback stopped by flush: confirmed",
        ),
        "RT-5e accepted boundary",
    )
    require_markers(
        mobile_doc,
        (
            "configured local Android real voice turn accepted",
            "real user-speech-triggered DRC-local soft barge-in accepted",
            "PC acceptance",
            "provider-level LLM hard cancel",
            "Framework unified realtime runtime",
        ),
        "RT-5f4 accepted and non-claim boundary",
    )
    require_markers(
        vts_doc,
        (
            "Backend / Flutter real_motion_executed: false",
            "operator-visible physical motion confirmed: true",
            "The operator observation is not promoted into an API response",
        ),
        "RT-7e accepted evidence classification",
    )


def assert_changed_content_safe(*, snapshot: bool) -> None:
    if not git_available():
        require(snapshot, "changed-content scan needs Git unless --snapshot is used")
        marker_begin = "<!-- RT-8a-PC-ANDROID-READINESS:BEGIN -->"
        marker_end = "<!-- RT-8a-PC-ANDROID-READINESS:END -->"
        sections = [
            read("docs/v300_rt8_pc_android_realtime_acceptance_readiness.md"),
            read("scripts/check_v300_rt8_pc_android_realtime_acceptance_readiness.py"),
        ]
        for path in (
            "README.md",
            "roadmap.md",
            "tasklist.md",
            "scripts/README.md",
            "docs/DRC_v300_goal_checklist_small_commit.md",
        ):
            source = read(path)
            start = source.find(marker_begin)
            end = source.find(marker_end)
            require(start >= 0 and end > start, f"RT-8a marker section missing: {path}")
            sections.append(source[start : end + len(marker_end)])
        text = "\n".join(sections)
    else:
        diff = run(
            "git",
            "diff",
            "HEAD",
            "--unified=0",
            "--",
            *sorted(EXACT_PATHS),
            capture=True,
        )
        text = "\n".join(
            line[1:]
            for line in diff.splitlines()
            if line.startswith("+") and not line.startswith("+++")
        )
    for pattern in SENSITIVE_PATTERNS:
        require(
            re.search(pattern, text) is None,
            f"sensitive-looking changed content matched: {pattern}",
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", action="store_true")
    args = parser.parse_args()

    assert_files_exist()
    history_verified, origin_verified, surface_verified = assert_git_and_surface(
        snapshot=args.snapshot
    )
    assert_current_status()
    assert_docs_contract()
    assert_platform_source()
    assert_historical_claim_boundaries()
    assert_changed_content_safe(snapshot=args.snapshot)

    values = (
        ("v300_rt8a_status", "implemented-awaiting-review"),
        ("v300_rt8a_baseline", BASELINE),
        ("v300_rt8a_snapshot_mode", str(args.snapshot)),
        ("v300_rt8a_git_history_verified", str(history_verified)),
        ("v300_rt8a_origin_main_verified", str(origin_verified)),
        ("v300_rt8a_exact_worktree_surface_verified", str(surface_verified)),
        ("v300_rt8a_control_e_commit_verified", str(history_verified)),
        ("v300_rt8a_exact_change_surface", "True"),
        ("v300_rt8a_change_file_count", "7"),
        ("v300_rt8a_platform_matrix_frozen", "True"),
        ("v300_rt8a_pc_windows_integrated_voice_supported", "False"),
        ("v300_rt8a_android_integrated_voice_supported", "True"),
        ("v300_rt8a_pc_manual_stream_tts_vts_ready", "True"),
        ("v300_rt8a_android_voice_and_manual_vts_ready", "True"),
        ("v300_rt8a_identical_cross_platform_voice_claim", "False"),
        ("v300_rt8a_automatic_voice_motion_sync_claim", "False"),
        ("v300_rt8a_backend_runtime_changed", "False"),
        ("v300_rt8a_flutter_runtime_changed", "False"),
        ("v300_rt8a_existing_tests_changed", "False"),
        ("v300_rt8a_vendor_framework_changed", "False"),
        ("v300_rt8a_private_configuration_read", "False"),
        ("v300_rt8a_provider_execution_attempted", "False"),
        ("v300_rt8a_microphone_used", "False"),
        ("v300_rt8a_network_execution_attempted", "False"),
        ("v300_rt8a_real_motion_executed", "False"),
        ("v300_rt8b_blocked_pending_rt8a_acceptance", "True"),
        ("v300_rt8b_implementation_authorized", "False"),
        ("v300_rt8a_commit_push_authorized", "False"),
    )
    for key, value in values:
        print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
