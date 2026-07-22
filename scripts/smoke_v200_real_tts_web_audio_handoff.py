"""Smoke check for the D-next-15 safe Web audio artifact handoff.

This check uses only fake MP3 marker bytes in a temporary directory. It does
not call a provider, start the backend, open a browser, play audio, inspect a
screenshot, author operator evidence, or create a release artifact.
"""

from __future__ import annotations

from pathlib import Path
import re
import sys
import tempfile

from fastapi import HTTPException
from fastapi.responses import FileResponse


ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = ROOT / "backend"
for import_root in (ROOT, BACKEND_ROOT):
    if str(import_root) not in sys.path:
        sys.path.insert(0, str(import_root))

from backend.app.api import voice_output_demo as voice_output_api  # noqa: E402
from backend.app.services.voice_output_artifact_store import (  # noqa: E402
    VoiceOutputArtifactStore,
)


_OPAQUE_URL_PATTERN = re.compile(r"^/demo/voice-output/audio/[0-9a-f]{32}$")


def main() -> int:
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_root = Path(temp_dir)
        store = VoiceOutputArtifactStore(temp_root / "store")

        published = _check_valid_publish_and_resolve(store)
        if published is None:
            return 1
        if not _check_route_file_response(store, published.artifact_id):
            return 1
        if not _check_outside_path_rejected(store, temp_root):
            return 1
        if not _check_unsupported_format_rejected(store):
            return 1
        if not _check_invalid_ids_rejected(store):
            return 1

    print("[smoke-v200-real-tts-web-audio-handoff] OK")
    print(
        "No real provider call, backend startup, browser action, audio playback, "
        "screenshot inspection, operator evidence acceptance, or release artifact was made."
    )
    return 0


def _check_valid_publish_and_resolve(store: VoiceOutputArtifactStore):
    source = store.framework_artifact_dir / "fake-fw-output.mp3"
    source.write_bytes(b"fake-mp3-marker")

    published = store.publish_framework_artifact(source, audio_format="mp3")
    if published is None:
        print("[smoke-v200-real-tts-web-audio-handoff] ERROR: valid staged MP3 was rejected.")
        return None
    if not _OPAQUE_URL_PATTERN.fullmatch(published.audio_url):
        print("[smoke-v200-real-tts-web-audio-handoff] ERROR: public URL was not opaque.")
        return None
    if str(store.framework_artifact_dir) in published.audio_url:
        print("[smoke-v200-real-tts-web-audio-handoff] ERROR: local staging path leaked into URL.")
        return None
    if source.exists():
        print("[smoke-v200-real-tts-web-audio-handoff] ERROR: source artifact was not moved out of staging.")
        return None

    resolved = store.resolve_public_artifact(published.artifact_id)
    if resolved is None or not resolved.is_file():
        print("[smoke-v200-real-tts-web-audio-handoff] ERROR: opaque ID did not resolve.")
        return None
    if resolved.name != f"{published.artifact_id}.mp3":
        print("[smoke-v200-real-tts-web-audio-handoff] ERROR: resolved filename was not opaque.")
        return None
    if store.media_type_for(resolved) != "audio/mpeg":
        print("[smoke-v200-real-tts-web-audio-handoff] ERROR: MP3 media type was not audio/mpeg.")
        return None

    print("v200_real_tts_web_audio_handoff_opaque_url: pass")
    print("v200_real_tts_web_audio_handoff_local_path_hidden: pass")
    return published


def _check_route_file_response(
    store: VoiceOutputArtifactStore,
    artifact_id: str,
) -> bool:
    original_store_class = voice_output_api.VoiceOutputArtifactStore
    voice_output_api.VoiceOutputArtifactStore = lambda: store
    try:
        response = voice_output_api.get_voice_output_demo_audio(artifact_id)
        if not isinstance(response, FileResponse):
            print("[smoke-v200-real-tts-web-audio-handoff] ERROR: route did not return FileResponse.")
            return False
        if response.media_type != "audio/mpeg":
            print("[smoke-v200-real-tts-web-audio-handoff] ERROR: route media type was not audio/mpeg.")
            return False
        headers = dict(response.headers)
        if headers.get("cache-control") != "no-store":
            print("[smoke-v200-real-tts-web-audio-handoff] ERROR: route did not disable caching.")
            return False
        if headers.get("x-content-type-options") != "nosniff":
            print("[smoke-v200-real-tts-web-audio-handoff] ERROR: route did not set nosniff.")
            return False

        try:
            voice_output_api.get_voice_output_demo_audio("../private")
        except HTTPException as exc:
            if exc.status_code != 404:
                print("[smoke-v200-real-tts-web-audio-handoff] ERROR: invalid route ID was not 404.")
                return False
        else:
            print("[smoke-v200-real-tts-web-audio-handoff] ERROR: invalid route ID was served.")
            return False
    finally:
        voice_output_api.VoiceOutputArtifactStore = original_store_class

    print("v200_real_tts_web_audio_handoff_file_route: pass")
    return True


def _check_outside_path_rejected(
    store: VoiceOutputArtifactStore,
    temp_root: Path,
) -> bool:
    outside = temp_root / "outside-private.mp3"
    outside.write_bytes(b"outside-fake-marker")

    published = store.publish_framework_artifact(outside, audio_format="mp3")
    if published is not None or not outside.exists():
        print("[smoke-v200-real-tts-web-audio-handoff] ERROR: outside artifact was accepted or moved.")
        return False

    print("v200_real_tts_web_audio_handoff_outside_path_rejected: pass")
    return True


def _check_unsupported_format_rejected(store: VoiceOutputArtifactStore) -> bool:
    wav_source = store.framework_artifact_dir / "fake-fw-output.wav"
    wav_source.write_bytes(b"fake-wav-marker")

    if store.publish_framework_artifact(wav_source, audio_format="wav") is not None:
        print("[smoke-v200-real-tts-web-audio-handoff] ERROR: unsupported WAV was published.")
        return False
    if not wav_source.exists():
        print("[smoke-v200-real-tts-web-audio-handoff] ERROR: rejected WAV was unexpectedly moved.")
        return False

    print("v200_real_tts_web_audio_handoff_unsupported_format_rejected: pass")
    return True


def _check_invalid_ids_rejected(store: VoiceOutputArtifactStore) -> bool:
    invalid_ids = (
        "",
        "../private",
        "a" * 31,
        "g" * 32,
        "a" * 32 + ".mp3",
        "%2e%2e%2fprivate",
    )
    if any(store.resolve_public_artifact(value) is not None for value in invalid_ids):
        print("[smoke-v200-real-tts-web-audio-handoff] ERROR: malformed artifact ID resolved.")
        return False

    print("v200_real_tts_web_audio_handoff_path_traversal_rejected: pass")
    return True


if __name__ == "__main__":
    raise SystemExit(main())
