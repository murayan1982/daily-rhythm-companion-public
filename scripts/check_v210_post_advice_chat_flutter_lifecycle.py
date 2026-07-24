"""Validate accepted C-1c Flutter chat lifecycle/recovery markers."""

from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

PROTECTED_RELEASE_HASHES = {
    "docs/DRC_v200_goal_checklist_small_commit.md": "4c043837986c626c6fc44e4f84f73b019b2c8c21da7531a3f029554006b7eb63",
    "release_notes/v2.0.0.md": "d2e13041ae51b9fef330a01a0d9124ccbfb6fb0850a0c2a29966baf96be3417b",
    "docs/DRC_v20x_maintenance_checklist.md": "02e6e2e49a54a5c1360ee5d95d6bed2314ab42aec5dce911f3ed72867c4d46f2",
    "docs/v201_patch_release_record.md": "9b724a6c5c7ffffdb3e699ad010ff75148ec4549b6cf2d940b44e62e161140bd",
    "release_notes/v2.0.1.md": "1e90c85e51ef848b64bddaa73f1f40c659457935e30831027310ea95fc94656b",
}

C1B_BACKEND_HASHES = {
    "backend/app/config.py": "ebe022db586ffbaaa6a37db2f43cddca218c4e1e91cee782ffd7b6c8e607d4a5",
    "backend/app/models/chat.py": "0463b3651664f2ee3f2aca6ecfe0c144aabff8a9b3831bc54de4d50e4ec3cb0f",
    "backend/app/services/post_advice_chat_service.py": "2a8087dfaa9cc260d9087a8d037c12189ed665106bad847b8e3109060efc90a7",
    "backend/app/api/chat.py": "1d113f84bf762dfa7b959325d075fda15a8489ef759e7d7c30aacdc60fa3efe5",
    "backend/tests/test_post_advice_chat_lifecycle.py": "7cec4d14730aeea554eeb92c43a08e5a03d39caa38e12b8e3956862bc6eb34c6",
    "backend/tests/test_post_advice_chat_outcomes.py": "53d7092286687812e265d1a249010f8f18251ade27b0d1e19bda2192a83e6c8d",
    "backend/tests/test_temporary_lifecycle_config.py": "9143e076cb805bbf4dac82f9a80b6ac253c1c9615f80547ec1db137478b49e05",
}


def read(relative: str) -> str:
    path = ROOT / relative
    if not path.is_file():
        raise AssertionError(f"Missing required file: {relative}")
    return path.read_text(encoding="utf-8")


def normalized_hash(relative: str) -> str:
    data = (ROOT / relative).read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return sha256(data).hexdigest()


