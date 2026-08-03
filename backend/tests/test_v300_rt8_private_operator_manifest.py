"""Credential-free tests for the strict RT-8 private manifest validator."""

from __future__ import annotations

import copy
import io
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import validate_v300_rt8_private_operator_manifest as validator

PC_SHA = "1" * 40
ANDROID_SHA = "2" * 40


def encoded(data: object) -> bytes:
    return json.dumps(data, separators=(",", ":")).encode("utf-8")


def assert_code(exc: pytest.ExceptionInfo[validator.ValidationError], code: str) -> None:
    assert exc.value.code == code


def test_committed_example_remains_rejected_template(capsys: pytest.CaptureFixture[str]) -> None:
    validator.check_example()
    output = capsys.readouterr().out
    assert "rejected-as-template" in output
    assert "example_accepted: False" in output


def test_synthetic_pc_manifest_is_accepted() -> None:
    data = validator.expected_manifest_for_stage("pc_windows", pc_head=PC_SHA)
    validator.validate_manifest_data(data, "pc-windows")


def test_synthetic_android_manifest_is_accepted() -> None:
    data = validator.expected_manifest_for_stage(
        "android", pc_head=PC_SHA, android_head=ANDROID_SHA
    )
    validator.validate_manifest_data(data, "android")


def test_synthetic_aggregate_manifest_is_accepted() -> None:
    data = validator.expected_manifest_for_stage(
        "aggregate", pc_head=PC_SHA, android_head=ANDROID_SHA
    )
    validator.validate_manifest_data(data, "aggregate")


def test_missing_key_is_rejected() -> None:
    data = validator.expected_manifest_for_stage("pc_windows", pc_head=PC_SHA)
    del data["privacy"]["credential_included"]
    with pytest.raises(validator.ValidationError) as exc:
        validator.validate_manifest_data(data, "pc-windows")
    assert_code(exc, "missing_key")


def test_unknown_key_is_rejected() -> None:
    data = validator.expected_manifest_for_stage("pc_windows", pc_head=PC_SHA)
    data["pc_windows"]["free_form_note"] = "not allowed"
    with pytest.raises(validator.ValidationError) as exc:
        validator.validate_manifest_data(data, "pc-windows")
    assert_code(exc, "unknown_key")


def test_duplicate_json_key_is_rejected() -> None:
    raw = b'{"schema_version":"a","schema_version":"b"}'
    with pytest.raises(validator.ValidationError) as exc:
        validator.load_json_bytes(raw)
    assert_code(exc, "duplicate_key")


def test_oversized_json_is_rejected() -> None:
    with pytest.raises(validator.ValidationError) as exc:
        validator.load_json_bytes(b"{" + b" " * validator.MAX_MANIFEST_BYTES + b"}")
    assert_code(exc, "manifest_too_large")


def test_malformed_utf8_is_rejected() -> None:
    with pytest.raises(validator.ValidationError) as exc:
        validator.load_json_bytes(b"{\xff}")
    assert_code(exc, "invalid_utf8")


def test_manifest_outside_operator_evidence_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "manifest.json"
    path.write_text("{}", encoding="utf-8")
    with pytest.raises(validator.ValidationError) as exc:
        validator.validate_private_manifest_path(
            path, root=tmp_path, ignored_check=lambda _: True
        )
    assert_code(exc, "manifest_outside_operator_evidence")


def test_nonignored_private_manifest_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "operator_evidence" / "manifest.json"
    path.parent.mkdir()
    path.write_text("{}", encoding="utf-8")
    with pytest.raises(validator.ValidationError) as exc:
        validator.validate_private_manifest_path(
            path, root=tmp_path, ignored_check=lambda _: False
        )
    assert_code(exc, "manifest_not_ignored")


def test_malformed_commit_hash_is_rejected() -> None:
    data = validator.expected_manifest_for_stage("pc_windows", pc_head=PC_SHA)
    data["pc_windows_candidate_source_head"] = "ABC"
    with pytest.raises(validator.ValidationError) as exc:
        validator.validate_manifest_data(data, "pc-windows")
    assert_code(exc, "invalid_commit_hash")


