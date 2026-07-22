"""Smoke check for the guarded v2.0.0 real TTS runtime contract.

This source-tree check does not call a real provider, open a browser, play
sound, read generated audio, or create release evidence. It verifies that:
- default config remains provider-free and audio-free;
- explicit opt-in is required before any framework voice-output call;
- a fake public FW v5 voice output boundary can be called through the neutral
  DRC request contract without DRC-owned provider-specific TTS code;
- only generated + audio_ready + exactly-one handoff is a playback candidate.
"""

from __future__ import annotations

import os
from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = ROOT / "backend"
for import_root in (ROOT, BACKEND_ROOT):
    if str(import_root) not in sys.path:
        sys.path.insert(0, str(import_root))

from backend.app.config import load_config  # noqa: E402
from backend.app.models.voice_output_demo import VoiceOutputDemoRequest  # noqa: E402
from backend.app.services.voice_output_artifact_store import VoiceOutputArtifactStore  # noqa: E402
from backend.app.services.voice_output_demo_service import VoiceOutputDemoService  # noqa: E402


_ENV_KEYS = (
    "CONVERSATION_ENGINE",
    "FRAMEWORK_ROOT",
    "FRAMEWORK_PROJECT_ROOT",
    "VOICE_OUTPUT_DEMO_ENABLED",
    "VOICE_OUTPUT_ADAPTER_MODE",
    "VOICE_OUTPUT_REAL_TTS_ENABLED",
    "VOICE_OUTPUT_UTTERANCE_PURPOSE",
    "DRC_SKIP_BACKEND_DOTENV",
)


def main() -> int:
    with _preserved_env(_ENV_KEYS):
        if not _check_default_guard():
            return 1
        if not _check_fake_framework_runtime_call():
            return 1
        if not _check_fake_framework_unavailable_result():
            return 1
        if not _check_fake_framework_conflicting_handoff_result():
            return 1
        if not _check_fake_framework_unsafe_url_result():
            return 1
        if not _check_no_drc_direct_framework_tts_imports():
            return 1

    print("[smoke-v200-real-tts-web-runtime-contract] OK")
    print("No real provider call, browser action, audio playback, raw audio read, or release artifact was made.")
    return 0


