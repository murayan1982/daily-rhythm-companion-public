# Validate DRC v3.0.0 RT-6b acceptance-state synchronization candidate.

from __future__ import annotations

import argparse
import ast
import os
from pathlib import Path
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.models.character_motion import (  # noqa: E402
    CHARACTER_MOTION_MAX_COMMANDS,
    CharacterMotionCue,
    CharacterMotionLifecycleFact,
    CharacterMotionMappingInput,
    CharacterMotionMappingOutcome,
)
from app.models.realtime import RealtimeState  # noqa: E402
from app.services.character_motion_mapper import CharacterMotionMapper  # noqa: E402


DRC_IMPLEMENTATION_HEAD = "17f0c46eb0b4e26e2fdf5ffd4090c15c69f4e594"
DRC_IMPLEMENTATION_PARENT = "6ed5f2252c6c6f47fc8c50f577c4f20b7fa0cb68"
FW_HEAD = "d313eb6acb643103fe25988720ebee5976a04f78"

EXPECTED_PATHS = {
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v300_goal_checklist_small_commit.md",
    "docs/v300_rt6b_provider_neutral_motion_mapping.md",
    "scripts/check_v300_rt6b_provider_neutral_motion_mapping.py",
}
IMPLEMENTATION_PATHS = EXPECTED_PATHS | {
    "backend/app/models/character_motion.py",
    "backend/app/services/character_motion_mapper.py",
    "backend/tests/test_character_motion_mapper.py",
}
RUNTIME_PATHS = {
    "backend/app/models/character_motion.py",
    "backend/app/services/character_motion_mapper.py",
}
TEST_PATHS = {"backend/tests/test_character_motion_mapper.py"}

SENSITIVE_PATTERNS = (
    r"(?i)sk-[a-z0-9_-]{12,}",
    r"(?i)bearer\s+[a-z0-9._~+/-]{12,}",
    r"(?i)(api[_-]?key|access[_-]?token|refresh[_-]?token|client[_-]?secret)\s*[:=]\s*['\"][^<][^'\"]{7,}",
    r"(?i)(?:^|\s)[a-z]:\\(?:users|work|home)\\",
    r"/(?:home|users)/[^/\s]+/",
    r"\b(?:10|127|169\.254|172\.(?:1[6-9]|2\d|3[01])|192\.168)\.\d{1,3}\.\d{1,3}\b",
)
FORBIDDEN_IMPORT_ROOTS = {
    "framework",
    "httpx",
    "requests",
    "socket",
    "websocket",
    "websockets",
    "pyvts",
}


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


def commit_paths(commit: str) -> set[str]:
    output = run(
        "git",
        "diff-tree",
        "--no-commit-id",
        "--name-only",
        "-r",
        commit,
        capture=True,
    )
    return {line.replace("\\", "/") for line in output.splitlines() if line}


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


def assert_repository_state(*, snapshot: bool) -> Path | None:
    actual = changed_paths()
    if actual != EXPECTED_PATHS:
        raise AssertionError(
            f"RT-6b acceptance-sync surface mismatch: {sorted(actual)}"
        )
    if snapshot:
        return None

    if run("git", "rev-parse", "HEAD", capture=True) != DRC_IMPLEMENTATION_HEAD:
        raise AssertionError("Unexpected DRC RT-6b implementation HEAD.")
    if run("git", "rev-parse", "origin/main", capture=True) != DRC_IMPLEMENTATION_HEAD:
        raise AssertionError("Unexpected DRC origin/main for RT-6b acceptance sync.")
    if run("git", "rev-parse", "HEAD^", capture=True) != DRC_IMPLEMENTATION_PARENT:
        raise AssertionError("Unexpected RT-6b implementation parent.")
    if commit_paths(DRC_IMPLEMENTATION_HEAD) != IMPLEMENTATION_PATHS:
        raise AssertionError("RT-6b implementation commit was not exact ten-file.")

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
    added = "\n".join(
        line[1:]
        for line in diff.splitlines()
        if line.startswith("+") and not line.startswith("+++")
    )
    for pattern in SENSITIVE_PATTERNS:
        if re.search(pattern, added):
            raise AssertionError(
                f"Sensitive-looking value in RT-6b acceptance sync: {pattern}"
            )