def test_stage_mismatch_is_rejected() -> None:
    data = validator.expected_manifest_for_stage("pc_windows", pc_head=PC_SHA)
    with pytest.raises(validator.ValidationError) as exc:
        validator.validate_manifest_data(data, "android")
    assert_code(exc, "stage_mismatch")


def test_free_form_text_is_rejected() -> None:
    data = validator.expected_manifest_for_stage("pc_windows", pc_head=PC_SHA)
    data["candidate_branch"] = "main with operator note"
    with pytest.raises(validator.ValidationError) as exc:
        validator.validate_manifest_data(data, "pc-windows")
    assert_code(exc, "value_mismatch")


@pytest.mark.parametrize(
    "unsafe",
    (
        "sk-example-secret-value-123456",
        r"C:\Users\private\manifest.json",
        "/home/private/operator/manifest.json",
        "192.168.10.25",
    ),
)
def test_sensitive_looking_values_are_rejected(unsafe: str) -> None:
    raw = encoded({"value": unsafe})
    with pytest.raises(validator.ValidationError) as exc:
        validator.load_json_bytes(raw)
    assert_code(exc, "sensitive_value_detected")


def test_error_output_never_echoes_private_value_or_path() -> None:
    secret = "sk-private-value-not-for-output-12345"
    try:
        validator.load_json_bytes(encoded({"value": secret}))
    except validator.ValidationError as exc:
        output = exc.public_message()
    else:
        raise AssertionError("sensitive value must be rejected")
    assert secret not in output
    assert "private" not in output.lower()
    assert output == "v300_rt8_manifest_error: sensitive_value_detected"

def test_rt8b1_schema_version_is_v2() -> None:
    assert validator.SCHEMA_VERSION == "drc.v3.rt8-platform-acceptance.2"


def test_rt8b1_v1_schema_is_rejected() -> None:
    data = validator.expected_manifest_for_stage("pc_windows", pc_head=PC_SHA)
    data["schema_version"] = "drc.v3.rt8-platform-acceptance.1"
    with pytest.raises(validator.ValidationError) as exc:
        validator.validate_manifest_data(data, "pc-windows")
    assert_code(exc, "value_mismatch")


def test_rt8b1_pc_counts_are_exact() -> None:
    data = validator.expected_manifest_for_stage("pc_windows", pc_head=PC_SHA)
    pc = data["pc_windows"]
    assert pc["manual_stream_start_count"] == 3
    assert pc["completed_stream_terminal_count"] == 2
    assert pc["cancelled_stream_terminal_count"] == 1
    assert pc["cooperative_cancel_request_count"] == 1
    assert pc["explicit_tts_enqueue_count"] == 2
    assert pc["explicit_tts_process_count"] == 2
    assert pc["explicit_flush_count"] == 1


def test_rt8b1_incorrect_stream_split_is_rejected() -> None:
    data = validator.expected_manifest_for_stage("pc_windows", pc_head=PC_SHA)
    data["pc_windows"]["manual_stream_start_count"] = 2
    data["pc_windows"]["completed_stream_terminal_count"] = 1
    data["pc_windows"]["cancelled_stream_terminal_count"] = 1
    with pytest.raises(validator.ValidationError) as exc:
        validator.validate_manifest_data(data, "pc-windows")
    assert_code(exc, "value_mismatch")


def test_rt8b1_incorrect_tts_counts_are_rejected() -> None:
    for key in ("explicit_tts_enqueue_count", "explicit_tts_process_count"):
        data = validator.expected_manifest_for_stage("pc_windows", pc_head=PC_SHA)
        data["pc_windows"][key] = 1
        with pytest.raises(validator.ValidationError) as exc:
            validator.validate_manifest_data(data, "pc-windows")
        assert_code(exc, "value_mismatch")
