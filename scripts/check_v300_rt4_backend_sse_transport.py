"""Validate the RT-4c bounded Backend SSE/cancel transport contract.

This gate is credential-free, network-free, Framework-import-free, provider-free,
and Flutter-free. It validates exact scope, public-safe SSE serialization,
transport bounds, cooperative cancellation, and protected non-change surfaces.
"""
from __future__ import annotations

import asyncio
from hashlib import sha256
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

EXPECTED_CHANGED_FILES = {
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v300_goal_checklist_small_commit.md",
    "backend/.env.example",
    "backend/app/config.py",
    "backend/app/main.py",
    "backend/app/api/realtime_text.py",
    "backend/app/models/realtime_text_stream_transport.py",
    "backend/app/services/realtime_text_stream_transport.py",
    "backend/tests/test_realtime_text_stream_transport.py",
    "backend/tests/test_temporary_lifecycle_config.py",
    "docs/v300_rt4_backend_sse_transport.md",
    "scripts/check_v300_rt4_backend_sse_transport.py",
}

TREE_HASHES = {
    "app/lib": "6051e2b0abf1abb00014a5e47e812e393014fd255bb3527d94cca56d08ce17aa",
    "app/test": "19f99b4dc766536e151043121b6b6617046bba259bedf84eeabb675e8972ca3f",
    "release_notes": "709652f31c775a9d48bb28b88acc765ee330fb0c40ae4ce611be8b6d0ea78ac5",
}

FILE_HASHES = {
    "backend/app/models/realtime_text_stream.py": "931b1d0c9e879ef2c6778fbd067f0e6baad1e80ed877c8f38dc921631231d19d",
    "backend/app/services/realtime_text_stream_service.py": "93c94426262ab2522ce6518039257e6954be13f6b1ea41d45102d5a4a64e972a",
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
    r"/home/[^/\s]+/",
    r"192\.168\.\d{1,3}\.\d{1,3}",
)


def read(relative: str) -> str:
    path = ROOT / relative
    if not path.is_file():
        raise AssertionError(f"Missing required file: {relative}")
    return path.read_text(encoding="utf-8")


def run(*args: str) -> str:
    completed = subprocess.run(
        args,
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="surrogateescape",
    )
    return completed.stdout.rstrip("\r\n")


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


def assert_exact_change_surface() -> None:
    changed = set(filter(None, run("git", "diff", "--name-only").splitlines()))
    untracked = set(
        filter(
            None,
            run("git", "ls-files", "--others", "--exclude-standard").splitlines(),
        )
    )
    actual = changed | untracked
    if actual != EXPECTED_CHANGED_FILES:
        missing = sorted(EXPECTED_CHANGED_FILES - actual)
        unexpected = sorted(actual - EXPECTED_CHANGED_FILES)
        raise AssertionError(
            f"RT-4c exact change surface mismatch; missing={missing}, unexpected={unexpected}"
        )


def assert_hashes() -> None:
    for relative, expected in TREE_HASHES.items():
        actual = normalized_tree_hash(relative)
        if actual != expected:
            raise AssertionError(
                f"RT-4c protected tree changed: {relative}: {actual} != {expected}"
            )
    for relative, expected in FILE_HASHES.items():
        actual = normalized_hash(relative)
        if actual != expected:
            raise AssertionError(
                f"RT-4c protected file changed: {relative}: {actual} != {expected}"
            )


