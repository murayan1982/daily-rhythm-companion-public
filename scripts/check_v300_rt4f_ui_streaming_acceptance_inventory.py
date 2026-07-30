"""Validate the RT-4f1 UI streaming acceptance inventory candidate.

This gate is source-tree-only. It checks exact docs/test-only scope, required
inventory markers, protected runtime/test surfaces, and public-safe added
content. It does not import Backend or Framework runtime and does not execute
network requests.
"""
from __future__ import annotations

from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
GATE_PATH = "scripts/check_v300_rt4f_ui_streaming_acceptance_inventory.py"

EXPECTED_CHANGED_FILES = {
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v300_goal_checklist_small_commit.md",
    "docs/v300_rt4f_ui_streaming_acceptance_inventory.md",
    GATE_PATH,
}

INSPECTED_PATHS = {
    "app/lib/screens/home_screen.dart",
    "app/lib/main.dart",
    "app/lib/services/backend_api_client.dart",
    "app/lib/services/backend_voice_input_staging_consumer.dart",
    "app/lib/services/microphone_capture.dart",
    "app/lib/services/microphone_capture_host_audio_handoff.dart",
    "app/lib/services/record_microphone_capture_engine.dart",
    "app/lib/models/voice_input_demo.dart",
    "app/lib/models/realtime_text_stream.dart",
    "app/lib/services/realtime_text_stream_client.dart",
    "app/lib/services/realtime_text_stream_controller.dart",
    "app/test/backend_voice_input_staging_consumer_test.dart",
    "app/test/microphone_capture_host_audio_handoff_test.dart",
    "app/test/post_advice_chat_lifecycle_widget_test.dart",
    "app/test/realtime_text_stream_client_test.dart",
    "app/test/realtime_text_stream_controller_test.dart",
    "app/test/widget_test.dart",
    "backend/app/api/realtime_text.py",
    "backend/app/api/voice_input_demo.py",
    "backend/app/config.py",
    "backend/app/main.py",
    "backend/app/models/voice_input_demo.py",
    "backend/app/services/voice_input_demo_service.py",
    "backend/app/services/framework_voice_input_fake_handoff.py",
    "backend/app/services/framework_voice_input_openai_fake_executor.py",
    "backend/app/services/framework_voice_input_openai_real_operator.py",
    "backend/app/services/realtime_text_stream_transport.py",
    "backend/app/services/framework_realtime_text_stream_adapter.py",
    "backend/tests/test_voice_input_fake_handoff_api.py",
    "backend/tests/test_voice_input_openai_fake_executor_api.py",
    "backend/tests/test_framework_voice_input_openai_real_operator.py",
    "backend/tests/test_realtime_text_stream_transport.py",
    "backend/tests/test_framework_realtime_text_stream_adapter.py",
}

PROTECTED_PREFIXES = (
    "app/lib/",
    "app/test/",
    "backend/",
    "release_notes/",
)

PROTECTED_FILES = {
    "app/pubspec.yaml",
    "app/pubspec.lock",
    "pubspec.yaml",
}

SENSITIVE_PATTERNS = (
    r"sk-[A-Za-z0-9_\-]{12,}",
    r"xai-[A-Za-z0-9_\-]{12,}",
    r"AIza[0-9A-Za-z_\-]{20,}",
    r"Bearer\s+[A-Za-z0-9_\-.]{16,}",
    r"[A-Za-z]:[\\/](?:Users|work)[^\r\n]+",
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
            "RT-4f1 exact change surface mismatch: "
            f"missing={sorted(EXPECTED_CHANGED_FILES - actual)}, "
            f"unexpected={sorted(actual - EXPECTED_CHANGED_FILES)}"
        )
    for path in actual:
        if path in PROTECTED_FILES:
            raise AssertionError(f"Protected dependency/version file changed: {path}")
        if any(path.startswith(prefix) for prefix in PROTECTED_PREFIXES) and path not in EXPECTED_CHANGED_FILES:
            raise AssertionError(f"Protected runtime/test/release path changed: {path}")