def assert_docs() -> None:
    sources = {
        "README": read("README.md"),
        "roadmap": read("roadmap.md"),
        "tasklist": read("tasklist.md"),
        "scripts README": read("scripts/README.md"),
        "checklist": read("docs/DRC_v300_goal_checklist_small_commit.md"),
        "contract": read("docs/v300_rt6b_provider_neutral_motion_mapping.md"),
    }
    combined = "\n".join(sources.values())
    for marker in (
        "RT-6: CURRENT / NOT_COMPLETED",
        "RT-6a: COMPLETED / ACCEPTED / PUSHED",
        "RT-6b: COMPLETED / ACCEPTED / PUSHED",
        "RT-6c: NOT_STARTED / READY_FOR_EXACT_CONTRACT_REVIEW / NOT_AUTHORIZED",
        "RT-6d through RT-6f: NOT_STARTED / NOT_AUTHORIZED",
        "RT-7: BLOCKED_REAL_LIVE2D_VTS_ADAPTER_NOT_IMPLEMENTED",
        DRC_IMPLEMENTATION_PARENT,
        DRC_IMPLEMENTATION_HEAD,
        FW_HEAD,
        "focused Backend: 37 passed",
        "Backend full: 241 passed, 3 dependency warnings",
        "Flutter analyze: No issues found",
        "Flutter full: 411 passed",
        "implementation surface: exact 10 files",
        "acceptance-sync surface: exact 7",
        "motion_active never produces recursive commands",
        "unknown is ignored rather than guessed",
        "RT-6c implementation remains NOT_AUTHORIZED",
        "acceptance-sync commit/push: NOT_AUTHORIZED",
    ):
        require(combined, marker, f"RT-6b acceptance marker {marker}")

    for relative in sorted(EXPECTED_PATHS):
        require(combined, relative, f"acceptance path {relative}")
    for relative in sorted(IMPLEMENTATION_PATHS):
        require(combined, relative, f"implementation path {relative}")

    active_status = "\n".join(
        (
            "\n".join(sources["README"].splitlines()[:25]),
            "\n".join(sources["roadmap"].splitlines()[:18]),
            "\n".join(sources["tasklist"].splitlines()[:25]),
            "\n".join(sources["checklist"].splitlines()[:22]),
        )
    )
    for stale in (
        "RT-6b provider-neutral motion mapping candidate",
        "IMPLEMENTED / AWAITING_REVIEW",
        "Current implementation commit: none",
        "current implementation commit: none",
        "review the exact ten-file RT-6b candidate",
    ):
        forbid(active_status, stale, f"stale active marker {stale}")


def imported_roots(relative: str) -> set[str]:
    tree = ast.parse(read(relative))
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".", 1)[0])
    return roots


def assert_source_boundaries() -> None:
    model_path = "backend/app/models/character_motion.py"
    mapper_path = "backend/app/services/character_motion_mapper.py"
    model = read(model_path)
    mapper = read(mapper_path)
    test = read("backend/tests/test_character_motion_mapper.py")

    for relative in (model_path, mapper_path):
        bad = imported_roots(relative) & FORBIDDEN_IMPORT_ROOTS
        if bad:
            raise AssertionError(f"Forbidden imports in {relative}: {sorted(bad)}")

    for marker in (
        "class CharacterMotionLifecycleFact",
        "class CharacterMotionCue",
        "class CharacterMotionCommandIntent",
        "class CharacterMotionMappingInput",
        "class CharacterMotionCommand",
        "class CharacterMotionPlan",
        'ConfigDict(extra="forbid", frozen=True)',
        "CHARACTER_MOTION_MAX_COMMANDS = 3",
    ):
        require(model, marker, f"model marker {marker}")

    for marker in (
        "class CharacterMotionMapper",
        "def map(",
        "def map_realtime_state(",
        "recursive_motion_fact_ignored",
        "unknown_fact_ignored",
        "idle_restoration",
        "thinking_presentation",
        "speaking_presentation",
        "failure_supportive",
        "terminal_stop_and_reset",
    ):
        require(mapper, marker, f"mapper marker {marker}")

    for marker in (
        "test_exact_lifecycle_mapping",
        "test_recursive_and_unknown_facts_fail_closed",
        "test_realtime_state_mapping_is_complete",
        "test_mapping_is_deterministic_and_preserves_safe_ids",
        "test_only_speaking_fact_sets_speaking_true",
        "test_stop_first_for_interrupted_and_terminal_failures",
        "test_models_reject_arbitrary_metadata_and_oversized_ids",
        "test_rt6b_source_has_no_framework_import",
    ):
        require(test, marker, f"focused test marker {marker}")

    combined = model + "\n" + mapper
    for marker in (
        "create_motion_session",
        "MotionSession(",
        "requests.",
        "httpx.",
        "websocket.",
        "pyvts.",
        "subprocess",
        "os.getenv",
        "datetime.now",
        "uuid4",
        "random.",
    ):
        forbid(combined, marker, f"runtime/execution marker {marker}")


def command_shape(plan) -> list[tuple[str, str | None, str | None, bool | None]]:
    return [
        (
            command.intent.value,
            command.expression_id,
            command.motion_event.value if command.motion_event else None,
            command.speaking,
        )
        for command in plan.commands
    ]


