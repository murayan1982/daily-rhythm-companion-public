from __future__ import annotations

import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASELINE = "ad28994b66df33d434dc16a1fbbbb0301416afd4"
GATE_PATH = "scripts/check_v300_rt4f4_configured_local_stream_acceptance.py"

EXPECTED_CHANGED_FILES = {
    "app/lib/main.dart",
    "app/lib/services/configured_realtime_text_stream_runtime.dart",
    "app/test/configured_realtime_text_stream_runtime_test.dart",
    "app/test/main_realtime_text_stream_wiring_widget_test.dart",
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v300_goal_checklist_small_commit.md",
    "docs/v300_rt4f_ui_streaming_acceptance_inventory.md",
    "docs/v300_rt4f3_transcript_stream_handoff.md",
    "docs/v300_rt4f4_configured_local_stream_acceptance.md",
    GATE_PATH,
}

PROTECTED_PATHS = {
    "app/lib/screens/home_screen.dart",
    "app/lib/services/realtime_text_stream_client.dart",
    "app/lib/services/realtime_text_stream_controller.dart",
    "app/lib/services/realtime_text_stream_transcript_handoff.dart",
    "app/lib/models/provider_neutral_transcript.dart",
    "app/pubspec.yaml",
    "app/pubspec.lock",
}

PROTECTED_PREFIXES = (
    "backend/",
    "backend\\",
    "release/",
    "release\\",
)

PRIVATE_LAN_IP_RE = re.compile(
    r"\b(?:"
    r"10(?:\.\d{1,3}){3}|"
    r"172\.(?:1[6-9]|2\d|3[01])(?:\.\d{1,3}){2}|"
    r"192\.168(?:\.\d{1,3}){2}"
    r")\b"
)
WINDOWS_DRIVE_ABSOLUTE_PATH_RE = re.compile(
    r"(?i)(?<![A-Za-z0-9_])[A-Z]:[\\/]"
)
WINDOWS_UNC_PATH_RE = re.compile(
    r"\\\\[^\\\r\n]+\\[^\\\r\n]+"
)