def assert_inspected_paths_exist() -> None:
    missing = sorted(path for path in INSPECTED_PATHS if not (ROOT / path).is_file())
    if missing:
        raise AssertionError(f"Missing inspected path(s): {missing}")


def assert_status_markers() -> None:
    combined = "\n".join(read(path) for path in EXPECTED_CHANGED_FILES if path.endswith(".md"))
    for marker in (
        "RT-4: CURRENT / NOT_COMPLETED",
        "RT-4e: COMPLETED / ACCEPTED / PUSHED",
        "RT-4e COMPLETED / ACCEPTED / PUSHED",
        "RT-4f: CURRENT / NOT_COMPLETED",
        "RT-4f1: IMPLEMENTED / AWAITING_ACCEPTANCE",
        "RT-4f2: NOT_STARTED",
        "RT-4f3: NOT_STARTED",
        "RT-4f4: NOT_STARTED",
        "Current small commit: RT-4f1 IMPLEMENTED / AWAITING_ACCEPTANCE",
        "Current implementation: RT-4f current behavior inventory and exact small-commit split",
        "Current implementation commit: none",
        "1cfe6134b0d19a4d14ebcf3ec76812ce07dac261",
        "964cbae19728618e85cef0917f747f21ae5c5e4e",
        "verify and accept RT-4f1 only; do not begin RT-4f2 before acceptance",
    ):
        require(combined, marker, f"status marker {marker}")


def assert_inventory_markers() -> None:
    doc = read("docs/v300_rt4f_ui_streaming_acceptance_inventory.md")
    for section in (
        "## HomeScreen Ownership",
        "## RT-3 Transcript Availability",
        "## RT-4e Integration Boundary",
        "## Backend Configured Path",
        "## UI Acceptance Requirements",
        "## Protected Boundaries",
        "## Resolved RT-4f Split",
        "## Non-Actions",
        "## Exact Change Surface",
    ):
        require(doc, section, f"inventory section {section}")

    for marker in (
        "`BackendApiClient apiClient`",
        "`VoiceOutputAudioEngine voiceOutputAudioEngine`",
        "`const HomeScreen()`",
        "has no import of `realtime_text_stream.dart`",
        "`VoiceInputDemoRequestResponse` has a nullable `transcript` field",
        "`VoiceInputDemoService.submit_request()` always returns `accepted=False`, `request_state=\"not_started\"`, and `transcript=None`",
        "Accepted real RT-3 transcript reaches Flutter/HomeScreen: false",
        "Metadata-only voice-input demo transcript: always null in production",
        "Fake Backend transcript routes wired to Flutter: false",
        "Real-STT transcript public API route: absent",
        "Real-STT transcript Flutter handoff: absent",
        "App-owned transcript-to-stream handoff: absent",
        "`BackendVoiceInputStagingConsumer` creates a path-free staging handle",
        "is not forwarded to post-advice chat, LLM, or realtime stream endpoints",
        "`RealtimeTextStreamClient` is constructed with a required `baseUrl`",
        "`RealtimeTextStreamController` is constructed with a `RealtimeTextStreamClient`",
        "`state`, `start(inputText:)`, `cancel()`, and `dispose()`",
        "simultaneous or active replacement starts",
        "Cancellation is cooperative",
        "`hardCancelSupported` is always false",
        "same-origin `eventsPath` and `cancelPath`",
        "`POST /realtime/text/sessions`",
        "`GET /realtime/text/sessions/{session_id}/events`",
        "`POST /realtime/text/sessions/{session_id}/cancel`",
        "`WEB_CORS_ORIGINS`",
        "`DRC_RT4_ENABLE_FRAMEWORK_TEXT_STREAM`",
        "root-public `create_text_chat_session()`",
        "no provider-level immediate hard cancellation",
        "an explicit user action starts exactly one stream",
        "provider-neutral transcript input or bounded manual test input is visibly identifiable",
        "The current source has no app-visible accepted real-STT transcript to connect.",
        "RT-4f3 must first add the missing app-owned provider-neutral handoff boundary.",
        "incremental generated text visibly updates",
        "no automatic TTS starts",
        "do not add TTS queue/flush/barge-in",
        "Runtime behavior changed: false",
    ):
        require(doc, marker, f"inventory marker {marker}")


