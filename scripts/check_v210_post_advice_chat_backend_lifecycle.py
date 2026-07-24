"""Validate C-1b Backend chat lifecycle/outcome implementation markers."""

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

UNCHANGED_FLUTTER_HASHES = {
    "app/lib/models/chat.dart": "b145e7c335a734ef8609ff579e3533fb0e11f701982ba9a8f7ab48bdb817f1e9",
    "app/lib/services/backend_api_client.dart": "8f790252327c65e7908bd37e13233e4ec5bee6a68b1f2e11b5f536750a82a362",
    "app/lib/screens/home_screen.dart": "3933240c97ec55308342da4b84c8b5087b3eb78f674c7be03f93a0540195d950",
    "app/test/widget_test.dart": "175eec29a41f1cd1731137eeb74444c4e11c02ec6e7494385eb7ca322a2fcfb1",
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
    contract = read("docs/v210_post_advice_chat_backend_lifecycle.md")
    roadmap = read("roadmap.md")
    tasklist = read("tasklist.md")
    scripts_readme = read("scripts/README.md")
    config = read("backend/app/config.py")
    env_example = read("backend/.env.example")
    models = read("backend/app/models/chat.py")
    service = read("backend/app/services/post_advice_chat_service.py")
    api = read("backend/app/api/chat.py")
    lifecycle_tests = read("backend/tests/test_post_advice_chat_lifecycle.py")
    outcome_tests = read("backend/tests/test_post_advice_chat_outcomes.py")
    config_tests = read("backend/tests/test_temporary_lifecycle_config.py")

    for source in (checklist, roadmap, tasklist):
        require(source, "C-1b", "C-1b state")
    require(checklist, "C-1b  COMPLETED / ACCEPTED", "C-1b accepted state")
    require(checklist, "C-1c  CURRENT / NOT_COMPLETED", "C-1c current state")
    require(checklist, "T-1  PLANNED", "T-1 planned state")
    require(contract, "Status: C-1b COMPLETED / ACCEPTED", "accepted state")
    require(contract, "implementation commit: 3055995", "implementation commit")
    require(scripts_readme, "check_v210_post_advice_chat_backend_lifecycle.py", "check command")

    for needle in (
        "post_advice_chat_ttl_seconds: int = 1800",
        "post_advice_chat_max_sessions: int = 100",
        "post_advice_chat_max_turns: int = 8",
        '"POST_ADVICE_CHAT_MAX_TURNS"',
    ):
        require(config, needle, "chat lifecycle config")
    require(env_example, "POST_ADVICE_CHAT_MAX_TURNS=8", "turn-limit env example")

    for needle in (
        "class ChatLifecycle",
        "class ChatOutcome",
        "class ChatSessionProblem",
        "lifecycle: ChatLifecycle",
        "outcome: ChatOutcome",
    ):
        require(models, needle, "structured chat model")

    for needle in (
        "CHAT_PROBLEM_EXPIRED",
        "CHAT_PROBLEM_EVICTED",
        "CHAT_PROBLEM_NOT_FOUND",
        "CHAT_PROBLEM_TURN_LIMIT",
        "class ChatSessionLookupResult",
        "class ChatMessageOperationResult",
        "def get_session_result",
        "def add_message_result",
        "_terminal_sessions",
        "_remember_terminal_locked",
        "_build_framework_outcome",
        'kind="configured"',
        'kind="fallback"',
        'kind="unavailable"',
        'kind="blocked"',
        'kind="skipped"',
    ):
        require(service, needle, "Backend lifecycle implementation")

    require(api, "status_code = 409 if problem.code == CHAT_PROBLEM_TURN_LIMIT else 404", "structured status mapping")
    require(api, "detail=problem.model_dump()", "structured API problem")

    for needle in (
        "test_api_distinguishes_evicted_and_unknown_sessions",
        "test_turn_limit_counts_user_turns_and_returns_restartable_conflict",
        "test_terminal_reason_cache_is_bounded_by_session_capacity",
    ):
        require(lifecycle_tests, needle, "lifecycle regression")
    require(outcome_tests, "test_framework_results_map_to_provider_neutral_outcomes", "outcome regression")
    require(outcome_tests, "test_mock_outcome_is_structured_and_turn_metadata_is_present", "mock outcome regression")
    require(config_tests, "POST_ADVICE_CHAT_MAX_TURNS", "config regression")

    for forbidden in ("requests.get(", "requests.post(", "httpx.", "backend/local_data"):
        if forbidden in lifecycle_tests + outcome_tests:
            raise AssertionError(f"C-1b tests are not mock-safe: {forbidden}")

    assert_hashes(PROTECTED_RELEASE_HASHES, "Protected release record")
    assert_hashes(UNCHANGED_FLUTTER_HASHES, "Flutter C-1c surface")

    for relative in (
        "README.md",
        "roadmap.md",
        "tasklist.md",
        "scripts/README.md",
        "docs/DRC_v210_goal_checklist_small_commit.md",
        "docs/v210_post_advice_chat_backend_lifecycle.md",
    ):
        assert_no_sensitive_values(relative, read(relative))

    print("v210_post_advice_chat_backend_lifecycle_status: completed-accepted")
    print("v210_post_advice_chat_backend_lifecycle_completed_small_commit: C-1b")
    print("v210_post_advice_chat_backend_lifecycle_current_small_commit: C-1c")
    print("v210_post_advice_chat_backend_lifecycle_parent_phase: C-1-current-not-completed")
    print("v210_post_advice_chat_backend_lifecycle_ttl_seconds: 1800")
    print("v210_post_advice_chat_backend_lifecycle_max_sessions: 100")
    print("v210_post_advice_chat_backend_lifecycle_max_turns: 8")
    print("v210_post_advice_chat_backend_lifecycle_structured_outcomes: true")
    print("v210_post_advice_chat_backend_lifecycle_missing_reason_classification: true")
    print("v210_post_advice_chat_backend_lifecycle_turn_limit_http_status: 409")
    print("v210_post_advice_chat_backend_lifecycle_backend_runtime_changed: true")
    print("v210_post_advice_chat_backend_lifecycle_flutter_runtime_changed: false")
    print("v210_post_advice_chat_backend_lifecycle_real_framework_execution: false")
    print("v210_post_advice_chat_backend_lifecycle_release_records_changed: false")
    print("[v210-post-advice-chat-backend-lifecycle-check] OK")


if __name__ == "__main__":
    main()
