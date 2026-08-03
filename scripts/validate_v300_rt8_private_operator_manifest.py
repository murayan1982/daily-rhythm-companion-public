#!/usr/bin/env python3
"""Strict, public-safe validator for ignored RT-8 private operator manifests.

The default ``--check-example`` mode validates only the committed rejected
example. ``--manifest-json`` is the only mode that reads a private manifest,
and that file must live under the ignored ``operator_evidence/`` directory.
No mode starts Backend or Flutter, opens a socket, requests microphone access,
reads audio, imports a provider, performs TTS/playback, or contacts VTube Studio.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any, Callable, Mapping

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_VERSION = "drc.v3.rt8-platform-acceptance.2"
MANIFEST_KIND = "private_rt8_pc_android_realtime_acceptance"
EXAMPLE_HEAD = "REPLACE_WITH_40_LOWERCASE_HEX"
EXAMPLE_MANIFEST = ROOT / "docs" / "operator_evidence_templates" / "v300_rt8_pc_android_realtime_acceptance.example.json"
MAX_MANIFEST_BYTES = 65536
SHA_RE = re.compile(r"[0-9a-f]{40}\Z")

PC_BOOLEAN_KEYS = (
    "default_off_startup_confirmed",
    "execution_before_explicit_action",
    "incremental_output_before_terminal",
    "completed_terminal",
    "cancelled_terminal",
    "partial_output_retained",
    "provider_hard_cancel_claimed",
    "real_tts_generated",
    "audible_playback_started",
    "audible_playback_completed_naturally",
    "active_playback_before_flush",
    "local_playback_stop_requested",
    "local_playback_stop_succeeded",
    "active_after_flush",
    "app_owned_motion_presentation_completed",
    "real_provider_motion_execution_claimed",
    "framework_session_created",
    "framework_session_closed",
    "provider_execution_attempted",
    "network_execution_attempted",
    "backend_flutter_real_motion_executed",
    "operator_visible_physical_motion_confirmed",
    "reset_additional_backend_request",
    "opt_out_additional_backend_request",
    "disposal_additional_backend_request",
    "additional_provider_execution",
    "additional_network_execution",
    "additional_visible_motion",
    "recognized_processes_stopped",
    "real_execution_flags_closed",
    "private_process_values_removed",
)
PC_COUNT_KEYS = (
    "manual_stream_start_count",
    "completed_stream_terminal_count",
    "cancelled_stream_terminal_count",
    "cooperative_cancel_request_count",
    "explicit_tts_enqueue_count",
    "explicit_tts_process_count",
    "explicit_flush_count",
    "pending_after_flush",
    "app_owned_motion_presentation_count",
    "manual_vts_apply_count",
    "vts_commands_requested",
    "vts_commands_applied",
    "vts_commands_completed",
)
ANDROID_BOOLEAN_KEYS = (
    "default_off_startup_confirmed",
    "execution_before_explicit_action",
    "bounded_microphone_capture_completed",
    "private_staging_consumed",
    "private_staging_cleaned",
    "real_stt_completed",
    "provider_neutral_transcript_handoff_completed",
    "incremental_stream_completed",
    "completed_terminal_to_tts_handoff",
    "real_tts_generated",
    "audible_playback_completed_naturally",
    "silent_negative_control_observed",
    "playback_remained_active_during_silence",
    "local_playback_stop_requested",
    "local_playback_stop_succeeded",
    "old_work_remained_inert",
    "old_audio_resumed",
    "late_old_completion_affected_current_state",
    "recovery_real_stt_completed",
    "recovery_stream_completed",
    "recovery_tts_completed",
    "recovery_playback_completed",
    "framework_session_created",
    "framework_session_closed",
    "provider_execution_attempted",
    "network_execution_attempted",
    "backend_flutter_real_motion_executed",
    "operator_visible_physical_motion_confirmed",
    "reset_additional_backend_request",
    "opt_out_additional_backend_request",
    "disposal_additional_backend_request",
    "additional_provider_execution",
    "additional_network_execution",
    "additional_visible_motion",
    "recognized_processes_stopped",
    "real_execution_flags_closed",
    "private_process_values_removed",
    "private_capture_artifacts_remaining",
    "private_audio_artifacts_remaining",
)
ANDROID_COUNT_KEYS = (
    "natural_voice_turn_count",
    "silent_control_interruption_count",
    "confirmed_user_speech_event_count",
    "drc_local_interruption_count",
    "pending_voice_output_after_interruption",
    "recovery_voice_turn_count",
    "manual_vts_apply_count",
    "vts_commands_requested",
    "vts_commands_applied",
    "vts_commands_completed",
)
AGGREGATE_BOOLEAN_KEYS = (
    "pc_accepted",
    "android_accepted",
    "both_candidate_commits_verified",
    "both_platform_cleanups_passed",
    "backend_processes_stopped",
    "flutter_processes_stopped",
    "private_environment_values_removed",
    "private_process_values_removed",
    "all_real_execution_flags_closed",
    "private_staged_audio_remaining",
    "private_logs_remaining",
    "private_backups_remaining",
    "operator_evidence_committed",
    "operator_evidence_pushed",
    "drc_working_tree_clean",
    "drc_head_origin_main_synchronized",
    "fw_working_tree_clean",
    "rt9_implementation_authorized",
)
PRIVACY_KEYS = (
    "spoken_text_included",
    "transcript_included",
    "generated_response_included",
    "raw_audio_or_pcm_included",
    "audio_url_or_artifact_id_included",
    "stream_session_or_turn_id_included",
    "provider_identity_included",
    "provider_model_included",
    "provider_payload_included",
    "credential_included",
    "token_included",
    "authorization_header_included",
    "private_endpoint_included",
    "private_path_included",
    "lan_ip_included",
    "device_identifier_included",
    "vts_model_or_hotkey_identity_included",
    "screenshot_or_recording_included",
    "raw_log_included",
    "raw_exception_included",
    "operator_evidence_file_committed",
    "operator_evidence_file_pushed",
)
NON_CLAIM_KEYS = (
    "pc_real_microphone_claimed",
    "pc_real_stt_claimed",
    "pc_soft_barge_in_claimed",
    "web_microphone_acceptance_claimed",
    "ios_acceptance_claimed",
    "all_android_devices_claimed",
    "always_on_microphone_claimed",
    "automatic_next_turn_capture_claimed",
    "provider_llm_hard_cancel_claimed",
    "provider_stt_hard_cancel_claimed",
    "provider_tts_hard_cancel_claimed",
    "backend_http_hard_cancel_claimed",
    "fw_real_tts_queue_flush_claimed",
    "fw_unified_realtime_runtime_claimed",
    "automatic_voice_motion_sync_claimed",
    "automatic_emotion_inference_claimed",
    "physical_motion_proven_by_runtime_claimed",
    "production_security_ready_claimed",
    "v300_release_ready_claimed",
)

SENSITIVE_PATTERNS = (
    re.compile(r"(?i)sk-[a-z0-9_-]{12,}"),
    re.compile(r"(?i)xai-[a-z0-9_-]{12,}"),
    re.compile(r"(?i)bearer\s+[a-z0-9._~+/-]{12,}"),
    re.compile(r"(?i)(?:api[_-]?key|access[_-]?token|refresh[_-]?token|client[_-]?secret)\s*[:=]"),
    re.compile(r"(?i)[a-z]:\\(?:users|work|home)\\"),
    re.compile(r"/(?:home|users)/[^/\s]+/"),
    re.compile(r"\b(?:10|127|169\.254|172\.(?:1[6-9]|2\d|3[01])|192\.168)\.\d{1,3}\.\d{1,3}\b"),
)


class ValidationError(Exception):
    def __init__(self, code: str, key: str | None = None) -> None:
        self.code = code
        self.key = key
        super().__init__(code)

    def public_message(self) -> str:
        suffix = f":{self.key}" if self.key else ""
        return f"v300_rt8_manifest_error: {self.code}{suffix}"


def _pairs_no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValidationError("duplicate_key", key)
        result[key] = value
    return result



def _scan_sensitive_values(value: Any) -> None:
    if isinstance(value, str):
        for pattern in SENSITIVE_PATTERNS:
            if pattern.search(value):
                raise ValidationError("sensitive_value_detected")
        return
    if isinstance(value, Mapping):
        for child in value.values():
            _scan_sensitive_values(child)
        return
    if isinstance(value, list):
        for child in value:
            _scan_sensitive_values(child)


def load_json_bytes(raw: bytes) -> Mapping[str, Any]:
    if len(raw) > MAX_MANIFEST_BYTES:
        raise ValidationError("manifest_too_large")
    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise ValidationError("invalid_utf8") from exc
    for pattern in SENSITIVE_PATTERNS:
        if pattern.search(text):
            raise ValidationError("sensitive_value_detected")
    try:
        value = json.loads(text, object_pairs_hook=_pairs_no_duplicates)
    except ValidationError:
        raise
    except (json.JSONDecodeError, UnicodeError) as exc:
        raise ValidationError("invalid_json") from exc
    if not isinstance(value, Mapping):
        raise ValidationError("root_not_object")
    _scan_sensitive_values(value)
    return value


def _zero_section(status: str, bool_keys: tuple[str, ...], count_keys: tuple[str, ...]) -> dict[str, Any]:
    result: dict[str, Any] = {"status": status}
    result.update({key: False for key in bool_keys})
    result.update({key: 0 for key in count_keys})
    return result


def _accepted_pc() -> dict[str, Any]:
    result = _zero_section("accepted", PC_BOOLEAN_KEYS, PC_COUNT_KEYS)
    for key in (
        "default_off_startup_confirmed",
        "incremental_output_before_terminal",
        "completed_terminal",
        "cancelled_terminal",
        "partial_output_retained",
        "real_tts_generated",
        "audible_playback_started",
        "audible_playback_completed_naturally",
        "active_playback_before_flush",
        "local_playback_stop_requested",
        "local_playback_stop_succeeded",
        "app_owned_motion_presentation_completed",
        "framework_session_created",
        "framework_session_closed",
        "provider_execution_attempted",
        "network_execution_attempted",
        "operator_visible_physical_motion_confirmed",
        "recognized_processes_stopped",
        "real_execution_flags_closed",
        "private_process_values_removed",
    ):
        result[key] = True
    result.update(
        manual_stream_start_count=3,
        completed_stream_terminal_count=2,
        cancelled_stream_terminal_count=1,
        cooperative_cancel_request_count=1,
        explicit_tts_enqueue_count=2,
        explicit_tts_process_count=2,
        explicit_flush_count=1,
        pending_after_flush=0,
        app_owned_motion_presentation_count=1,
        manual_vts_apply_count=1,
        vts_commands_requested=1,
        vts_commands_applied=1,
        vts_commands_completed=1,
    )
    return result


def _accepted_android() -> dict[str, Any]:
    result = _zero_section("accepted", ANDROID_BOOLEAN_KEYS, ANDROID_COUNT_KEYS)
    for key in (
        "default_off_startup_confirmed",
        "bounded_microphone_capture_completed",
        "private_staging_consumed",
        "private_staging_cleaned",
        "real_stt_completed",
        "provider_neutral_transcript_handoff_completed",
        "incremental_stream_completed",
        "completed_terminal_to_tts_handoff",
        "real_tts_generated",
        "audible_playback_completed_naturally",
        "silent_negative_control_observed",
        "playback_remained_active_during_silence",
        "local_playback_stop_requested",
        "local_playback_stop_succeeded",
        "old_work_remained_inert",
        "recovery_real_stt_completed",
        "recovery_stream_completed",
        "recovery_tts_completed",
        "recovery_playback_completed",
        "framework_session_created",
        "framework_session_closed",
        "provider_execution_attempted",
        "network_execution_attempted",
        "operator_visible_physical_motion_confirmed",
        "recognized_processes_stopped",
        "real_execution_flags_closed",
        "private_process_values_removed",
    ):
        result[key] = True
    result.update(
        natural_voice_turn_count=1,
        silent_control_interruption_count=0,
        confirmed_user_speech_event_count=1,
        drc_local_interruption_count=1,
        pending_voice_output_after_interruption=0,
        recovery_voice_turn_count=1,
        manual_vts_apply_count=1,
        vts_commands_requested=1,
        vts_commands_applied=1,
        vts_commands_completed=1,
    )
    return result


def _accepted_aggregate() -> dict[str, Any]:
    result = _zero_section("accepted", AGGREGATE_BOOLEAN_KEYS, ())
    for key in (
        "pc_accepted",
        "android_accepted",
        "both_candidate_commits_verified",
        "both_platform_cleanups_passed",
        "backend_processes_stopped",
        "flutter_processes_stopped",
        "private_environment_values_removed",
        "private_process_values_removed",
        "all_real_execution_flags_closed",
        "drc_working_tree_clean",
        "drc_head_origin_main_synchronized",
        "fw_working_tree_clean",
    ):
        result[key] = True
    return result


def expected_manifest_for_stage(
    stage: str,
    *,
    pc_head: str = EXAMPLE_HEAD,
    android_head: str = EXAMPLE_HEAD,
) -> dict[str, Any]:
    normalized = stage.replace("-", "_")
    if normalized not in {"example", "pc_windows", "android", "aggregate"}:
        raise ValidationError("unsupported_stage")
    status = "example_not_accepted" if normalized == "example" else "accepted"
    manifest: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "manifest_kind": MANIFEST_KIND,
        "stage": normalized,
        "status": status,
        "candidate_branch": "main",
        "pc_windows_candidate_source_head": pc_head,
        "android_candidate_source_head": android_head,
        "pc_windows": _zero_section("not_run", PC_BOOLEAN_KEYS, PC_COUNT_KEYS),
        "android": _zero_section("not_run", ANDROID_BOOLEAN_KEYS, ANDROID_COUNT_KEYS),
        "aggregate_cleanup": _zero_section("not_run", AGGREGATE_BOOLEAN_KEYS, ()),
        "privacy": {key: False for key in PRIVACY_KEYS},
        "non_claims": {key: False for key in NON_CLAIM_KEYS},
    }
    if normalized in {"pc_windows", "android", "aggregate"}:
        manifest["pc_windows"] = _accepted_pc()
    if normalized in {"android", "aggregate"}:
        manifest["android"] = _accepted_android()
    if normalized == "aggregate":
        manifest["aggregate_cleanup"] = _accepted_aggregate()
    return manifest


def _compare_exact(actual: Any, expected: Any, path: str = "root") -> None:
    if isinstance(expected, Mapping):
        if not isinstance(actual, Mapping):
            raise ValidationError("type_mismatch", path)
        actual_keys = set(actual)
        expected_keys = set(expected)
        missing = sorted(expected_keys - actual_keys)
        unknown = sorted(actual_keys - expected_keys)
        if missing:
            raise ValidationError("missing_key", f"{path}.{missing[0]}")
        if unknown:
            raise ValidationError("unknown_key", f"{path}.{unknown[0]}")
        for key in expected:
            _compare_exact(actual[key], expected[key], f"{path}.{key}")
        return
    if type(actual) is not type(expected):
        raise ValidationError("type_mismatch", path)
    if actual != expected:
        raise ValidationError("value_mismatch", path)


def validate_manifest_data(data: Mapping[str, Any], expected_stage: str) -> None:
    normalized = expected_stage.replace("-", "_")
    actual_stage = data.get("stage")
    if actual_stage != normalized:
        raise ValidationError("stage_mismatch", "root.stage")
    pc_head = data.get("pc_windows_candidate_source_head")
    android_head = data.get("android_candidate_source_head")
    if normalized == "example":
        expected = expected_manifest_for_stage("example")
    else:
        if not isinstance(pc_head, str) or not SHA_RE.fullmatch(pc_head):
            raise ValidationError("invalid_commit_hash", "root.pc_windows_candidate_source_head")
        if normalized in {"android", "aggregate"}:
            if not isinstance(android_head, str) or not SHA_RE.fullmatch(android_head):
                raise ValidationError("invalid_commit_hash", "root.android_candidate_source_head")
        elif android_head != EXAMPLE_HEAD:
            raise ValidationError("value_mismatch", "root.android_candidate_source_head")
        expected = expected_manifest_for_stage(normalized, pc_head=pc_head, android_head=android_head)
    _compare_exact(data, expected)


def _git_output(*args: str, root: Path = ROOT) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        text=True,
        encoding="utf-8",
        errors="strict",
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    return completed.stdout.strip()


def _git_ok(*args: str, root: Path = ROOT) -> bool:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    ).returncode == 0


def validate_private_manifest_path(
    manifest_path: Path,
    *,
    root: Path = ROOT,
    ignored_check: Callable[[Path], bool] | None = None,
) -> bytes:
    operator_root = (root / "operator_evidence").resolve()
    if manifest_path.is_symlink():
        raise ValidationError("manifest_not_regular_file")
    resolved = manifest_path.resolve()
    try:
        relative = resolved.relative_to(operator_root)
    except ValueError as exc:
        raise ValidationError("manifest_outside_operator_evidence") from exc
    if relative == Path(".") or not resolved.is_file() or resolved.is_symlink():
        raise ValidationError("manifest_not_regular_file")
    if ignored_check is None:
        ignored_check = lambda path: _git_ok("check-ignore", "--quiet", "--", path.as_posix(), root=root)
    repo_relative = resolved.relative_to(root.resolve())
    if not ignored_check(repo_relative):
        raise ValidationError("manifest_not_ignored")
    raw = resolved.read_bytes()
    if len(raw) > MAX_MANIFEST_BYTES:
        raise ValidationError("manifest_too_large")
    return raw


def verify_git_state(data: Mapping[str, Any], stage: str, minimum_source_head: str) -> None:
    if not SHA_RE.fullmatch(minimum_source_head):
        raise ValidationError("invalid_minimum_source_head")
    branch = _git_output("branch", "--show-current")
    head = _git_output("rev-parse", "HEAD")
    origin_main = _git_output("rev-parse", "origin/main")
    if branch != "main":
        raise ValidationError("branch_not_main")
    if head != origin_main:
        raise ValidationError("origin_main_not_synchronized")
    if _git_output("status", "--porcelain"):
        raise ValidationError("working_tree_not_clean")
    if not _git_ok("cat-file", "-e", f"{minimum_source_head}^{{commit}}"):
        raise ValidationError("minimum_source_commit_missing")
    if not _git_ok("merge-base", "--is-ancestor", minimum_source_head, head):
        raise ValidationError("minimum_source_not_ancestor")
    pc_head = str(data["pc_windows_candidate_source_head"])
    android_head = str(data["android_candidate_source_head"])
    normalized = stage.replace("-", "_")
    for candidate in (pc_head, android_head):
        if candidate != EXAMPLE_HEAD and not _git_ok("cat-file", "-e", f"{candidate}^{{commit}}"):
            raise ValidationError("candidate_source_commit_missing")
    if normalized == "pc_windows":
        if pc_head != head:
            raise ValidationError("pc_candidate_not_current_head")
    elif normalized == "android":
        if android_head != head:
            raise ValidationError("android_candidate_not_current_head")
        if not _git_ok("merge-base", "--is-ancestor", pc_head, android_head):
            raise ValidationError("pc_candidate_not_ancestor")
    elif normalized == "aggregate":
        for candidate in (pc_head, android_head):
            if not _git_ok("merge-base", "--is-ancestor", candidate, head):
                raise ValidationError("candidate_not_ancestor")


def check_example() -> None:
    data = load_json_bytes(EXAMPLE_MANIFEST.read_bytes())
    validate_manifest_data(data, "example")
    print("v300_rt8_private_manifest_example_status: rejected-as-template")
    print("v300_rt8_private_manifest_example_accepted: False")
    print("v300_rt8_private_manifest_private_file_read: False")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check-example", action="store_true")
    mode.add_argument("--manifest-json", type=Path)
    parser.add_argument("--stage", choices=("pc-windows", "android", "aggregate"))
    parser.add_argument("--minimum-source-head")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    try:
        args = parse_args(argv)
        if args.check_example:
            if args.stage or args.minimum_source_head:
                raise ValidationError("example_mode_extra_argument")
            check_example()
            return 0
        if not args.stage or not args.minimum_source_head:
            raise ValidationError("private_mode_argument_missing")
        raw = validate_private_manifest_path(args.manifest_json)
        data = load_json_bytes(raw)
        validate_manifest_data(data, args.stage)
        verify_git_state(data, args.stage, args.minimum_source_head)
        print(f"v300_rt8_private_manifest_stage: {args.stage}")
        print("v300_rt8_private_manifest_status: accepted")
        print("v300_rt8_private_manifest_schema_valid: True")
        print("v300_rt8_private_manifest_git_state_valid: True")
        print("v300_rt8_private_manifest_private_values_printed: False")
        return 0
    except ValidationError as exc:
        print(exc.public_message(), file=sys.stderr)
        return 2
    except (OSError, subprocess.SubprocessError):
        print("v300_rt8_manifest_error: bounded_validation_failed", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
