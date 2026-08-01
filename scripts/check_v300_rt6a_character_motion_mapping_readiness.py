# Validate DRC v3.0.0 RT-6a character-motion mapping readiness candidate.

from __future__ import annotations

import argparse
import os
from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parents[1]
DRC_BASELINE_HEAD = "ca1bd17ed32aba1e6b7d4dfd4f8eea3f10652ef7"
FW_HEAD = "d313eb6acb643103fe25988720ebee5976a04f78"

EXPECTED_PATHS = {
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v300_goal_checklist_small_commit.md",
    "docs/v300_rt6a_character_motion_mapping_readiness.md",
    "scripts/check_v300_rt6a_character_motion_mapping_readiness.py",
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
    return (root / relative).read_text(encoding="utf-8")


def require(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise AssertionError(f"Missing {label}: {needle!r}")


def forbid(text: str, needle: str, label: str) -> None:
    if needle in text:
        raise AssertionError(f"Unexpected {label}: {needle!r}")


def changed_paths() -> set[str]:
    output = run(
        "git",
        "status",
        "--porcelain",
        "--untracked-files=all",
        capture=True,
    )
    paths: set[str] = set()
    for line in output.splitlines():
        if not line:
            continue
        path = line[3:]
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        paths.add(path.replace("\\", "/"))
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
    raise AssertionError(
        "Set FRAMEWORK_ROOT to the clean FW v5.4.0 checkout."
    )


def assert_repository_state(*, snapshot: bool) -> Path | None:
    actual = changed_paths()
    if actual != EXPECTED_PATHS:
        raise AssertionError(
            f"RT-6a changed surface mismatch: {sorted(actual)}"
        )
    if snapshot:
        return None

    if run("git", "rev-parse", "HEAD", capture=True) != DRC_BASELINE_HEAD:
        raise AssertionError("Unexpected DRC baseline HEAD.")
    if run("git", "rev-parse", "origin/main", capture=True) != DRC_BASELINE_HEAD:
        raise AssertionError("Unexpected DRC origin/main.")

    fw_root = resolve_framework_root()
    if run("git", "rev-parse", "HEAD", cwd=fw_root, capture=True) != FW_HEAD:
        raise AssertionError("Unexpected FW HEAD.")
    if run("git", "rev-list", "-n", "1", "v5.4.0", cwd=fw_root, capture=True) != FW_HEAD:
        raise AssertionError("Unexpected FW v5.4.0 tag target.")
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


def assert_changed_content_safe() -> None:
    diff = run(
        "git",
        "diff",
        "HEAD",
        "--unified=0",
        "--",
        *sorted(EXPECTED_PATHS),
        capture=True,
    )
    added_lines = [
        line[1:]
        for line in diff.splitlines()
        if line.startswith("+") and not line.startswith("+++")
    ]
    untracked = set(
        run(
            "git",
            "ls-files",
            "--others",
            "--exclude-standard",
            capture=True,
        ).splitlines()
    )
    for relative in sorted(EXPECTED_PATHS & untracked):
        added_lines.append(read(relative))
    added = "\n".join(added_lines)
    for pattern in SENSITIVE_PATTERNS:
        if re.search(pattern, added):
            raise AssertionError(
                f"Sensitive-looking value in RT-6a added content: {pattern}"
            )


def assert_docs_and_split() -> None:
    sources = {
        "README": read("README.md"),
        "roadmap": read("roadmap.md"),
        "tasklist": read("tasklist.md"),
        "scripts README": read("scripts/README.md"),
        "checklist": read("docs/DRC_v300_goal_checklist_small_commit.md"),
        "contract": read("docs/v300_rt6a_character_motion_mapping_readiness.md"),
    }
    combined = "\n".join(sources.values())
    for marker in (
        "RT-6: CURRENT / NOT_COMPLETED",
        "RT-6a: IMPLEMENTED / AWAITING_REVIEW",
        "RT-6b through RT-6f: NOT_STARTED / NOT_AUTHORIZED",
        "RT-7: BLOCKED_REAL_LIVE2D_VTS_ADAPTER_NOT_IMPLEMENTED",
        DRC_BASELINE_HEAD,
        FW_HEAD,
        "exact seven docs/static-gate files",
        "READY_FOR_RT6_APP_OWNED_MOCK_SAFE_MAPPING_WORK",
        "BLOCKED_FOR_REAL_LIVE2D_VTS_EXECUTION",
        "RT-6b — app-owned provider-neutral motion mapping contract",
        "RT-6c — guarded FW root-public mock motion-session adapter",
        "RT-6d — Flutter motion presentation model/client/controller",
        "RT-6e — default-off HomeScreen character-motion wiring",
        "RT-6f — configured local mock-motion presentation acceptance",
        "RT-6b authorization: blocked pending RT-6a acceptance",
    ):
        require(combined, marker, f"RT-6a documentation marker {marker}")

    for relative in sorted(EXPECTED_PATHS):
        require(combined, relative, f"exact path {relative}")

    for marker in (
        "Current small commit: RT-5f4 acceptance-state sync awaiting review",
        "RT-6  NOT_STARTED / READY_FOR_EXACT_CONTRACT_REVIEW / NOT_AUTHORIZED",
    ):
        forbid(sources["README"], marker, f"stale README marker {marker}")


def assert_existing_drc_motion_boundary() -> None:
    api = read("backend/app/api/motion_demo.py")
    service = read("backend/app/services/motion_demo_service.py")
    model = read("backend/app/models/motion_demo.py")

    require(api, '@router.get("/demo/motion/status"', "motion status route")
    require(api, '@router.post("/demo/motion"', "motion request route")
    for marker in (
        '"greeting"',
        '"thinking"',
        '"happy"',
        '"tired_supportive"',
        '"speaking"',
        '"idle"',
        'accepted=False',
        'request_state="not_started"',
        'motion_sent=False',
        'vts_connection_used=False',
    ):
        require(service, marker, f"metadata-only motion marker {marker}")
    require(model, "class MotionDemoRequest", "motion request model")
    require(model, "class MotionDemoRequestResponse", "motion response model")

    for marker in (
        "\nfrom framework",
        "\nimport framework",
        "create_motion_session",
        "MotionSession(",
        "pyvts",
        "websocket",
    ):
        forbid(service, marker, f"wired motion execution marker {marker}")


def assert_existing_flutter_presentation() -> None:
    presentation = read("app/lib/models/character_display_presentation.dart")
    widget = read("app/lib/widgets/character_display_card.dart")
    player = read("app/lib/services/voice_output_audio_player.dart")

    require(
        presentation,
        "enum CharacterDisplayActivityState",
        "character display activity enum",
    )
    for marker in ("idle,", "loading,", "speaking,"):
        require(presentation, marker, f"character activity {marker}")
    require(
        presentation,
        "playbackPhase == VoiceOutputPlaybackPhase.playing",
        "playback speaking mapping",
    )
    require(widget, "CharacterDisplayActivityState.speaking", "speaking widget state")
    require(player, "enum VoiceOutputPlaybackPhase", "voice playback phase")

    future_paths = (
        "app/lib/models/realtime_character_motion.dart",
        "app/lib/services/realtime_character_motion_client.dart",
        "app/lib/services/realtime_character_motion_controller.dart",
        "app/lib/services/framework_motion_session_adapter.dart",
    )
    existing = [path for path in future_paths if (ROOT / path).exists()]
    if existing:
        raise AssertionError(f"Unexpected RT-6 runtime paths already exist: {existing}")


def assert_framework_public_motion(fw_root: Path) -> None:
    root_public = read("framework/__init__.py", root=fw_root)
    motion = read("framework/motion.py", root=fw_root)
    session = read("framework/motion_session.py", root=fw_root)

    for marker in (
        "MotionAdapterStatus",
        "MotionCapability",
        "MotionErrorCode",
        "MotionEventType",
        "MotionIntent",
        "MotionOutcome",
        "MotionRequest",
        "MotionResult",
        "MotionState",
        "MotionSession",
        "MotionSessionInfo",
        "create_motion_session",
    ):
        require(root_public, marker, f"FW root-public symbol {marker}")

    for marker in (
        'MOCK_AVAILABLE = "mock_available"',
        'NOT_IMPLEMENTED = "not_implemented"',
        'EXPRESSION = "expression"',
        'EMOTION = "emotion"',
        'SPEAKING_STATE = "speaking_state"',
        'IDLE_MOTION = "idle_motion"',
        'STOP_MOTION = "stop_motion"',
        "supports_real_adapter: bool = False",
        "def mock_available",
    ):
        require(motion, marker, f"FW motion contract {marker}")

    for marker in (
        "Public motion session skeleton.",
        'adapter == "mock" and not self._real_adapter_enabled',
        "MotionCapability.mock_available()",
        "MotionAdapterStatus.NOT_IMPLEMENTED",
        "real_adapter_supported=capability.supports_real_adapter",
        "def on_event",
        "def apply_motion",
        "def create_motion_session",
    ):
        require(session, marker, f"FW mock motion session {marker}")

    for marker in ("import pyvts", "import websocket", "from pyvts"):
        forbid(session, marker, f"FW public session provider import {marker}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--snapshot",
        action="store_true",
        help="Skip DRC/FW commit/tag/worktree checks for extracted snapshot review.",
    )
    args = parser.parse_args()

    fw_root = assert_repository_state(snapshot=args.snapshot)
    assert_changed_content_safe()
    assert_docs_and_split()
    assert_existing_drc_motion_boundary()
    assert_existing_flutter_presentation()
    if fw_root is not None:
        assert_framework_public_motion(fw_root)

    print("v300_rt6a_status: implemented-awaiting-review")
    print("v300_rt6a_exact_change_surface: True")
    print("v300_rt6a_change_file_count: 7")
    print("v300_rt6a_backend_runtime_changed: False")
    print("v300_rt6a_flutter_runtime_changed: False")
    print("v300_rt6a_existing_tests_changed: False")
    print("v300_rt6a_framework_changed: False")
    print("v300_rt6a_dependencies_changed: False")
    print("v300_rt6a_existing_motion_demo_boundary_exists: True")
    print("v300_rt6a_existing_motion_demo_is_metadata_only: True")
    print("v300_rt6a_existing_motion_send_enabled: False")
    print("v300_rt6a_existing_vts_connection_enabled: False")
    print("v300_rt6a_static_character_presentation_exists: True")
    print("v300_rt6a_realtime_motion_mapping_exists: False")
    print("v300_rt6a_motion_controller_exists: False")
    print("v300_rt6a_fw_root_public_motion_contract_exists: True")
    print("v300_rt6a_fw_mock_motion_available: True")
    print("v300_rt6a_fw_real_motion_adapter_supported: False")
    print("v300_rt6a_fw_real_motion_adapter_implemented: False")
    print("v300_rt6a_exact_child_split_frozen: True")
    print("v300_rt6a_rt6b_authorized: False")
    print("v300_rt6a_network_execution: False")
    print("v300_rt6a_provider_execution: False")
    print("v300_rt6a_vts_connection_used: False")
    print("v300_rt6a_live2d_runtime_loaded: False")
    print("v300_rt6a_private_credential_read: False")
    print("v300_rt6a_snapshot_mode:", args.snapshot)


if __name__ == "__main__":
    main()
