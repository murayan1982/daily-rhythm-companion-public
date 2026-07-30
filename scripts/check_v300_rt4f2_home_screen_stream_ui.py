"""Validate the RT-4f2 HomeScreen stream UI implementation candidate."""
from __future__ import annotations

from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
GATE_PATH = "scripts/check_v300_rt4f2_home_screen_stream_ui.py"

EXPECTED_CHANGED_FILES = {
    "app/lib/screens/home_screen.dart",
    "app/test/realtime_text_stream_home_screen_widget_test.dart",
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v300_goal_checklist_small_commit.md",
    "docs/v300_rt4f_ui_streaming_acceptance_inventory.md",
    "docs/v300_rt4f2_home_screen_stream_ui.md",
    GATE_PATH,
}

PROTECTED_UNCHANGED = {
    "app/lib/main.dart",
    "app/lib/models/realtime_text_stream.dart",
    "app/lib/services/realtime_text_stream_client.dart",
    "app/lib/services/realtime_text_stream_controller.dart",
    "app/lib/services/backend_api_client.dart",
    "app/test/realtime_text_stream_client_test.dart",
    "app/test/realtime_text_stream_controller_test.dart",
    "app/pubspec.yaml",
    "app/pubspec.lock",
}

SENSITIVE_PATTERNS = (
    r"sk-[A-Za-z0-9_\-]{12,}",
    r"xai-[A-Za-z0-9_\-]{12,}",
    r"AIza[0-9A-Za-z_\-]{20,}",
    r"Bearer\s+[A-Za-z0-9_\-.]{16,}",
    r"[A-Za-z]:[\\/](?:Users|work)[^\r\n]+",
    r"/(?:home|users)/[^/\s]+/",
    r"192\.168\.\d{1,3}\.\d{1,3}",
    r"transcript\s*[:=]\s*['\"][^'\"]+['\"]",
    r"provider[_ -]payload\s*[:=]",
    r"raw_audio",
    r"screenshot",
    r"operator evidence",
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
            "RT-4f2 exact change surface mismatch: "
            f"missing={sorted(EXPECTED_CHANGED_FILES - actual)}, "
            f"unexpected={sorted(actual - EXPECTED_CHANGED_FILES)}"
        )
    protected_changed = sorted(actual & PROTECTED_UNCHANGED)
    if protected_changed:
        raise AssertionError(f"Protected file changed: {protected_changed}")
    for path in actual:
        if path.startswith("backend/"):
            raise AssertionError(f"Backend file changed: {path}")


def assert_status_markers() -> None:
    combined = "\n".join(
        read(path)
        for path in EXPECTED_CHANGED_FILES
        if path.endswith(".md")
    )
    for marker in (
        "RT-4: CURRENT / NOT_COMPLETED",
        "RT-4e: COMPLETED / ACCEPTED / PUSHED",
        "RT-4f: CURRENT / NOT_COMPLETED",
        "RT-4f1: COMPLETED / ACCEPTED / PUSHED",
        "RT-4f2: IMPLEMENTED / AWAITING_ACCEPTANCE",
        "RT-4f3: NOT_STARTED",
        "RT-4f4: NOT_STARTED",
        "Current small commit: RT-4f2 IMPLEMENTED / AWAITING_ACCEPTANCE",
        "Current implementation commit: none",
        "f54e8638f0255b28e015702bc64b624a6d4a36af",
        "verify and accept RT-4f2 only; do not begin RT-4f3 transcript handoff",
        "RT-5 TTS queue/flush/barge-in",
    ):
        require(combined, marker, f"status marker {marker}")
    require(
        read("scripts/README.md"),
        "v300_rt4f_ui_streaming_acceptance_inventory_status: implemented-awaiting-acceptance",
        "historical RT-4f1 marker",
    )


