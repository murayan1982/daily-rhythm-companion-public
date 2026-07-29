"""Validate the RT-4b provider-neutral Backend text-stream contract.

This gate is credential-free, network-free, Framework-import-free, route-free,
and fake-callback-only. It validates the DRC-owned state machine and protects
transport, Flutter, versions, and release records from RT-4b changes.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

TREE_HASHES = {
    "backend/app/api": "9866448f37fb18f0cef368786bc458ff33e74236ba5b7a6c08afa6cba9b82343",
    "app/lib": "6051e2b0abf1abb00014a5e47e812e393014fd255bb3527d94cca56d08ce17aa",
    "app/test": "19f99b4dc766536e151043121b6b6617046bba259bedf84eeabb675e8972ca3f",
    "release_notes": "709652f31c775a9d48bb28b88acc765ee330fb0c40ae4ce611be8b6d0ea78ac5",
}

FILE_HASHES = {
    "backend/app/main.py": "6ead9b1570b1453d7029496db3b554156b0e6752b1cb2369053e9341a81d3c27",
    "backend/app/models/realtime.py": "617ad2c6660ce816e6704d679692b09b40b8765817b1aded48a48587579ac140",
    "backend/app/services/framework_realtime_normalizer.py": "977fab20e3bad55cda4209cb7d2e1c82531094d5a7adea6911a29fa942e64853",
    "app/pubspec.yaml": "5de06f3041d7f150b83638e1cd2cc913b286c107e3b58a37178f678a37e7a428",
}

SENSITIVE_PATTERNS = (
    r"sk-[A-Za-z0-9_\-]{12,}",
    r"xai-[A-Za-z0-9_\-]{12,}",
    r"AIza[0-9A-Za-z_\-]{20,}",
    r"Bearer\s+[A-Za-z0-9_\-.]{16,}",
    r"[A-Za-z]:\\Users\\[^<\r\n]+",
    r"[A-Za-z]:\\work\\[^<\r\n]+",
    r"/(?:home|users)/[^/\s]+/",
    r"192\.168\.\d{1,3}\.\d{1,3}",
)


def read(relative: str) -> str:
    path = ROOT / relative
    if not path.is_file():
        raise AssertionError(f"Missing required file: {relative}")
    return path.read_text(encoding="utf-8")


def normalized_bytes(path: Path) -> bytes:
    return path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def normalized_hash(relative: str) -> str:
    return sha256(normalized_bytes(ROOT / relative)).hexdigest()


def normalized_tree_hash(relative: str) -> str:
    base = ROOT / relative
    if not base.is_dir():
        raise AssertionError(f"Missing required directory: {relative}")
    digest = sha256()
    for path in sorted(
        candidate
        for candidate in base.rglob("*")
        if candidate.is_file()
        and "__pycache__" not in candidate.parts
        and candidate.suffix.lower() not in {".pyc", ".pyo"}
    ):
        digest.update(path.relative_to(ROOT).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(normalized_bytes(path))
        digest.update(b"\0")
    return digest.hexdigest()


def require(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise AssertionError(f"Missing {label}: {needle!r}")


def forbid(text: str, needle: str, label: str) -> None:
    if needle in text:
        raise AssertionError(f"Unexpected {label}: {needle!r}")


def assert_no_sensitive_values(relative: str, text: str) -> None:
    for pattern in SENSITIVE_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            raise AssertionError(f"Sensitive-looking value in {relative}: {pattern}")


def assert_hashes() -> None:
    for relative, expected in TREE_HASHES.items():
        actual = normalized_tree_hash(relative)
        if actual != expected:
            raise AssertionError(
                f"RT-4b protected tree changed: {relative}: {actual} != {expected}"
            )
    for relative, expected in FILE_HASHES.items():
        actual = normalized_hash(relative)
        if actual != expected:
            raise AssertionError(
                f"RT-4b protected file changed: {relative}: {actual} != {expected}"
            )


def assert_source_contract() -> None:
    model = read("backend/app/models/realtime_text_stream.py")
    service = read("backend/app/services/realtime_text_stream_service.py")
    tests = read("backend/tests/test_realtime_text_stream_service.py")
    doc = read("docs/v300_rt4_backend_stream_contract.md")
    checklist = read("docs/DRC_v300_goal_checklist_small_commit.md")
    progress = "\n".join(
        read(relative)
        for relative in (
            "README.md",
            "roadmap.md",
            "tasklist.md",
            "scripts/README.md",
        )
    )

    for marker in (
        "REALTIME_TEXT_STREAM_MAX_CHUNK_CHARS = 512",
        "REALTIME_TEXT_STREAM_MAX_OUTPUT_CHARS = 4096",
        "REALTIME_TEXT_STREAM_MAX_SAFE_MESSAGE_CHARS = 240",
    ):
        require(model, marker, f"RT-4b model bound {marker}")

    for symbol in (
        "class RealtimeTextStreamState",
        "class RealtimeTextStreamEventType",
        "class RealtimeTextStreamTerminalOutcome",
        "class RealtimeTextStreamCallbackReason",
        "class RealtimeTextStreamSession",
        "class RealtimeTextStreamTurn",
        "class RealtimeTextStreamChunk",
        "class RealtimeTextStreamTerminal",
        "class RealtimeTextStreamEvent",
        "class RealtimeTextStreamCallbackResult",
    ):
        require(model, symbol, f"RT-4b model {symbol}")

    for marker in (
        "class RealtimeTextStreamService",
        "DEFAULT_MAX_STREAM_CHUNK_CHARS = REALTIME_TEXT_STREAM_MAX_CHUNK_CHARS",
        "DEFAULT_MAX_STREAM_OUTPUT_CHARS = REALTIME_TEXT_STREAM_MAX_OUTPUT_CHARS",
        "def start_turn",
        "def append_chunk",
        "def request_cancel",
        "def complete",
        "def cancel",
        "def fail",
        "def close",
        "hard_cancel_supported=False",
        "RealtimeTextStreamCallbackReason.STALE_TURN",
        "RealtimeTextStreamCallbackReason.CANCEL_REQUESTED",
        'public_error_code="chunk_limit_exceeded"',
        'public_error_code="output_limit_exceeded"',
    ):
        require(service, marker, f"RT-4b service marker {marker}")

    for forbidden_runtime in (
        "FastAPI",
        "APIRouter",
        "StreamingResponse",
        "WebSocket",
        "EventSource",
        "httpx",
        "requests",
        "import framework",
        "from framework",
        "create_text_chat_session",
        "ask_stream(",
    ):
        forbid(model + service + tests, forbidden_runtime, "RT-4b runtime wiring")

    for test_name in (
        "test_start_turn_exposes_provider_neutral_soft_cancel_capability",
        "test_second_turn_cannot_replace_an_active_turn",
        "test_chunks_are_bounded_and_sequences_are_monotonic",
        "test_cancel_request_rejects_late_chunks_and_finishes_cancelled",
        "test_complete_after_cancel_request_resolves_to_cancelled",
        "test_oversized_chunk_fails_without_storing_unbounded_text",
        "test_output_limit_fails_before_overflowing_aggregate",
        "test_old_turn_callback_is_rejected_after_a_new_turn_starts",
        "test_close_terminalizes_active_turn_and_rejects_future_callbacks",
    ):
        require(tests, test_name, f"RT-4b regression {test_name}")

    combined_docs = doc + checklist + progress
    for marker in (
        "RT-4a: COMPLETED / ACCEPTED",
        "RT-4b: IMPLEMENTED / AWAITING_ACCEPTANCE",
        "RT-4c: NOT_STARTED",
        "cancel_mode: cooperative",
        "hard_cancel_supported: false",
        "provider-level hard cancellation",
        "exact ten-file",
    ):
        require(combined_docs, marker, f"RT-4b documentation marker {marker}")

    for relative, text in (
        ("model", model),
        ("service", service),
        ("tests", tests),
        ("doc", doc),
        ("checklist", checklist),
    ):
        assert_no_sensitive_values(relative, text)


def assert_runtime_contract() -> None:
    framework_before = {
        name for name in sys.modules if name == "framework" or name.startswith("framework.")
    }

    from app.models.realtime_text_stream import (
        RealtimeTextStreamCallbackReason,
        RealtimeTextStreamEventType,
        RealtimeTextStreamTerminalOutcome,
    )
    from app.services.realtime_text_stream_service import RealtimeTextStreamService

    service = RealtimeTextStreamService(
        session_id="rt4b-session",
        max_chunk_chars=8,
        max_output_chars=12,
    )
    started = service.start_turn(turn_id="rt4b-turn")
    first = service.append_chunk(turn_id="rt4b-turn", text="hello ")
    requested = service.request_cancel(turn_id="rt4b-turn")
    late = service.append_chunk(turn_id="rt4b-turn", text="late")
    terminal = service.complete(turn_id="rt4b-turn")

    sequences = [
        started.event.sequence if started.event else None,
        first.event.sequence if first.event else None,
        requested.event.sequence if requested.event else None,
        terminal.event.sequence if terminal.event else None,
    ]
    if sequences != [1, 2, 3, 4]:
        raise AssertionError(f"RT-4b sequence contract failed: {sequences}")
    if late.accepted or late.reason is not RealtimeTextStreamCallbackReason.CANCEL_REQUESTED:
        raise AssertionError("RT-4b late callback rejection failed")
    if terminal.event is None or terminal.event.event_type is not RealtimeTextStreamEventType.STREAM_CANCELLED:
        raise AssertionError("RT-4b cancel/completion race did not resolve to cancelled")
    if terminal.event.terminal is None:
        raise AssertionError("RT-4b terminal payload is missing")
    if terminal.event.terminal.outcome is not RealtimeTextStreamTerminalOutcome.CANCELLED:
        raise AssertionError("RT-4b terminal outcome is not cancelled")
    if terminal.event.terminal.final_text != "hello ":
        raise AssertionError("RT-4b bounded partial output changed unexpectedly")
    if terminal.session.hard_cancel_supported:
        raise AssertionError("RT-4b incorrectly claims hard cancellation")

    service.start_turn(turn_id="rt4b-next")
    stale = service.append_chunk(turn_id="rt4b-turn", text="stale")
    if stale.accepted or stale.reason is not RealtimeTextStreamCallbackReason.STALE_TURN:
        raise AssertionError("RT-4b stale-turn callback was not rejected")

    framework_after = {
        name for name in sys.modules if name == "framework" or name.startswith("framework.")
    }
    if framework_after != framework_before:
        raise AssertionError("RT-4b imported AI Character Framework unexpectedly")


def main() -> None:
    assert_source_contract()
    assert_runtime_contract()
    assert_hashes()

    print("v300_rt4_backend_stream_status: implemented-awaiting-acceptance")
    print("v300_rt4b_backend_models_added: True")
    print("v300_rt4b_fake_only_service_added: True")
    print("v300_rt4b_monotonic_sequence_enforced: True")
    print("v300_rt4b_bounded_text_enforced: True")
    print("v300_rt4b_stale_callback_rejected: True")
    print("v300_rt4b_backend_route_added: False")
    print("v300_rt4b_framework_imported: False")
    print("v300_rt4b_provider_execution: False")
    print("v300_rt4b_hard_cancel_claimed: False")
    print("v300_rt4b_flutter_changed: False")
    print("v300_rt4c_authorization: blocked-pending-rt4b-acceptance")


if __name__ == "__main__":
    main()
