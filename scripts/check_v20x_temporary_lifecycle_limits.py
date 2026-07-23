"""Verify M-5 bounded temporary chat and TTS artifact lifecycles."""

from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
HISTORICAL_HASHES = {
    "docs/DRC_v200_goal_checklist_small_commit.md": "4c043837986c626c6fc44e4f84f73b019b2c8c21da7531a3f029554006b7eb63",
    "release_notes/v2.0.0.md": "d2e13041ae51b9fef330a01a0d9124ccbfb6fb0850a0c2a29966baf96be3417b",
}


def read(relative: str) -> str:
    path = ROOT / relative
    if not path.is_file():
        raise AssertionError(f"Missing required file: {relative}")
    return path.read_text(encoding="utf-8")


def require(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise AssertionError(f"Missing {label}: {needle!r}")


def reject(text: str, needle: str, label: str) -> None:
    if needle in text:
        raise AssertionError(f"Unexpected {label}: {needle!r}")


def snapshot_local_data() -> tuple[tuple[str, int, int], ...] | None:
    local_data = ROOT / "backend/local_data"
    if not local_data.exists():
        return None
    entries: list[tuple[str, int, int]] = []
    for path in sorted(local_data.rglob("*")):
        stat = path.lstat()
        entries.append((path.relative_to(local_data).as_posix(), stat.st_size, stat.st_mtime_ns))
    return tuple(entries)


def assert_historical_hashes() -> None:
    for relative, expected in HISTORICAL_HASHES.items():
        normalized = (ROOT / relative).read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
        actual = sha256(normalized).hexdigest()
        if actual != expected:
            raise AssertionError(f"Historical release record changed: {relative}: {actual} != {expected}")


def run_check(relative: str) -> None:
    subprocess.run([sys.executable, str(ROOT / relative)], cwd=ROOT, check=True)


def run_pytest() -> None:
    subprocess.run([sys.executable, "-m", "pytest", "-q", "backend/tests"], cwd=ROOT, check=True)


def main() -> None:
    local_data_before = snapshot_local_data()

    config = read("backend/app/config.py")
    for needle in (
        "post_advice_chat_ttl_seconds: int = 1800",
        "post_advice_chat_max_sessions: int = 100",
        "voice_output_artifact_ttl_seconds: int = 86400",
        "voice_output_artifact_max_count: int = 100",
        '"POST_ADVICE_CHAT_TTL_SECONDS"',
        '"POST_ADVICE_CHAT_MAX_SESSIONS"',
        '"VOICE_OUTPUT_ARTIFACT_TTL_SECONDS"',
        '"VOICE_OUTPUT_ARTIFACT_MAX_COUNT"',
        "def _env_positive_int",
    ):
        require(config, needle, "bounded lifecycle config")

    for relative in ("backend/.env.example", "backend/env_profiles/mock_safe.env"):
        source = read(relative)
        for needle in (
            "POST_ADVICE_CHAT_TTL_SECONDS=1800",
            "POST_ADVICE_CHAT_MAX_SESSIONS=100",
            "VOICE_OUTPUT_ARTIFACT_TTL_SECONDS=86400",
            "VOICE_OUTPUT_ARTIFACT_MAX_COUNT=100",
        ):
            require(source, needle, f"{relative} lifecycle default")

    chat_service = read("backend/app/services/post_advice_chat_service.py")
    for needle in (
        "class _StoredChatSession",
        "now: Callable[[], float] | None = None",
        "def cleanup(self) -> int",
        "_cleanup_expired_locked",
        "_evict_for_new_session_locked",
        "post_advice_chat_ttl_seconds",
        "post_advice_chat_max_sessions",
    ):
        require(chat_service, needle, "chat lifecycle implementation")

    artifact_store = read("backend/app/services/voice_output_artifact_store.py")
    for needle in (
        "class VoiceOutputArtifactCleanupResult",
        "now: Callable[[], float] | None = None",
        "def cleanup(self) -> VoiceOutputArtifactCleanupResult",
        "voice_output_artifact_ttl_seconds",
        "voice_output_artifact_max_count",
        "os.utime",
        "protected_paths",
        "entry.is_symlink()",
    ):
        require(artifact_store, needle, "artifact lifecycle implementation")
    reject(artifact_store, "rglob(", "recursive artifact cleanup")

    require(read("backend/app/services/voice_output_demo_service.py"), "VoiceOutputArtifactStore(config=config)", "voice service active config")
    require(read("backend/app/api/voice_output_demo.py"), "VoiceOutputArtifactStore()", "audio resolver backward-compatible store construction")

    tests = "\n".join(
        read(relative)
        for relative in (
            "backend/tests/test_temporary_lifecycle_config.py",
            "backend/tests/test_post_advice_chat_lifecycle.py",
            "backend/tests/test_voice_output_artifact_store.py",
        )
    )
    for needle in (
        "test_temporary_lifecycle_defaults_are_bounded",
        "test_invalid_temporary_lifecycle_values_use_safe_defaults",
        "test_session_expires_after_idle_ttl_and_successful_get_refreshes_it",
        "test_capacity_evicts_least_recently_used_session",
        "test_cleanup_and_api_keep_existing_not_found_contract",
        "test_public_artifact_expires_from_publish_time",
        "test_public_artifact_capacity_removes_oldest_without_touching_on_resolve",
        "test_cleanup_bounds_staging_leftovers_by_ttl_and_capacity",
        "test_publish_succeeds_when_capacity_is_one",
        "test_publish_rejects_expired_staging_artifact",
        "test_symlink_artifacts_are_not_published_served_or_deleted",
    ):
        require(tests, needle, "M-5 regression coverage")
    for forbidden in ("time.sleep(", "requests.get(", "requests.post(", "backend/local_data"):
        reject(tests, forbidden, "non-mock-safe test dependency")

    documentation = read("docs/v20x_temporary_lifecycle_limits.md")
    for needle in (
        "Status: COMPLETED / ACCEPTED",
        "least-recently-used",
        "Resolving or downloading an artifact does not refresh its TTL",
        "does not recurse or follow/delete symlinks",
        "M-5 was accepted on 2026-07-22",
    ):
        require(documentation, needle, "M-5 documentation")

    checklist = read("docs/DRC_v20x_maintenance_checklist.md")
    require(checklist, "Current small commit: none (M-6 accepted; M-7 planned)", "M-6 checklist accepted state")
    m4 = checklist.split("# M-4", 1)[1].split("# M-5", 1)[0]
    require(m4, "Status: COMPLETED", "M-4 completed state")
    m5 = checklist.split("# M-5", 1)[1].split("# M-6", 1)[0]
    require(m5, "Status: COMPLETED", "M-5 completed state")
    require(m5, "M-5 was accepted on 2026-07-22", "M-5 acceptance record")
    m6 = checklist.split("# M-6", 1)[1].split("# Planned queue", 1)[0]
    require(m6, "Status: COMPLETED / ACCEPTED", "M-6 accepted state")
    require(m6, "M-6 was accepted on 2026-07-23", "M-6 acceptance record")
    for item in range(7, 10):
        section = checklist.split(f"## M-{item}", 1)[1]
        if item < 9:
            section = section.split(f"## M-{item + 1}", 1)[0]
        require(section, "Status: PLANNED", f"M-{item} planned state")

    assert_historical_hashes()
    run_check("scripts/check_v20x_framework_fallback_voice_artifact_regression.py")
    run_pytest()

    if snapshot_local_data() != local_data_before:
        raise AssertionError("Normal M-5 checks must not create or modify backend/local_data")

    print("v20x_temporary_lifecycle_status: m5-completed-accepted")
    print("v20x_temporary_lifecycle_chat_ttl_seconds: 1800")
    print("v20x_temporary_lifecycle_chat_max_sessions: 100")
    print("v20x_temporary_lifecycle_artifact_ttl_seconds: 86400")
    print("v20x_temporary_lifecycle_artifact_max_count: 100")
    print("v20x_temporary_lifecycle_credentials_required: False")
    print("v20x_temporary_lifecycle_release_created: False")
    print("[v20x-temporary-lifecycle-limits-check] OK")


if __name__ == "__main__":
    main()