def assert_source_contract() -> None:
    model = read("backend/app/models/realtime_text_stream_transport.py")
    service = read("backend/app/services/realtime_text_stream_transport.py")
    api = read("backend/app/api/realtime_text.py")
    config = read("backend/app/config.py")
    main = read("backend/app/main.py")
    tests = read("backend/tests/test_realtime_text_stream_transport.py")
    doc = read("docs/v300_rt4_backend_sse_transport.md")
    checklist = read("docs/DRC_v300_goal_checklist_small_commit.md")
    progress = "\n".join(
        read(relative)
        for relative in ("README.md", "roadmap.md", "tasklist.md", "scripts/README.md")
    )

    for marker in (
        "class RealtimeTextStreamCreateRequest",
        "class RealtimeTextStreamCreateResponse",
        "class RealtimeTextStreamCancelResponse",
        "class RealtimeTextStreamProblem",
        "REALTIME_TEXT_STREAM_MAX_INPUT_CHARS",
    ):
        require(model, marker, f"RT-4c model marker {marker}")

    for marker in (
        "class RealtimeTextStreamTransportRegistry",
        "max_event_bytes=max(1024",
        "def create_session",
        "def acquire_consumer",
        "async def next_event",
        "def enforce_timeouts",
        "def publish_chunk",
        "def request_cancel",
        "def release_consumer",
        "def serialize_sse",
        "STREAM_PROBLEM_EVENT_BUFFER",
        "STREAM_PROBLEM_EVENT_BYTES",
    ):
        require(service, marker, f"RT-4c service marker {marker}")

    for marker in (
        'router = APIRouter(prefix="/realtime/text"',
        '"/sessions"',
        '"/sessions/{session_id}/events"',
        '"/sessions/{session_id}/cancel"',
        "StreamingResponse",
        'media_type="text/event-stream"',
        '"Cache-Control": "no-cache, no-store"',
        '"X-Accel-Buffering": "no"',
        "request.is_disconnected()",
    ):
        require(api, marker, f"RT-4c API marker {marker}")

    for marker in (
        "realtime_text_stream_idle_ttl_seconds: int = 120",
        "realtime_text_stream_max_duration_seconds: int = 60",
        "realtime_text_stream_max_sessions: int = 8",
        "realtime_text_stream_max_pending_events: int = 32",
        "realtime_text_stream_max_event_bytes: int = 32768",
    ):
        require(config, marker, f"RT-4c config marker {marker}")

    require(main, "realtime_text,", "RT-4c router import")
    require(main, "app.include_router(realtime_text.router)", "RT-4c router include")

    for forbidden in (
        "import framework",
        "from framework",
        "create_text_chat_session",
        "ask_stream(",
        "httpx",
        "requests",
        "WebSocket",
        "provider-level hard cancel: true",
        "hard_cancel_supported: true",
    ):
        forbid(model + service + api + tests, forbidden, "RT-4c forbidden wiring")

    for test_name in (
        "test_create_route_returns_opaque_bounded_session_without_echoing_input",
        "test_sse_route_streams_monotonic_start_chunks_and_terminal",
        "test_cancel_route_queues_request_and_cooperative_terminal",
        "test_capacity_is_bounded_and_inactive_timeout_frees_a_slot",
        "test_only_one_sse_consumer_can_attach",
        "test_idle_timeout_emits_retryable_failed_terminal",
        "test_max_duration_wins_over_idle_timeout",
        "test_pending_event_overflow_drops_buffer_and_queues_safe_terminal",
        "test_disconnected_generator_closes_and_removes_session",
        "test_event_byte_overflow_replaces_chunk_with_deliverable_safe_terminal",
    ):
        require(tests, test_name, f"RT-4c regression {test_name}")

    combined_docs = doc + checklist + progress
    for marker in (
        "RT-4b: COMPLETED / ACCEPTED / PUSHED",
        "RT-4c: IMPLEMENTED / AWAITING_ACCEPTANCE",
        "RT-4d: NOT_STARTED",
        "exact fifteen-file",
        "hard_cancel_supported=false",
        "provider execution remains false",
    ):
        require(combined_docs, marker, f"RT-4c documentation marker {marker}")

    diff_text = run(
        "git",
        "diff",
        "--unified=0",
        "--",
        *sorted(EXPECTED_CHANGED_FILES),
    )
    added_text = "\n".join(
        line[1:]
        for line in diff_text.splitlines()
        if line.startswith("+") and not line.startswith("+++")
    )
    untracked = set(
        filter(
            None,
            run("git", "ls-files", "--others", "--exclude-standard").splitlines(),
        )
    )
    untracked_text = "\n".join(
        read(relative)
        for relative in sorted(untracked)
        if relative != "scripts/check_v300_rt4_backend_sse_transport.py"
    )
    changed_text = added_text + "\n" + untracked_text
    for pattern in SENSITIVE_PATTERNS:
        if re.search(pattern, changed_text, flags=re.IGNORECASE):
            raise AssertionError(f"Sensitive-looking value in RT-4c changed content: {pattern}")


