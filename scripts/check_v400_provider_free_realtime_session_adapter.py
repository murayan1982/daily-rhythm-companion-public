#!/usr/bin/env python3
"""DRC-V4-2 provider-free FW v6 RealtimeSession adapter acceptance gate."""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_BASELINE = "e6ec8fcfbb819a35f5f74be9386ff2c63a5c64f3"
FRAMEWORK_RELEASE = "v6.0.0"
FRAMEWORK_TAG_TARGET = "61e15f62d1ecc5faee016abae82200f8de56c5dd"
FRAMEWORK_ZIP = "ai-character-framework_v6.0.0.zip"
FRAMEWORK_ZIP_SHA256 = "6b303dba53830dc9bd65ec881bac6f498dbf80f0d0adf1385cea728a86e066f2"
FRAMEWORK_DISTRIBUTION = "ai-character-framework"
FRAMEWORK_VERSION = "6.0.0"
FRAMEWORK_ROOT_PUBLIC_INVENTORY = "127 names / frozen"
EXPECTED_FILES = (
    "README.md",
    "backend/app/models/framework_v600_realtime.py",
    "backend/app/services/framework_v600_realtime_session_adapter.py",
    "backend/tests/test_framework_v600_realtime_session_adapter.py",
    "docs/DRC_v400_goal_checklist_small_commit.md",
    "docs/v400_provider_free_realtime_session_adapter.md",
    "roadmap.md",
    "scripts/README.md",
    "scripts/check_v400_provider_free_realtime_session_adapter.py",
    "tasklist.md",
)
PROTECTED_FILES = (
    "backend/app/models/realtime.py",
    "backend/app/services/framework_realtime_normalizer.py",
    "backend/app/services/framework_realtime_text_stream_adapter.py",
    "backend/app/services/framework_mock_motion_session_adapter.py",
    "backend/app/config.py",
    "backend/app/version.py",
    "app/pubspec.yaml",
    "app/pubspec.lock",
    "backend/requirements.txt",
    "backend/requirements-dev.txt",
    "backend/requirements-framework.txt",
    ".gitignore",
    "docs/DRC_v300_goal_checklist_small_commit.md",
    "docs/v300_release_record.md",
    "release_notes/v3.0.0.md",
)
CANONICAL_EVENTS = (
    "1. realtime.turn.started",
    "2. realtime.listening.started",
    "3. realtime.listening.completed",
    "4. realtime.transcript.final",
    "5. realtime.response.started",
    "6. realtime.response.completed",
    "7. realtime.synthesis.started",
    "8. realtime.synthesis.completed",
    "9. realtime.turn.completed",
)
DOC_MARKERS = (
    "DRC-V4-2: IMPLEMENTED / AWAITING_REVIEW",
    "DRC-V4-1: CLOSED / ACCEPTED",
    "current released version: v3.0.0 RELEASED / ACCEPTED",
    "DRC v4 release status: development work / not released",
    f"Framework release: {FRAMEWORK_RELEASE}",
    f"Framework annotated tag target: {FRAMEWORK_TAG_TARGET}",
    f"Framework official ZIP: {FRAMEWORK_ZIP}",
    f"Framework official ZIP SHA-256: {FRAMEWORK_ZIP_SHA256}",
    f"Framework distribution name: {FRAMEWORK_DISTRIBUTION}",
    f"Framework required distribution version: {FRAMEWORK_VERSION}",
    f"Framework root-public inventory: {FRAMEWORK_ROOT_PUBLIC_INVENTORY}",
    "provider-free FW v6 RealtimeSession adapter first",
    "initial FW imports from root framework only",
    "explicit FW submodule adoption requires a separate exact review",
    "existing accepted v3 real adapters remain retained",
    "removal of v3 real adapters is NOT_AUTHORIZED",
    "real unified RealtimeSession remains NOT_CLAIMED / NOT_AVAILABLE",
    "real unified runtime available: False",
    "unified real STT -> streaming LLM -> TTS -> motion: NOT_CLAIMED",
    "typed cooperative interrupt observation: supported",
    "provider hard cancel: NOT_CLAIMED",
    "real TTS cancellation: NOT_CLAIMED",
    "real playback stop: NOT_EXECUTED",
    "real barge-in acceptance: NOT_CLAIMED",
    "stale_completion_count == 0",
    "duplicate_terminal_count == 0",
    "overflow_count == 0",
    "commit / push: NOT_AUTHORIZED",
)
STALE_CURRENT_STATUS_MARKERS = (
    "DRC-V4-2 remains **NOT_STARTED / NOT_AUTHORIZED**",
    "DRC-V4-2 is still **NOT_STARTED / NOT_AUTHORIZED**",
)
PROHIBITED_ADAPTER_MARKERS = (
    "framework.realtime",
    "framework.realtime_session",
    "framework.identity",
    "framework.session_diagnostics",
    "sys.path",
    "sys.modules",
    "invalidate_caches",
    "os.chdir",
    "FRAMEWORK_ROOT",
    "framework_project_root",
    "inspect.signature",
    "dir(",
    "real_runtime_enabled=True",
    "voice_input_stage",
    "text_generation_stage",
    "voice_output_stage",
    "motion_stage",
)
SENSITIVE_PATTERNS = (
    re.compile(r"(?i)sk-[a-z0-9_-]{12,}"),
    re.compile(r"(?i)xai-[a-z0-9_-]{12,}"),
    re.compile(r"(?i)bearer\s+[a-z0-9._~+/-]{12,}"),
    re.compile(r"(?i)(?:api[_-]?key|access[_-]?token|refresh[_-]?token|client[_-]?secret)\s*[:=]"),
    re.compile(r"(?i)\b[a-z]:\\(?:users|home)\\"),
    re.compile(r"/(?:home|users)/[^/\s]+/"),
    re.compile(r"\b(?:10|169\.254|172\.(?:1[6-9]|2\d|3[01])|192\.168)\.\d{1,3}\.\d{1,3}\b"),
)


