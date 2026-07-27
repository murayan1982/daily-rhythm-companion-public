"""Private voice-input staging lifecycle regression tests."""

from __future__ import annotations

import io
import os
from pathlib import Path
import wave

import pytest

from app.services.voice_input_staging_store import (
    StagedVoiceInputArtifact,
    VoiceInputStagingError,
    VoiceInputStagingStore,
)


def _wav_payload(*, frames: int = 32) -> bytes:
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as writer:
        writer.setnchannels(1)
        writer.setsampwidth(2)
        writer.setframerate(16000)
        writer.writeframes(b"\x00\x00" * frames)
    return buffer.getvalue()


class MutableClock:
    def __init__(self, value: float = 1_700_000_000.0) -> None:
        self.value = value

    def __call__(self) -> float:
        return self.value

    def advance(self, seconds: float) -> None:
        self.value += seconds


def test_stage_returns_path_free_opaque_metadata_and_scoped_consume(tmp_path: Path) -> None:
    store = VoiceInputStagingStore(tmp_path / "voice_input")
    payload = _wav_payload()

    staged = store.stage_chunks((payload[:7], payload[7:]))

    assert len(staged.staging_id) == 32
    assert all(char in "0123456789abcdef" for char in staged.staging_id)
    assert staged.audio_format == "wav"
    assert staged.media_type == "audio/wav"
    assert staged.byte_count == len(payload)
    assert "path" not in staged.__dict__
    assert store.has_artifact(staged.staging_id)

    def consumer(path: Path, metadata: StagedVoiceInputArtifact) -> dict[str, object]:
        assert path.exists()
        assert path.parent == (tmp_path / "voice_input" / "staging").resolve()
        assert path.name == f"{staged.staging_id}.wav"
        assert metadata == staged
        return {"status": "fake-consumed", "byte_count": path.stat().st_size}

    result = store.consume(staged.staging_id, consumer)

    assert result == {"status": "fake-consumed", "byte_count": len(payload)}
    assert not store.has_artifact(staged.staging_id)
    assert store.artifact_count() == 0


def test_application_octet_stream_is_normalized_to_safe_wav_metadata(tmp_path: Path) -> None:
    store = VoiceInputStagingStore(tmp_path / "voice_input")

    staged = store.stage_chunks(
        (_wav_payload(),),
        media_type="application/octet-stream; charset=binary",
    )

    assert staged.media_type == "audio/wav"
    assert staged.audio_format == "wav"


def test_stage_rejects_unsupported_format_media_type_and_invalid_header(
    tmp_path: Path,
) -> None:
    store = VoiceInputStagingStore(tmp_path / "voice_input")

    with pytest.raises(VoiceInputStagingError) as format_error:
        store.stage_chunks((_wav_payload(),), audio_format="mp3")
    assert format_error.value.code == "unsupported_audio_format"

    with pytest.raises(VoiceInputStagingError) as media_error:
        store.stage_chunks((_wav_payload(),), media_type="audio/mpeg")
    assert media_error.value.code == "unsupported_media_type"

    with pytest.raises(VoiceInputStagingError) as header_error:
        store.stage_chunks((b"not-a-wave-file",))
    assert header_error.value.code == "invalid_wav_header"
    assert store.artifact_count() == 0


def test_stage_rejects_empty_invalid_chunk_and_oversized_body_without_leftovers(
    tmp_path: Path,
) -> None:
    root = tmp_path / "voice_input"
    store = VoiceInputStagingStore(root, max_bytes=64)

    with pytest.raises(VoiceInputStagingError) as empty_error:
        store.stage_chunks((b"",))
    assert empty_error.value.code == "empty_audio"

    with pytest.raises(VoiceInputStagingError) as chunk_error:
        store.stage_chunks((_wav_payload(), "invalid"))  # type: ignore[arg-type]
    assert chunk_error.value.code == "artifact_too_large"

    with pytest.raises(VoiceInputStagingError) as size_error:
        store.stage_chunks((_wav_payload(frames=64),))
    assert size_error.value.code == "artifact_too_large"

    staging_dir = root / "staging"
    assert not tuple(staging_dir.glob("*.wav"))
    assert not tuple(staging_dir.glob(".*.part"))


def test_invalid_chunk_type_is_rejected_when_within_size_limit(tmp_path: Path) -> None:
    store = VoiceInputStagingStore(tmp_path / "voice_input", max_bytes=4096)

    with pytest.raises(VoiceInputStagingError) as error:
        store.stage_chunks((_wav_payload(), "invalid"))  # type: ignore[arg-type]

    assert error.value.code == "invalid_audio_chunk"
    assert store.artifact_count() == 0


