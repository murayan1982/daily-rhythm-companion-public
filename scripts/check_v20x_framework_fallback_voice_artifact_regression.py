"""Verify the accepted M-4 Framework fallback and artifact safety boundary."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


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


def run_check(relative: str) -> None:
    subprocess.run([sys.executable, str(ROOT / relative)], cwd=ROOT, check=True)


def run_m4_pytest() -> None:
    subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "backend/tests/test_framework_advice.py",
            "backend/tests/test_voice_output_artifact_store.py::test_publish_moves_managed_mp3_behind_opaque_url",
            "backend/tests/test_voice_output_artifact_store.py::test_publish_rejects_file_outside_managed_staging",
            "backend/tests/test_voice_output_artifact_store.py::test_publish_rejects_unsupported_or_mismatched_format",
            "backend/tests/test_voice_output_artifact_store.py::test_resolve_rejects_traversal_and_malformed_artifact_ids",
        ],
        cwd=ROOT,
        check=True,
    )


def main() -> None:
    local_data_before = snapshot_local_data()
    framework_test = read("backend/tests/test_framework_advice.py")
    for needle in (
        "FrameworkConversationEngine",
        "create_text_chat_session(*, preset, character_name)",
        'response.source.engine == "framework"',
        'response.source.framework_character_source == "mapped_default"',
        'pytest.raises(FrameworkEngineError, match="empty response")',
        'engine_basis == "framework_fallback"',
        'response.source.engine == "framework_fallback"',
    ):
        require(framework_test, needle, "Framework regression")

    artifact_test = read("backend/tests/test_voice_output_artifact_store.py")
    for needle in (
        'VoiceOutputArtifactStore(tmp_path / "voice_output")',
        "store.framework_artifact_dir",
        'published.audio_url == f"/demo/voice-output/audio/{published.artifact_id}"',
        "test_publish_rejects_file_outside_managed_staging",
        "test_publish_rejects_unsupported_or_mismatched_format",
        "test_resolve_rejects_traversal_and_malformed_artifact_ids",
    ):
        require(artifact_test, needle, "voice artifact regression")

    combined = framework_test + "\n" + artifact_test
    for forbidden in ("OPENAI_API_KEY", "GEMINI_API_KEY", "ELEVENLABS_API_KEY", "requests.get(", "requests.post("):
        reject(combined, forbidden, "real execution dependency")

    documentation = read("docs/v20x_framework_fallback_voice_artifact_regression.md")
    require(documentation, "Status: COMPLETED", "M-4 accepted documentation")
    require(documentation, "M-4 was accepted before M-5", "M-4 acceptance handoff")

    checklist = read("docs/DRC_v20x_maintenance_checklist.md")
    require(checklist, "Current small commit: none (M-9 accepted; v2.0.1 released)", "M-6 accepted state")
    m4 = checklist.split("# M-4", 1)[1].split("# M-5", 1)[0]
    require(m4, "Status: COMPLETED", "M-4 completed state")
    m5 = checklist.split("# M-5", 1)[1].split("# M-6", 1)[0]
    require(m5, "Status: COMPLETED", "M-5 completed state")
    m6 = checklist.split("# M-6", 1)[1].split("# Planned queue", 1)[0]
    require(m6, "Status: COMPLETED / ACCEPTED", "M-6 accepted state")
    require(m6, "M-6 was accepted on 2026-07-23", "M-6 acceptance record")
    m7 = checklist.split("## M-7", 1)[1].split("## M-8", 1)[0]
    require(m7, "Status: COMPLETED / ACCEPTED", "M-7 accepted state")
    require(m7, "M-7 was accepted on 2026-07-23", "M-7 acceptance record")
    m8 = checklist.split("## M-8", 1)[1].split("\n## M-9 — Patch release", 1)[0]
    require(m8, "Status: COMPLETED / ACCEPTED", "M-8 accepted state")
    require(m8, "M-8 was accepted on 2026-07-23", "M-8 acceptance record")
    m9 = checklist.split("\n## M-9 — Patch release", 1)[1].split("# Future-version boundary", 1)[0]
    require(m9, "Status: COMPLETED / ACCEPTED", "M-9 accepted state")

    run_check("scripts/check_v20x_backend_mock_safe_regression.py")
    run_m4_pytest()

    if snapshot_local_data() != local_data_before:
        raise AssertionError("Accepted M-4 checks must not create or modify backend/local_data")

    print("v20x_framework_fallback_voice_artifact_status: m4-completed")
    print("v20x_framework_fallback_voice_artifact_runtime_change: False")
    print("v20x_framework_fallback_voice_artifact_release_created: False")
    print("[v20x-framework-fallback-voice-artifact-regression-check] OK")


if __name__ == "__main__":
    main()
