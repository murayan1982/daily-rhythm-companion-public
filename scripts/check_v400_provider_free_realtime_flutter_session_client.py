#!/usr/bin/env python3
"""DRC-V4-4 provider-free FW v6 Flutter session client acceptance gate."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_BASELINE = "d194c213fdecc84ec06d8b63f0cb94f8689c5ed7"
EXPECTED_FILES = (
    "README.md",
    "app/lib/models/framework_v600_realtime_session.dart",
    "app/lib/services/framework_v600_realtime_session_client.dart",
    "app/lib/services/framework_v600_realtime_session_controller.dart",
    "app/test/framework_v600_realtime_session_client_test.dart",
    "app/test/framework_v600_realtime_session_controller_test.dart",
    "app/test/framework_v600_realtime_session_model_test.dart",
    "docs/DRC_v400_goal_checklist_small_commit.md",
    "docs/v400_provider_free_realtime_flutter_session_client.md",
    "roadmap.md",
    "scripts/README.md",
    "scripts/check_v400_provider_free_realtime_flutter_session_client.py",
    "tasklist.md",
)
PROTECTED_FILES = (
    "backend/app/models/framework_v600_realtime.py",
    "backend/app/models/framework_v600_realtime_api.py",
    "backend/app/services/framework_v600_realtime_session_adapter.py",
    "backend/app/services/framework_v600_realtime_api_registry.py",
    "backend/app/api/framework_v600_realtime.py",
    "backend/app/main.py",
    "backend/tests/test_framework_v600_realtime_session_adapter.py",
    "backend/tests/test_framework_v600_realtime_api.py",
    "scripts/check_v400_provider_free_realtime_session_adapter.py",
    "scripts/check_v400_provider_free_realtime_backend_api.py",
    "docs/v400_provider_free_realtime_session_adapter.md",
    "docs/v400_provider_free_realtime_backend_api.md",
    "app/lib/models/realtime_text_stream.dart",
    "app/lib/services/realtime_text_stream_client.dart",
    "app/lib/services/realtime_text_stream_controller.dart",
    "app/lib/services/configured_realtime_text_stream_runtime.dart",
    "app/lib/main.dart",
    "app/pubspec.yaml",
    "app/pubspec.lock",
    "backend/requirements.txt",
    "backend/requirements-dev.txt",
    "backend/requirements-framework.txt",
    ".gitignore",
    "docs/DRC_v300_goal_checklist_small_commit.md",
    "docs/v300_release_record.md",
    "release_notes/v3.0.0.md",
)
CURRENT_DOCS = (
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v400_goal_checklist_small_commit.md",
)
DART_FILES = (
    "app/lib/models/framework_v600_realtime_session.dart",
    "app/lib/services/framework_v600_realtime_session_client.dart",
    "app/lib/services/framework_v600_realtime_session_controller.dart",
)
TEST_FILES = (
    "app/test/framework_v600_realtime_session_model_test.dart",
    "app/test/framework_v600_realtime_session_client_test.dart",
    "app/test/framework_v600_realtime_session_controller_test.dart",
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
        raise GateError(f"exact 13-file surface mismatch: expected={expected}, actual={actual}")
    changed = set(git("diff", "--name-only").splitlines())
    changed.update(git("ls-files", "--others", "--exclude-standard").splitlines())
    protected = sorted(set(PROTECTED_FILES).intersection(path.replace("\\", "/") for path in changed))
    if protected:
        raise GateError(f"protected file changed: {protected}")


def check_docs() -> None:
    contract = read("docs/v400_provider_free_realtime_flutter_session_client.md")
    required = (
        "DRC-V4-4 IMPLEMENTED / AWAITING_REVIEW",
        "Backend HTTP capability: YES / explicit method invocation only",
        "automatic network on construction/startup: NO",
        "verification network: NO / fake injected HTTP client only",
        "external provider execution: NO",
        "provider network: NO",
        "microphone: NO",
        "real STT: NO",
        "real LLM: NO",
        "real TTS: NO",
        "playback: NO",
        "VTube Studio: NO",
        "HomeScreen wiring: NOT_IMPLEMENTED",
        "main.dart wiring: NOT_IMPLEMENTED",
        "configured runtime wiring: NOT_IMPLEMENTED",
        "direct Framework import: NOT_IMPLEMENTED",
        "real unified runtime: NOT_CLAIMED",
        "commit / push: NOT_AUTHORIZED",
        "/realtime/framework-v6/provider-free",
    )
    for marker in required:
        if marker not in contract:
            raise GateError(f"missing V4-4 contract doc marker: {marker}")
    for doc in CURRENT_DOCS:
        text = read(doc)
        for marker in (
            "DRC-V4-4: IMPLEMENTED / AWAITING_REVIEW",
            "commit / push: NOT_AUTHORIZED",
            "d194c213fdecc84ec06d8b63f0cb94f8689c5ed7",
            "provider-free FW v6 Flutter session client/controller",
        ):
            if marker not in text:
                raise GateError(f"missing current doc marker in {doc}: {marker}")
        for stale in (
            "Current small commit: DRC-V4-3 final acceptance sync",
            "current small commit: DRC-V4-3 final acceptance sync",
            "Current implementation state: COMPLETED / VERIFIED / ACCEPTED / COMMITTED / PUSHED / CLOSED",
            "current implementation state: COMPLETED / VERIFIED / ACCEPTED / COMMITTED / PUSHED / CLOSED",
        ):
            if stale in text:
                raise GateError(f"stale V4-4 current-status marker in {doc}: {stale}")


def check_dart_contract() -> None:
    model = read("app/lib/models/framework_v600_realtime_session.dart")
    client = read("app/lib/services/framework_v600_realtime_session_client.dart")
    controller = read("app/lib/services/framework_v600_realtime_session_controller.dart")
    combined = "\n".join((model, client, controller))
    for marker in (
        "drc.v4.framework-v600-open-result.1",
        "drc.v4.framework-v600-turn-result.1",
        "drc.v4.framework-v600-interrupt-result.1",
        "drc.v4.framework-v600-diagnostics.1",
        "drc.v4.framework-v600-capability-snapshot.1",
        "drc.v4.framework-v600-realtime-event.1",
        r"^fw_session_[0-9a-f]{32}$",
        r"^fw_turn_[0-9a-f]{32}$",
        r"^fw_generation_[0-9a-f]{32}$",
        "FrameworkV600RealtimeProblem",
        "FrameworkV600RealtimeProblemException",
        "FrameworkV600RealtimeCapabilitySnapshot",
        "FrameworkV600RealtimeOpenResult",
        "FrameworkV600RealtimeEventSummary",
        "FrameworkV600RealtimeTurnResult",
        "FrameworkV600RealtimeInterruptResult",
        "FrameworkV600RealtimeDiagnosticsSnapshot",
        "realRuntimeEnabled",
        "realUnifiedRuntimeAvailable",
        "unifiedRealPipelineClaimed",
        "hostPlaybackOwnedByDrc",
    ):
        if marker not in combined:
            raise GateError(f"missing Flutter model marker: {marker}")
    for marker in (
        "required String baseUrl",
        "required http.Client client",
        "Future<FrameworkV600RealtimeOpenResult> createSession()",
        "Future<FrameworkV600RealtimeTurnResult> runTurn",
        "Future<FrameworkV600RealtimeInterruptResult> interrupt",
        "Future<FrameworkV600RealtimeDiagnosticsSnapshot> diagnostics",
        "Future<void> closeSession",
        "realtime/framework-v6/provider-free/sessions",
        "'input_text': inputText",
        "frameworkV600RealtimeMaxInputChars",
        "frameworkV600RealtimeMaxBodyBytes",
        "response_body_too_large",
        "current_turn",
        "host_app_request",
    ):
        if marker not in client:
            raise GateError(f"missing Flutter client marker: {marker}")
    if "http.Client()" in client:
        raise GateError("client must not instantiate an implicit production http.Client")
    for marker in (
        "extends ChangeNotifier",
        "required FrameworkV600RealtimeSessionClient client",
        "FrameworkV600RealtimeSessionPhase.idle",
        "FrameworkV600RealtimeSessionPhase.opening",
        "FrameworkV600RealtimeSessionPhase.ready",
        "FrameworkV600RealtimeSessionPhase.turnRunning",
        "FrameworkV600RealtimeSessionPhase.closing",
        "FrameworkV600RealtimeSessionPhase.closed",
        "FrameworkV600RealtimeSessionPhase.failed",
        "interruptInFlight",
        "diagnosticsInFlight",
        "turn_already_active",
        "_generation",
        "_openInFlight",
        "_closeInFlight",
        "session_open_not_allowed",
    ):
        if marker not in controller:
            raise GateError(f"missing Flutter controller marker: {marker}")
    bounded_start = client.find("Future<String> _boundedBody")
    if bounded_start == -1:
        raise GateError("missing _boundedBody implementation")
    bounded_end = client.find("\n  T _parse", bounded_start)
    bounded_body = client[bounded_start:] if bounded_end == -1 else client[bounded_start:bounded_end]
    guard_index = bounded_body.find("builder.length + chunk.length > frameworkV600RealtimeMaxBodyBytes")
    append_index = bounded_body.find("builder.add(chunk)")
    if guard_index == -1 or append_index == -1 or append_index < guard_index:
        raise GateError("R1 body-size guard must run before builder.add(chunk)")
    close_start = controller.find("Future<void> close()")
    if close_start == -1:
        raise GateError("missing close() implementation")
    close_end = controller.find("\n  Future<void> _performClose", close_start)
    close_body = controller[close_start:] if close_end == -1 else controller[close_start:close_end]
    if "final closeFuture = _performClose()" in close_body:
        raise GateError("R3 close single-flight must not call _performClose before assignment")
    close_assignment = close_body.find("_closeInFlight = sharedFuture")
    perform_invocation = close_body.find("_performClose()")
    if close_assignment == -1 or perform_invocation == -1 or perform_invocation < close_assignment:
        raise GateError("_closeInFlight must be established before close lifecycle starts")
    forbidden = (
        "package:framework",
        "from framework",
        ".env",
        "api_key",
        "access_token",
        "client_secret",
        "microphone",
        "record",
        "audioplayers",
        "VTube",
        "WebSocket",
        "EventSource",
        "rawPayload",
        "rawEvent",
        "rawJson",
        "providerPayload",
        "debugPayload",
    )
    for marker in forbidden:
        if marker in combined:
            raise GateError(f"forbidden Flutter V4-4 marker: {marker}")
    if "payload" in model and "payload_marker" not in "\n".join(read(path) for path in TEST_FILES):
        raise GateError("event payload boundary test marker missing")


def check_tests() -> None:
    tests = "\n".join(read(path) for path in TEST_FILES)
    markers = (
        "constructor makes zero requests",
        "wrong schema version rejected",
        "canonical session turn and generation ids are validated",
        "provider-free invariants reject real runtime contradictions",
        "event metadata projected but payload not retained or exposed",
        "turn sends only input_text and forwards valid input exactly",
        "blank and oversized turn rejected before HTTP",
        "invalid interrupt scope and reason rejected before HTTP",
        "oversized response raw body and input text are not exposed",
        "interrupt can execute during in-flight turn without corrupting phase",
        "late turn diagnostics and interrupt results ignored after close",
        "no automatic retry reopen or input retention in public problem",
        "open re-entry rejected while opening",
        "open re-entry rejected while ready keeps existing session",
        "open re-entry rejected while turnRunning keeps turn state",
        "close during opening cleans late-created session",
        "close during opening cleanup failure remains closed",
        "exact 64 KiB boundary is not response_body_too_large",
        "pre-append oversized body guard rejects before later chunks",
        "concurrent close while ready uses single flight",
        "reentrant close from closing notification uses single flight",
        "concurrent close during opening uses one cleanup delete",
        "concurrent close cleanup failure remains closed",
    )
    for marker in markers:
        if marker not in tests:
            raise GateError(f"missing focused Flutter test marker: {marker}")


def check_privacy() -> None:
    for relative in EXPECTED_FILES:
        tracked = subprocess.run(
            ["git", "-C", str(ROOT), "ls-files", "--error-unmatch", relative],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        ).returncode == 0
        text = git("diff", "--", relative) if tracked else read(relative)
        for pattern in SENSITIVE_PATTERNS:
            if pattern.search(text):
                raise GateError(f"privacy marker matched in {relative}: {pattern.pattern}")


def main() -> int:
    try:
        check_surface()
        check_docs()
        check_dart_contract()
        check_tests()
        check_privacy()
    except GateError as exc:
        print(f"DRC-V4-4 provider-free Flutter session client gate: FAIL: {exc}")
        return 1
    print("DRC-V4-4 provider-free Flutter session client gate: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