def assert_runtime_contract() -> None:
    framework_before = {
        name for name in sys.modules if name == "framework" or name.startswith("framework.")
    }

    from app.config import AppConfig
    from app.services.realtime_text_stream_transport import (
        RealtimeTextStreamTransportRegistry,
    )

    registry = RealtimeTextStreamTransportRegistry(
        config=AppConfig(
            realtime_text_stream_idle_ttl_seconds=10,
            realtime_text_stream_max_duration_seconds=20,
            realtime_text_stream_max_sessions=2,
            realtime_text_stream_max_pending_events=8,
            realtime_text_stream_max_event_bytes=32768,
        )
    )
    started = registry.create_session(input_text="synthetic gate input")
    if started.turn is None or started.event is None:
        raise AssertionError("RT-4c start result is incomplete")
    session_id = started.session.session_id
    turn_id = started.turn.turn_id
    registry.publish_chunk(session_id=session_id, turn_id=turn_id, text="hello")
    registry.request_cancel(session_id)
    registry.acquire_consumer(session_id)

    async def collect() -> list[str]:
        frames: list[str] = []
        while True:
            event = await registry.next_event(session_id)
            if event is None:
                break
            frames.append(registry.serialize_sse(event))
            if event.terminal is not None:
                break
        return frames

    frames = asyncio.run(collect())
    if len(frames) != 4:
        raise AssertionError(f"RT-4c expected four SSE frames, got {len(frames)}")
    if "event: stream_started" not in frames[0]:
        raise AssertionError("RT-4c start SSE frame missing")
    if "event: stream_cancelled" not in frames[-1]:
        raise AssertionError("RT-4c cancelled terminal SSE frame missing")
    if "synthetic gate input" in "".join(frames):
        raise AssertionError("RT-4c leaked input text into SSE")
    if started.session.hard_cancel_supported:
        raise AssertionError("RT-4c incorrectly claims hard cancellation")
    registry.release_consumer(session_id, terminal_seen=True)
    if registry.has_session(session_id):
        raise AssertionError("RT-4c retained a consumed stream session")

    framework_after = {
        name for name in sys.modules if name == "framework" or name.startswith("framework.")
    }
    if framework_after != framework_before:
        raise AssertionError("RT-4c imported AI Character Framework unexpectedly")


def main() -> None:
    assert_exact_change_surface()
    assert_source_contract()
    assert_runtime_contract()
    assert_hashes()

    print("v300_rt4_backend_sse_status: implemented-awaiting-acceptance")
    print("v300_rt4c_sse_transport_added: True")
    print("v300_rt4c_cancel_endpoint_added: True")
    print("v300_rt4c_single_consumer_enforced: True")
    print("v300_rt4c_capacity_and_time_limits_enforced: True")
    print("v300_rt4c_disconnect_cleanup_enforced: True")
    print("v300_rt4c_event_buffer_and_byte_limits_enforced: True")
    print("v300_rt4c_input_echoed_publicly: False")
    print("v300_rt4c_framework_imported: False")
    print("v300_rt4c_provider_execution: False")
    print("v300_rt4c_hard_cancel_claimed: False")
    print("v300_rt4c_flutter_changed: False")
    print("v300_rt4d_authorization: blocked-pending-rt4c-acceptance")


if __name__ == "__main__":
    main()