def assert_home_screen_contract() -> None:
    home = read("app/lib/screens/home_screen.dart")
    for marker in (
        "import '../models/realtime_text_stream.dart';",
        "import '../services/realtime_text_stream_controller.dart';",
        "RealtimeTextStreamController Function()?",
        "realtimeTextStreamControllerFactory",
        ".realtimeTextStreamControllerFactory",
        "_handleRealtimeTextStreamControllerChanged",
        "addListener(",
        "removeListener(",
        "_realtimeTextStreamController?.dispose()",
        "_realtimeTextStreamInputController.dispose()",
        "_startRealtimeTextStream",
        "_cancelRealtimeTextStream",
        "inputText.runes.length > realtimeTextStreamMaxOutputChars",
        "realtimeTextStreamMaxProblemMessageChars",
        "compact.runes.length",
        "compact.runes.take(realtimeTextStreamMaxProblemMessageChars)",
        "String.fromCharCodes(",
        "realtime-text-stream-section",
        "realtime-text-stream-input",
        "realtime-text-stream-start-button",
        "realtime-text-stream-cancel-button",
        "realtime-text-stream-phase",
        "realtime-text-stream-output",
        "realtime-text-stream-error",
        "realtime-text-stream-cancel-mode",
        "realtime-text-stream-hard-cancel-supported",
        "realtime-text-stream-unconfigured",
        "unconfigured",
        "cancel_requested",
        "Hard cancel supported:",
    ):
        require(home, marker, f"HomeScreen marker {marker}")
    for forbidden in (
        "eventsPath",
        "cancelPath",
        "submitVoiceInputDemoRequest(textHint: _realtimeTextStreamInputController",
    ):
        forbid(home, forbidden, f"HomeScreen forbidden marker {forbidden}")

    init_body = _method_body(home, "void initState()")
    if init_body.count("realtimeTextStreamControllerFactory") != 1:
        raise AssertionError("Realtime factory must be invoked once in initState")
    outside_init = home.replace(init_body, "")
    forbid(outside_init, "realtimeTextStreamControllerFactory?.call()", "factory call outside initState")


def _method_body(text: str, signature: str) -> str:
    start = text.find(signature)
    if start < 0:
        raise AssertionError(f"Missing method: {signature}")
    brace = text.find("{", start)
    depth = 0
    for index in range(brace, len(text)):
        char = text[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start : index + 1]
    raise AssertionError(f"Could not parse method body: {signature}")


def assert_widget_test_contract() -> None:
    test = read("app/test/realtime_text_stream_home_screen_widget_test.dart")
    for marker in (
        "_FakeBackendApiClient",
        "_FakeRealtimeHttpClient extends http.BaseClient",
        "RealtimeTextStreamClient(",
        "RealtimeTextStreamController(",
        "POST",
        "GET",
        "cancelCalls",
        "closed",
        "factoryCalls",
        "duplicate start",
        "incremental completion",
        "cooperative cancellation",
        "safe failure",
        "closed terminal",
        "stream completion does not start voice output",
        "EditableText",
        "widgetList<Text>",
        "final output = tester.widget<Text>",
        "realtime-text-stream-output",
        "longSafeMessage",
        "displayedError.data!.runes.length",
        "realtimeTextStreamMaxProblemMessageChars",
        "_FakeVoiceOutputAudioEngine",
        "http://backend.test",
    ):
        require(test, marker, f"widget test marker {marker}")
    for forbidden in (
        "localhost",
        "127.0.0.1",
        "Socket",
        "Framework",
        "provider_payload",
    ):
        forbid(test, forbidden, f"widget test forbidden marker {forbidden}")


def _changed_text_for_private_scan(relative: str) -> str:
    if relative in untracked_paths():
        text = read(relative)
    else:
        diff = run("git", "diff", "--unified=0", "--", relative)
        lines = []
        for line in diff.splitlines():
            if line.startswith("+++") or not line.startswith("+"):
                continue
            lines.append(line[1:])
        text = "\n".join(lines)
    if relative == GATE_PATH:
        text = re.sub(
            r"SENSITIVE_PATTERNS = \([\s\S]*?\)\n\n",
            "SENSITIVE_PATTERNS = (MASKED_FOR_SELF_SCAN,)\n\n",
            text,
            count=1,
        )
    return text


def assert_private_scan() -> None:
    added = "\n".join(
        _changed_text_for_private_scan(path)
        for path in sorted(changed_paths())
        if path in EXPECTED_CHANGED_FILES
    )
    for pattern in SENSITIVE_PATTERNS:
        match = re.search(pattern, added, flags=re.IGNORECASE)
        if match:
            raise AssertionError(f"Sensitive added content matched: {pattern}")


def main() -> None:
    assert_exact_surface()
    assert_status_markers()
    assert_home_screen_contract()
    assert_widget_test_contract()
    assert_private_scan()
    print("v300_rt4f2_home_screen_stream_ui_status: implemented-awaiting-acceptance")
    print("v300_rt4f2_exact_change_surface: True")
    print("v300_rt4f2_home_screen_factory_owned_controller: True")
    print("v300_rt4f2_real_network_execution: False")
    print("v300_rt4f2_stt_handoff_added: False")
    print("v300_rt4f2_incremental_output_ui: True")
    print("v300_rt4f2_cooperative_cancel_ui: True")
    print("v300_rt4f2_hard_cancel_supported: False")
    print("v300_rt4f2_tts_auto_start: False")
    print("v300_rt4f3_status: not-started")
    print("v300_rt4f4_status: not-started")


if __name__ == "__main__":
    main()
