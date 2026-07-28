from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import re
from threading import RLock
from time import time
from typing import AsyncIterable, Callable, Iterable, TypeVar
from uuid import uuid4

from app.config import AppConfig, load_config


@dataclass(frozen=True)
class StagedVoiceInputArtifact:
    """Path-free metadata for one private Backend voice-input artifact."""

    staging_id: str
    audio_format: str
    media_type: str
    byte_count: int


@dataclass(frozen=True)
class VoiceInputStagingCleanupResult:
    """Counts removed by one bounded private staging cleanup pass."""

    expired_removed: int
    capacity_removed: int
    partial_removed: int

    @property
    def total_removed(self) -> int:
        return self.expired_removed + self.capacity_removed + self.partial_removed


class VoiceInputStagingError(RuntimeError):
    """Typed private-staging failure suitable for later API normalization."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


_T = TypeVar("_T")
_STAGING_STORE_LOCK = RLock()


class VoiceInputStagingStore:
    """Own bounded, private, single-use WAV artifacts for later FW handoff.

    The store has no public file-serving surface. It returns only an opaque
    hexadecimal staging ID and safe audio metadata. A private filesystem path is
    available only inside ``consume()`` while an injected Backend consumer runs.
    """

    _STAGING_ID_PATTERN = re.compile(r"^[0-9a-f]{32}$")
    _SUPPORTED_AUDIO_FORMAT = "wav"
    _SUPPORTED_MEDIA_TYPES = {"audio/wav", "application/octet-stream"}
    _PUBLIC_MEDIA_TYPE = "audio/wav"

    def __init__(
        self,
        root_dir: str | Path | None = None,
        *,
        config: AppConfig | None = None,
        now: Callable[[], float] | None = None,
        ttl_seconds: int | None = None,
        max_artifacts: int | None = None,
        max_bytes: int | None = None,
    ) -> None:
        backend_root = Path(__file__).resolve().parents[2]
        configured_root = (
            Path(root_dir).expanduser()
            if root_dir is not None
            else backend_root / "local_data" / "voice_input"
        )
        loaded_config = config or load_config()
        configured_ttl = (
            ttl_seconds
            if ttl_seconds is not None
            else loaded_config.voice_input_staging_ttl_seconds
        )
        configured_max = (
            max_artifacts
            if max_artifacts is not None
            else loaded_config.voice_input_staging_max_count
        )
        configured_max_bytes = (
            max_bytes
            if max_bytes is not None
            else loaded_config.voice_input_staging_max_bytes
        )

        self._root_dir = configured_root.resolve()
        self._staging_dir = self._root_dir / "staging"
        self._ttl_seconds = configured_ttl if configured_ttl > 0 else 300
        self._max_artifacts = configured_max if configured_max > 0 else 8
        self._max_bytes = configured_max_bytes if configured_max_bytes > 0 else 1048576
        self._now = now or time

    def stage_chunks(
        self,
        chunks: Iterable[bytes],
        *,
        audio_format: str = "wav",
        media_type: str = "audio/wav",
    ) -> StagedVoiceInputArtifact:
        """Write one bounded WAV body into private staging.

        The caller may provide streamed chunks. The method never returns the
        private path and removes every partial file after rejection or error.
        """

        normalized_format = audio_format.strip().lower().lstrip(".")
        normalized_media_type = media_type.strip().lower().split(";", 1)[0].strip()
        if normalized_format != self._SUPPORTED_AUDIO_FORMAT:
            raise VoiceInputStagingError(
                "unsupported_audio_format",
                "Voice-input staging accepts WAV audio only.",
            )
        if normalized_media_type not in self._SUPPORTED_MEDIA_TYPES:
            raise VoiceInputStagingError(
                "unsupported_media_type",
                "Voice-input staging accepts audio/wav or application/octet-stream only.",
            )

        with _STAGING_STORE_LOCK:
            self._staging_dir.mkdir(parents=True, exist_ok=True)
            self._cleanup_locked(current_time=self._now(), max_count=self._max_artifacts)

            staging_id = uuid4().hex
            partial_path = self._staging_dir / f".{staging_id}.part"
            final_path = self._staging_dir / f"{staging_id}.wav"
            byte_count = 0
            header = bytearray()

            try:
                with partial_path.open("xb") as handle:
                    for chunk in chunks:
                        if not isinstance(chunk, (bytes, bytearray, memoryview)):
                            raise VoiceInputStagingError(
                                "invalid_audio_chunk",
                                "Voice-input staging chunks must be bytes-like values.",
                            )
                        payload = bytes(chunk)
                        if not payload:
                            continue

                        next_size = byte_count + len(payload)
                        if next_size > self._max_bytes:
                            raise VoiceInputStagingError(
                                "artifact_too_large",
                                "Voice-input audio exceeded the configured staging byte limit.",
                            )

                        if len(header) < 12:
                            header.extend(payload[: 12 - len(header)])
                        handle.write(payload)
                        byte_count = next_size

                if byte_count == 0:
                    raise VoiceInputStagingError(
                        "empty_audio",
                        "Voice-input staging rejected an empty audio body.",
                    )
                if len(header) < 12 or header[:4] != b"RIFF" or header[8:12] != b"WAVE":
                    raise VoiceInputStagingError(
                        "invalid_wav_header",
                        "Voice-input staging rejected a body without a RIFF/WAVE header.",
                    )

                partial_path.replace(final_path)
                staged_at = self._now()
                os.utime(final_path, (staged_at, staged_at))
                self._cleanup_locked(
                    current_time=staged_at,
                    max_count=self._max_artifacts,
                    protected_paths=(final_path,),
                )
                if not final_path.exists():
                    raise VoiceInputStagingError(
                        "staging_failed",
                        "Voice-input staging could not retain the completed artifact.",
                    )
            except VoiceInputStagingError:
                self._unlink(partial_path)
                self._unlink(final_path)
                raise
            except Exception as exc:
                self._unlink(partial_path)
                self._unlink(final_path)
                raise VoiceInputStagingError(
                    "staging_failed",
                    "Voice-input staging failed inside the private managed store.",
                ) from exc

            return StagedVoiceInputArtifact(
                staging_id=staging_id,
                audio_format=self._SUPPORTED_AUDIO_FORMAT,
                media_type=self._PUBLIC_MEDIA_TYPE,
                byte_count=byte_count,
            )

    async def stage_async_chunks(
        self,
        chunks: AsyncIterable[bytes],
        *,
        audio_format: str = "wav",
        media_type: str = "audio/wav",
    ) -> StagedVoiceInputArtifact:
        """Stream one bounded WAV request body into private staging.

        The request iterator is consumed incrementally. No complete request body,
        private path, or raw audio payload is returned to the caller.
        """

        normalized_format = audio_format.strip().lower().lstrip(".")
        normalized_media_type = media_type.strip().lower().split(";", 1)[0].strip()
        if normalized_format != self._SUPPORTED_AUDIO_FORMAT:
            raise VoiceInputStagingError(
                "unsupported_audio_format",
                "Voice-input staging accepts WAV audio only.",
            )
        if normalized_media_type not in self._SUPPORTED_MEDIA_TYPES:
            raise VoiceInputStagingError(
                "unsupported_media_type",
                "Voice-input staging accepts audio/wav or application/octet-stream only.",
            )

        with _STAGING_STORE_LOCK:
            self._staging_dir.mkdir(parents=True, exist_ok=True)
            self._cleanup_locked(current_time=self._now(), max_count=self._max_artifacts)
            staging_id = uuid4().hex
            partial_path = self._staging_dir / f".{staging_id}.part"
            final_path = self._staging_dir / f"{staging_id}.wav"

        byte_count = 0
        header = bytearray()
        try:
            with partial_path.open("xb") as handle:
                async for chunk in chunks:
                    if not isinstance(chunk, (bytes, bytearray, memoryview)):
                        raise VoiceInputStagingError(
                            "invalid_audio_chunk",
                            "Voice-input staging chunks must be bytes-like values.",
                        )
                    payload = bytes(chunk)
                    if not payload:
                        continue

                    next_size = byte_count + len(payload)
                    if next_size > self._max_bytes:
                        raise VoiceInputStagingError(
                            "artifact_too_large",
                            "Voice-input audio exceeded the configured staging byte limit.",
                        )

                    if len(header) < 12:
                        header.extend(payload[: 12 - len(header)])
                    handle.write(payload)
                    byte_count = next_size

            if byte_count == 0:
                raise VoiceInputStagingError(
                    "empty_audio",
                    "Voice-input staging rejected an empty audio body.",
                )
            if len(header) < 12 or header[:4] != b"RIFF" or header[8:12] != b"WAVE":
                raise VoiceInputStagingError(
                    "invalid_wav_header",
                    "Voice-input staging rejected a body without a RIFF/WAVE header.",
                )

            with _STAGING_STORE_LOCK:
                partial_path.replace(final_path)
                staged_at = self._now()
                os.utime(final_path, (staged_at, staged_at))
                self._cleanup_locked(
                    current_time=staged_at,
                    max_count=self._max_artifacts,
                    protected_paths=(final_path,),
                )
                if not final_path.exists():
                    raise VoiceInputStagingError(
                        "staging_failed",
                        "Voice-input staging could not retain the completed artifact.",
                    )
        except VoiceInputStagingError:
            self._unlink(partial_path)
            self._unlink(final_path)
            raise
        except Exception as exc:
            self._unlink(partial_path)
            self._unlink(final_path)
            raise VoiceInputStagingError(
                "staging_failed",
                "Voice-input staging failed inside the private managed store.",
            ) from exc

        return StagedVoiceInputArtifact(
            staging_id=staging_id,
            audio_format=self._SUPPORTED_AUDIO_FORMAT,
            media_type=self._PUBLIC_MEDIA_TYPE,
            byte_count=byte_count,
        )

    def consume(
        self,
        staging_id: str,
        consumer: Callable[[Path, StagedVoiceInputArtifact], _T],
    ) -> _T:
        """Run one scoped private-path consumer and discard the artifact once."""

        normalized_id = self._normalize_staging_id(staging_id)
        if normalized_id is None:
            raise VoiceInputStagingError(
                "invalid_staging_id",
                "Voice-input staging ID is malformed.",
            )

        with _STAGING_STORE_LOCK:
            current_time = self._now()
            self._cleanup_locked(current_time=current_time, max_count=self._max_artifacts)
            artifact_path = self._resolve_artifact_locked(normalized_id)
            if artifact_path is None:
                raise VoiceInputStagingError(
                    "artifact_not_found",
                    "Voice-input staging artifact is missing or expired.",
                )

            try:
                byte_count = artifact_path.stat(follow_symlinks=False).st_size
            except OSError as exc:
                raise VoiceInputStagingError(
                    "artifact_not_found",
                    "Voice-input staging artifact is unavailable.",
                ) from exc

            metadata = StagedVoiceInputArtifact(
                staging_id=normalized_id,
                audio_format=self._SUPPORTED_AUDIO_FORMAT,
                media_type=self._PUBLIC_MEDIA_TYPE,
                byte_count=byte_count,
            )

            consumer_error: BaseException | None = None
            try:
                return consumer(artifact_path, metadata)
            except BaseException as exc:
                consumer_error = exc
                raise
            finally:
                removed = self._unlink(artifact_path)
                if not removed and artifact_path.exists():
                    cleanup_error = VoiceInputStagingError(
                        "cleanup_failed",
                        "Voice-input staging artifact cleanup failed after consume.",
                    )
                    if consumer_error is not None:
                        raise cleanup_error from consumer_error
                    raise cleanup_error

    def discard(self, staging_id: str) -> bool:
        """Explicitly discard one private staged artifact without exposing a path."""

        normalized_id = self._normalize_staging_id(staging_id)
        if normalized_id is None:
            return False

        with _STAGING_STORE_LOCK:
            self._cleanup_locked(current_time=self._now(), max_count=self._max_artifacts)
            artifact_path = self._resolve_artifact_locked(normalized_id)
            if artifact_path is None:
                return False
            return self._unlink(artifact_path)

    def has_artifact(self, staging_id: str) -> bool:
        """Return whether one non-expired opaque ID remains staged."""

        normalized_id = self._normalize_staging_id(staging_id)
        if normalized_id is None:
            return False

        with _STAGING_STORE_LOCK:
            self._cleanup_locked(current_time=self._now(), max_count=self._max_artifacts)
            return self._resolve_artifact_locked(normalized_id) is not None

    def artifact_count(self) -> int:
        """Return the bounded count of non-expired staged WAV artifacts."""

        with _STAGING_STORE_LOCK:
            self._cleanup_locked(current_time=self._now(), max_count=self._max_artifacts)
            return len(self._managed_artifacts_locked())

    def cleanup(self) -> VoiceInputStagingCleanupResult:
        """Remove expired, excess, and stale partial files from private staging."""

        with _STAGING_STORE_LOCK:
            return self._cleanup_locked(
                current_time=self._now(),
                max_count=self._max_artifacts,
            )

    def _cleanup_locked(
        self,
        *,
        current_time: float,
        max_count: int,
        protected_paths: Iterable[Path] = (),
    ) -> VoiceInputStagingCleanupResult:
        try:
            entries = tuple(self._staging_dir.iterdir())
        except OSError:
            return VoiceInputStagingCleanupResult(0, 0, 0)

        protected = {path.absolute() for path in protected_paths}
        retained: list[tuple[Path, float]] = []
        expired_removed = 0
        capacity_removed = 0
        partial_removed = 0

        for entry in entries:
            try:
                if entry.is_symlink() or not entry.is_file():
                    continue
                modified_at = entry.stat(follow_symlinks=False).st_mtime
            except OSError:
                continue

            age = current_time - modified_at
            if entry.name.startswith(".") and entry.suffix == ".part":
                if age >= self._ttl_seconds and self._unlink(entry):
                    partial_removed += 1
                continue

            if not self._is_managed_wav_name(entry.name):
                continue

            if age >= self._ttl_seconds and entry.absolute() not in protected:
                if self._unlink(entry):
                    expired_removed += 1
                continue

            retained.append((entry, modified_at))

        excess = max(0, len(retained) - max_count)
        if excess:
            for entry, _modified_at in sorted(
                retained,
                key=lambda item: (item[1], item[0].name),
            ):
                if excess <= 0:
                    break
                if entry.absolute() in protected:
                    continue
                if self._unlink(entry):
                    capacity_removed += 1
                    excess -= 1

        return VoiceInputStagingCleanupResult(
            expired_removed=expired_removed,
            capacity_removed=capacity_removed,
            partial_removed=partial_removed,
        )

    def _resolve_artifact_locked(self, staging_id: str) -> Path | None:
        try:
            staging_dir = self._staging_dir.resolve(strict=True)
            candidate_ref = staging_dir / f"{staging_id}.wav"
            if candidate_ref.is_symlink():
                return None
            candidate = candidate_ref.resolve(strict=True)
        except (OSError, RuntimeError):
            return None

        if not self._is_within(candidate, staging_dir):
            return None
        if not candidate.is_file() or candidate.suffix.lower() != ".wav":
            return None
        return candidate

    def _managed_artifacts_locked(self) -> tuple[Path, ...]:
        try:
            entries = tuple(self._staging_dir.iterdir())
        except OSError:
            return ()

        managed: list[Path] = []
        for entry in entries:
            try:
                if entry.is_symlink() or not entry.is_file():
                    continue
            except OSError:
                continue
            if self._is_managed_wav_name(entry.name):
                managed.append(entry)
        return tuple(managed)

    @classmethod
    def _normalize_staging_id(cls, value: str) -> str | None:
        normalized = value.strip().lower()
        if not cls._STAGING_ID_PATTERN.fullmatch(normalized):
            return None
        return normalized

    @classmethod
    def _is_managed_wav_name(cls, name: str) -> bool:
        if not name.lower().endswith(".wav"):
            return False
        return cls._STAGING_ID_PATTERN.fullmatch(name[:-4].lower()) is not None

    @staticmethod
    def _unlink(path: Path) -> bool:
        try:
            path.unlink()
        except FileNotFoundError:
            return False
        except OSError:
            return False
        return True

    @staticmethod
    def _is_within(candidate: Path, parent: Path) -> bool:
        try:
            candidate.relative_to(parent)
        except ValueError:
            return False
        return True
