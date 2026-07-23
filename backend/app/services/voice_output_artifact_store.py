from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import re
from threading import RLock
from time import time
from typing import Callable, Iterable
from uuid import uuid4

from app.config import AppConfig, load_config


@dataclass(frozen=True)
class PublishedVoiceOutputArtifact:
    """Public-safe metadata for one DRC-managed Web audio artifact."""

    artifact_id: str
    audio_url: str
    audio_format: str
    media_type: str


@dataclass(frozen=True)
class VoiceOutputArtifactCleanupResult:
    """Counts removed by one bounded artifact cleanup pass."""

    staging_removed: int
    public_removed: int


_ARTIFACT_STORE_LOCK = RLock()


class VoiceOutputArtifactStore:
    """Keep FW audio artifacts behind a bounded DRC-owned opaque handoff.

    Framework synthesis writes only into the local staging directory. DRC then
    moves an accepted MP3 into a separate public directory with a random opaque
    ID. Both managed directories receive lazy TTL cleanup; the public artifact
    set and staging leftovers are bounded by the configured count limit.
    """

    _ARTIFACT_ID_PATTERN = re.compile(r"^[0-9a-f]{32}$")
    _SUPPORTED_FORMATS = {"mp3": "audio/mpeg"}

    def __init__(
        self,
        root_dir: str | Path | None = None,
        *,
        config: AppConfig | None = None,
        now: Callable[[], float] | None = None,
        ttl_seconds: int | None = None,
        max_artifacts: int | None = None,
    ) -> None:
        backend_root = Path(__file__).resolve().parents[2]
        configured_root = (
            Path(root_dir).expanduser()
            if root_dir is not None
            else backend_root / "local_data" / "voice_output"
        )
        loaded_config = config or load_config()
        self._root_dir = configured_root.resolve()
        self._staging_dir = self._root_dir / "staging"
        self._public_dir = self._root_dir / "public"
        configured_ttl = (
            ttl_seconds
            if ttl_seconds is not None
            else loaded_config.voice_output_artifact_ttl_seconds
        )
        configured_max = (
            max_artifacts
            if max_artifacts is not None
            else loaded_config.voice_output_artifact_max_count
        )
        self._ttl_seconds = configured_ttl if configured_ttl > 0 else 86400
        self._max_artifacts = configured_max if configured_max > 0 else 100
        self._now = now or time

    @property
    def framework_artifact_dir(self) -> Path:
        """Return the private FW staging directory after lazy cleanup."""

        with _ARTIFACT_STORE_LOCK:
            self._staging_dir.mkdir(parents=True, exist_ok=True)
            self._cleanup_directory(
                self._staging_dir,
                current_time=self._now(),
                max_count=max(0, self._max_artifacts - 1),
            )
            return self._staging_dir

    def publish_framework_artifact(
        self,
        artifact_ref: str | Path | None,
        *,
        audio_format: str | None,
    ) -> PublishedVoiceOutputArtifact | None:
        """Move one validated FW artifact behind an opaque DRC URL."""

        normalized_format = self._normalize_audio_format(audio_format)
        media_type = self._SUPPORTED_FORMATS.get(normalized_format)
        if media_type is None or artifact_ref is None:
            return None

        with _ARTIFACT_STORE_LOCK:
            try:
                source_ref = Path(artifact_ref).expanduser()
                if source_ref.is_symlink():
                    return None
                source = source_ref.resolve(strict=True)
                staging_dir = self._staging_dir.resolve(strict=True)
            except (OSError, RuntimeError):
                return None

            if not self._is_within(source, staging_dir):
                return None
            if not source.is_file() or source.suffix.lower() != f".{normalized_format}":
                return None

            current_time = self._now()
            try:
                source_modified_at = source.stat(follow_symlinks=False).st_mtime
            except OSError:
                return None
            if current_time - source_modified_at >= self._ttl_seconds:
                self._unlink(source)
                return None

            self._cleanup_directory(
                staging_dir,
                current_time=current_time,
                max_count=self._max_artifacts,
                protected_paths=(source,),
            )
            if not source.exists():
                return None

            self._public_dir.mkdir(parents=True, exist_ok=True)
            public_dir = self._public_dir.resolve(strict=True)

            for _ in range(4):
                artifact_id = uuid4().hex
                destination = public_dir / f"{artifact_id}.{normalized_format}"
                if destination.exists():
                    continue

                try:
                    source.replace(destination)
                    published_at = self._now()
                    os.utime(destination, (published_at, published_at))
                except OSError:
                    return None

                self._cleanup_directory(
                    public_dir,
                    current_time=published_at,
                    max_count=self._max_artifacts,
                    protected_paths=(destination,),
                )

                return PublishedVoiceOutputArtifact(
                    artifact_id=artifact_id,
                    audio_url=f"/demo/voice-output/audio/{artifact_id}",
                    audio_format=normalized_format,
                    media_type=media_type,
                )

            return None

    def resolve_public_artifact(self, artifact_id: str) -> Path | None:
        """Resolve one non-expired opaque ID without path traversal or escapes."""

        normalized_id = artifact_id.strip().lower()
        if not self._ARTIFACT_ID_PATTERN.fullmatch(normalized_id):
            return None

        with _ARTIFACT_STORE_LOCK:
            self.cleanup()
            try:
                public_dir = self._public_dir.resolve(strict=True)
                candidate_ref = public_dir / f"{normalized_id}.mp3"
                if candidate_ref.is_symlink():
                    return None
                candidate = candidate_ref.resolve(strict=True)
            except (OSError, RuntimeError):
                return None

            if not self._is_within(candidate, public_dir):
                return None
            if not candidate.is_file() or candidate.suffix.lower() != ".mp3":
                return None

            return candidate

    def cleanup(self) -> VoiceOutputArtifactCleanupResult:
        """Run one lazy cleanup pass over managed staging and public files."""

        with _ARTIFACT_STORE_LOCK:
            current_time = self._now()
            staging_removed = self._cleanup_directory(
                self._staging_dir,
                current_time=current_time,
                max_count=self._max_artifacts,
            )
            public_removed = self._cleanup_directory(
                self._public_dir,
                current_time=current_time,
                max_count=self._max_artifacts,
            )
            return VoiceOutputArtifactCleanupResult(
                staging_removed=staging_removed,
                public_removed=public_removed,
            )

    @staticmethod
    def media_type_for(path: Path) -> str | None:
        """Return the safe media type for a resolved public artifact."""

        if path.suffix.lower() == ".mp3":
            return "audio/mpeg"
        return None

    def _cleanup_directory(
        self,
        directory: Path,
        *,
        current_time: float,
        max_count: int,
        protected_paths: Iterable[Path] = (),
    ) -> int:
        try:
            entries = tuple(directory.iterdir())
        except OSError:
            return 0

        protected = {path.absolute() for path in protected_paths}
        managed_files: list[tuple[Path, float]] = []
        removed = 0

        for entry in entries:
            try:
                if entry.is_symlink() or not entry.is_file():
                    continue
                modified_at = entry.stat(follow_symlinks=False).st_mtime
            except OSError:
                continue

            if current_time - modified_at >= self._ttl_seconds:
                if entry.absolute() in protected:
                    managed_files.append((entry, modified_at))
                    continue
                if self._unlink(entry):
                    removed += 1
                continue

            managed_files.append((entry, modified_at))

        if len(managed_files) <= max_count:
            return removed

        excess = len(managed_files) - max_count
        for entry, _modified_at in sorted(
            managed_files,
            key=lambda item: (item[1], item[0].name),
        ):
            if excess <= 0:
                break
            if entry.absolute() in protected:
                continue
            if self._unlink(entry):
                removed += 1
                excess -= 1

        return removed

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
    def _normalize_audio_format(value: str | None) -> str:
        normalized = (value or "mp3").strip().lower().lstrip(".")
        return normalized or "mp3"

    @staticmethod
    def _is_within(candidate: Path, parent: Path) -> bool:
        try:
            candidate.relative_to(parent)
        except ValueError:
            return False
        return True
