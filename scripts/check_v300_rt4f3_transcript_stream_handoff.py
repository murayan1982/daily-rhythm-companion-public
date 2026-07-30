from __future__ import annotations

import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASELINE = "a5cf2db58f3a9a1b76d0b6dcfb4f3d252421d005"
GATE_PATH = "scripts/check_v300_rt4f3_transcript_stream_handoff.py"

EXPECTED_CHANGED_FILES = {
    "app/lib/models/provider_neutral_transcript.dart",
    "app/lib/services/realtime_text_stream_transcript_handoff.dart",
    "app/lib/screens/home_screen.dart",
    "app/test/realtime_text_stream_transcript_handoff_test.dart",
    "app/test/realtime_text_stream_transcript_handoff_home_screen_widget_test.dart",
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v300_goal_checklist_small_commit.md",
    "docs/v300_rt4f_ui_streaming_acceptance_inventory.md",
    "docs/v300_rt4f3_transcript_stream_handoff.md",
    GATE_PATH,
}

PROTECTED_PREFIXES = (
    "backend/",
    "app/lib/main.dart",
    "app/lib/models/voice_input_demo.dart",
    "app/lib/models/realtime_text_stream.dart",
    "app/lib/services/realtime_text_stream_client.dart",
    "app/lib/services/realtime_text_stream_controller.dart",
    "app/lib/services/backend_api_client.dart",
    "app/test/realtime_text_stream_home_screen_widget_test.dart",
    "app/test/realtime_text_stream_client_test.dart",
    "app/test/realtime_text_stream_controller_test.dart",
    "app/pubspec.yaml",
    "app/pubspec.lock",
    "release/",
)

SENSITIVE_PATTERNS = (
    re.compile(r"[A-Za-z]:\\(?:Users|work)\\"),
    re.compile(r"/home/[^/\s]+/"),
    re.compile(r"\b(?:192\.168|10\.|172\.(?:1[6-9]|2\d|3[01]))\.\d{1,3}\.\d{1,3}\b"),
    re.compile(r"sk-[A-Za-z0-9_-]{12,}"),
    re.compile(r"provider_payload", re.IGNORECASE),
    re.compile(r"operator evidence", re.IGNORECASE),
    re.compile(r"raw audio", re.IGNORECASE),
    re.compile(r"screenshot", re.IGNORECASE),
)


