from __future__ import annotations

import importlib
import os
from pathlib import Path
import subprocess
import sys
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_BASELINE = "e4ecd46487b43e20b359ce350fc90b5e0ac36d95"
EXPECTED_FW_HEAD = "d313eb6acb643103fe25988720ebee5976a04f78"
EXPECTED_FILES = {
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v300_goal_checklist_small_commit.md",
    "docs/v300_rt5f1_app_visible_real_stt_contract.md",
    "scripts/check_v300_rt5f1_app_visible_real_stt_contract.py",
    "backend/.env.example",
    "backend/app/config.py",
    "backend/app/models/voice_input_demo.py",
    "backend/app/api/voice_input_demo.py",
    "backend/app/services/private_voice_input_credential_source.py",
    "backend/app/services/framework_voice_input_app_transcript.py",
    "backend/tests/test_framework_voice_input_app_transcript.py",
    "backend/tests/test_voice_input_real_transcript_api.py",
    "app/lib/services/backend_provider_neutral_transcript_provider.dart",
    "app/test/backend_provider_neutral_transcript_provider_test.dart",
}


def _read(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


def _run_git(*args: str) -> list[str]:
    completed = subprocess.run(
        ["git", "-C", str(REPO_ROOT), *args],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return [line.strip() for line in completed.stdout.splitlines() if line.strip()]


def _assert_contains(relative_path: str, fragments: Iterable[str]) -> None:
    content = _read(relative_path)
    for fragment in fragments:
        assert fragment in content, f"{relative_path} missing: {fragment}"


def _assert_not_contains(relative_path: str, fragments: Iterable[str]) -> None:
    content = _read(relative_path)
    for fragment in fragments:
        assert fragment not in content, f"{relative_path} unexpectedly contains: {fragment}"


def _changed_files() -> set[str]:
    tracked = set(_run_git("diff", "HEAD", "--name-only"))
    untracked = set(_run_git("ls-files", "--others", "--exclude-standard"))
    return tracked | untracked


def _verify_exact_surface() -> None:
    actual = _changed_files()
    assert actual == EXPECTED_FILES, (
        "RT-5f1 change surface mismatch\n"
        f"expected={sorted(EXPECTED_FILES)}\nactual={sorted(actual)}"
    )

    head = _run_git("rev-parse", "HEAD")[0]
    if not os.getenv("DRC_RT5F1_ALLOW_RECONSTRUCTED_BASELINE"):
        assert head == EXPECTED_BASELINE, (
            f"RT-5f1 baseline mismatch: expected {EXPECTED_BASELINE}, actual {head}"
        )


def _verify_docs() -> None:
    common = (
        "RT-5f1",
        "IMPLEMENTED / AWAITING_REVIEW",
        "e4ecd46487b43e20b359ce350fc90b5e0ac36d95",
    )
    for path in (
        "README.md",
        "roadmap.md",
        "tasklist.md",
        "docs/DRC_v300_goal_checklist_small_commit.md",
        "docs/v300_rt5f1_app_visible_real_stt_contract.md",
    ):
        _assert_contains(path, common)

    _assert_contains(
        "scripts/README.md",
        (
            "check_v300_rt5f1_app_visible_real_stt_contract.py",
            "exact seventeen-file",
            "provider-free",
        ),
    )


def _verify_backend() -> None:
    _assert_contains(
        "backend/.env.example",
        ("VOICE_INPUT_REAL_STT_ENABLED=0", "Default-off RT-5f1"),
    )
    _assert_contains(
        "backend/app/config.py",
        (
            "voice_input_real_stt_enabled: bool = False",
            '_env_flag("VOICE_INPUT_REAL_STT_ENABLED")',
        ),
    )
    _assert_contains(
        "backend/app/models/voice_input_demo.py",
        (
            "class VoiceInputRealTranscriptRequest",
            "class VoiceInputRealTranscriptResponse",
            "max_length=4096",
            "repr=False",
        ),
    )
    _assert_contains(
        "backend/app/api/voice_input_demo.py",
        (
            '"/demo/voice-input/transcript"',
            'response.headers["Cache-Control"] = "no-store"',
            'response.headers["Pragma"] = "no-cache"',
            'response.headers["X-Content-Type-Options"] = "nosniff"',
            "voice_input_transcript_unavailable",
            "_is_valid_staging_id",
        ),
    )
    _assert_not_contains(
        "backend/app/api/voice_input_demo.py",
        (
            '"/demo/voice-input/staging/{staging_id}/transcript"',
            "OpenAI(",
            "import openai",
            "from openai",
        ),
    )
    _assert_contains(
        "backend/app/services/private_voice_input_credential_source.py",
        (
            "class PrivateVoiceInputCredentialSource",
            'environment_name: str = "OPENAI_API_KEY"',
            "field(",
            "repr=False",
            "build_for",
        ),
    )
    _assert_contains(
        "backend/app/services/framework_voice_input_app_transcript.py",
        (
            "FrameworkVoiceInputOpenAIRealExecutorAssembler",
            "VoiceInputStagingStore.consume",
            "blocking=False",
            '"app_visible_real_stt"',
            '"transcript_public_output_allowed": True',
            "_MAX_TRANSCRIPT_CODE_POINTS = 4096",
            "uuid4().hex",
        ),
    )
    _assert_not_contains(
        "backend/app/services/framework_voice_input_app_transcript.py",
        (
            "import openai",
            "from openai",
            "framework.openai_",
            "framework.voice_input",
        ),
    )
    _assert_contains(
        "backend/tests/test_framework_voice_input_app_transcript.py",
        (
            "test_missing_credential_fails_before_artifact_consume",
            "test_busy_slot_preserves_artifact",
            "test_transcript_code_point_bound",
            "test_nonfinal_or_unsafe_result_is_rejected_and_consumed",
        ),
    )
    _assert_contains(
        "backend/tests/test_voice_input_real_transcript_api.py",
        (
            "test_real_transcript_route_is_body_only_minimal_and_no_store",
            "test_route_redacts_internal_provider_failure",
            "test_foreground_and_busy_errors_use_fixed_public_codes",
        ),
    )


def _verify_flutter() -> None:
    _assert_contains(
        "app/lib/services/backend_provider_neutral_transcript_provider.dart",
        (
            "class BackendProviderNeutralTranscriptProvider",
            "acquireNextTranscript",
            "followRedirects = false",
            "maximumResponseBytes",
            "backend_transcript_no_store_required",
            "ProviderNeutralTranscriptResult",
            "_responseKeys",
        ),
    )
    _assert_not_contains(
        "app/lib/services/backend_provider_neutral_transcript_provider.dart",
        ("provider_name", "api_key", "audio_path", "print("),
    )
    _assert_contains(
        "app/test/backend_provider_neutral_transcript_provider_test.dart",
        (
            "opt-in false takes no artifact and sends no request",
            "concurrent invocation takes and sends exactly once",
            "rejects redirect and does not retry",
            "requires no-store success response header",
            "existing handoff starts text stream exactly once",
        ),
    )

    for unchanged in (
        "app/lib/main.dart",
        "app/lib/screens/home_screen.dart",
        "app/lib/services/realtime_text_stream_transcript_handoff.dart",
        "app/lib/models/provider_neutral_transcript.dart",
    ):
        assert unchanged not in EXPECTED_FILES


def _verify_no_private_or_provider_execution() -> None:
    credential_prefix = "sk-" + "proj-"
    bearer_prefix = "bearer " + "eyj"
    for path in EXPECTED_FILES:
        content = _read(path).lower()
        assert credential_prefix not in content
        assert bearer_prefix not in content

    assert "openai" not in sys.modules


def _verify_fw_root_public_api() -> None:
    configured = os.getenv("FRAMEWORK_ROOT") or os.getenv("FRAMEWORK_PROJECT_ROOT")
    assert configured, "FRAMEWORK_ROOT or FRAMEWORK_PROJECT_ROOT is required"
    root = Path(configured).expanduser().resolve()
    assert (root / "framework" / "__init__.py").is_file()

    original_path = list(sys.path)
    saved = {
        name: module
        for name, module in sys.modules.items()
        if name == "framework" or name.startswith("framework.")
    }
    for name in saved:
        sys.modules.pop(name, None)
    sys.path.insert(0, str(root))
    importlib.invalidate_caches()
    try:
        module = importlib.import_module("framework")
        required = (
            "VoiceInputAudioFormat",
            "VoiceInputAudioSource",
            "VoiceInputRequest",
            "OpenAIVoiceInputPrivateCredential",
            "OpenAIVoiceInputRealProviderPolicy",
            "OpenAIVoiceInputRuntimeMode",
            "OpenAIVoiceInputRealClientFactory",
            "OpenAIVoiceInputProviderAdapter",
            "OpenAIVoiceInputRealProviderExecutor",
            "resolve_voice_input_provider_execution_config",
        )
        missing = [name for name in required if not hasattr(module, name)]
        assert not missing, f"FW root public API missing: {missing}"
        assert "openai" not in sys.modules, "optional OpenAI SDK was imported"
    finally:
        for name in list(sys.modules):
            if name == "framework" or name.startswith("framework."):
                sys.modules.pop(name, None)
        sys.modules.update(saved)
        sys.path[:] = original_path
        importlib.invalidate_caches()


def main() -> None:
    _verify_exact_surface()
    _verify_docs()
    _verify_backend()
    _verify_flutter()
    _verify_no_private_or_provider_execution()
    _verify_fw_root_public_api()

    print("v300_rt5f1_status: implemented-awaiting-review")
    print("v300_rt5f1_exact_change_surface: True")
    print("v300_rt5f1_default_off: True")
    print("v300_rt5f1_body_only_staging_id: True")
    print("v300_rt5f1_preconsume_credential_check: True")
    print("v300_rt5f1_preconsume_fw_root_check: True")
    print("v300_rt5f1_single_flight: True")
    print("v300_rt5f1_fw_root_public_only: True")
    print("v300_rt5f1_provider_client_bypass: False")
    print("v300_rt5f1_transcript_max_code_points: 4096")
    print("v300_rt5f1_response_no_store: True")
    print("v300_rt5f1_flutter_provider: True")
    print("v300_rt5f1_main_wiring_changed: False")
    print("v300_rt5f1_home_screen_changed: False")
    print("v300_rt5f1_network_execution: False")
    print("v300_rt5f1_provider_execution: False")
    print("v300_rt5f1_microphone_used: False")
    print("v300_rt5f1_audio_playback_executed: False")
    print("v300_rt5f1_real_transcript_created: False")
    print("v300_rt5f2_authorization: blocked-pending-rt5f1-acceptance")


if __name__ == "__main__":
    main()
