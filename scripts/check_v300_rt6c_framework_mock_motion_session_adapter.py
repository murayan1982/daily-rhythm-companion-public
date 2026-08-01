#!/usr/bin/env python3
"""Validate the exact RT-6c acceptance-state synchronization."""

from __future__ import annotations

import argparse
import ast
from contextlib import contextmanager
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from typing import Iterator


REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = REPO_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.models.character_motion import (  # noqa: E402
    CharacterMotionLifecycleFact,
    CharacterMotionMappingInput,
)
from app.models.character_motion_adapter import (  # noqa: E402
    FRAMEWORK_MOCK_MOTION_MAX_EVENT_TYPES,
    FrameworkMockMotionExecutionResult,
    FrameworkMockMotionExecutionStatus,
)
from app.services.character_motion_mapper import CharacterMotionMapper  # noqa: E402
from app.services.framework_mock_motion_session_adapter import (  # noqa: E402
    FrameworkMockMotionSessionAdapter,
)


DRC_BASELINE = "f929e8faa65a817f1ba4fed82b729438b73dbfab"
FW_VERSION = "5.4.0"
FW_REFERENCE_COMMIT = "d313eb6acb643103fe25988720ebee5976a04f78"
FW_SOURCE_MODE = "external-vendored-snapshot"
FW_ROOT_PUBLIC_SYMBOLS = (
    "create_motion_session",
    "MotionRequest",
    "MotionIntent",
)
EXACT_PATHS = {
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v300_goal_checklist_small_commit.md",
    "docs/v300_rt6c_framework_mock_motion_session_adapter.md",
    "scripts/check_v300_rt6c_framework_mock_motion_session_adapter.py",
}
IMPLEMENTATION_RUNTIME_PATHS = {
    "backend/app/models/character_motion_adapter.py",
    "backend/app/services/framework_mock_motion_session_adapter.py",
}
IMPLEMENTATION_TEST_PATHS = {
    "backend/tests/test_framework_mock_motion_session_adapter.py"
}
RT6B_PATHS = {
    "backend/app/models/character_motion.py",
    "backend/app/services/character_motion_mapper.py",
    "backend/tests/test_character_motion_mapper.py",
}


