from __future__ import annotations

from dataclasses import dataclass
import re
from pathlib import Path
from uuid import uuid4


@dataclass(frozen=True)
class PublishedVoiceOutputArtifact:
    """Public-safe metadata for one DRC-managed Web audio artifact."""

    artifact_id: str
    audio_url: str
    audio_format: str
    media_type: str


class VoiceOutputArtifactStore:
    """Keep FW audio artifacts behind a DRC-owned opaque Web handoff.

    Framework synthesis writes only into the local staging directory. DRC then
    moves an accepted MP3 into a separate public directory with a random opaque
    ID. API responses expose only the relative URL; local paths and FW artifact
    references stay inside the backend process.
    """

    _ARTIFACT_ID_PATTERN = re.compile(r"^[0-9a-f]{32}$")
    _SUPPORTED_FORMATS = {"mp3": "audio/mpeg"}

    def __init__(self, root_dir: str | Path | None = None) -> None:
        backend_root = Path(__file__).resolve().parents[2]
        configured_root = (
            Path(root_dir).expanduser()
            if root_dir is not None
            else backend_root / "local_data" / "voice_output"
        )
        self._root_dir = configured_root.resolve()
        self._staging_dir = self._root_dir / "staging"
        self._public_dir = self._root_dir / "public"

    @property
    def framework_artifact_dir(self) -> Path:
        """Return the private directory FW may use for generated artifacts."""

        self._staging_dir.mkdir(parents=True, exist_ok=True)
        return self._staging_dir

    def publish_framework_artifact(
        self,
        artifact_ref: str | Path | None,
        *,
        audio_format: str | None,
    ) -> PublishedVoiceOutputArtifact | None:
        """Move one validated FW artifact behind an opaque DRC URL.

        The source must be a regular MP3 file inside this store's staging
        directory. Files outside that boundary, symlink escapes, unsupported
        formats, missing files, and malformed references are rejected.
        """

        normalized_format = self._normalize_audio_format(audio_format)
        media_type = self._SUPPORTED_FORMATS.get(normalized_format)
        if media_type is None or artifact_ref is None:
            return None

        try:
            source = Path(artifact_ref).expanduser().resolve(strict=True)
            staging_dir = self.framework_artifact_dir.resolve(strict=True)
        except (OSError, RuntimeError):
            return None

        if not self._is_within(source, staging_dir):
            return None
        if not source.is_file() or source.suffix.lower() != f".{normalized_format}":
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
            except OSError:
                return None

            return PublishedVoiceOutputArtifact(
                artifact_id=artifact_id,
                audio_url=f"/demo/voice-output/audio/{artifact_id}",
                audio_format=normalized_format,
                media_type=media_type,
            )

        return None

    def resolve_public_artifact(self, artifact_id: str) -> Path | None:
        """Resolve one opaque ID without allowing path traversal or escapes."""

        normalized_id = artifact_id.strip().lower()
        if not self._ARTIFACT_ID_PATTERN.fullmatch(normalized_id):
            return None

        try:
            public_dir = self._public_dir.resolve(strict=True)
            candidate = (public_dir / f"{normalized_id}.mp3").resolve(strict=True)
        except (OSError, RuntimeError):
            return None

        if not self._is_within(candidate, public_dir):
            return None
        if not candidate.is_file() or candidate.suffix.lower() != ".mp3":
            return None

        return candidate

    @staticmethod
    def media_type_for(path: Path) -> str | None:
        """Return the safe media type for a resolved public artifact."""

        if path.suffix.lower() == ".mp3":
            return "audio/mpeg"
        return None

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