def assert_mapping_contract() -> None:
    mapper = CharacterMotionMapper()
    expected = {
        CharacterMotionLifecycleFact.IDLE: (
            CharacterMotionCue.IDLE,
            [("speaking_state", None, None, False), ("reset_expression", None, None, None), ("idle_motion", None, "idle", None)],
        ),
        CharacterMotionLifecycleFact.LISTENING: (
            CharacterMotionCue.IDLE,
            [("speaking_state", None, None, False), ("expression", "supportive", None, None)],
        ),
        CharacterMotionLifecycleFact.TRANSCRIBING: (
            CharacterMotionCue.THINKING,
            [("speaking_state", None, None, False), ("expression", "thinking", None, None)],
        ),
        CharacterMotionLifecycleFact.THINKING: (
            CharacterMotionCue.THINKING,
            [("speaking_state", None, None, False), ("expression", "thinking", None, None)],
        ),
        CharacterMotionLifecycleFact.RESPONDING: (
            CharacterMotionCue.THINKING,
            [("speaking_state", None, None, False), ("expression", "thinking", None, None)],
        ),
        CharacterMotionLifecycleFact.TTS_PREPARING: (
            CharacterMotionCue.THINKING,
            [("speaking_state", None, None, False), ("expression", "thinking", None, None)],
        ),
        CharacterMotionLifecycleFact.SPEAKING: (
            CharacterMotionCue.SPEAKING,
            [("expression", "speaking", None, None), ("speaking_state", None, None, True)],
        ),
        CharacterMotionLifecycleFact.INTERRUPTED: (
            CharacterMotionCue.IDLE,
            [("stop_motion", None, None, None), ("speaking_state", None, None, False), ("reset_expression", None, None, None)],
        ),
        CharacterMotionLifecycleFact.COMPLETED: (
            CharacterMotionCue.IDLE,
            [("speaking_state", None, None, False), ("reset_expression", None, None, None), ("idle_motion", None, "idle", None)],
        ),
        CharacterMotionLifecycleFact.FAILED: (
            CharacterMotionCue.TIRED_SUPPORTIVE,
            [("stop_motion", None, None, None), ("speaking_state", None, None, False), ("expression", "supportive", None, None)],
        ),
        CharacterMotionLifecycleFact.CLOSED: (
            CharacterMotionCue.IDLE,
            [("stop_motion", None, None, None), ("speaking_state", None, None, False), ("reset_expression", None, None, None)],
        ),
        CharacterMotionLifecycleFact.UNAVAILABLE: (
            CharacterMotionCue.IDLE,
            [("stop_motion", None, None, None), ("speaking_state", None, None, False), ("reset_expression", None, None, None)],
        ),
    }

    for fact, (cue, commands) in expected.items():
        source = CharacterMotionMappingInput(
            fact=fact,
            source_event_type="safe-event",
            session_id="session-1",
            turn_id="turn-1",
            character_id="gentle_mina",
        )
        first = mapper.map(source)
        second = mapper.map(source)
        if first != second:
            raise AssertionError(f"Non-deterministic RT-6b mapping for {fact.value}")
        if first.outcome is not CharacterMotionMappingOutcome.MAPPED:
            raise AssertionError(f"Expected mapped outcome for {fact.value}")
        if first.cue is not cue or command_shape(first) != commands:
            raise AssertionError(f"Unexpected exact mapping for {fact.value}")
        if len(first.commands) > CHARACTER_MOTION_MAX_COMMANDS:
            raise AssertionError(f"Unbounded command plan for {fact.value}")
        if [command.order for command in first.commands] != list(range(1, len(first.commands) + 1)):
            raise AssertionError(f"Unexpected command order for {fact.value}")

    for fact, reason in (
        (CharacterMotionLifecycleFact.MOTION_ACTIVE, "recursive_motion_fact_ignored"),
        (CharacterMotionLifecycleFact.UNKNOWN, "unknown_fact_ignored"),
    ):
        plan = mapper.map(CharacterMotionMappingInput(fact=fact))
        if plan.outcome is not CharacterMotionMappingOutcome.IGNORED:
            raise AssertionError(f"Expected ignored outcome for {fact.value}")
        if plan.reason_code != reason or plan.cue is not None or plan.commands:
            raise AssertionError(f"Unsafe ignored plan for {fact.value}")

    expected_realtime = {
        RealtimeState.IDLE: CharacterMotionLifecycleFact.IDLE,
        RealtimeState.LISTENING: CharacterMotionLifecycleFact.LISTENING,
        RealtimeState.TRANSCRIBING: CharacterMotionLifecycleFact.TRANSCRIBING,
        RealtimeState.THINKING: CharacterMotionLifecycleFact.THINKING,
        RealtimeState.RESPONDING: CharacterMotionLifecycleFact.RESPONDING,
        RealtimeState.SPEAKING: CharacterMotionLifecycleFact.SPEAKING,
        RealtimeState.MOTION: CharacterMotionLifecycleFact.MOTION_ACTIVE,
        RealtimeState.INTERRUPTED: CharacterMotionLifecycleFact.INTERRUPTED,
        RealtimeState.FAILED: CharacterMotionLifecycleFact.FAILED,
        RealtimeState.COMPLETED: CharacterMotionLifecycleFact.COMPLETED,
        RealtimeState.CLOSED: CharacterMotionLifecycleFact.CLOSED,
        RealtimeState.UNAVAILABLE: CharacterMotionLifecycleFact.UNAVAILABLE,
        RealtimeState.UNKNOWN: CharacterMotionLifecycleFact.UNKNOWN,
    }
    for state, fact in expected_realtime.items():
        if mapper.map_realtime_state(state).source_fact is not fact:
            raise AssertionError(f"Unexpected RealtimeState mapping for {state.value}")

    speaking_true_facts = []
    for fact in CharacterMotionLifecycleFact:
        plan = mapper.map(CharacterMotionMappingInput(fact=fact))
        if any(command.speaking is True for command in plan.commands):
            speaking_true_facts.append(fact)
    if speaking_true_facts != [CharacterMotionLifecycleFact.SPEAKING]:
        raise AssertionError("Only speaking lifecycle fact may set speaking=true.")