def assert_source_facts() -> None:
    home = read("app/lib/screens/home_screen.dart")
    main = read("app/lib/main.dart")
    backend_client = read("app/lib/services/backend_api_client.dart")
    voice_model = read("app/lib/models/voice_input_demo.dart")
    staging_consumer = read("app/lib/services/backend_voice_input_staging_consumer.dart")
    stream_client = read("app/lib/services/realtime_text_stream_client.dart")
    stream_controller = read("app/lib/services/realtime_text_stream_controller.dart")
    voice_api = read("backend/app/api/voice_input_demo.py")
    voice_service = read("backend/app/services/voice_input_demo_service.py")
    real_operator = read("backend/app/services/framework_voice_input_openai_real_operator.py")
    realtime_api = read("backend/app/api/realtime_text.py")
    backend_config = read("backend/app/config.py")
    backend_main = read("backend/app/main.py")
    adapter = read("backend/app/services/framework_realtime_text_stream_adapter.py")

    require(home, "this.apiClient = const BackendApiClient()", "HomeScreen api client injection")
    require(home, "this.voiceOutputAudioEngine", "HomeScreen voice output injection")
    require(home, "void initState()", "HomeScreen initState")
    require(home, "void dispose()", "HomeScreen dispose")
    require(home, "_voiceInputDemoResponse", "HomeScreen voice input state")
    require(home, "_postAdviceChatSession", "HomeScreen post-advice chat state")
    require(home, "_buildVoiceInputDemoSection", "HomeScreen voice input section")
    require(home, "_buildPostAdviceChatSection", "HomeScreen post-advice chat section")
    require(home, "submitVoiceInputDemoRequest", "HomeScreen metadata-only voice input call")
    forbid(home, "realtime_text_stream", "HomeScreen realtime import")
    forbid(home, "BackendVoiceInputStagingConsumer", "HomeScreen staging consumer integration")
    require(main, "home: const HomeScreen()", "main HomeScreen construction")
    forbid(main, "RealtimeTextStream", "main realtime injection")
    require(backend_client, "submitVoiceInputDemoRequest", "voice input client method")
    forbid(backend_client, "RealtimeTextStreamClient", "BackendApiClient realtime stream construction")
    require(voice_model, "final String? transcript;", "Flutter transcript field")
    require(voice_model, "String get displayTranscript", "Flutter transcript display helper")
    require(staging_consumer, "class BackendVoiceInputStagingConsumer", "staging consumer class")
    require(staging_consumer, "takeStagedArtifact()", "staging handle transfer")
    require(staging_consumer, "does not execute STT", "staging consumer no STT marker")
    require(voice_api, "metadata-only voice input demo request", "metadata-only endpoint")
    require(voice_api, "fake_transcribe_staged_voice_input", "fake transcript route")
    require(voice_api, "execute_openai_fake_staged_voice_input", "openai fake transcript route")
    forbid(voice_api, "FrameworkVoiceInputOpenAIRealOperator", "real transcript public API route")
    require(voice_service, "accepted=False", "metadata demo accepted false")
    require(voice_service, 'request_state="not_started"', "metadata demo not started")
    require(voice_service, "transcript=None", "metadata demo transcript null")
    require(real_operator, "_transcript: str = field(repr=False, compare=False)", "private transcript field")
    require(real_operator, "def private_transcript", "private transcript property")
    require(real_operator, "No API route, console evidence, provider payload, private path, raw audio, or", "no public route/persistence marker")
    require(stream_client, "required http.Client client", "injected HTTP client")
    require(stream_client, "_resolveSameOriginPath", "same-origin path resolver")
    require(stream_controller, "extends ChangeNotifier", "stream controller")
    require(stream_controller, "Future<void> start({required String inputText})", "controller start")
    require(stream_controller, "Future<void> cancel()", "controller cancel")
    require(stream_controller, "hardCancelSupported: false", "controller hard cancel false")
    require(stream_controller, "active_stream_replacement_rejected", "simultaneous start rejection")
    require(realtime_api, '@router.post(\n    "/sessions"', "create route")
    require(realtime_api, '@router.get("/sessions/{session_id}/events")', "events route")
    require(realtime_api, '"/sessions/{session_id}/cancel"', "cancel route")
    require(backend_main, "CORSMiddleware", "Backend CORS middleware")
    require(backend_main, "allow_origins=list(config.web_cors_origins)", "configured CORS origins")
    require(backend_config, "WEB_CORS_DEFAULT_ORIGINS = (\"*\",)", "default CORS")
    require(backend_config, "realtime_text_stream_framework_enabled: bool = False", "default-off streaming")
    require(backend_config, "DRC_RT4_ENABLE_FRAMEWORK_TEXT_STREAM", "streaming opt-in flag")
    require(adapter, "create_text_chat_session", "FW root-public create")
    require(adapter, "ask_stream", "FW root-public ask_stream")
    require(adapter, "interrupt", "FW root-public interrupt")