class GateError(RuntimeError):
    pass


def git(*args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(ROOT), *args],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if completed.returncode:
        raise GateError(completed.stderr.strip() or completed.stdout.strip())
    return completed.stdout


def status_paths() -> tuple[str, ...]:
    lines = git("status", "--short", "--untracked-files=normal").splitlines()
    paths: list[str] = []
    for line in lines:
        path = line[3:].strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        paths.append(path.replace("\\", "/"))
    return tuple(sorted(paths))


def read(relative: str) -> str:
    path = ROOT / relative
    if not path.is_file():
        raise GateError(f"missing required file: {relative}")
    return path.read_text(encoding="utf-8")


def check_surface() -> None:
    if git("rev-parse", "HEAD").strip() != EXPECTED_BASELINE:
        raise GateError("unexpected baseline HEAD")
    actual = status_paths()
    expected = tuple(sorted(EXPECTED_FILES))
    if actual != expected:
        raise GateError(f"exact 10-file surface mismatch: expected={expected}, actual={actual}")
    changed = set(git("diff", "--name-only").splitlines())
    changed.update(git("ls-files", "--others", "--exclude-standard").splitlines())
    protected = sorted(set(PROTECTED_FILES).intersection(path.replace("\\", "/") for path in changed))
    if protected:
        raise GateError(f"protected files changed: {protected}")


def check_docs() -> None:
    contract = read("docs/v400_provider_free_realtime_session_adapter.md")
    current_docs = (
        "README.md",
        "roadmap.md",
        "tasklist.md",
        "scripts/README.md",
        "docs/DRC_v400_goal_checklist_small_commit.md",
    )
    current_text = "\n".join(read(path) for path in current_docs)
    for marker in STALE_CURRENT_STATUS_MARKERS:
        if marker in current_text:
            raise GateError(f"stale DRC-V4-2 current-status marker present: {marker}")
    for marker in ("DRC-V4-2: IMPLEMENTED / AWAITING_REVIEW", "commit / push: NOT_AUTHORIZED"):
        if marker not in current_text and marker not in contract:
            raise GateError(f"missing current DRC-V4-2 status marker: {marker}")
    for marker in DOC_MARKERS:
        if marker not in contract and marker not in current_text:
            raise GateError(f"missing documentation marker: {marker}")
    for marker in CANONICAL_EVENTS:
        if marker not in contract:
            raise GateError(f"missing canonical event marker: {marker}")
    if "FW v6.0.0 does NOT provide a production real unified\nRealtimeSession.run_turn() pipeline coordinating\nreal STT -> streaming LLM -> TTS -> motion." not in contract:
        raise GateError("missing critical RealtimeSession.run_turn non-claim")


