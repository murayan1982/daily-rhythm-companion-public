#!/usr/bin/env python3
"""DRC-V4-3 provider-free FW v6 Backend API acceptance gate."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_BASELINE = "384006073aa9e8757c904cb89d9bcd62a2b9fb35"
EXPECTED_FILES = (
    "README.md",
    "backend/app/api/framework_v600_realtime.py",
    "backend/app/main.py",
    "backend/app/models/framework_v600_realtime_api.py",
    "backend/app/services/framework_v600_realtime_api_registry.py",
    "backend/tests/test_framework_v600_realtime_api.py",
    "docs/DRC_v400_goal_checklist_small_commit.md",
    "docs/v400_provider_free_realtime_backend_api.md",
    "roadmap.md",
    "scripts/README.md",
    "scripts/check_v400_provider_free_realtime_backend_api.py",
    "tasklist.md",
)
PROTECTED_FILES = (
    "backend/app/models/framework_v600_realtime.py",
    "backend/app/services/framework_v600_realtime_session_adapter.py",
    "backend/tests/test_framework_v600_realtime_session_adapter.py",
    "scripts/check_v400_provider_free_realtime_session_adapter.py",
    "docs/v400_provider_free_realtime_session_adapter.md",
    "backend/app/api/realtime_text.py",
    "backend/app/models/realtime.py",
    "backend/app/models/realtime_text_stream_transport.py",
    "backend/app/services/framework_realtime_normalizer.py",
    "backend/app/services/framework_realtime_text_stream_adapter.py",
    "backend/app/services/framework_mock_motion_session_adapter.py",
    "backend/app/services/realtime_text_stream_transport.py",
    "backend/tests/test_realtime_text_stream_service.py",
    "backend/tests/test_realtime_text_stream_transport.py",
    "backend/app/config.py",
    "backend/app/version.py",
    "backend/requirements.txt",
    "backend/requirements-dev.txt",
    "backend/requirements-framework.txt",
    "app/pubspec.yaml",
    "app/pubspec.lock",
    ".gitignore",
    "docs/DRC_v300_goal_checklist_small_commit.md",
    "docs/v300_release_record.md",
    "release_notes/v3.0.0.md",
)
NEW_PRODUCTION_FILES = (
    "backend/app/api/framework_v600_realtime.py",
    "backend/app/models/framework_v600_realtime_api.py",
    "backend/app/services/framework_v600_realtime_api_registry.py",
)
CURRENT_DOCS = (
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v400_goal_checklist_small_commit.md",
)
DOC_MARKERS = (
    "DRC-V4-3: IMPLEMENTED / AWAITING_REVIEW",
    "Commit: NOT_AUTHORIZED",
    "Push: NOT_AUTHORIZED",
    "commit / push: NOT_AUTHORIZED",
    "/realtime/framework-v6/provider-free",
    "POST   /realtime/framework-v6/provider-free/sessions",
    "POST   /realtime/framework-v6/provider-free/sessions/{session_id}/turns",
    "POST   /realtime/framework-v6/provider-free/sessions/{session_id}/interrupt",
    "GET    /realtime/framework-v6/provider-free/sessions/{session_id}/diagnostics",
    "DELETE /realtime/framework-v6/provider-free/sessions/{session_id}",
    "provider-free only: true",
    "real_runtime_enabled: False",
    "provider execution: False",
    "network: False",
    "microphone: False",
    "real STT: False",
    "real LLM: False",
    "real TTS: False",
    "playback: False",
    "VTube Studio / real motion: False",
    "Flutter wiring: False",
    "existing v3 runtime replacement: False",
    "existing accepted v3 real adapters remain retained",
    "removal of v3 real adapters is NOT_AUTHORIZED",
    "does not claim or enable",
    "DRC v4 release status: development work / not released",
)
PROHIBITED_SOURCE_MARKERS = (
    "import framework",
    "from framework",
    "framework.",
    "sys.path",
    "sys.modules",
    "invalidate_caches",
    "os.chdir",
    "FRAMEWORK_ROOT",
    "framework_project_root",
    "inspect.signature",
    "real_runtime_enabled=True",
    "voice_input_stage",
    "text_generation_stage",
    "voice_output_stage",
    "motion_stage",
    "provider_client",
    "api_key",
    "access_token",
    "refresh_token",
    "client_secret",
    "requests.",
    "httpx.",
    "urllib.",
    "socket.",
    "microphone",
    "playback",
    "VTube",
    "websocket",
)
SENSITIVE_PATTERNS = (
    re.compile(r"(?i)sk-[a-z0-9_-]{12,}"),
    re.compile(r"(?i)xai-[a-z0-9_-]{12,}"),
    re.compile(r"(?i)bearer\s+[a-z0-9._~+/-]{12,}"),
    re.compile(r"(?i)(?:api[_-]?key|access[_-]?token|refresh[_-]?token|client[_-]?secret)\s*[:=]"),
    re.compile(r"(?i)\b[a-z]:\\(?:users|home)\\"),
    re.compile(r"/(?:home|users)/[^/\s]+/"),
    re.compile(r"\b(?:10|169\.254|172\.(?:1[6-9]|2\d|3[01])|192\.168)\.\d{1,3}\.\d{1,3}\b"),
)


class GateError(RuntimeError):
    pass


def git(*args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(ROOT), *args],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if completed.returncode:
        raise GateError(completed.stderr.strip() or completed.stdout.strip())
    return completed.stdout


def read(relative: str) -> str:
    path = ROOT / relative
    if not path.is_file():
        raise GateError(f"missing required file: {relative}")
    return path.read_text(encoding="utf-8")


def status_paths() -> tuple[str, ...]:
    lines = git("status", "--short", "--untracked-files=normal").splitlines()
    paths: list[str] = []
    for line in lines:
        path = line[3:].strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        paths.append(path.replace("\\", "/"))
    return tuple(sorted(paths))


def check_surface() -> None:
    if git("rev-parse", "HEAD").strip() != EXPECTED_BASELINE:
        raise GateError("unexpected baseline HEAD")
    actual = status_paths()
    expected = tuple(sorted(EXPECTED_FILES))
    if actual != expected:
        raise GateError(f"exact 12-file surface mismatch: expected={expected}, actual={actual}")
    changed = set(git("diff", "--name-only").splitlines())
    changed.update(git("ls-files", "--others", "--exclude-standard").splitlines())
    protected = sorted(set(PROTECTED_FILES).intersection(path.replace("\\", "/") for path in changed))
    if protected:
        raise GateError(f"protected file changed: {protected}")


def check_main_router() -> None:
    source = read("backend/app/main.py")
    if "framework_v600_realtime" not in source:
        raise GateError("main.py does not import the DRC-V4-3 router")
    if "app.include_router(framework_v600_realtime.router)" not in source:
        raise GateError("main.py does not include the DRC-V4-3 router")
    if "app.include_router(realtime_text.router)" not in source:
        raise GateError("existing realtime_text router registration missing")


def check_api_contract() -> None:
    router = read("backend/app/api/framework_v600_realtime.py")
    models = read("backend/app/models/framework_v600_realtime_api.py")
    registry = read("backend/app/services/framework_v600_realtime_api_registry.py")
    combined = "\n".join((router, models, registry))
    for marker in PROHIBITED_SOURCE_MARKERS:
        if marker in combined:
            raise GateError(f"forbidden V4-3 production marker: {marker}")
    for marker in (
        'prefix="/realtime/framework-v6/provider-free"',
        '"/sessions"',
        '"/sessions/{session_id}/turns"',
        '"/sessions/{session_id}/interrupt"',
        '"/sessions/{session_id}/diagnostics"',
        "status.HTTP_204_NO_CONTENT",
        "FrameworkV600OpenResult",
        "FrameworkV600TurnResult",
        "FrameworkV600InterruptResult",
        "FrameworkV600DiagnosticsSnapshot",
        "FrameworkV600RealtimeApiProblem",
        "FrameworkV600RealtimeTurnRequest",
        "FrameworkV600RealtimeInterruptRequest",
        "MAX_INPUT_TEXT_CHARS",
    ):
        if marker not in combined:
            raise GateError(f"missing V4-3 API marker: {marker}")
    if "MAX_SESSIONS = 8" not in registry:
        raise GateError("registry MAX_SESSIONS is not frozen at 8")
    for marker in (
        "RequestValidationError",
        "FrameworkV600SafeValidationRoute(APIRoute)",
        "route_class=FrameworkV600SafeValidationRoute",
        "request_validation_failed",
        "Request validation failed.",
    ):
        if marker not in router:
            raise GateError(f"missing safe validation handler marker: {marker}")
    for marker in ("exc.errors()", "exc.body", "request.body()"):
        if marker in router:
            raise GateError(f"unsafe validation-error response marker: {marker}")
    if "ConfigDict" not in models:
        raise GateError("API request models do not import ConfigDict")
    for request_model in (
        "class FrameworkV600RealtimeTurnRequest(BaseModel):",
        "class FrameworkV600RealtimeInterruptRequest(BaseModel):",
    ):
        start = models.find(request_model)
        if start == -1:
            raise GateError(f"missing request model: {request_model}")
        next_class = models.find("\nclass ", start + len(request_model))
        block = models[start:] if next_class == -1 else models[start:next_class]
        if 'model_config = ConfigDict(extra="forbid")' not in block:
            raise GateError(f"request model does not reject extra fields: {request_model}")
    if "_lock" not in registry or "RLock" not in registry:
        raise GateError("registry lock boundary missing")
    turn_block = registry.split("async def run_turn", 1)[1].split("def interrupt", 1)[0]
    if "with self._lock" in turn_block:
        raise GateError("registry holds global lock across async turn")
    if "session_not_found" not in registry or "session_capacity_reached" not in registry:
        raise GateError("registry public error codes missing")
    if "message=\"FW v6 provider-free session was not found.\"" not in registry:
        raise GateError("unknown-session message may echo supplied id")


def check_docs() -> None:
    contract = read("docs/v400_provider_free_realtime_backend_api.md")
    current_text = "\n".join(read(path) for path in CURRENT_DOCS)
    all_docs = contract + "\n" + current_text
    for marker in DOC_MARKERS:
        if marker not in all_docs:
            raise GateError(f"missing documentation marker: {marker}")
    if "/realtime/text" not in contract or "retained and untouched" not in contract:
        raise GateError("existing v3 realtime path retention is not documented")


def check_tests() -> None:
    tests = read("backend/tests/test_framework_v600_realtime_api.py")
    for marker in (
        "test_create_returns_201",
        "test_create_preserves_canonical_fw_session_id",
        "test_create_does_not_generate_separate_drc_session_id",
        "test_capacity_accepts_eight_sessions",
        "test_ninth_session_returns_429",
        "test_async_turn_forwards_exact_input_text",
        "test_overlong_input_text_validation_response_is_public_safe",
        "test_turn_request_rejects_unexpected_extra_field",
        "test_turn_extra_field_validation_response_is_public_safe",
        "test_typed_failed_turn_remains_200",
        "test_all_approved_interrupt_scopes_are_accepted",
        "test_all_approved_interrupt_reasons_are_accepted",
        "test_invalid_interrupt_validation_response_is_public_safe",
        "test_interrupt_request_rejects_unexpected_extra_field",
        "test_unknown_turn_session_returns_404",
        "test_unknown_interrupt_session_returns_404",
        "test_unknown_diagnostics_session_returns_404",
        "test_duplicate_close_returns_204",
        "test_unavailable_open_returns_503",
        "test_raw_exception_strings_do_not_leak",
        "test_filesystem_paths_do_not_leak",
        "test_input_text_does_not_leak_in_safe_error",
        "test_provider_execution_false",
        "test_no_real_runtime_construction_knob_supplied",
        "test_v4_2_response_model_types_are_reused",
    ):
        if marker not in tests:
            raise GateError(f"missing focused API test marker: {marker}")


def check_privacy() -> None:
    diff = git("diff", "--", *EXPECTED_FILES)
    for path in NEW_PRODUCTION_FILES + (
        "docs/v400_provider_free_realtime_backend_api.md",
        "scripts/check_v400_provider_free_realtime_backend_api.py",
        "backend/tests/test_framework_v600_realtime_api.py",
    ):
        diff += "\n" + read(path)
    for pattern in SENSITIVE_PATTERNS:
        if pattern.search(diff):
            raise GateError(f"sensitive pattern detected: {pattern.pattern}")


def main() -> int:
    try:
        check_surface()
        check_main_router()
        check_api_contract()
        check_docs()
        check_tests()
        check_privacy()
    except GateError as error:
        print(f"DRC-V4-3 provider-free Backend API gate: FAIL - {error}")
        return 1
    print("DRC-V4-3 provider-free Backend API gate: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