def run(*args: str) -> str:
    completed = subprocess.run(
        args,
        cwd=ROOT,
        check=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return completed.stdout


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def require(text: str, marker: str, label: str) -> None:
    if marker not in text:
        raise AssertionError(f"Missing {label}: {marker}")


def forbid(text: str, marker: str, label: str) -> None:
    if marker in text:
        raise AssertionError(f"Forbidden {label}: {marker}")


def changed_paths() -> set[str]:
    tracked = {
        path.replace("\\", "/")
        for path in run("git", "diff", "--name-only").splitlines()
        if path.strip()
    }
    untracked = {
        path.replace("\\", "/")
        for path in run("git", "ls-files", "--others", "--exclude-standard").splitlines()
        if path.strip()
    }
    return tracked | untracked


def assert_exact_surface() -> None:
    actual = changed_paths()
    missing = sorted(EXPECTED_CHANGED_FILES - actual)
    unexpected = sorted(actual - EXPECTED_CHANGED_FILES)
    if missing or unexpected:
        raise AssertionError(
            "RT-4f3 exact change surface mismatch: "
            f"missing={missing}, unexpected={unexpected}"
        )
    for path in actual:
        for protected in PROTECTED_PREFIXES:
            if path == protected or path.startswith(protected):
                raise AssertionError(f"Protected path changed: {path}")


def assert_baseline() -> None:
    head = run("git", "rev-parse", "HEAD").strip()
    if head != BASELINE:
        raise AssertionError(f"Unexpected HEAD: {head}")


def assert_docs_contract() -> None:
    combined = "\n".join(
        read(path)
        for path in (
            "README.md",
            "roadmap.md",
            "tasklist.md",
            "scripts/README.md",
            "docs/DRC_v300_goal_checklist_small_commit.md",
            "docs/v300_rt4f_ui_streaming_acceptance_inventory.md",
            "docs/v300_rt4f3_transcript_stream_handoff.md",
        )
    )
    for marker in (
        "RT-4f3: IMPLEMENTED / AWAITING_ACCEPTANCE",
        "RT-4f3 IMPLEMENTED / AWAITING_ACCEPTANCE",
        "RT-4f4: NOT_STARTED",
        "RT-4f4  NOT_STARTED",
        "App-owned provider-neutral transcript-to-stream handoff",
        "1e1a4b27a0fe7c105eec344bfde39afe6a077f8a",
        "VoiceInputDemo transcript wired: false",
        "RT-5 TTS queue/flush/barge-in remains excluded",
        "v300_rt4f3_transcript_stream_handoff_status: implemented-awaiting-acceptance",
    ):
        require(combined, marker, f"doc marker {marker}")
    for forbidden in (
        "RT-4f3: AUTHORIZED / NOT_STARTED",
        "Current small commit: RT-4f3 AUTHORIZED / NOT_STARTED",
        "accepted real-STT transcript reaches Flutter: true",
        "RT-4f4 configured execution has started",
    ):
        forbid(combined, forbidden, f"stale doc marker {forbidden}")


def assert_model_contract() -> None:
    model = read("app/lib/models/provider_neutral_transcript.dart")
    for marker in (
        "class ProviderNeutralTranscriptResult",
        "required this.resultId",
        "required this.text",
        "required this.isFinal",
        "providerNeutralTranscriptMaxTextChars = 4096",
        "providerNeutralTranscriptMaxResultIdChars = 128",
        "providerNeutralTranscriptMaxRememberedResultIds = 32",
    ):
        require(model, marker, f"model marker {marker}")
    for forbidden in (
        "providerName",
        "modelName",
        "confidence",
        "audioPath",
        "providerPayload",
        "rawResponse",
        "credential",
    ):
        forbid(model, forbidden, f"model field {forbidden}")


def assert_service_contract() -> None:
    service = read("app/lib/services/realtime_text_stream_transcript_handoff.dart")
    for marker in (
        "typedef ProviderNeutralTranscriptProvider",
        "Future<ProviderNeutralTranscriptResult?> Function()",
        "required RealtimeTextStreamController controller",
        "required ProviderNeutralTranscriptProvider transcriptProvider",
        "RealtimeTextStreamTranscriptHandoffState",
        "phase == RealtimeTextStreamTranscriptHandoffPhase.acquiring",
        "bool _startInFlight = false;",
        "if (_startInFlight) {\n      return;",
        "_startInFlight = true;",
        "finally {\n      _startInFlight = false;",
        "if (_controller.state.isActive)",
        "await _transcriptProvider()",
        "result.resultId.trim()",
        "providerNeutralTranscriptMaxResultIdChars",
        "providerNeutralTranscriptMaxTextChars",
        "_consumedResultIds.contains(resultId)",
        "_rememberResultId(resultId)",
        "await _controller.start(inputText: normalizedTranscript)",
        "providerNeutralTranscriptMaxRememberedResultIds",
        "_consumedResultIds.removeAt(0)",
        "compact.runes.length <= realtimeTextStreamMaxProblemMessageChars",
        "compact.runes.take(realtimeTextStreamMaxProblemMessageChars)",
        "if (_isDisposed)",
    ):
        require(service, marker, f"service marker {marker}")
    start_index = service.index("await _controller.start(inputText: normalizedTranscript)")
    remember_index = service.index("_rememberResultId(resultId)")
    if remember_index > start_index:
        raise AssertionError("Result ID must be consumed before controller.start")
    if service.count("await _controller.start(inputText: normalizedTranscript)") != 1:
        raise AssertionError("Expected exactly one controller.start call in handoff service")
    duplicate_branch = service[
        service.index("if (_startInFlight) {") : service.index(
            "if (_controller.state.isActive)"
        )
    ]
    forbid(
        duplicate_branch,
        "_reject(",
        "in-flight duplicate branch must not reject or alter phase",
    )
    start_body = _method_body(service, "Future<void> startFromNextTranscript()")
    if "finally" not in start_body:
        raise AssertionError("startFromNextTranscript must clear in-flight in finally")
    for forbidden in (
        "_controller.dispose()",
        "BackendApiClient",
        "http.Client",
        "VoiceInputDemoRequestResponse",
        "String? _transcript",
        "normalizedTranscript;",
        "retry",
    ):
        forbid(service, forbidden, f"service forbidden marker {forbidden}")


def assert_home_screen_contract() -> None:
    home = read("app/lib/screens/home_screen.dart")
    for marker in (
        "import '../services/realtime_text_stream_transcript_handoff.dart';",
        "RealtimeTextStreamTranscriptHandoffFactory?",
        "realtimeTextStreamTranscriptHandoffFactory",
        "_realtimeTextStreamTranscriptHandoff",
        "_handleRealtimeTextStreamTranscriptHandoffChanged",
        "_realtimeTextStreamTranscriptHandoff?.removeListener",
        "_realtimeTextStreamTranscriptHandoff?.dispose()",
        "widget.realtimeTextStreamTranscriptHandoffFactory?.call(",
        "realtimeTextStreamController",
        "realtime-text-stream-transcript-handoff",
        "realtime-text-stream-transcript-start-button",
        "realtime-text-stream-transcript-status",
        "realtime-text-stream-transcript-error",
        "realtime-text-stream-transcript-unconfigured",
        "realtime-text-stream-transcript-privacy-note",
        "Start from injected provider-neutral transcript",
        "Transcript text is not displayed or stored by this UI.",
        "_startRealtimeTextStreamTranscriptHandoff",
    ):
        require(home, marker, f"HomeScreen marker {marker}")
    init_body = _method_body(home, "void initState()")
    if init_body.count("realtimeTextStreamTranscriptHandoffFactory") != 1:
        raise AssertionError("Handoff factory must be invoked once in initState")
    outside_init = home.replace(init_body, "")
    forbid(
        outside_init,
        "realtimeTextStreamTranscriptHandoffFactory?.call(",
        "handoff factory call outside initState",
    )
    home_added = _changed_text_for_private_scan("app/lib/screens/home_screen.dart")
    for forbidden in (
        "_voiceInputDemoResponse.transcript",
        "_realtimeTextStreamInputController.text =",
        "_voiceOutputAudioPlayerController.play(",
        "VoiceInputDemoRequestResponse.transcript",
    ):
        forbid(home_added, forbidden, f"HomeScreen added forbidden marker {forbidden}")


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


def assert_test_contract() -> None:
    unit = read("app/test/realtime_text_stream_transcript_handoff_test.dart")
    widget = read(
        "app/test/realtime_text_stream_transcript_handoff_home_screen_widget_test.dart"
    )
    for marker in (
        "valid final transcript",
        "active stream rejects before invoking provider",
        "simultaneous duplicate invocation",
        "simultaneous duplicate invocation during create failure creates once",
        "final third = handoff.startFromNextTranscript()",
        "providerCalls, 1",
        "fakeHttp.createCalls, 0",
        "fakeHttp.createCalls, 1",
        "RealtimeTextStreamTranscriptHandoffPhase.acquiring",
        "non-final transcript",
        "whitespace transcript",
        "over 4096 code point transcript",
        "invalid and overlong result IDs",
        "duplicate consumed result ID",
        "provider returns null",
        "provider throws",
        "controller create failure",
        "long safe message",
        "disposal during pending provider",
        "consumed result ID memory is bounded",
        "RealtimeTextStreamClient(",
        "RealtimeTextStreamController(",
        "http.BaseClient",
    ):
        require(unit, marker, f"unit test marker {marker}")
    for marker in (
        "default app shows transcript handoff unconfigured",
        "factory lifecycle passes owned controller",
        "successful handoff starts stream without transcript display",
        "rapid duplicate tap",
        "Transcript handoff: acquiring",
        "providerCalls, 1",
        "fakeHttp.createCalls, 0",
        "invalid transcript",
        "active stream disables transcript handoff",
        "safe failure is bounded",
        "VoiceInputDemo transcript does not trigger stream handoff",
        "completed stream from transcript does not start TTS playback",
        "EditableText",
        "widgetList<Text>",
        "_FakeVoiceOutputAudioEngine",
        "http://backend.test",
    ):
        require(widget, marker, f"widget test marker {marker}")
    combined = unit + "\n" + widget
    for forbidden in (
        "localhost",
        "127.0.0.1",
        "Socket",
        "Framework",
        "provider" "_payload",
    ):
        forbid(combined, forbidden, f"test forbidden marker {forbidden}")


def _changed_text_for_private_scan(relative: str) -> str:
    if relative in run("git", "ls-files", "--others", "--exclude-standard").splitlines():
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
            r"SENSITIVE_PATTERNS = \((?:.|\n)*?\n\)",
            "SENSITIVE_PATTERNS = (<masked>)",
            text,
            count=1,
        )
    return text