def check_adapter_source() -> None:
    source = read("backend/app/services/framework_v600_realtime_session_adapter.py")
    if 'importlib.import_module("framework")' not in source and 'import_module("framework")' not in source:
        raise GateError("adapter does not lazy-import root framework")
    for marker in PROHIBITED_ADAPTER_MARKERS:
        if marker in source:
            raise GateError(f"forbidden adapter marker: {marker}")
    for marker in (
        "real_runtime_requested",
        "real_runtime_enabled",
        "runtime_executable",
        "mock_ready",
        "run_turn_async",
        "InterruptRequest",
        "diagnostics_snapshot",
        "last_terminal_result",
        "current_turn",
        "host_app_request",
        "as_v6_dict",
        "as_dict",
        "Mapping",
        'getattr(value, "value"',
    ):
        if marker not in source:
            raise GateError(f"adapter missing required contract marker: {marker}")


def check_tests() -> None:
    tests = read("backend/tests/test_framework_v600_realtime_session_adapter.py")
    for marker in CANONICAL_EVENTS:
        event = marker.split(" ", 1)[1]
        if event not in tests:
            raise GateError(f"test missing canonical event: {event}")
    for marker in (
        "MappingProxyType",
        "RealtimeSessionConstructionStatus",
        "CapabilitySnapshotScope",
        "RealtimeState",
        "RealtimePhase",
        "InterruptOutcome",
        "last_terminal_result",
        "current_turn",
        "host_app_request",
        "operator_requested",
        "test_adapter_module_import_alone_does_not_import_framework",
        "test_missing_distribution_returns_typed_unavailable_without_session",
        "test_wrong_distribution_version_returns_typed_unavailable_without_session",
        "test_correct_version_allows_lazy_root_import_and_only_root_framework_module",
        "test_open_does_not_mutate_sys_path_cwd_or_use_project_root_behavior",
        "test_close_is_idempotent_and_use_after_close_fails_safely",
    ):
        if marker not in tests:
            raise GateError(f"test missing requirement: {marker}")


def changed_content() -> str:
    tracked = git("diff", "--unified=0", "--", *[p for p in EXPECTED_FILES if (ROOT / p).is_file()])
    added_lines = [
        line[1:]
        for line in tracked.splitlines()
        if line.startswith("+") and not line.startswith("+++")
    ]
    for relative in EXPECTED_FILES:
        if relative in git("ls-files", "--others", "--exclude-standard").splitlines():
            added_lines.append(read(relative))
    return "\n".join(added_lines)


