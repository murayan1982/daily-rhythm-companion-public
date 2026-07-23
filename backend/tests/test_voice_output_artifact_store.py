"""Voice output artifact publication safety regression tests."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

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


class MutableClock:
    def __init__(self, value: float = 1_700_000_000.0) -> None:
        self.value = value

    def __call__(self) -> float:
        return self.value

    def advance(self, seconds: float) -> None:
        self.value += seconds


def _publish_test_artifact(
    store: VoiceOutputArtifactStore,
    name: str,
    payload: bytes,
):
    source = store.framework_artifact_dir / name
    source.write_bytes(payload)
    published = store.publish_framework_artifact(source, audio_format="mp3")
    assert published is not None
    return published


def test_public_artifact_expires_from_publish_time(tmp_path: Path) -> None:
    clock = MutableClock()
    store = VoiceOutputArtifactStore(
        tmp_path / "voice_output",
        now=clock,
        ttl_seconds=10,
        max_artifacts=3,
    )
    published = _publish_test_artifact(store, "first.mp3", b"first")

    clock.advance(9)
    assert store.resolve_public_artifact(published.artifact_id) is not None

    clock.advance(1)
    assert store.resolve_public_artifact(published.artifact_id) is None
    assert store.cleanup().public_removed == 0


def test_public_artifact_capacity_removes_oldest_without_touching_on_resolve(
    tmp_path: Path,
) -> None:
    clock = MutableClock()
    store = VoiceOutputArtifactStore(
        tmp_path / "voice_output",
        now=clock,
        ttl_seconds=100,
        max_artifacts=2,
    )

    first = _publish_test_artifact(store, "first.mp3", b"first")
    clock.advance(1)
    second = _publish_test_artifact(store, "second.mp3", b"second")
    assert store.resolve_public_artifact(first.artifact_id) is not None
    clock.advance(1)
    third = _publish_test_artifact(store, "third.mp3", b"third")

    assert store.resolve_public_artifact(first.artifact_id) is None
    assert store.resolve_public_artifact(second.artifact_id) is not None
    assert store.resolve_public_artifact(third.artifact_id) is not None


def test_cleanup_bounds_staging_leftovers_by_ttl_and_capacity(tmp_path: Path) -> None:
    clock = MutableClock()
    store = VoiceOutputArtifactStore(
        tmp_path / "voice_output",
        now=clock,
        ttl_seconds=10,
        max_artifacts=2,
    )
    staging = store.framework_artifact_dir

    oldest = staging / "oldest.mp3"
    oldest.write_bytes(b"oldest")
    os.utime(oldest, (clock(), clock()))
    clock.advance(1)
    middle = staging / "middle.mp3"
    middle.write_bytes(b"middle")
    os.utime(middle, (clock(), clock()))
    clock.advance(1)
    newest = staging / "newest.mp3"
    newest.write_bytes(b"newest")
    os.utime(newest, (clock(), clock()))

    first_cleanup = store.cleanup()
    assert first_cleanup.staging_removed == 1
    assert not oldest.exists()
    assert middle.exists()
    assert newest.exists()

    clock.advance(10)
    second_cleanup = store.cleanup()
    assert second_cleanup.staging_removed == 2
    assert not middle.exists()
    assert not newest.exists()


def test_publish_succeeds_when_capacity_is_one(tmp_path: Path) -> None:
    clock = MutableClock()
    store = VoiceOutputArtifactStore(
        tmp_path / "voice_output",
        now=clock,
        ttl_seconds=100,
        max_artifacts=1,
    )

    first = _publish_test_artifact(store, "first.mp3", b"first")
    clock.advance(1)
    second = _publish_test_artifact(store, "second.mp3", b"second")

    assert store.resolve_public_artifact(first.artifact_id) is None
    assert store.resolve_public_artifact(second.artifact_id) is not None


def test_publish_rejects_expired_staging_artifact(tmp_path: Path) -> None:
    clock = MutableClock()
    store = VoiceOutputArtifactStore(
        tmp_path / "voice_output",
        now=clock,
        ttl_seconds=10,
        max_artifacts=2,
    )
    source = store.framework_artifact_dir / "expired.mp3"
    source.write_bytes(b"expired")
    os.utime(source, (clock(), clock()))
    clock.advance(10)

    assert store.publish_framework_artifact(source, audio_format="mp3") is None
    assert not source.exists()


def test_symlink_artifacts_are_not_published_served_or_deleted(tmp_path: Path) -> None:
    clock = MutableClock()
    root = tmp_path / "voice_output"
    store = VoiceOutputArtifactStore(
        root,
        now=clock,
        ttl_seconds=10,
        max_artifacts=2,
    )
    outside = tmp_path / "outside.mp3"
    outside.write_bytes(b"outside")
    staging_link = store.framework_artifact_dir / "linked.mp3"
    public_dir = root / "public"
    public_dir.mkdir(parents=True, exist_ok=True)
    public_link = public_dir / f"{'a' * 32}.mp3"

    try:
        staging_link.symlink_to(outside)
        public_link.symlink_to(outside)
    except (OSError, NotImplementedError) as exc:
        pytest.skip(f"symlink creation is unavailable: {exc}")

    assert store.publish_framework_artifact(staging_link, audio_format="mp3") is None
    assert store.resolve_public_artifact("a" * 32) is None

    clock.advance(10)
    cleanup = store.cleanup()
    assert cleanup.staging_removed == 0
    assert cleanup.public_removed == 0
    assert staging_link.is_symlink()
    assert public_link.is_symlink()
    assert outside.read_bytes() == b"outside"
