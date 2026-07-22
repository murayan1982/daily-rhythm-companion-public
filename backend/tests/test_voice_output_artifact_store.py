"""Voice output artifact publication safety regression tests."""

from __future__ import annotations

from pathlib import Path

from app.services.voice_output_artifact_store import VoiceOutputArtifactStore


def test_publish_moves_managed_mp3_behind_opaque_url(tmp_path: Path) -> None:
    store = VoiceOutputArtifactStore(tmp_path / "voice_output")
    source = store.framework_artifact_dir / "framework-result.mp3"
    source.write_bytes(b"ID3-safe-test-audio")

    published = store.publish_framework_artifact(source, audio_format="mp3")

    assert published is not None
    assert len(published.artifact_id) == 32
    assert all(char in "0123456789abcdef" for char in published.artifact_id)
    assert published.audio_url == f"/demo/voice-output/audio/{published.artifact_id}"
    assert published.audio_format == "mp3"
    assert published.media_type == "audio/mpeg"
    assert not source.exists()

    resolved = store.resolve_public_artifact(published.artifact_id)
    assert resolved is not None
    assert resolved.read_bytes() == b"ID3-safe-test-audio"
    assert str(tmp_path.resolve()) not in published.audio_url


def test_publish_rejects_file_outside_managed_staging(tmp_path: Path) -> None:
    store = VoiceOutputArtifactStore(tmp_path / "voice_output")
    outside = tmp_path / "outside.mp3"
    outside.write_bytes(b"outside")

    published = store.publish_framework_artifact(outside, audio_format="mp3")

    assert published is None
    assert outside.exists()


def test_publish_rejects_unsupported_or_mismatched_format(tmp_path: Path) -> None:
    store = VoiceOutputArtifactStore(tmp_path / "voice_output")
    wav_source = store.framework_artifact_dir / "framework-result.wav"
    wav_source.write_bytes(b"RIFF")
    mp3_source = store.framework_artifact_dir / "framework-result.mp3"
    mp3_source.write_bytes(b"ID3")

    assert store.publish_framework_artifact(wav_source, audio_format="wav") is None
    assert store.publish_framework_artifact(mp3_source, audio_format="wav") is None
    assert wav_source.exists()
    assert mp3_source.exists()


def test_resolve_rejects_traversal_and_malformed_artifact_ids(tmp_path: Path) -> None:
    store = VoiceOutputArtifactStore(tmp_path / "voice_output")

    for artifact_id in (
        "../secret",
        "..\\secret",
        "/absolute/path",
        "g" * 32,
        "a" * 31,
        "a" * 33,
        "",
    ):
        assert store.resolve_public_artifact(artifact_id) is None