def check_privacy() -> None:
    text = changed_content()
    for pattern in SENSITIVE_PATTERNS:
        if pattern.search(text):
            raise GateError(f"private-looking value introduced: {pattern.pattern}")
    for marker in ("raw audio", "transcripts", "provider payloads", "operator evidence", "screenshots", "private configuration"):
        if marker not in text:
            raise GateError(f"privacy boundary marker missing: {marker}")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run_fixed_sdk_smoke() -> str:
    supplied = os.environ.get("DRC_FW_V600_OFFICIAL_ZIP")
    if not supplied:
        return "NOT_RUN / OFFICIAL_ZIP_NOT_SUPPLIED"
    zip_path = Path(supplied)
    if not zip_path.is_file():
        raise GateError("fixed SDK ZIP supplied but missing")
    if sha256(zip_path) != FRAMEWORK_ZIP_SHA256:
        raise GateError("fixed SDK source hash mismatch")
    with tempfile.TemporaryDirectory(prefix="drc_v4_2_fw600_") as temp:
        temp_path = Path(temp)
        with zipfile.ZipFile(zip_path) as archive:
            archive.extractall(temp_path)
        pythonpath = [str(temp_path), *(str(path) for path in temp_path.iterdir() if path.is_dir())]
        code = (
            "import asyncio, importlib, json\n"
            "from importlib import metadata\n"
            "from collections.abc import Mapping\n"
            "def public(v):\n"
            "    if hasattr(v, 'as_v6_dict'):\n"
            "        v = v.as_v6_dict()\n"
            "    elif hasattr(v, 'as_dict'):\n"
            "        v = v.as_dict()\n"
            "    if isinstance(v, Mapping):\n"
            "        return {str(k): public(x) for k, x in v.items()}\n"
            "    enum_value = getattr(v, 'value', None)\n"
            "    if isinstance(enum_value, str):\n"
            "        return enum_value\n"
            "    if isinstance(v, (str, int, bool)) or v is None:\n"
            "        return v\n"
            "    return {name: public(getattr(v, name)) for name in (\n"
            "        'snapshot_scope','snapshot_generation','session_id','supports_text_chat',\n"
            "        'supports_voice_input','supports_voice_output','supports_motion','real_runtime_enabled',\n"
            "        'hard_cancel_supported','tts_queue_flush_supported','text_generation','voice_input',\n"
            "        'voice_output','motion',\n"
            "        'runtime','fake_runtime','real_runtime','guarded','runtime_available',\n"
            "        'unavailable_reason','cooperative_cancel_supported','provider_hard_cancel_supported',\n"
            "        'pending_flush_supported','host_playback_owned_by_drc','host_playback_stop_supported',\n"
            "        'streaming_supported','streaming_audio_supported','generation_cancel_supported',\n"
            "        'active_audio_invalidation_supported','playback_ownership',\n"
            "        'host_playback_stop_request_supported','host_playback_stop_ack_supported',\n"
            "        'request_cancel_supported','completion_event_supported','provider_neutral_intent_supported',\n"
            "        'stop_motion_supported',\n"
            "    ) if hasattr(v, name)}\n"
            "def sid(v):\n"
            "    return str(v) if v is not None else None\n"
            "def enum(v):\n"
            "    x = getattr(v, 'value', None)\n"
            "    return x if isinstance(x, str) else v\n"
            "def project_construction(v):\n"
            "    m = public(v)\n"
            "    metadata_payload = m.get('public_metadata')\n"
            "    if not isinstance(metadata_payload, dict):\n"
            "        metadata_payload = public(getattr(v, 'public_metadata', None))\n"
            "    return {\n"
            "        'status': enum(getattr(v, 'status', m.get('status'))),\n"
            "        'session_id': sid(getattr(v, 'session_id', m.get('session_id'))),\n"
            "        'runtime_executable': getattr(v, 'runtime_executable', m.get('runtime_executable')),\n"
            "        'real_runtime_requested': getattr(v, 'real_runtime_requested', m.get('real_runtime_requested')),\n"
            "        'real_runtime_enabled': getattr(v, 'real_runtime_enabled', m.get('real_runtime_enabled')),\n"
            "        'provider_execution_performed': metadata_payload.get('provider_execution_performed') if isinstance(metadata_payload, dict) else None,\n"
            "    }\n"
            "def project_result(v):\n"
            "    m = public(v)\n"
            "    return {\n"
            "        'session_id': sid(getattr(v, 'session_id', m.get('session_id'))),\n"
            "        'turn_id': sid(getattr(v, 'turn_id', m.get('turn_id'))),\n"
            "        'generation_id': sid(getattr(v, 'generation_id', m.get('generation_id'))),\n"
            "        'outcome': enum(getattr(v, 'outcome', m.get('outcome'))),\n"
            "        'is_terminal': getattr(v, 'is_terminal', m.get('is_terminal')),\n"
            "        'public_error_code': enum(getattr(v, 'public_error_code', m.get('public_error_code'))),\n"
            "        'retryable': getattr(v, 'retryable', m.get('retryable')),\n"
            "        'recovery_action': enum(getattr(v, 'recovery_action', m.get('recovery_action'))),\n"
            "    }\n"
            "framework = importlib.import_module('framework')\n"
            "try:\n"
            "    version = metadata.version('ai-character-framework')\n"
            "except Exception:\n"
            "    version = getattr(framework, '__version__', None)\n"
            "s = framework.create_realtime_session()\n"
            "events=[]\n"
            "s.on_event(lambda e: events.append(public(e)))\n"
            "r = asyncio.run(s.run_turn_async(input_text='provider-free smoke'))\n"
            "c = public(getattr(s, 'capabilities', None))\n"
            "d = public(getattr(s, 'diagnostics_snapshot', None))\n"
            "cr = project_construction(getattr(s, 'construction_result', None))\n"
            "rr = project_result(r)\n"
            "close_succeeded = False\n"
            "try:\n"
            "    close_result = s.close()\n"
            "    close_succeeded = close_result is None or bool(public(close_result).get('closed', True))\n"
            "except Exception:\n"
            "    close_succeeded = False\n"
            "print(json.dumps({\n"
            "    'version': version,\n"
            "    'construction': cr,\n"
            "    'events': events,\n"
            "    'result': rr,\n"
            "    'capabilities': c,\n"
            "    'diagnostics': d,\n"
            "    'close_succeeded': close_succeeded,\n"
            "}, sort_keys=True))\n"
        )
        env = dict(os.environ)
        env["PYTHONPATH"] = os.pathsep.join(pythonpath)
        completed = subprocess.run(
            [sys.executable, "-c", code],
            cwd=temp_path,
            env=env,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if completed.returncode:
            raise GateError("fixed SDK provider-free smoke failed")
        try:
            payload = json.loads(completed.stdout.strip().splitlines()[-1])
        except (IndexError, json.JSONDecodeError) as error:
            raise GateError("fixed SDK provider-free smoke did not return valid JSON") from error
        _validate_fixed_sdk_smoke_payload(payload)
    return "PASS"


def _validate_fixed_sdk_smoke_payload(payload: dict[str, object]) -> None:
    if payload.get("version") != FRAMEWORK_VERSION:
        raise GateError("fixed SDK metadata version mismatch")
    construction = payload.get("construction")
    if not isinstance(construction, dict):
        raise GateError("fixed SDK construction payload missing")
    if construction.get("status") != "mock_ready":
        raise GateError("fixed SDK construction was not mock_ready")
    if construction.get("real_runtime_requested") is not False:
        raise GateError("fixed SDK construction requested real runtime")
    if construction.get("real_runtime_enabled") is not False:
        raise GateError("fixed SDK construction enabled real runtime")
    if construction.get("runtime_executable") is not True:
        raise GateError("fixed SDK provider-free runtime not executable")
    if construction.get("provider_execution_performed") not in (None, False):
        raise GateError("fixed SDK provider execution was performed")
    events = payload.get("events")
    if not isinstance(events, list):
        raise GateError("fixed SDK events payload missing")
    event_types = [event.get("type") or event.get("event_type") for event in events if isinstance(event, dict)]
    if event_types != [marker.split(" ", 1)[1] for marker in CANONICAL_EVENTS]:
        raise GateError("fixed SDK canonical event sequence mismatch")
    terminals = [event for event in events if isinstance(event, dict) and event.get("terminal") is True]
    if len(terminals) != 1 or (terminals[0].get("type") or terminals[0].get("event_type")) != "realtime.turn.completed":
        raise GateError("fixed SDK terminal event count mismatch")
    session_ids = {str(event.get("session_id")) for event in events if isinstance(event, dict)}
    turn_ids = {str(event.get("turn_id")) for event in events if isinstance(event, dict)}
    generation_ids = {str(event.get("generation_id")) for event in events if isinstance(event, dict)}
    if len(session_ids) != 1 or not re.fullmatch(r"fw_session_[0-9a-f]{32}", next(iter(session_ids))):
        raise GateError("fixed SDK session identity mismatch")
    if len(turn_ids) != 1 or not re.fullmatch(r"fw_turn_[0-9a-f]{32}", next(iter(turn_ids))):
        raise GateError("fixed SDK turn identity mismatch")
    if len(generation_ids) != 1 or not re.fullmatch(r"fw_generation_[0-9a-f]{32}", next(iter(generation_ids))):
        raise GateError("fixed SDK generation identity mismatch")
    result = payload.get("result")
    if not isinstance(result, dict) or result.get("outcome") != "completed":
        raise GateError("fixed SDK turn outcome mismatch")
    if result.get("is_terminal") is not True:
        raise GateError("fixed SDK turn result was not terminal")
    if result.get("session_id") != next(iter(session_ids)) or result.get("turn_id") != next(iter(turn_ids)) or result.get("generation_id") != next(iter(generation_ids)):
        raise GateError("fixed SDK result identity correlation mismatch")
    capabilities = payload.get("capabilities")
    if not isinstance(capabilities, dict):
        raise GateError("fixed SDK capabilities payload missing")
    if capabilities.get("real_runtime_enabled") is not False:
        raise GateError("fixed SDK capabilities enabled real runtime")
    if capabilities.get("supports_motion") is not False:
        raise GateError("fixed SDK capabilities unexpectedly support motion")
    if capabilities.get("tts_queue_flush_supported") is not False:
        raise GateError("fixed SDK capabilities unexpectedly support TTS queue flush")
    for stage_name in ("text_generation", "voice_input", "voice_output", "motion"):
        stage = capabilities.get(stage_name)
        if not isinstance(stage, dict):
            raise GateError(f"fixed SDK {stage_name} capability missing")
        runtime = stage.get("runtime")
        if not isinstance(runtime, dict):
            raise GateError(f"fixed SDK {stage_name} runtime missing")
        if runtime.get("real_runtime") is not False:
            raise GateError(f"fixed SDK {stage_name} selected real runtime")
    for stage_name in ("text_generation", "voice_input", "voice_output"):
        stage = capabilities.get(stage_name)
        runtime = stage.get("runtime") if isinstance(stage, dict) else None
        if not isinstance(runtime, dict) or runtime.get("fake_runtime") is not True:
            raise GateError(f"fixed SDK {stage_name} did not select fake runtime")
    motion = capabilities.get("motion")
    motion_runtime = motion.get("runtime") if isinstance(motion, dict) else None
    if not isinstance(motion_runtime, dict):
        raise GateError("fixed SDK motion runtime missing")
    if motion_runtime.get("fake_runtime") is not False or motion_runtime.get("runtime_available") is not False:
        raise GateError("fixed SDK motion runtime default truth mismatch")
    voice_output = capabilities.get("voice_output")
    if isinstance(voice_output, dict):
        if voice_output.get("pending_flush_supported") is not False:
            raise GateError("fixed SDK voice output pending flush unexpectedly supported")
        if voice_output.get("provider_hard_cancel_supported") is not False:
            raise GateError("fixed SDK voice output provider hard cancel unexpectedly supported")
        if voice_output.get("playback_ownership") != "host":
            raise GateError("fixed SDK voice output playback ownership mismatch")
        if voice_output.get("host_playback_stop_request_supported") is not True:
            raise GateError("fixed SDK voice output host playback stop request unsupported")
        if voice_output.get("host_playback_stop_ack_supported") is not True:
            raise GateError("fixed SDK voice output host playback stop ack unsupported")
    text_generation = capabilities.get("text_generation")
    if isinstance(text_generation, dict) and text_generation.get("provider_hard_cancel_supported") is not False:
        raise GateError("fixed SDK text generation provider hard cancel unexpectedly supported")
    diagnostics = payload.get("diagnostics")
    if not isinstance(diagnostics, dict):
        raise GateError("fixed SDK diagnostics payload missing")
    if diagnostics.get("stale_completion_count") != 0 or diagnostics.get("duplicate_terminal_count") != 0 or diagnostics.get("overflow_count") != 0:
        raise GateError("fixed SDK diagnostics counters were nonzero")
    if payload.get("close_succeeded") is not True:
        raise GateError("fixed SDK close did not succeed")


def main() -> int:
    try:
        check_surface()
        check_docs()
        check_adapter_source()
        check_tests()
        check_privacy()
        smoke = run_fixed_sdk_smoke()
        print("v400_drc_v4_2_status: implemented-awaiting-review")
        print("v400_drc_v4_2_baseline:", EXPECTED_BASELINE)
        print("v400_drc_v4_1_status: closed-accepted")
        print("v400_drc_v4_2_exact_change_surface: True")
        print("v400_drc_v4_2_change_file_count:", len(EXPECTED_FILES))
        print("v400_framework_release:", FRAMEWORK_RELEASE)
        print("v400_framework_annotated_tag_target:", FRAMEWORK_TAG_TARGET)
        print("v400_framework_official_zip:", FRAMEWORK_ZIP)
        print("v400_framework_official_zip_sha256:", FRAMEWORK_ZIP_SHA256)
        print("v400_framework_distribution:", FRAMEWORK_DISTRIBUTION)
        print("v400_framework_required_version:", FRAMEWORK_VERSION)
        print("v400_framework_root_public_inventory:", FRAMEWORK_ROOT_PUBLIC_INVENTORY)
        print("v400_provider_free_only: True")
        print("v400_root_framework_import_only: True")
        print("v400_fw_submodule_imports: False")
        print("v400_sys_path_cwd_project_root_workaround: False")
        print("v400_real_runtime_enabled_true: False")
        print("v400_real_stage_injection: False")
        print("v400_canonical_9_event_sequence_encoded: True")
        print("v400_exactly_once_terminal_required: True")
        print("v400_framework_owned_stale_result_semantics: True")
        print("v400_capability_truthfulness_required: True")
        print("v400_real_unified_runtime_claimed: False")
        print("v400_existing_v3_runtime_retained: True")
        print("v400_diagnostics_privacy_boundary: True")
        print("v400_fixed_fw_v600_sdk_smoke:", smoke)
        print("v400_commit_push_authorized: False")
        return 0
    except (GateError, OSError, zipfile.BadZipFile) as error:
        print(f"v400_provider_free_realtime_session_adapter_gate_error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