def assert_private_scan() -> None:
    for relative in sorted(changed_paths()):
        text = _changed_text_for_private_scan(relative)
        for pattern in SENSITIVE_PATTERNS:
            if pattern.search(text):
                raise AssertionError(f"Sensitive marker found in {relative}")


def main() -> None:
    assert_baseline()
    assert_exact_surface()
    assert_docs_contract()
    assert_model_contract()
    assert_service_contract()
    assert_home_screen_contract()
    assert_test_contract()
    assert_private_scan()
    print("v300_rt4f3_transcript_stream_handoff_status: implemented-awaiting-acceptance")
    print("v300_rt4f3_exact_change_surface: True")
    print("v300_rt4f3_provider_neutral_transcript_model: True")
    print("v300_rt4f3_exactly_one_stream_start: True")
    print("v300_rt4f3_consumed_result_ids_bounded: True")
    print("v300_rt4f3_transcript_text_retained_in_state: False")
    print("v300_rt4f3_voice_input_demo_transcript_wired: False")
    print("v300_rt4f3_real_stt_execution: False")
    print("v300_rt4f3_real_network_execution: False")
    print("v300_rt4f3_main_runtime_wiring: False")
    print("v300_rt4f3_tts_auto_start: False")
    print("v300_rt4f4_status: not-started")


if __name__ == "__main__":
    main()