def require(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise AssertionError(f"Missing {label}: {needle!r}")


def assert_hashes(expected: dict[str, str], label: str) -> None:
    for relative, expected_hash in expected.items():
        actual = normalized_hash(relative)
        if actual != expected_hash:
            raise AssertionError(f"{label} changed: {relative}: {actual} != {expected_hash}")


def assert_no_sensitive_values(relative: str, text: str) -> None:
    patterns = (
        r"sk-[A-Za-z0-9_\-]{12,}",
        r"xai-[A-Za-z0-9_\-]{12,}",
        r"AIza[0-9A-Za-z_\-]{20,}",
        r"Bearer\s+[A-Za-z0-9_\-.]{16,}",
        r"[A-Za-z]:\\Users\\[^<\r\n]+",
        r"192\.168\.\d{1,3}\.\d{1,3}",
    )
    for pattern in patterns:
        if re.search(pattern, text, flags=re.IGNORECASE):
            raise AssertionError(f"Sensitive-looking value in {relative}: {pattern}")


def main() -> None:
    checklist = read("docs/DRC_v210_goal_checklist_small_commit.md")
    contract = read("docs/v210_post_advice_chat_flutter_lifecycle.md")
    roadmap = read("roadmap.md")
    tasklist = read("tasklist.md")
    scripts_readme = read("scripts/README.md")
    models = read("app/lib/models/chat.dart")
    client = read("app/lib/services/backend_api_client.dart")
    home = read("app/lib/screens/home_screen.dart")
    model_tests = read("app/test/post_advice_chat_lifecycle_test.dart")
    widget_tests = read("app/test/post_advice_chat_lifecycle_widget_test.dart")

    for source in (checklist, roadmap, tasklist, scripts_readme):
        require(source, "C-1c", "C-1c state")
    require(checklist, "C-1c  COMPLETED / ACCEPTED", "C-1c current state")
    require(checklist, "Status: COMPLETED / ACCEPTED", "C-1c accepted status")
    require(checklist, "T-1  COMPLETED / ACCEPTED", "T-1 planned state")
    require(contract, "Status: COMPLETED / ACCEPTED", "detailed contract state")
    require(contract, "Parent phase: C-1 COMPLETED / ACCEPTED", "parent phase state")
    require(scripts_readme, "check_v210_post_advice_chat_flutter_lifecycle.py", "C-1c check command")

    for needle in (
        "class ChatLifecycle",
        "class ChatOutcome",
        "class ChatSessionProblem",
        "class PostAdviceChatApiException",
        "factory ChatLifecycle.legacy",
        "factory ChatOutcome.legacy",
        "bool get canSendMessage",
        "bool get canRestart",
    ):
        require(models, needle, "Flutter structured chat model")

    for needle in (
        "ChatSessionProblem? problem",
        "decoded['detail'] is Map",
        "ChatSessionProblem.fromJson",
        "throw PostAdviceChatApiException",
    ):
        require(client, needle, "typed API problem handling")

    for needle in (
        "ChatSessionProblem? _postAdviceChatProblem",
        "Future<void> _restartPostAdviceChat()",
        "on PostAdviceChatApiException catch",
        "post-advice-chat-message-field",
        "post-advice-chat-send-button",
        "post-advice-chat-restart-button",
        "session.lifecycle.displayState",
        "session.lifecycle.displayProgress",
        "session.outcome.displayLabel",
        "開発者向け詳細",
    ):
        require(home, needle, "Flutter lifecycle/recovery UI")

    for needle in (
        "structured lifecycle and outcome fields",
        "legacy chat payload remains parseable",
        "ChatSessionProblem exposes restartable",
        "PostAdviceChatApiException prefers structured",
    ):
        require(model_tests, needle, "focused model regression")

    for needle in (
        "turn-limit lifecycle disables sending and offers restart",
        "expired session clears stale state and can restart directly",
        "unavailable outcome shows user copy and restart action",
    ):
        require(widget_tests, needle, "focused widget regression")

    for forbidden in (
        "http.get(",
        "http.post(",
        "requests.get(",
        "requests.post(",
        "backend/local_data",
        "credentials.json",
    ):
        if forbidden in model_tests + widget_tests:
            raise AssertionError(f"C-1c focused tests are not mock-safe: {forbidden}")

    assert_hashes(PROTECTED_RELEASE_HASHES, "Protected release record")
    assert_hashes(C1B_BACKEND_HASHES, "Accepted C-1b Backend boundary")

    for relative in (
        "README.md",
        "roadmap.md",
        "tasklist.md",
        "scripts/README.md",
        "docs/DRC_v210_goal_checklist_small_commit.md",
        "docs/v210_post_advice_chat_flutter_lifecycle.md",
    ):
        assert_no_sensitive_values(relative, read(relative))

    print("v210_post_advice_chat_flutter_lifecycle_status: completed-accepted")
    print("v210_post_advice_chat_flutter_lifecycle_current_small_commit: V-1")
    print("v210_post_advice_chat_flutter_lifecycle_parent_phase: C-1-completed-accepted")
    print("v210_post_advice_chat_flutter_lifecycle_structured_models: true")
    print("v210_post_advice_chat_flutter_lifecycle_structured_problem: true")
    print("v210_post_advice_chat_flutter_lifecycle_terminal_restart: true")
    print("v210_post_advice_chat_flutter_lifecycle_turn_progress: true")
    print("v210_post_advice_chat_flutter_lifecycle_backend_runtime_changed: false")
    print("v210_post_advice_chat_flutter_lifecycle_flutter_runtime_changed: true")
    print("v210_post_advice_chat_flutter_lifecycle_real_framework_execution: false")
    print("v210_post_advice_chat_flutter_lifecycle_release_records_changed: false")
    print("[v210-post-advice-chat-flutter-lifecycle-check] OK")


if __name__ == "__main__":
    main()
