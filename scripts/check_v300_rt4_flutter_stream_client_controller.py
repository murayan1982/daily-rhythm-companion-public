"""Validate the RT-4e Flutter stream client/controller candidate.

This gate is source-tree-only. It checks exact scope, Flutter model/client/
controller/test markers, protected non-change surfaces, and public-safe added
content. It does not run a Backend, import Framework, call providers, or read
credentials/transcripts/operator evidence.
"""
from __future__ import annotations

from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]

EXPECTED_CHANGED_FILES = {
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v300_goal_checklist_small_commit.md",
    "app/lib/models/realtime_text_stream.dart",
    "app/lib/services/realtime_text_stream_client.dart",
    "app/lib/services/realtime_text_stream_controller.dart",
    "app/test/realtime_text_stream_client_test.dart",
    "app/test/realtime_text_stream_controller_test.dart",
    "docs/v300_rt4_flutter_stream_client_controller.md",
    "scripts/check_v300_rt4_flutter_stream_client_controller.py",
}

FORBIDDEN_CHANGED_PREFIXES = (
    "backend/",
    "release_notes/",
    "framework/",
)

PROTECTED_FILES = {
    "app/lib/screens/home_screen.dart",
    "app/lib/main.dart",
    "app/lib/services/backend_api_client.dart",
    "app/pubspec.yaml",
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


def run(*args: str) -> str:
    completed = subprocess.run(
        args,
        cwd=ROOT,
        check=True,
        text=True,
        encoding="utf-8",
        errors="surrogateescape",
        capture_output=True,
    )
    return completed.stdout.rstrip("\r\n")


def read(relative: str) -> str:
    path = ROOT / relative
    if not path.is_file():
        raise AssertionError(f"Missing required file: {relative}")
    return path.read_text(encoding="utf-8")


def require(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise AssertionError(f"Missing {label}: {needle!r}")


def forbid(text: str, needle: str, label: str) -> None:
    if needle in text:
        raise AssertionError(f"Unexpected {label}: {needle!r}")


def changed_paths() -> set[str]:
    changed = set(filter(None, run("git", "diff", "--name-only").splitlines()))
    untracked = set(
        filter(None, run("git", "ls-files", "--others", "--exclude-standard").splitlines())
    )
    return {path.replace("\\", "/") for path in changed | untracked}


def untracked_paths() -> set[str]:
    return {
        path.replace("\\", "/")
        for path in filter(
            None,
            run("git", "ls-files", "--others", "--exclude-standard").splitlines(),
        )
    }


def assert_exact_surface() -> None:
    actual = changed_paths()
    if actual != EXPECTED_CHANGED_FILES:
        raise AssertionError(
            "RT-4e exact change surface mismatch: "
            f"missing={sorted(EXPECTED_CHANGED_FILES - actual)}, "
            f"unexpected={sorted(actual - EXPECTED_CHANGED_FILES)}"
        )
    for path in actual:
        if path in PROTECTED_FILES:
            raise AssertionError(f"Protected Flutter file changed: {path}")
        if any(path.startswith(prefix) for prefix in FORBIDDEN_CHANGED_PREFIXES):
            raise AssertionError(f"Forbidden RT-4e path changed: {path}")


def assert_source_markers() -> None:
    model = read("app/lib/models/realtime_text_stream.dart")
    client = read("app/lib/services/realtime_text_stream_client.dart")
    controller = read("app/lib/services/realtime_text_stream_controller.dart")
    client_test = read("app/test/realtime_text_stream_client_test.dart")
    controller_test = read("app/test/realtime_text_stream_controller_test.dart")
    doc = read("docs/v300_rt4_flutter_stream_client_controller.md")

    for marker in (
        "enum RealtimeTextStreamState",
        "enum RealtimeTextStreamEventType",
        "enum RealtimeTextStreamTerminalOutcome",
        "class RealtimeTextStreamSession",
        "class RealtimeTextStreamTurn",
        "class RealtimeTextStreamChunk",
        "class RealtimeTextStreamTerminal",
        "class RealtimeTextStreamEvent",
        "class RealtimeTextStreamCreateResponse",
        "class RealtimeTextStreamCancelResponse",
        "class RealtimeTextStreamProblem",
        "realtimeTextStreamMaxChunkChars = 512",
        "realtimeTextStreamMaxOutputChars = 4096",
        "hardCancelSupported",
    ):
        require(model, marker, f"model marker {marker}")

    for marker in (
        "required http.Client client",
        "POST",
        "GET",
        "utf8.decoder",
        "_parseSseFrame",
        "id",
        "event",
        "data",
        "out_of_order_stream_event",
        "mismatched_stream_session",
        "stale_stream_turn",
        "stream_event_bytes_exceeded",
    ):
        require(client, marker, f"client marker {marker}")

    for marker in (
        "extends ChangeNotifier",
        "RealtimeTextStreamControllerState",
        "active_stream_replacement_rejected",
        "cancelRequested",
        "output_limit_exceeded",
        "unawaited(_subscription?.cancel())",
        "hardCancelSupported: false",
    ):
        require(controller, marker, f"controller marker {marker}")

    for marker in (
        "UTF-8 split across response chunks",
        "multiple SSE frames in one response chunk",
        "chunk and event fields split",
        "posts cooperative cancel path",
        "malformed JSON",
        "missing sequence",
        "duplicate or out-of-order sequence",
        "oversized chunk and output",
        "_FakeSseHttpClient extends http.BaseClient",
    ):
        require(client_test, marker, f"client test marker {marker}")

    for marker in (
        "rejects active stream replacement",
        "requests cooperative cancel",
        "failed terminal exposes bounded safe problem",
        "rejects oversized accumulated output",
        "ignores late events after terminal and dispose",
        "keeps input text out of public state",
    ):
        require(controller_test, marker, f"controller test marker {marker}")

    for forbidden in (
        "WebSocket",
        "EventSource",
        "import 'package:app/screens/home_screen.dart'",
        "framework",
        "OpenAI",
        "provider-level hard cancel: true",
        "hardCancelSupported: true",
    ):
        forbid(model + client + controller + client_test + controller_test, forbidden, forbidden)

    require(doc, "RT-4e: IMPLEMENTED / AWAITING_ACCEPTANCE", "doc state")
    require(doc, "HomeScreen integration: false", "HomeScreen non-action")


def assert_changed_content_safe() -> None:
    diff = run("git", "diff", "--unified=0", "--", *sorted(EXPECTED_CHANGED_FILES))
    added_lines = [
        _mask_gate_regex_definitions(line[1:])
        for line in diff.splitlines()
        if line.startswith("+") and not line.startswith("+++")
    ]
    new_untracked = untracked_paths() & EXPECTED_CHANGED_FILES
    for relative in sorted(new_untracked):
        added_lines.append(_changed_text_for_private_scan(relative))
    added = "\n".join(added_lines)
    for pattern in SENSITIVE_PATTERNS:
        if re.search(pattern, added):
            raise AssertionError(f"Sensitive-looking value in RT-4e added content: {pattern}")


def _changed_text_for_private_scan(relative: str) -> str:
    text = read(relative)
    if relative == "scripts/check_v300_rt4_flutter_stream_client_controller.py":
        return _mask_gate_regex_definitions(text)
    return text


def _mask_gate_regex_definitions(text: str) -> str:
    return re.sub(
        r"SENSITIVE_PATTERNS\s*=\s*\([\s\S]*?\n\)",
        "SENSITIVE_PATTERNS = (<masked-self-regex-definitions>)",
        text,
    )


def assert_protected_markers() -> None:
    for path in PROTECTED_FILES:
        if path in changed_paths():
            raise AssertionError(f"Protected file changed: {path}")
    for changed in changed_paths():
        if changed.startswith("backend/"):
            raise AssertionError(f"Backend tree changed in RT-4e: {changed}")
        if changed.startswith("release_notes/"):
            raise AssertionError(f"Release notes changed in RT-4e: {changed}")


def assert_gate_regression_markers() -> None:
    gate = read("scripts/check_v300_rt4_flutter_stream_client_controller.py")
    forbidden_private_scan = "untracked = " + "changed_paths() & EXPECTED_CHANGED_FILES"
    require(gate, "def untracked_paths() -> set[str]:", "untracked_paths helper")
    require(
        gate,
        "new_untracked = untracked_paths() & EXPECTED_CHANGED_FILES",
        "private scan untracked helper use",
    )
    forbid(
        gate,
        forbidden_private_scan,
        "private scan changed_paths misuse",
    )


def main() -> None:
    assert_exact_surface()
    assert_source_markers()
    assert_changed_content_safe()
    assert_protected_markers()
    assert_gate_regression_markers()

    print("v300_rt4_flutter_stream_client_controller_status: implemented-awaiting-acceptance")
    print("v300_rt4e_exact_change_surface: True")
    print("v300_rt4e_flutter_models_added: True")
    print("v300_rt4e_sse_client_added: True")
    print("v300_rt4e_controller_added: True")
    print("v300_rt4e_fake_transport_tests_added: True")
    print("v300_rt4e_home_screen_changed: False")
    print("v300_rt4e_backend_changed: False")
    print("v300_rt4e_real_network_execution: False")
    print("v300_rt4e_framework_imported: False")
    print("v300_rt4e_provider_level_hard_cancel_claimed: False")
    print("v300_rt4f_authorization: blocked-pending-rt4e-acceptance")


if __name__ == "__main__":
    main()