SENSITIVE_PATTERNS = (
    WINDOWS_DRIVE_ABSOLUTE_PATH_RE,
    WINDOWS_UNC_PATH_RE,
    re.compile(r"/home/[^/\s]+/"),
    PRIVATE_LAN_IP_RE,
    re.compile(r"sk-[A-Za-z0-9_-]{12,}"),
    re.compile(r"api[_-]?key\s*[:=]\s*['\"][^'\"]+", re.IGNORECASE),
    re.compile(r"provider[_ -]?payload\s*[:=]", re.IGNORECASE),
    re.compile(r"raw[_ -]?audio\s*[:=]", re.IGNORECASE),
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


def assert_baseline() -> None:
    head = run("git", "rev-parse", "HEAD").strip()
    if head != BASELINE:
        raise AssertionError(f"Unexpected HEAD: {head}")


def assert_exact_surface() -> None:
    actual = changed_paths()
    missing = sorted(EXPECTED_CHANGED_FILES - actual)
    unexpected = sorted(actual - EXPECTED_CHANGED_FILES)
    if missing or unexpected:
        raise AssertionError(
            "RT-4f4 exact change surface mismatch: "
            f"missing={missing}, unexpected={unexpected}"
        )
    for path in actual:
        if path in PROTECTED_PATHS:
            raise AssertionError(f"Protected path changed: {path}")
        if any(path.startswith(prefix.replace("\\", "/")) for prefix in PROTECTED_PREFIXES):
            raise AssertionError(f"Protected path changed: {path}")


def assert_runtime_contract() -> None:
    service = read("app/lib/services/configured_realtime_text_stream_runtime.dart")
    for marker in (
        "typedef RealtimeTextStreamHttpClientFactory = http.Client Function();",
        "class ConfiguredRealtimeTextStreamRuntime",
        "required this.enabled",
        "required this.baseUrl",
        "BackendApiClient apiClient = const BackendApiClient()",
        "'DRC_RT4_ENABLE_CONFIGURED_TEXT_STREAM'",
        "defaultValue: false",
        "final configuredBaseUrl = baseUrl.trim();",
        "if (!enabled || !_isValidBaseUrl(configuredBaseUrl))",
        "return null;",
        "Uri.tryParse(value.trim())",
        "!uri.isAbsolute",
        "uri.scheme != 'http' && uri.scheme != 'https'",
        "uri.host.isEmpty",
        "uri.hasFragment",
        "uri.userInfo.isNotEmpty",
        "final httpClient = _httpClientFactory();",
        "RealtimeTextStreamClient(",
        "baseUrl: configuredBaseUrl",
        "RealtimeTextStreamController(client: streamClient)",
    ):
        require(service, marker, f"runtime marker {marker}")
    factory_index = service.index("return () {")
    http_index = service.index("final httpClient = _httpClientFactory();")
    if http_index < factory_index:
        raise AssertionError("HTTP client factory must be called lazily inside controller factory")
    for forbidden in (
        "Framework",
        "provider",
        "transcriptProvider",
        "VoiceInputDemo",
        "throw",
        "print(",
    ):
        forbid(service, forbidden, f"runtime forbidden marker {forbidden}")


def assert_main_contract() -> None:
    main = read("app/lib/main.dart")
    for marker in (
        "import 'services/backend_api_client.dart';",
        "import 'services/configured_realtime_text_stream_runtime.dart';",
        "const apiClient = BackendApiClient();",
        "ConfiguredRealtimeTextStreamRuntime(",
        "'DRC_RT4_ENABLE_CONFIGURED_TEXT_STREAM'",
        "baseUrl: apiClient.baseUrl",
        "DailyRhythmCompanionApp(",
        "apiClient: apiClient",
        ".buildControllerFactory()",
        "final BackendApiClient apiClient;",
        "RealtimeTextStreamController Function()?",
        "HomeScreen(",
        "realtimeTextStreamControllerFactory:",
    ):
        require(main, marker, f"main marker {marker}")
    forbid(main, "const HomeScreen()", "main must pass injected app values to HomeScreen")


def assert_test_contract() -> None:
    unit = read("app/test/configured_realtime_text_stream_runtime_test.dart")
    widget = read("app/test/main_realtime_text_stream_wiring_widget_test.dart")
    for marker in (
        "disabled runtime returns null",
        "enabled runtime accepts valid HTTP and HTTPS URLs",
        "runtime construction and factory lookup are lazy",
        "controller factory creates independent controllers and clients",
        "controller creation alone sends no request",
        "trimmed base URL is used at the client request boundary",
        "https://example.invalid:8443/api/",
        "uri.path, '/api/realtime/text/sessions'",
        "invalid URLs return null without creating clients or throwing",
        "sendCalls, 0",
        "closeCalls, 1",
        "ftp://backend.test",
        "https://user:pass@backend.test",
        "https://backend.test/#fragment",
    ):
        require(unit, marker, f"unit test marker {marker}")
    for marker in (
        "default app constructor remains valid",
        "without factory realtime stream remains unconfigured",
        "configured factory is used once",
        "configured stream leaves transcript handoff unconfigured",
        "widget dispose disposes controller and closes HTTP client",
        "DailyRhythmCompanionApp(",
        "_FakeBackendApiClient",
        "realtime-text-stream-unconfigured",
        "realtime-text-stream-input",
        "realtime-text-stream-transcript-unconfigured",
        "sendCalls, 0",
        "closeCalls, 1",
    ):
        require(widget, marker, f"widget test marker {marker}")
    combined = unit + "\n" + widget
    for forbidden in (
        "localhost",
        "Socket",
        "Framework",
        "provider_payload",
        "VoiceInputDemoRequestResponse.transcript",
    ):
        forbid(combined, forbidden, f"test forbidden marker {forbidden}")


def assert_docs_contract() -> None:
    required_markers_by_path = {
        Path("README.md"): (
            "Current small commit: RT-4f4 (**IMPLEMENTED / AWAITING_REVIEW**)",
            "Current implementation state: IMPLEMENTED / AWAITING_REVIEW",
            "Current implementation commit: none",
            "Last accepted small commit: RT-4f3 (**COMPLETED / ACCEPTED / PUSHED**)",
            "Current realtime phase: RT-4 (**CURRENT / NOT_COMPLETED**)",
            "RT-4f  CURRENT / NOT_COMPLETED",
            "d651a00be8713a70be3a46524f33c787299bbe9c",
        ),
        Path("roadmap.md"): (
            "Status: RT-4 CURRENT / NOT_COMPLETED",
            "Current small commit: RT-4f4 IMPLEMENTED / AWAITING_REVIEW",
            "Current implementation state: IMPLEMENTED / AWAITING_REVIEW",
            "Current implementation commit: none",
            "RT-4f is CURRENT / NOT_COMPLETED",
            "RT-4f3 is COMPLETED / ACCEPTED / PUSHED",
            "d651a00be8713a70be3a46524f33c787299bbe9c",
        ),
        Path("tasklist.md"): (
            "current parent phase: RT-4 CURRENT / NOT_COMPLETED",
            "current small commit: RT-4f4 IMPLEMENTED / AWAITING_REVIEW",
            "current implementation state: IMPLEMENTED / AWAITING_REVIEW",
            "current implementation commit: none",
            "RT-4f is CURRENT / NOT_COMPLETED",
            "RT-4f3 is COMPLETED / ACCEPTED / PUSHED",
            "d651a00be8713a70be3a46524f33c787299bbe9c",
        ),
        Path("scripts/README.md"): (
            "RT-4f3 COMPLETED / ACCEPTED / PUSHED",
            "RT-4f4 implementation candidate is IMPLEMENTED / AWAITING_REVIEW",
            "v300_rt4f3_transcript_stream_handoff_status: implemented-awaiting-acceptance",
            "v300_rt4f4_configured_local_stream_acceptance_status: implemented-awaiting-acceptance",
            "v300_rt5_status: not-started",
        ),
        Path("docs/DRC_v300_goal_checklist_small_commit.md"): (
            "Current small commit: RT-4f4 IMPLEMENTED / AWAITING_REVIEW",
            "Current implementation state: IMPLEMENTED / AWAITING_REVIEW",
            "Current implementation commit: none",
            "Last accepted small commit: RT-4f3 COMPLETED / ACCEPTED / PUSHED",
            "RT-4 CURRENT / NOT_COMPLETED",
            "RT-4f  CURRENT / NOT_COMPLETED",
            "d651a00be8713a70be3a46524f33c787299bbe9c",
        ),
        Path("docs/v300_rt4f_ui_streaming_acceptance_inventory.md"): (
            "RT-4: CURRENT / NOT_COMPLETED",
            "RT-4f: CURRENT / NOT_COMPLETED",
            "RT-4f3: COMPLETED / ACCEPTED / PUSHED",
            "RT-4f4: IMPLEMENTED / AWAITING_REVIEW",
            "Current implementation commit: none",
            "d651a00be8713a70be3a46524f33c787299bbe9c",
        ),
        Path("docs/v300_rt4f3_transcript_stream_handoff.md"): (
            "RT-4: CURRENT / NOT_COMPLETED",
            "RT-4f: CURRENT / NOT_COMPLETED",
            "RT-4f3: COMPLETED / ACCEPTED / PUSHED",
            "RT-4f4: IMPLEMENTED / AWAITING_REVIEW",
            "Current implementation commit: none",
            "implementation commit:",
            "d651a00be8713a70be3a46524f33c787299bbe9c",
            "scripts/check_v300_rt4f3_transcript_stream_handoff.py",
        ),
        Path("docs/v300_rt4f4_configured_local_stream_acceptance.md"): (
            "RT-4: CURRENT / NOT_COMPLETED",
            "RT-4f: CURRENT / NOT_COMPLETED",
            "RT-4f3: COMPLETED / ACCEPTED / PUSHED",
            "RT-4f4: IMPLEMENTED / AWAITING_REVIEW",
            "Current implementation commit: none",
            "RT-4f3 implementation:",
            "d651a00be8713a70be3a46524f33c787299bbe9c",
            "RT-4f3 acceptance docs:",
            "ad28994",
            "DRC_RT4_ENABLE_CONFIGURED_TEXT_STREAM",
            "DRC_BACKEND_API_BASE_URL",
            "DRC_RT4_ENABLE_FRAMEWORK_TEXT_STREAM",
            "default-off",
            "Mock-Safe",
            "Real-STT-to-stream acceptance is false",
            "is not claimed by this candidate.",
            "`hard_cancel_supported` remains false",
            "RT-5 TTS queue/flush/barge-in",
            "app/lib/main.dart",
            "scripts/check_v300_rt4f4_configured_local_stream_acceptance.py",
        ),
    }
    docs = "\n".join(read(str(path).replace("\\", "/")) for path in required_markers_by_path)
    for path, markers in required_markers_by_path.items():
        text = read(str(path).replace("\\", "/"))
        for marker in markers:
            require(text, marker, f"{path} docs marker {marker}")
    for forbidden in (
        "RT-4f4 ACCEPTED: true",
        "RT-4f4 PUSHED: true",
        "configured real Backend/FW execution passed: true",
        "real-STT-to-stream accepted: true",
        "provider-level hard cancel supported: true",
        "RT-4 completed: true",
        "RT-4f completed: true",
    ):
        forbid(docs, forbidden, f"docs forbidden marker {forbidden}")


def _changed_text_for_private_scan(relative: str) -> str:
    untracked = {
        path.replace("\\", "/")
        for path in run("git", "ls-files", "--others", "--exclude-standard").splitlines()
    }
    if relative in untracked:
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
        text = re.sub(
            r"PRIVATE_LAN_IP_RE = re\.compile\((?:.|\n)*?\n\)",
            "PRIVATE_LAN_IP_RE = re.compile(<masked>)",
            text,
            count=1,
        )
        text = re.sub(
            r"WINDOWS_DRIVE_ABSOLUTE_PATH_RE = re\.compile\((?:.|\n)*?\n\)",
            "WINDOWS_DRIVE_ABSOLUTE_PATH_RE = re.compile(<masked>)",
            text,
            count=1,
        )
        text = re.sub(
            r"WINDOWS_UNC_PATH_RE = re\.compile\((?:.|\n)*?\n\)",
            "WINDOWS_UNC_PATH_RE = re.compile(<masked>)",
            text,
            count=1,
        )
        text = re.sub(
            r"def assert_scanner_self_checks\(\) -> None:(?:.|\n)*?(?=\ndef assert_private_scan)",
            "def assert_scanner_self_checks() -> None:\n    <masked>\n",
            text,
            count=1,
        )
    return text


def assert_scanner_self_checks() -> None:
    assert PRIVATE_LAN_IP_RE.search("10.1.2.3")
    assert PRIVATE_LAN_IP_RE.search("10.123.45.67")
    assert PRIVATE_LAN_IP_RE.search("172.16.1.2")
    assert PRIVATE_LAN_IP_RE.search("172.31.1.2")
    assert PRIVATE_LAN_IP_RE.search("192.168.1.2")
    assert PRIVATE_LAN_IP_RE.search("192.168.100.200")

    assert not PRIVATE_LAN_IP_RE.search("8.8.8.8")
    assert not PRIVATE_LAN_IP_RE.search("172.15.1.2")
    assert not PRIVATE_LAN_IP_RE.search("172.32.1.2")
    assert not PRIVATE_LAN_IP_RE.search("<PC_LAN_IP>")

    assert WINDOWS_DRIVE_ABSOLUTE_PATH_RE.search(r"C:\private\file.txt")
    assert WINDOWS_DRIVE_ABSOLUTE_PATH_RE.search(r"D:\workspace\secret")
    assert WINDOWS_DRIVE_ABSOLUTE_PATH_RE.search("E:/private/file.txt")
    assert WINDOWS_UNC_PATH_RE.search(r"\\private-server\share\file.txt")

    assert not WINDOWS_DRIVE_ABSOLUTE_PATH_RE.search(r"backend\tests")
    assert not WINDOWS_DRIVE_ABSOLUTE_PATH_RE.search("app/lib/main.dart")
    assert not PRIVATE_LAN_IP_RE.search("http://<PC_LAN_IP>:8000")


def assert_private_scan() -> None:
    for relative in sorted(changed_paths()):
        text = _changed_text_for_private_scan(relative)
        for pattern in SENSITIVE_PATTERNS:
            if pattern.search(text):
                raise AssertionError(f"Sensitive marker found in {relative}")


def main() -> None:
    assert_baseline()
    assert_exact_surface()
    assert_runtime_contract()
    assert_main_contract()
    assert_test_contract()
    assert_docs_contract()
    assert_scanner_self_checks()
    assert_private_scan()
    print("v300_rt4f4_configured_local_stream_acceptance_status: implemented-awaiting-acceptance")
    print("v300_rt4f4_exact_change_surface: True")
    print("v300_rt4f4_default_enabled: False")
    print("v300_rt4f4_main_runtime_wiring: True")
    print("v300_rt4f4_reuses_backend_base_url: True")
    print("v300_rt4f4_controller_factory_lazy: True")
    print("v300_rt4f4_mock_tests_real_network_execution: False")
    print("v300_rt4f4_real_stt_source_configured: False")
    print("v300_rt4f4_real_stt_to_stream_accepted: False")
    print("v300_rt4f4_cooperative_cancel_only: True")
    print("v300_rt4f4_hard_cancel_supported: False")
    print("v300_rt4f4_tts_auto_start: False")
    print("v300_rt4f4_private_lan_scanner_self_check: True")
    print("v300_rt4f4_windows_absolute_path_scanner_self_check: True")
    print("v300_rt4f4_per_document_status_checks: True")
    print("v300_rt4f4_normalized_base_url_reused: True")
    print("v300_rt5_status: not-started")


if __name__ == "__main__":
    main()