def _mask_gate_regex_definitions(text: str) -> str:
    return re.sub(
        r"SENSITIVE_PATTERNS = \((?:.|\n)*?\)\n",
        "SENSITIVE_PATTERNS = (<masked-self-patterns>)\n",
        text,
    )


def _changed_text_for_private_scan(relative: str) -> str:
    text = read(relative)
    if relative == GATE_PATH:
        return _mask_gate_regex_definitions(text)
    return text


def assert_changed_content_safe() -> None:
    diff = run("git", "diff", "--unified=0", "--", *sorted(EXPECTED_CHANGED_FILES))
    added_lines = [
        line[1:]
        for line in diff.splitlines()
        if line.startswith("+") and not line.startswith("+++")
    ]
    new_untracked = untracked_paths() & EXPECTED_CHANGED_FILES
    for relative in sorted(new_untracked):
        added_lines.append(_changed_text_for_private_scan(relative))
    added = "\n".join(added_lines)
    added = _mask_gate_regex_definitions(added)
    for pattern in SENSITIVE_PATTERNS:
        if re.search(pattern, added, flags=re.IGNORECASE):
            raise AssertionError(f"Sensitive/private marker found in added content: {pattern}")


def main() -> None:
    assert_exact_surface()
    assert_inspected_paths_exist()
    assert_status_markers()
    assert_inventory_markers()
    assert_source_facts()
    assert_changed_content_safe()
    print("v300_rt4f_ui_streaming_acceptance_inventory_status: implemented-awaiting-acceptance")
    print("v300_rt4f1_exact_change_surface: True")
    print("v300_rt4f1_docs_test_only: True")
    print("v300_rt4f1_home_screen_realtime_import: False")
    print("v300_rt4f1_transcript_forwarded_to_stream: False")
    print("v300_rt4f1_real_stt_transcript_reaches_flutter: False")
    print("v300_rt4f1_metadata_demo_transcript_nonnull: False")
    print("v300_rt4f1_real_stt_public_api_route: False")
    print("v300_rt4f1_app_transcript_stream_handoff: False")
    print("v300_rt4f1_backend_framework_streaming_default_on: False")
    print("v300_rt4f1_provider_level_hard_cancel_claimed: False")
    print("v300_rt4f2_status: not-started")
    print("v300_rt4f3_status: not-started")
    print("v300_rt4f4_status: not-started")


if __name__ == "__main__":
    main()