def test_stage_cleans_partial_when_chunk_iterable_raises(tmp_path: Path) -> None:
    root = tmp_path / "voice_input"
    store = VoiceInputStagingStore(root, max_bytes=4096)
    payload = _wav_payload()

    def failing_chunks():
        yield payload[:12]
        raise ValueError("synthetic stream failed")

    with pytest.raises(VoiceInputStagingError) as error:
        store.stage_chunks(failing_chunks())

    assert error.value.code == "staging_failed"
    staging_dir = root / "staging"
    assert not tuple(staging_dir.glob("*.wav"))
    assert not tuple(staging_dir.glob(".*.part"))


def test_capacity_cleanup_removes_oldest_without_exceeding_bound(tmp_path: Path) -> None:
    clock = MutableClock()
    store = VoiceInputStagingStore(
        tmp_path / "voice_input",
        now=clock,
        ttl_seconds=100,
        max_artifacts=2,
    )

    first = store.stage_chunks((_wav_payload(frames=1),))
    clock.advance(1)
    second = store.stage_chunks((_wav_payload(frames=2),))
    clock.advance(1)
    third = store.stage_chunks((_wav_payload(frames=3),))

    assert not store.has_artifact(first.staging_id)
    assert store.has_artifact(second.staging_id)
    assert store.has_artifact(third.staging_id)
    assert store.artifact_count() == 2


def test_expiry_cleanup_and_expired_consume_are_bounded(tmp_path: Path) -> None:
    clock = MutableClock()
    store = VoiceInputStagingStore(
        tmp_path / "voice_input",
        now=clock,
        ttl_seconds=10,
        max_artifacts=8,
    )
    staged = store.stage_chunks((_wav_payload(),))

    clock.advance(10)
    cleanup = store.cleanup()

    assert cleanup.expired_removed == 1
    assert cleanup.total_removed == 1
    assert not store.has_artifact(staged.staging_id)
    with pytest.raises(VoiceInputStagingError) as error:
        store.consume(staged.staging_id, lambda _path, _metadata: None)
    assert error.value.code == "artifact_not_found"


def test_consume_is_single_use_and_cleans_up_after_consumer_exception(tmp_path: Path) -> None:
    store = VoiceInputStagingStore(tmp_path / "voice_input")
    staged = store.stage_chunks((_wav_payload(),))

    def failing_consumer(_path: Path, _metadata: StagedVoiceInputArtifact) -> None:
        raise ValueError("fake consumer failed")

    with pytest.raises(ValueError, match="fake consumer failed"):
        store.consume(staged.staging_id, failing_consumer)

    assert not store.has_artifact(staged.staging_id)
    with pytest.raises(VoiceInputStagingError) as second_error:
        store.consume(staged.staging_id, lambda _path, _metadata: None)
    assert second_error.value.code == "artifact_not_found"


def test_explicit_discard_and_malformed_ids_do_not_expose_or_escape_paths(
    tmp_path: Path,
) -> None:
    store = VoiceInputStagingStore(tmp_path / "voice_input")
    staged = store.stage_chunks((_wav_payload(),))

    for staging_id in (
        "../secret",
        "..\\secret",
        "/absolute/path",
        "g" * 32,
        "a" * 31,
        "a" * 33,
        "",
    ):
        assert not store.has_artifact(staging_id)
        assert not store.discard(staging_id)

    assert store.discard(staged.staging_id)
    assert not store.discard(staged.staging_id)
    assert store.artifact_count() == 0


def test_cleanup_removes_expired_partial_file_but_preserves_unmanaged_and_symlink(
    tmp_path: Path,
) -> None:
    clock = MutableClock()
    root = tmp_path / "voice_input"
    store = VoiceInputStagingStore(root, now=clock, ttl_seconds=10)
    staged = store.stage_chunks((_wav_payload(),))
    staging_dir = root / "staging"

    partial = staging_dir / ".orphan.part"
    partial.write_bytes(b"partial")
    unmanaged = staging_dir / "notes.txt"
    unmanaged.write_text("keep", encoding="utf-8")
    outside = tmp_path / "outside.wav"
    outside.write_bytes(_wav_payload())
    link = staging_dir / f"{'a' * 32}.wav"

    try:
        link.symlink_to(outside)
    except (OSError, NotImplementedError) as exc:
        pytest.skip(f"symlink creation is unavailable: {exc}")

    os.utime(partial, (clock(), clock()))
    clock.advance(10)
    cleanup = store.cleanup()

    assert cleanup.partial_removed == 1
    assert not partial.exists()
    assert unmanaged.read_text(encoding="utf-8") == "keep"
    assert link.is_symlink()
    assert outside.exists()
    assert not store.has_artifact("a" * 32)
    assert store.has_artifact(staged.staging_id) is False
