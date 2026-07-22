"""Verify M-4 Framework fallback and voice artifact safety regression.

The check inspects the credential-free tests and runs the full backend pytest
suite. It never uses real provider credentials, a real Framework checkout,
network access, synthesized audio, or release actions.
"""

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
        entries.append(
            (
                path.relative_to(local_data).as_posix(),
                stat.st_size,
                stat.st_mtime_ns,
            )
        )
    return tuple(entries)


def run_check(relative: str) -> None:
    subprocess.run([sys.executable, str(ROOT / relative)], cwd=ROOT, check=True)


def run_pytest() -> None:
    subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "backend/tests"],
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
        'sys.modules.pop("app.api.advice", None)',
        'monkeypatch.setattr(saver_module, "DailyRecordStore"',
    ):
        require(framework_test, needle, "Framework regression")

    artifact_test = read("backend/tests/test_voice_output_artifact_store.py")
    for needle in (
        'VoiceOutputArtifactStore(tmp_path / "voice_output")',
        "store.framework_artifact_dir",
        'published.audio_url == f"/demo/voice-output/audio/{published.artifact_id}"',
        "store.resolve_public_artifact(published.artifact_id)",
        "test_publish_rejects_file_outside_managed_staging",
        "test_publish_rejects_unsupported_or_mismatched_format",
        "test_resolve_rejects_traversal_and_malformed_artifact_ids",
    ):
        require(artifact_test, needle, "voice artifact regression")

    combined = framework_test + "\n" + artifact_test
    for forbidden in (
        "OPENAI_API_KEY",
        "GEMINI_API_KEY",
        "ELEVENLABS_API_KEY",
        "requests.get(",
        "requests.post(",
        "http://",
        "https://",
        "backend/local_data/daily_records.sqlite3",
    ):
        reject(combined, forbidden, "real execution or local-data dependency")

    documentation = read("docs/v20x_framework_fallback_voice_artifact_regression.md")
    for needle in (
        "temporary fake package",
        "AdviceSource.engine=framework_fallback",
        "pytest `tmp_path`",
        "outside the managed staging directory",
        "M-4 does not alter the published DRC_v2.0.0 asset",
    ):
        require(documentation, needle, "M-4 documentation")

    checklist = read("docs/DRC_v20x_maintenance_checklist.md")
    require(checklist, "Current small commit: M-4", "M-4 checklist current item")
    m4 = checklist.split("# M-4", 1)[1].split("# Planned queue", 1)[0]
    require(m4, "Status: CURRENT / NOT_COMPLETED", "M-4 incomplete state")
    require(m4, "M-4 must remain `CURRENT / NOT_COMPLETED`", "M-4 no early completion")
    for item in range(5, 10):
        section = checklist.split(f"## M-{item}", 1)[1]
        if item < 9:
            section = section.split(f"## M-{item + 1}", 1)[0]
        require(section, "Status: PLANNED", f"M-{item} planned state")

    run_check("scripts/check_v20x_backend_mock_safe_regression.py")
    run_pytest()

    local_data_after = snapshot_local_data()
    if local_data_after != local_data_before:
        raise AssertionError("Normal M-4 checks must not create or modify backend/local_data")

    print("v20x_framework_fallback_voice_artifact_status: m4-current-not-completed")
    print("v20x_framework_fallback_voice_artifact_test_modules_added: 2")
    print("v20x_framework_fallback_voice_artifact_credentials_required: False")
    print("v20x_framework_fallback_voice_artifact_real_framework_execution: False")
    print("v20x_framework_fallback_voice_artifact_real_tts_execution: False")
    print("v20x_framework_fallback_voice_artifact_runtime_change: False")
    print("v20x_framework_fallback_voice_artifact_release_created: False")
    print("[v20x-framework-fallback-voice-artifact-regression-check] OK")


if __name__ == "__main__":
    main()