def assert_existing_boundaries_unchanged() -> None:
    motion_service = read("backend/app/services/motion_demo_service.py")
    realtime_model = read("backend/app/models/realtime.py")
    for marker in (
        'accepted=False',
        'request_state="not_started"',
        'motion_sent=False',
        'vts_connection_used=False',
    ):
        require(motion_service, marker, f"existing metadata-only marker {marker}")
    for marker in (
        'IDLE = "idle"',
        'LISTENING = "listening"',
        'MOTION = "motion"',
        'UNKNOWN = "unknown"',
    ):
        require(realtime_model, marker, f"existing RealtimeState marker {marker}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--snapshot",
        action="store_true",
        help="Skip commit/tag/clean-checkout assertions for extracted snapshots.",
    )
    args = parser.parse_args()

    assert_repository_state(snapshot=args.snapshot)
    assert_changed_content_safe()
    assert_docs()
    assert_source_boundaries()
    assert_mapping_contract()
    assert_existing_boundaries_unchanged()

    markers = {
        "v300_rt6b_status": "completed-accepted-pushed",
        "v300_rt6b_exact_acceptance_sync_surface": True,
        "v300_rt6b_acceptance_sync_file_count": len(EXPECTED_PATHS),
        "v300_rt6b_implementation_commit": DRC_IMPLEMENTATION_HEAD,
        "v300_rt6b_implementation_surface": len(IMPLEMENTATION_PATHS),
        "v300_rt6b_backend_runtime_file_count": len(RUNTIME_PATHS),
        "v300_rt6b_backend_test_file_count": len(TEST_PATHS),
        "v300_rt6b_focused_backend_passed": 37,
        "v300_rt6b_backend_full_passed": 241,
        "v300_rt6b_backend_warning_count": 3,
        "v300_rt6b_flutter_analyze_passed": True,
        "v300_rt6b_flutter_full_passed": 411,
        "v300_rt6b_mapping_deterministic": True,
        "v300_rt6b_max_commands_per_plan": CHARACTER_MOTION_MAX_COMMANDS,
        "v300_rt6b_recursive_motion_fact_ignored": True,
        "v300_rt6b_unknown_fact_ignored": True,
        "v300_rt6b_runtime_changed_by_acceptance_sync": False,
        "v300_rt6b_backend_runtime_changed_by_acceptance_sync": False,
        "v300_rt6b_backend_tests_changed_by_acceptance_sync": False,
        "v300_rt6b_api_routes_changed": False,
        "v300_rt6b_flutter_changed": False,
        "v300_rt6b_framework_changed": False,
        "v300_rt6b_dependencies_changed": False,
        "v300_rt6b_network_execution": False,
        "v300_rt6b_provider_execution": False,
        "v300_rt6b_vts_connection_used": False,
        "v300_rt6b_live2d_runtime_loaded": False,
        "v300_rt6_status": "current-not-completed",
        "v300_rt6c_status": "ready-for-exact-contract-review-not-authorized",
        "v300_rt6c_implementation_authorized": False,
        "v300_rt7_real_adapter_blocked": True,
        "v300_rt6b_acceptance_sync_commit_push_authorized": False,
        "v300_rt6b_snapshot_mode": args.snapshot,
    }
    for key, value in markers.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