def _check_default_guard() -> bool:
    _clear_env(_ENV_KEYS)
    os.environ.update(
        {
            "CONVERSATION_ENGINE": "framework",
            "VOICE_OUTPUT_DEMO_ENABLED": "1",
            "VOICE_OUTPUT_ADAPTER_MODE": "framework",
            "DRC_SKIP_BACKEND_DOTENV": "1",
        }
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        framework_root = Path(temp_dir)
        _write_fake_framework(framework_root, result_mode="generated_url")
        os.environ["FRAMEWORK_ROOT"] = str(framework_root)

        service = VoiceOutputDemoService(
            load_config(),
            artifact_store=VoiceOutputArtifactStore(framework_root / "drc-artifacts"),
        )
        response = service.submit_request(
            VoiceOutputDemoRequest(
                client_event_id="smoke-default-guard",
                text_content="Public-safe fake text.",
                voice_profile_id="fake-profile",
                audio_format="mp3",
                utterance_purpose="smoke",
            )
        )

    if response.accepted:
        print("[smoke-v200-real-tts-web-runtime-contract] ERROR: default guard accepted audio.")
        return False
    if response.request_state != "guarded_not_started":
        print(
            "[smoke-v200-real-tts-web-runtime-contract] ERROR: "
            f"unexpected default state {response.request_state}."
        )
        return False
    if response.framework_call_state != "not_called":
        print("[smoke-v200-real-tts-web-runtime-contract] ERROR: framework was called without opt-in.")
        return False

    print("v200_real_tts_runtime_default_guard: pass")
    return True


def _check_fake_framework_runtime_call() -> bool:
    response = _submit_fake_runtime_request(result_mode="generated_artifact_ref")

    if not response.accepted:
        print("[smoke-v200-real-tts-web-runtime-contract] ERROR: fake FW runtime was not accepted.")
        return False
    if response.request_state != "generated":
        print(
            "[smoke-v200-real-tts-web-runtime-contract] ERROR: "
            f"unexpected runtime state {response.request_state}."
        )
        return False
    if response.framework_call_state != "generated":
        print(
            "[smoke-v200-real-tts-web-runtime-contract] ERROR: "
            f"unexpected framework call state {response.framework_call_state}."
        )
        return False
    if not response.audio_ready or not response.has_audio_handoff or not response.is_generated:
        print("[smoke-v200-real-tts-web-runtime-contract] ERROR: FW v5 generated handoff flags were not set.")
        return False
    if response.audio_handoff_kind != "url":
        print(
            "[smoke-v200-real-tts-web-runtime-contract] ERROR: "
            f"unexpected DRC Web handoff kind {response.audio_handoff_kind}."
        )
        return False
    if not response.audio_url or not response.audio_url.startswith("/demo/voice-output/audio/"):
        print("[smoke-v200-real-tts-web-runtime-contract] ERROR: opaque DRC audio URL was not returned.")
        return False
    if response.audio_artifact_ref is not None:
        print("[smoke-v200-real-tts-web-runtime-contract] ERROR: local FW artifact ref was exposed.")
        return False
    if response.framework_api_name != "framework.create_voice_output_session().create_output":
        print(
            "[smoke-v200-real-tts-web-runtime-contract] ERROR: "
            f"unexpected FW v5 API name {response.framework_api_name}."
        )
        return False
    if response.evidence_status != "not_evidence":
        print("[smoke-v200-real-tts-web-runtime-contract] ERROR: smoke response must not count as evidence.")
        return False

    print("v200_real_tts_runtime_fake_fw_v5_call: pass")
    print("v200_real_tts_runtime_evidence_status: not_evidence")
    return True


def _check_fake_framework_unavailable_result() -> bool:
    response = _submit_fake_runtime_request(result_mode="unavailable")

    if response.accepted:
        print("[smoke-v200-real-tts-web-runtime-contract] ERROR: unavailable result was accepted.")
        return False
    if response.request_state != "unavailable":
        print(
            "[smoke-v200-real-tts-web-runtime-contract] ERROR: "
            f"unexpected unavailable state {response.request_state}."
        )
        return False
    if response.audio_ready or response.has_audio_handoff or response.is_generated:
        print("[smoke-v200-real-tts-web-runtime-contract] ERROR: unavailable result exposed playable flags.")
        return False

    print("v200_real_tts_runtime_unavailable_is_non_playable: pass")
    return True


def _check_fake_framework_conflicting_handoff_result() -> bool:
    response = _submit_fake_runtime_request(result_mode="conflicting_handoff")

    if response.accepted:
        print("[smoke-v200-real-tts-web-runtime-contract] ERROR: conflicting handoff result was accepted.")
        return False
    if response.request_state != "generated_handoff_invalid":
        print(
            "[smoke-v200-real-tts-web-runtime-contract] ERROR: "
            f"unexpected conflicting handoff state {response.request_state}."
        )
        return False
    if response.has_audio_handoff:
        print("[smoke-v200-real-tts-web-runtime-contract] ERROR: conflicting handoff was marked usable.")
        return False
    if response.audio_artifact_ref is not None:
        print("[smoke-v200-real-tts-web-runtime-contract] ERROR: conflicting local artifact ref leaked.")
        return False
    if response.audio_handoff_kind != "conflicting":
        print(
            "[smoke-v200-real-tts-web-runtime-contract] ERROR: "
            f"unexpected conflicting handoff kind {response.audio_handoff_kind}."
        )
        return False
    if not response.is_generated:
        print("[smoke-v200-real-tts-web-runtime-contract] ERROR: conflicting generated result lost generated flag.")
        return False

    print("v200_real_tts_runtime_conflicting_handoff_is_non_playable: pass")
    return True


def _check_fake_framework_unsafe_url_result() -> bool:
    response = _submit_fake_runtime_request(result_mode="unsafe_file_url")

    if response.accepted:
        print("[smoke-v200-real-tts-web-runtime-contract] ERROR: unsafe file URL was accepted.")
        return False
    if response.request_state != "generated_handoff_invalid":
        print(
            "[smoke-v200-real-tts-web-runtime-contract] ERROR: "
            f"unexpected unsafe URL state {response.request_state}."
        )
        return False
    if response.audio_url is not None or response.audio_artifact_ref is not None:
        print("[smoke-v200-real-tts-web-runtime-contract] ERROR: unsafe URL or local ref leaked.")
        return False
    if response.audio_ready or response.has_audio_handoff:
        print("[smoke-v200-real-tts-web-runtime-contract] ERROR: unsafe URL remained playable.")
        return False

    print("v200_real_tts_runtime_unsafe_url_is_non_playable: pass")
    return True


def _check_no_drc_direct_framework_tts_imports() -> bool:
    forbidden_terms = (
        "tts.voice_engine",
        "framework.tts.voice_engine",
        "from tts import voice_engine",
        "import tts.voice_engine",
    )
    scan_roots = (ROOT / "backend" / "app", ROOT / "scripts")
    offenders: list[str] = []

    for scan_root in scan_roots:
        for path in scan_root.rglob("*.py"):
            if path == Path(__file__).resolve():
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            if any(term in text for term in forbidden_terms):
                offenders.append(str(path.relative_to(ROOT)))

    if offenders:
        print("[smoke-v200-real-tts-web-runtime-contract] ERROR: direct FW/private TTS import found:")
        for offender in offenders:
            print(f"  - {offender}")
        return False

    print("v200_real_tts_runtime_no_direct_private_tts_imports: pass")
    return True


def _submit_fake_runtime_request(result_mode: str):
    _clear_env(_ENV_KEYS)
    os.environ.update(
        {
            "CONVERSATION_ENGINE": "framework",
            "VOICE_OUTPUT_DEMO_ENABLED": "1",
            "VOICE_OUTPUT_ADAPTER_MODE": "framework",
            "VOICE_OUTPUT_REAL_TTS_ENABLED": "1",
            "VOICE_OUTPUT_UTTERANCE_PURPOSE": "smoke",
            "DRC_SKIP_BACKEND_DOTENV": "1",
        }
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_root = Path(temp_dir)
        framework_root = temp_root / "fw"
        artifact_store = VoiceOutputArtifactStore(temp_root / "drc-artifacts")
        _write_fake_framework(framework_root, result_mode=result_mode)
        os.environ["FRAMEWORK_ROOT"] = str(framework_root)

        service = VoiceOutputDemoService(load_config(), artifact_store=artifact_store)
        return service.submit_request(
            VoiceOutputDemoRequest(
                client_event_id=f"smoke-fake-runtime-{result_mode}",
                text_content="Public-safe fake text.",
                voice_profile_id="fake-profile",
                audio_format="mp3",
                utterance_purpose="smoke",
            )
        )


def _write_fake_framework(root: Path, *, result_mode: str) -> None:
    framework_dir = root / "framework"
    runtime_dir = framework_dir / "runtime"
    runtime_dir.mkdir(parents=True)
    (runtime_dir / "voice_output.py").write_text("# fake boundary marker\n", encoding="utf-8")
    (framework_dir / "facade.py").write_text("# fake facade marker\n", encoding="utf-8")
    (framework_dir / "__init__.py").write_text(
        f"""
from pathlib import Path


class VoiceOutputRequest:
    def __init__(
        self,
        text,
        voice_profile_id=None,
        requested_audio_format=None,
        utterance_purpose=None,
        language_code=None,
    ):
        self.text = text
        self.voice_profile_id = voice_profile_id
        self.requested_audio_format = requested_audio_format
        self.utterance_purpose = utterance_purpose
        self.language_code = language_code


class VoiceOutputResult:
    def __init__(
        self,
        request_state,
        audio_ready=False,
        audio_url=None,
        audio_artifact_ref=None,
        audio_format=None,
    ):
        self.request_state = request_state
        self.audio_ready = audio_ready
        self.audio_url = audio_url
        self.audio_artifact_ref = audio_artifact_ref
        self.audio_format = audio_format


class VoiceOutputSession:
    def __init__(self, artifact_dir):
        self.artifact_dir = Path(artifact_dir)

    def create_output(self, request):
        if request.text != 'Public-safe fake text.':
            raise ValueError('unexpected text')
        if request.voice_profile_id != 'fake-profile':
            raise ValueError('unexpected voice profile')
        if request.requested_audio_format != 'mp3':
            raise ValueError('unexpected format')
        if request.language_code != 'ja':
            raise ValueError('unexpected language')
        mode = {result_mode!r}
        if mode == 'generated_url':
            return VoiceOutputResult(
                request_state='generated',
                audio_ready=True,
                audio_url='/demo/voice-output/audio/fake-smoke.mp3',
                audio_format=request.requested_audio_format,
            )
        if mode == 'generated_artifact_ref':
            self.artifact_dir.mkdir(parents=True, exist_ok=True)
            artifact_path = self.artifact_dir / 'fake-fw-output.mp3'
            artifact_path.write_bytes(b'fake-mp3-audio')
            return VoiceOutputResult(
                request_state='generated',
                audio_ready=True,
                audio_artifact_ref=str(artifact_path),
                audio_format=request.requested_audio_format,
            )
        if mode == 'unsafe_file_url':
            return VoiceOutputResult(
                request_state='generated',
                audio_ready=True,
                audio_url='file:///__test__/voice-output.mp3',
                audio_format=request.requested_audio_format,
            )
        if mode == 'unavailable':
            return VoiceOutputResult(
                request_state='unavailable',
                audio_ready=False,
                audio_format=request.requested_audio_format,
            )
        if mode == 'conflicting_handoff':
            return VoiceOutputResult(
                request_state='generated',
                audio_ready=True,
                audio_url='/demo/voice-output/audio/fake-smoke.mp3',
                audio_artifact_ref='private-artifact-ref-that-must-not-count',
                audio_format=request.requested_audio_format,
            )
        raise ValueError('unknown fake result mode')


def create_voice_output_session(
    *,
    project_root=None,
    default_voice_profile_id='default',
    real_tts_enabled=None,
    artifact_dir=None,
):
    if project_root is None:
        raise ValueError('project_root must be passed through DRC')
    if not (Path(project_root).resolve() / 'framework' / '__init__.py').is_file():
        raise ValueError('unexpected project_root')
    if default_voice_profile_id != 'fake-profile':
        raise ValueError('unexpected default voice profile')
    if real_tts_enabled is not True:
        raise ValueError('real_tts_enabled must be explicitly forwarded')
    if artifact_dir is None:
        raise ValueError('D-next-15 must provide a managed artifact directory')
    return VoiceOutputSession(artifact_dir)
""".lstrip(),
        encoding="utf-8",
    )


def _clear_env(keys: tuple[str, ...]) -> None:
    for key in keys:
        os.environ.pop(key, None)


class _preserved_env:
    def __init__(self, keys: tuple[str, ...]) -> None:
        self._keys = keys
        self._saved: dict[str, str | None] = {}

    def __enter__(self) -> None:
        self._saved = {key: os.environ.get(key) for key in self._keys}

    def __exit__(self, exc_type, exc, traceback) -> None:
        for key, value in self._saved.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


if __name__ == "__main__":
    raise SystemExit(main())
