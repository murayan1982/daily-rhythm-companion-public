"""Smoke check for DRC's FW v5 public voice output boundary assumptions.

This source-tree check uses only fake framework checkouts. It does not call a
real provider, start the backend, open a browser, play audio, inspect
screenshots, create audio artifacts, or accept v2.0.0 evidence. It verifies
that DRC keeps relying on the FW public voice output boundary shape and that
non-generated results cannot become evidence-success paths.
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


_EXPECTED_NON_EVIDENCE_MODES = {
    "unavailable": ("unavailable", "unavailable"),
    "skipped": ("skipped", "skipped"),
    "rejected": ("rejected", "rejected"),
    "failed": ("failed", "failed"),
    "generated_unready": ("audio_generated_unserved", "audio_generated_unserved"),
    "generated_no_handoff": ("generated_handoff_invalid", "generated_handoff_invalid"),
    "generated_conflicting_handoff": ("generated_handoff_invalid", "generated_handoff_invalid"),
    "legacy_url": ("legacy_audio_ready", "legacy_audio_ready"),
}


_PUBLIC_REQUIRED_CHECKS = {
    "voice_output_demo_enabled": "pass",
    "conversation_engine": "pass",
    "voice_output_adapter_mode": "pass",
    "framework_root": "pass",
    "framework_voice_output_boundary": "pass",
    "framework_voice_output_public_boundary": "pass",
}


def main() -> int:
    with _preserved_env(_ENV_KEYS):
        if not _check_public_boundary_probe_without_runtime_gate():
            return 1
        if not _check_framework_root_required():
            return 1
        if not _check_adapter_mode_required():
            return 1
        if not _check_public_boundary_runtime_uses_public_modules_only():
            return 1
        if not _check_non_generated_results_remain_non_evidence():
            return 1

    print("[smoke-v200-fw-voice-output-boundary-for-drc] OK")
    print(
        "No real provider call, backend startup/request, browser action, audio playback, "
        "screenshot inspection, raw audio read, or release artifact was made."
    )
    return 0


def _check_public_boundary_probe_without_runtime_gate() -> bool:
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

        status = VoiceOutputDemoService(load_config()).build_status()

    check_statuses = {check.name: check.status for check in status.checks}
    for check_name, expected_status in _PUBLIC_REQUIRED_CHECKS.items():
        if check_statuses.get(check_name) != expected_status:
            print(
                "[smoke-v200-fw-voice-output-boundary-for-drc] ERROR: "
                f"{check_name} expected {expected_status}, got {check_statuses.get(check_name)}."
            )
            return False

    if status.capability.status != "unavailable":
        print(
            "[smoke-v200-fw-voice-output-boundary-for-drc] ERROR: "
            f"public boundary without runtime gate should be unavailable, got {status.capability.status}."
        )
        return False
    if status.capability.source != "real_tts_runtime_disabled":
        print(
            "[smoke-v200-fw-voice-output-boundary-for-drc] ERROR: "
            f"unexpected capability source {status.capability.source}."
        )
        return False
    if "framework/runtime/voice_output.py" not in status.candidate_paths:
        print("[smoke-v200-fw-voice-output-boundary-for-drc] ERROR: FW boundary file not detected.")
        return False
    if not any("VoiceOutputRequest" in candidate for candidate in status.public_api_candidates):
        print("[smoke-v200-fw-voice-output-boundary-for-drc] ERROR: VoiceOutputRequest not detected.")
        return False
    if not any("VoiceOutputResult" in candidate for candidate in status.public_api_candidates):
        print("[smoke-v200-fw-voice-output-boundary-for-drc] ERROR: VoiceOutputResult not detected.")
        return False
    if not any("create_voice_output_session" in candidate for candidate in status.public_api_candidates):
        print("[smoke-v200-fw-voice-output-boundary-for-drc] ERROR: session factory not detected.")
        return False

    print("v200_fw_voice_output_boundary_probe_without_runtime_gate: pass")
    return True


def _check_framework_root_required() -> bool:
    _clear_env(_ENV_KEYS)
    os.environ.update(
        {
            "CONVERSATION_ENGINE": "framework",
            "VOICE_OUTPUT_DEMO_ENABLED": "1",
            "VOICE_OUTPUT_ADAPTER_MODE": "framework",
            "VOICE_OUTPUT_REAL_TTS_ENABLED": "1",
            "DRC_SKIP_BACKEND_DOTENV": "1",
        }
    )

    status = VoiceOutputDemoService(load_config()).build_status()
    check_statuses = {check.name: check.status for check in status.checks}

    if status.capability.source != "framework_config_missing":
        print(
            "[smoke-v200-fw-voice-output-boundary-for-drc] ERROR: "
            f"missing FRAMEWORK_ROOT source was {status.capability.source}."
        )
        return False
    if check_statuses.get("framework_root") != "fail":
        print("[smoke-v200-fw-voice-output-boundary-for-drc] ERROR: missing FRAMEWORK_ROOT did not fail.")
        return False
    if status.public_api_candidates:
        print("[smoke-v200-fw-voice-output-boundary-for-drc] ERROR: public API candidates found without root.")
        return False

    print("v200_fw_voice_output_boundary_framework_root_required: pass")
    return True


def _check_adapter_mode_required() -> bool:
    _clear_env(_ENV_KEYS)
    os.environ.update(
        {
            "CONVERSATION_ENGINE": "framework",
            "VOICE_OUTPUT_DEMO_ENABLED": "1",
            "VOICE_OUTPUT_ADAPTER_MODE": "disabled",
            "VOICE_OUTPUT_REAL_TTS_ENABLED": "1",
            "DRC_SKIP_BACKEND_DOTENV": "1",
        }
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        framework_root = Path(temp_dir)
        _write_fake_framework(framework_root, result_mode="generated_url")
        os.environ["FRAMEWORK_ROOT"] = str(framework_root)

        status = VoiceOutputDemoService(load_config()).build_status()

    check_statuses = {check.name: check.status for check in status.checks}
    if status.capability.source != "voice_output_adapter_unsupported":
        print(
            "[smoke-v200-fw-voice-output-boundary-for-drc] ERROR: "
            f"unsupported adapter source was {status.capability.source}."
        )
        return False
    if check_statuses.get("voice_output_adapter_mode") != "fail":
        print("[smoke-v200-fw-voice-output-boundary-for-drc] ERROR: unsupported adapter mode did not fail.")
        return False
    if status.candidate_paths or status.public_api_candidates:
        print("[smoke-v200-fw-voice-output-boundary-for-drc] ERROR: adapter-mode failure still scanned FW APIs.")
        return False

    print("v200_fw_voice_output_boundary_adapter_mode_required: pass")
    return True


def _check_public_boundary_runtime_uses_public_modules_only() -> bool:
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        framework_root = temp_path / "fw"
        marker = temp_path / "private_tts_module_imported.marker"
        _write_fake_framework(framework_root, result_mode="generated_artifact_ref", private_import_marker=marker)
        response = _submit_fake_runtime_request(framework_root, result_mode="generated_artifact_ref")

        private_module_suffix = ".".join(("tts", "voice_engine"))
        loaded_private_modules = [name for name in sys.modules if name.endswith(private_module_suffix)]

        if marker.exists():
            print("[smoke-v200-fw-voice-output-boundary-for-drc] ERROR: fake private TTS marker was written.")
            return False
        if loaded_private_modules:
            print("[smoke-v200-fw-voice-output-boundary-for-drc] ERROR: fake private TTS module was imported.")
            return False

    if not response.accepted:
        print("[smoke-v200-fw-voice-output-boundary-for-drc] ERROR: public boundary generated response was not accepted.")
        return False
    if response.framework_api_name != "framework.create_voice_output_session().create_output":
        print(
            "[smoke-v200-fw-voice-output-boundary-for-drc] ERROR: "
            f"unexpected public API name {response.framework_api_name}."
        )
        return False
    if response.audio_handoff_kind != "url":
        print(
            "[smoke-v200-fw-voice-output-boundary-for-drc] ERROR: "
            f"unexpected DRC Web handoff kind {response.audio_handoff_kind}."
        )
        return False
    if not response.audio_url or not response.audio_url.startswith("/demo/voice-output/audio/"):
        print("[smoke-v200-fw-voice-output-boundary-for-drc] ERROR: opaque DRC audio URL was not returned.")
        return False
    if response.audio_artifact_ref is not None:
        print("[smoke-v200-fw-voice-output-boundary-for-drc] ERROR: local FW artifact ref was exposed.")
        return False
    if response.evidence_status != "not_evidence":
        print("[smoke-v200-fw-voice-output-boundary-for-drc] ERROR: fake runtime counted as evidence.")
        return False

    print("v200_fw_voice_output_boundary_public_modules_only: pass")
    print("v200_fw_voice_output_boundary_fake_generated_evidence_status: not_evidence")
    return True


def _check_non_generated_results_remain_non_evidence() -> bool:
    for result_mode, (expected_request_state, expected_framework_state) in _EXPECTED_NON_EVIDENCE_MODES.items():
        with tempfile.TemporaryDirectory() as temp_dir:
            framework_root = Path(temp_dir)
            _write_fake_framework(framework_root, result_mode=result_mode)
            response = _submit_fake_runtime_request(framework_root, result_mode=result_mode)

        if response.accepted:
            print(
                "[smoke-v200-fw-voice-output-boundary-for-drc] ERROR: "
                f"{result_mode} was accepted."
            )
            return False
        if response.request_state != expected_request_state:
            print(
                "[smoke-v200-fw-voice-output-boundary-for-drc] ERROR: "
                f"{result_mode} request_state expected {expected_request_state}, got {response.request_state}."
            )
            return False
        if response.framework_call_state != expected_framework_state:
            print(
                "[smoke-v200-fw-voice-output-boundary-for-drc] ERROR: "
                f"{result_mode} framework state expected {expected_framework_state}, got {response.framework_call_state}."
            )
            return False
        if response.evidence_status != "not_evidence":
            print(
                "[smoke-v200-fw-voice-output-boundary-for-drc] ERROR: "
                f"{result_mode} evidence status was {response.evidence_status}."
            )
            return False
        if response.audio_playback_status != "not_started":
            print(
                "[smoke-v200-fw-voice-output-boundary-for-drc] ERROR: "
                f"{result_mode} playback status was {response.audio_playback_status}."
            )
            return False

    print("v200_fw_voice_output_boundary_non_generated_results_not_evidence: pass")
    return True


def _submit_fake_runtime_request(framework_root: Path, *, result_mode: str):
    _clear_env(_ENV_KEYS)
    os.environ.update(
        {
            "CONVERSATION_ENGINE": "framework",
            "VOICE_OUTPUT_DEMO_ENABLED": "1",
            "VOICE_OUTPUT_ADAPTER_MODE": "framework",
            "VOICE_OUTPUT_REAL_TTS_ENABLED": "1",
            "VOICE_OUTPUT_UTTERANCE_PURPOSE": "smoke",
            "FRAMEWORK_ROOT": str(framework_root),
            "DRC_SKIP_BACKEND_DOTENV": "1",
        }
    )

    artifact_store = VoiceOutputArtifactStore(framework_root.parent / "drc-artifacts")
    return VoiceOutputDemoService(
        load_config(),
        artifact_store=artifact_store,
    ).submit_request(
        VoiceOutputDemoRequest(
            client_event_id=f"smoke-fw-boundary-{result_mode}",
            text_content="Public-safe fake text.",
            voice_profile_id="fake-profile",
            audio_format="mp3",
            utterance_purpose="smoke",
        )
    )


def _write_fake_framework(
    root: Path,
    *,
    result_mode: str,
    private_import_marker: Path | None = None,
) -> None:
    framework_dir = root / "framework"
    runtime_dir = framework_dir / "runtime"
    private_tts_dir = framework_dir / "tts"
    runtime_dir.mkdir(parents=True)
    private_tts_dir.mkdir(parents=True)
    (runtime_dir / "voice_output.py").write_text("# fake public boundary marker\n", encoding="utf-8")
    (framework_dir / "facade.py").write_text("# fake facade marker\n", encoding="utf-8")
    (private_tts_dir / "__init__.py").write_text("# fake private package\n", encoding="utf-8")

    marker_text = ""
    if private_import_marker is not None:
        marker_text = (
            "from pathlib import Path\n"
            f"Path({str(private_import_marker)!r}).write_text('imported', encoding='utf-8')\n"
            "raise RuntimeError('fake private framework TTS module must not be imported')\n"
        )
    (private_tts_dir / "voice_engine.py").write_text(marker_text, encoding="utf-8")

    (framework_dir / "__init__.py").write_text(
        f'''
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
        if request.utterance_purpose != 'smoke':
            raise ValueError('unexpected purpose')
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
        if mode in {{'unavailable', 'skipped', 'rejected', 'failed'}}:
            return VoiceOutputResult(
                request_state=mode,
                audio_ready=False,
                audio_format=request.requested_audio_format,
            )
        if mode == 'generated_unready':
            return VoiceOutputResult(
                request_state='generated',
                audio_ready=False,
                audio_url='/demo/voice-output/audio/fake-smoke.mp3',
                audio_format=request.requested_audio_format,
            )
        if mode == 'generated_no_handoff':
            return VoiceOutputResult(
                request_state='generated',
                audio_ready=True,
                audio_format=request.requested_audio_format,
            )
        if mode == 'generated_conflicting_handoff':
            return VoiceOutputResult(
                request_state='generated',
                audio_ready=True,
                audio_url='/demo/voice-output/audio/fake-smoke.mp3',
                audio_artifact_ref='fake-private-artifact-ref-that-must-not-count',
                audio_format=request.requested_audio_format,
            )
        if mode == 'legacy_url':
            return VoiceOutputResult(
                request_state=None,
                audio_ready=True,
                audio_url='/demo/voice-output/audio/fake-legacy.mp3',
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
'''.lstrip(),
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