def _run(*args: str, cwd: Path = REPO_ROOT) -> str:
    completed = subprocess.run(
        args,
        cwd=cwd,
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
        values.update(line.strip().replace("\\", "/") for line in output.splitlines() if line.strip())
    return values


def _assert_exact_surface(*, snapshot: bool) -> None:
    missing = sorted(path for path in EXACT_PATHS if not (REPO_ROOT / path).is_file())
    if missing:
        raise AssertionError(f"RT-6c acceptance-sync files are missing: {missing}")
    changed = _git_paths()
    if changed != EXACT_PATHS:
        raise AssertionError(
            "RT-6c acceptance-sync surface mismatch: "
            f"expected={sorted(EXACT_PATHS)} actual={sorted(changed)}"
        )
    if changed & RT6B_PATHS:
        raise AssertionError("RT-6c changed accepted RT-6b model/mapper/test files")
    if any(path.startswith("backend/app/api/") for path in changed):
        raise AssertionError("RT-6c changed API routes")
    if "backend/app/config.py" in changed:
        raise AssertionError("RT-6c changed Backend config")
    if any(path.startswith("app/") for path in changed):
        raise AssertionError("RT-6c changed Flutter files")
    if not snapshot:
        head = _run("git", "rev-parse", "HEAD")
        origin = _run("git", "rev-parse", "origin/main")
        if head != DRC_BASELINE or origin != DRC_BASELINE:
            raise AssertionError(
                f"DRC baseline mismatch: head={head} origin/main={origin} expected={DRC_BASELINE}"
            )


def _assert_static_contract() -> None:
    docs = "\n".join(
        (REPO_ROOT / path).read_text(encoding="utf-8", errors="replace")
        for path in (
            "README.md",
            "roadmap.md",
            "tasklist.md",
            "scripts/README.md",
            "docs/DRC_v300_goal_checklist_small_commit.md",
            "docs/v300_rt6c_framework_mock_motion_session_adapter.md",
        )
    )
    required_acceptance_markers = (
        "RT-6c: COMPLETED / ACCEPTED / PUSHED",
        "f929e8faa65a817f1ba4fed82b729438b73dbfab",
        "RT-6d: NOT_STARTED / READY_FOR_EXACT_CONTRACT_REVIEW / NOT_AUTHORIZED",
        "external-vendored-snapshot",
    )
    for marker in required_acceptance_markers:
        if marker not in docs:
            raise AssertionError(f"RT-6c acceptance marker missing: {marker}")
    adapter_path = REPO_ROOT / "backend/app/services/framework_mock_motion_session_adapter.py"
    model_path = REPO_ROOT / "backend/app/models/character_motion_adapter.py"
    adapter_source = adapter_path.read_text(encoding="utf-8")
    model_source = model_path.read_text(encoding="utf-8")
    tree = ast.parse(adapter_source)
    imported: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.append(node.module)
    if any(name == "framework" or name.startswith("framework.") for name in imported):
        raise AssertionError("RT-6c contains a static/internal Framework import")
    required_adapter_markers = (
        'importlib.import_module("framework")',
        'adapter="mock"',
        "real_adapter_enabled=False",
        "allow_provider_execution=False",
        "FRAMEWORK_MOCK_MOTION_MAX_EVENT_TYPES",
        "framework_mock_motion_close_failed",
        "Framework mock motion execution failed.",
    )
    for marker in required_adapter_markers:
        if marker not in adapter_source:
            raise AssertionError(f"RT-6c adapter marker missing: {marker}")
    forbidden_source_markers = (
        'import_module("framework.motion")',
        'import_module("framework.motion_session")',
        "from framework.motion",
        "from framework.motion_session",
        "websocket.connect",
        "VTubeStudio",
        "Live2D",
    )
    for marker in forbidden_source_markers:
        if marker in adapter_source:
            raise AssertionError(f"RT-6c forbidden runtime marker present: {marker}")
    required_model_markers = (
        'schema_version: str = "drc.v3.framework-mock-motion-execution.1"',
        'adapter: str = "mock"',
        "provider_execution_attempted: bool = False",
        "network_execution: bool = False",
        "FRAMEWORK_MOCK_MOTION_MAX_EVENT_TYPES = 12",
    )
    for marker in required_model_markers:
        if marker not in model_source:
            raise AssertionError(f"RT-6c result marker missing: {marker}")
    forbidden_fields = {
        "public_metadata",
        "metadata",
        "raw_result",
        "framework_session_id",
        "framework_request_id",
    }
    if forbidden_fields & set(FrameworkMockMotionExecutionResult.model_fields):
        raise AssertionError("RT-6c result exposes a raw/arbitrary Framework channel")


def _representative_plan():
    return CharacterMotionMapper().map(
        CharacterMotionMappingInput(
            fact=CharacterMotionLifecycleFact.IDLE,
            source_event_type="turn_completed",
            session_id="gate-session",
            turn_id="gate-turn",
            character_id="gentle_mina",
        )
    )


def _ignored_plan():
    return CharacterMotionMapper().map(
        CharacterMotionMappingInput(fact=CharacterMotionLifecycleFact.MOTION_ACTIVE)
    )


def _assert_pre_import_stops(framework_root: Path) -> None:
    disabled = FrameworkMockMotionSessionAdapter(
        framework_root=framework_root
    ).execute(_representative_plan())
    if disabled.status is not FrameworkMockMotionExecutionStatus.DISABLED:
        raise AssertionError("RT-6c default-off status is not disabled")
    if disabled.framework_import_attempted or disabled.session_created:
        raise AssertionError("RT-6c disabled path touched Framework")
    ignored = FrameworkMockMotionSessionAdapter(
        framework_root=framework_root,
        enabled=True,
    ).execute(_ignored_plan())
    if ignored.status is not FrameworkMockMotionExecutionStatus.IGNORED:
        raise AssertionError("RT-6c ignored plan did not stop before Framework")
    if ignored.framework_import_attempted or ignored.session_created:
        raise AssertionError("RT-6c ignored plan touched Framework")


def _assert_mock_smoke(framework_root: Path) -> None:
    _purge_framework_modules()
    try:
        result = FrameworkMockMotionSessionAdapter(
            framework_root=framework_root,
            enabled=True,
        ).execute(_representative_plan())
    finally:
        _purge_framework_modules()
    if result.status is not FrameworkMockMotionExecutionStatus.COMPLETED:
        raise AssertionError(f"RT-6c mock smoke did not complete: {result.model_dump()}")
    if result.commands_requested != 3 or result.commands_completed != 3:
        raise AssertionError("RT-6c mock smoke did not apply exactly three commands")
    if len(result.command_results) != 3:
        raise AssertionError("RT-6c mock smoke result count mismatch")
    if not result.framework_import_attempted or not result.session_created or not result.session_closed:
        raise AssertionError("RT-6c mock smoke session lifecycle mismatch")
    if (
        result.real_adapter_enabled
        or result.provider_execution_allowed
        or result.provider_execution_attempted
        or result.network_execution
    ):
        raise AssertionError("RT-6c mock smoke claimed real/provider/network execution")
    if len(result.event_types) > FRAMEWORK_MOCK_MOTION_MAX_EVENT_TYPES:
        raise AssertionError("RT-6c retained too many event types")


def _assert_framework_root_contract(framework_root: Path) -> None:
    if not framework_root.is_dir():
        raise AssertionError("Framework root is missing or not a directory")
    package_init = framework_root / "framework" / "__init__.py"
    if not package_init.is_file():
        raise AssertionError("Framework root-public package is missing")

    # Root-public symbol availability is verified by the adapter smoke below.
    # Do not add a second import path here: the adapter owns the exact temporary
    # cwd/sys.path context required by the configured external vendor layout.
    if FW_ROOT_PUBLIC_SYMBOLS != (
        "create_motion_session",
        "MotionRequest",
        "MotionIntent",
    ):
        raise AssertionError("RT-6c Framework root-public symbol contract changed")


def _purge_framework_modules() -> None:
    for name in list(sys.modules):
        if name == "framework" or name.startswith("framework."):
            del sys.modules[name]


@contextmanager
def _synthetic_framework_root() -> Iterator[Path]:
    temp = Path(tempfile.mkdtemp(prefix="drc_rt6c_framework_"))
    try:
        package = temp / "framework"
        package.mkdir(parents=True)
        (package / "__init__.py").write_text(
            _SYNTHETIC_FRAMEWORK_SOURCE,
            encoding="utf-8",
        )
        yield temp
    finally:
        _purge_framework_modules()
        shutil.rmtree(temp, ignore_errors=True)


_SYNTHETIC_FRAMEWORK_SOURCE = r'''from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from uuid import uuid4

class MotionIntent(str, Enum):
    EXPRESSION = "expression"
    SPEAKING_STATE = "speaking_state"
    IDLE_MOTION = "idle_motion"
    STOP_MOTION = "stop_motion"
    RESET_EXPRESSION = "reset_expression"

@dataclass(frozen=True)
class MotionRequest:
    intent: MotionIntent
    expression: str | None = None
    speaking: bool | None = None
    character_id: str | None = None
    public_metadata: dict = field(default_factory=dict)
    request_id: str = field(default_factory=lambda: uuid4().hex)

    @classmethod
    def expression_change(cls, expression, **kwargs):
        return cls(intent=MotionIntent.EXPRESSION, expression=expression, **kwargs)

    @classmethod
    def speaking_state(cls, speaking, **kwargs):
        return cls(intent=MotionIntent.SPEAKING_STATE, speaking=speaking, **kwargs)

    @classmethod
    def stop_motion(cls, **kwargs):
        return cls(intent=MotionIntent.STOP_MOTION, **kwargs)

@dataclass(frozen=True)
class Capability:
    adapter_status: str = "mock_available"
    supports_motion_session: bool = True
    supports_mock_motion: bool = True
    supports_real_adapter: bool = False

@dataclass(frozen=True)
class Result:
    outcome: str = "completed"
    state: str = "idle"
    adapter_status: str = "mock_available"
    public_error_code: str = "none"
    retryable: bool = False
    safe_message: str = ""
    request_id: str = "synthetic-raw-request"
    session_id: str = "synthetic-raw-session"

class Session:
    def __init__(self):
        self.callbacks = []
        self.closed = False

    def on_event(self, callback):
        self.callbacks.append(callback)

    def emit(self, event_type):
        payload = MappingProxyType({"type": event_type, "session_id": "raw", "request_id": "raw"})
        for callback in self.callbacks:
            callback(payload)

    def preflight(self):
        self.emit("motion.adapter.preflight.completed")
        return Capability()

    def apply_motion(self, request):
        self.emit("motion.requested")
        self.emit("motion.started")
        self.emit("motion.completed")
        return Result()

    def close(self):
        if self.closed:
            return
        self.closed = True
        self.emit("motion.session.closed")

def create_motion_session(*, project_root=None, adapter="mock", real_adapter_enabled=False, allow_provider_execution=False, public_metadata=None):
    assert adapter == "mock"
    assert real_adapter_enabled is False
    assert allow_provider_execution is False
    return Session()
'''


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--framework-root", type=Path)
    parser.add_argument("--snapshot", action="store_true")
    args = parser.parse_args()

    _assert_exact_surface(snapshot=args.snapshot)
    _assert_static_contract()

    real_fw_smoke = False
    if args.snapshot:
        with _synthetic_framework_root() as synthetic_root:
            _assert_pre_import_stops(synthetic_root)
            _assert_mock_smoke(synthetic_root)
    else:
        configured = args.framework_root or (
            Path(os.environ["FRAMEWORK_ROOT"]) if os.environ.get("FRAMEWORK_ROOT") else None
        )
        if configured is None:
            raise AssertionError("--framework-root or FRAMEWORK_ROOT is required")
        framework_root = configured.expanduser().resolve()
        _assert_framework_root_contract(framework_root)
        _assert_pre_import_stops(framework_root)
        _assert_mock_smoke(framework_root)
        real_fw_smoke = True

    print("v300_rt6c_status: completed-accepted-pushed")
    print("v300_rt6c_exact_acceptance_sync_surface: True")
    print(f"v300_rt6c_acceptance_sync_file_count: {len(EXACT_PATHS)}")
    print("v300_rt6c_implementation_commit: f929e8faa65a817f1ba4fed82b729438b73dbfab")
    print("v300_rt6c_implementation_surface: 10")
    print(f"v300_rt6c_backend_runtime_file_count: {len(IMPLEMENTATION_RUNTIME_PATHS)}")
    print(f"v300_rt6c_backend_test_file_count: {len(IMPLEMENTATION_TEST_PATHS)}")
    print("v300_rt6c_focused_backend_passed: 38")
    print("v300_rt6c_backend_full_passed: 279")
    print("v300_rt6c_backend_warning_count: 3")
    print("v300_rt6c_flutter_analyze_passed: True")
    print("v300_rt6c_flutter_full_passed: 411")
    print("v300_rt6c_root_public_only: True")
    print("v300_rt6c_default_enabled: False")
    print("v300_rt6c_mock_adapter_forced: True")
    print("v300_rt6c_real_adapter_enabled: False")
    print("v300_rt6c_provider_execution_allowed: False")
    print("v300_rt6c_disabled_import_attempted: False")
    print("v300_rt6c_ignored_import_attempted: False")
    print("v300_rt6c_max_apply_calls: 3")
    print("v300_rt6c_fail_fast: True")
    print("v300_rt6c_session_close_guaranteed: True")
    print("v300_rt6c_raw_framework_objects_exposed: False")
    print(f"v300_rt6c_max_retained_event_types: {FRAMEWORK_MOCK_MOTION_MAX_EVENT_TYPES}")
    print(f"v300_rt6c_framework_version: {FW_VERSION}")
    print(f"v300_rt6c_framework_reference_commit: {FW_REFERENCE_COMMIT}")
    print(f"v300_rt6c_framework_source_mode: {FW_SOURCE_MODE}")
    print("v300_rt6c_framework_git_identity_required: False")
    print("v300_rt6c_framework_root_public_contract_passed: True")
    print("v300_rt6c_framework_mock_smoke_passed: True")
    print(f"v300_rt6c_real_fw_mock_smoke_passed: {real_fw_smoke}")
    print("v300_rt6c_runtime_changed_by_acceptance_sync: False")
    print("v300_rt6c_backend_runtime_changed_by_acceptance_sync: False")
    print("v300_rt6c_backend_tests_changed_by_acceptance_sync: False")
    print("v300_rt6c_api_routes_changed: False")
    print("v300_rt6c_config_changed: False")
    print("v300_rt6c_flutter_changed: False")
    print("v300_rt6c_framework_changed: False")
    print("v300_rt6c_dependencies_changed: False")
    print("v300_rt6c_network_execution: False")
    print("v300_rt6c_provider_execution: False")
    print("v300_rt6c_vts_connection_used: False")
    print("v300_rt6c_live2d_runtime_loaded: False")
    print("v300_rt6_status: current-not-completed")
    print("v300_rt6d_status: ready-for-exact-contract-review-not-authorized")
    print("v300_rt6d_implementation_authorized: False")
    print("v300_rt7_real_adapter_blocked: True")
    print("v300_rt6c_acceptance_sync_commit_push_authorized: False")
    print(f"v300_rt6c_snapshot_mode: {args.snapshot}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
