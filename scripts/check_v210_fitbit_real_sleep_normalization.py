"""Validate the accepted W-3 Fitbit sleep normalization source-tree contract."""

from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

PROTECTED_RELEASE_HASHES = {
    "docs/DRC_v200_goal_checklist_small_commit.md": "4c043837986c626c6fc44e4f84f73b019b2c8c21da7531a3f029554006b7eb63",
    "release_notes/v2.0.0.md": "d2e13041ae51b9fef330a01a0d9124ccbfb6fb0850a0c2a29966baf96be3417b",
    "docs/DRC_v20x_maintenance_checklist.md": "02e6e2e49a54a5c1360ee5d95d6bed2314ab42aec5dce911f3ed72867c4d46f2",
    "docs/v20x_patch_release.md": "eb6ae9770a4611a463ddb227a1dd8ce8816ee310cddaed327a02404a34a7935d",
    "docs/v201_patch_release_record.md": "9b724a6c5c7ffffdb3e699ad010ff75148ec4549b6cf2d940b44e62e161140bd",
    "release_notes/v2.0.1.md": "1e90c85e51ef848b64bddaa73f1f40c659457935e30831027310ea95fc94656b",
    "build_v200_final_fixed_release_zip_from_head.ps1": "4a4439341b0ad00d56b50038993631fcb48fb417cd0f0648dc3abc5e72d3b360",
    "build_v201_fixed_release_zip_from_head.ps1": "89d3fe3e39484b36272d9c8ec8499276ffe305ec844a87cca5d90fef8931ab1b",
    "scripts/check_v20x_patch_release.py": "e4eefc408abcbccc2651c1113ae8264269cce1d77525067173e0a06a7ef685cf",
}

W3_UNCHANGED_HASHES = {
    "backend/app/config.py": "063b9fdd7c1b5c3132a5885eddb56fc2b2202d45b202dda25b745393b35ccc06",
    "backend/app/api/fitbit.py": "44463bb3ce7c0e325c7a2a31602a68b0bc436cff615ef03ea70a3d4be6641b66",
    "backend/app/api/sleep.py": "80ea9be0988dee24492821990a039608be3ee7dc5a3179d758151461809e5c3a",
    "backend/app/models/fitbit.py": "5474e1f121b43f7d25a6959954bd1d7caed8f37478453fa3a7e7c672c4948b52",
    "backend/app/models/sleep.py": "4fd063af3ff7cfb4f0ed1c26fe252ab60907622720081ce7cafdcb8296a72961",
    "backend/app/services/fitbit_service.py": "18c00c52a9e9a2f24eab027f0a484d658729635d76ec61fb85c942eed971adc1",
    "backend/app/services/fitbit_token_store.py": "9215e20d1a02e8b97906e75875279cb3ee228a0bf640f418820623318fb62fb3",
    "backend/app/services/fitbit_oauth_state_store.py": "507e83ecc93a81737c17c7786c869cfb32fcaec9a4677f93a9ffd963507fe282",
    "backend/app/services/fitbit_token_exchange.py": "60c4cc3ca7942c1334b443e0089547b97d6e7a4cc9ad1d745077d3be9a45d136",
    "backend/app/services/sleep_providers/factory.py": "b898031e0b499a00ff88e5355e3851b280436377d0d0f35263d68e481289c3e6",
    "backend/tests/test_fitbit_current_state_contract.py": "fad33f7a99f59f60903d84cccdb14b8d58c715f2666a74c97ff7dbdaae0f67bb",
    "backend/tests/test_fitbit_token_status_reconnect.py": "340ea380ad6ffbe84be5a769f47cd988515ee576be582ef324a55ccb7f8d42cb",
    "app/lib/models/sleep_summary.dart": "f28173aeb89b996e284771243fe6cbd6e037098a634647b827ac096cef4d11e8",
    "app/lib/models/fitbit_status.dart": "3c06914f0eb992ae11fd7febf5589b5ffe44fd639d3c847d9fe26ec11b513814",
    "app/lib/models/fitbit_connect_response.dart": "b2f897316bb6dd52f271e994bc15c6ddb1096b4c5c6ca2f499cc9495de77ed1c",
    "app/lib/services/backend_api_client.dart": "98bbd40caef0c6a55892dfd9d9a146d524e3427f0a2cfe3ce71cc36eb34fab25",
    "app/lib/screens/home_screen.dart": "344ec16c252448ed89087818a66432522b5e162b2f58c52c3b5660bb33847e90",
    "app/test/fitbit_current_state_contract_test.dart": "d753b8163410e78dd33c354a7adfab0153358b598f741743b300b8f254e9acb0",
    "app/test/fitbit_token_status_reconnect_test.dart": "6a1390b1b0e014a8fcc1f0aa47d1e30f0716fe099e8dcd4afbf312ac67dbf15b",
    "app/pubspec.yaml": "fe4921649f69a5c9a7fe9dc4caad7d41f796cdb1b6adcd8687974a89cec85f86",
}

W3_FILES = (
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v210_goal_checklist_small_commit.md",
    "docs/v210_fitbit_real_sleep_normalization.md",
    "backend/app/services/fitbit_api_client.py",
    "backend/app/services/fitbit_sleep_service.py",
    "backend/app/services/fitbit_sleep_normalizer.py",
    "backend/app/services/sleep_providers/fitbit.py",
    "backend/tests/test_fitbit_real_sleep_normalization.py",
    "scripts/check_v210_fitbit_current_behavior_inventory.py",
    "scripts/check_v210_fitbit_real_sleep_normalization.py",
)


def read(relative: str) -> str:
    path = ROOT / relative
    if not path.is_file():
        raise AssertionError(f"Missing required file: {relative}")
    return path.read_text(encoding="utf-8")


def normalized_hash(relative: str) -> str:
    normalized = (ROOT / relative).read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return sha256(normalized).hexdigest()


def require(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise AssertionError(f"Missing {label}: {needle!r}")


def assert_hashes(expected: dict[str, str], label: str) -> None:
    for relative, digest in expected.items():
        actual = normalized_hash(relative)
        if actual != digest:
            raise AssertionError(f"{label} changed: {relative}: {actual} != {digest}")


def assert_no_sensitive_values(relative: str, text: str) -> None:
    patterns = (
        r"sk-[A-Za-z0-9_\-]{12,}",
        r"xai-[A-Za-z0-9_\-]{12,}",
        r"AIza[0-9A-Za-z_\-]{20,}",
        r"Bearer\s+[A-Za-z0-9_\-.]{16,}",
        r"[A-Za-z]:\\Users\\[^<\r\n]+",
        r"192\.168\.\d{1,3}\.\d{1,3}",
    )
    for pattern in patterns:
        if re.search(pattern, text, flags=re.IGNORECASE):
            raise AssertionError(f"Sensitive-looking value in {relative}: {pattern}")


def main() -> None:
    files = {relative: read(relative) for relative in W3_FILES}

    checklist = files["docs/DRC_v210_goal_checklist_small_commit.md"]
    require(checklist, "Current small commit: W-4", "W-4 current commit")
    require(checklist, "Current small-commit state: CURRENT / NOT_COMPLETED", "W-4 incomplete state")
    require(checklist, "W-1 state: COMPLETED / ACCEPTED", "W-1 accepted state")
    require(checklist, "W-2 state: COMPLETED / ACCEPTED", "W-2 accepted state")
    require(checklist, "W-3 state: COMPLETED / ACCEPTED", "W-3 accepted state")
    require(checklist, "Implementation state: COMPLETED / ACCEPTED", "W-3 implementation state")
    require(checklist, "W-3  COMPLETED / ACCEPTED", "W-3 queue state")
    require(checklist, "W-4  CURRENT / NOT_COMPLETED", "W-4 queue state")
    for phase in ("W-5", "C-1", "T-1", "V-1", "R-1"):
        require(checklist, f"{phase}  PLANNED", f"{phase} planned state")

    api_client = files["backend/app/services/fitbit_api_client.py"]
    for marker in (
        "FITBIT_API_ERROR_UNAUTHORIZED",
        "FITBIT_API_ERROR_PERMISSION_DENIED",
        "FITBIT_API_ERROR_SCOPE_MISSING",
        "FITBIT_API_ERROR_RATE_LIMITED",
        "FITBIT_API_ERROR_PROVIDER_UNAVAILABLE",
        "http_get",
        "_extract_safe_error_markers",
    ):
        require(api_client, marker, "API classification boundary")

    sleep_service = files["backend/app/services/fitbit_sleep_service.py"]
    for marker in (
        "FITBIT_SLEEP_ERROR_RECONNECT_REQUIRED",
        "FITBIT_SLEEP_ERROR_PERMISSION_DENIED",
        "FITBIT_SLEEP_ERROR_SCOPE_MISSING",
        "FITBIT_SLEEP_ERROR_RATE_LIMITED",
        "FITBIT_SLEEP_ERROR_PROVIDER_UNAVAILABLE",
        "FITBIT_SLEEP_ERROR_INVALID_RESPONSE",
        "api_get",
    ):
        require(sleep_service, marker, "sleep service safe state")

    normalizer = files["backend/app/services/fitbit_sleep_normalizer.py"]
    for marker in (
        "total_sleep_minutes <= 0",
        "quality_label",
        "confidence",
        "is_real_data=True",
        "totalMinutesAsleep",
    ):
        require(normalizer, marker, "normalization semantics")

    provider = files["backend/app/services/sleep_providers/fitbit.py"]
    for marker in (
        "sleep_start=summary.main_sleep_start_time",
        "sleep_end=summary.main_sleep_end_time",
        "quality_label=summary.quality_label",
        "confidence=summary.confidence",
        "is_real_data=summary.is_real_data",
        "unavailable_reason=unavailable_reason",
    ):
        require(provider, marker, "SleepSummary mapping")

    backend_test = files["backend/tests/test_fitbit_real_sleep_normalization.py"]
    for marker in (
        "test_api_client_classifies_401_without_exposing_payload",
        "test_api_client_classifies_scope_and_permission_403",
        "test_normalizer_prefers_main_sleep_and_maps_real_fields",
        "test_normalizer_uses_summary_total_as_medium_confidence_fallback",
        "test_provider_maps_failures_into_safe_unavailable_summary",
        "test_sleep_summary_api_returns_w3_real_data_semantics",
    ):
        require(backend_test, marker, "W-3 backend regression")

    contract = files["docs/v210_fitbit_real_sleep_normalization.md"]
    require(contract, "COMPLETED / ACCEPTED", "contract accepted state")
    require(contract, "Configured real acceptance remains W-5", "real operator boundary")
    require(contract, "synthetic public-safe Fitbit-shaped dictionaries", "fixture policy")

    assert_hashes(PROTECTED_RELEASE_HASHES, "Protected release record")
    assert_hashes(W3_UNCHANGED_HASHES, "W-3 unchanged boundary")

    for relative, text in files.items():
        assert_no_sensitive_values(relative, text)

    print("v210_fitbit_real_sleep_normalization_status: completed-accepted")
    print("v210_fitbit_real_sleep_normalization_completed_small_commit: W-3")
    print("v210_fitbit_real_sleep_normalization_current_small_commit: W-4")
    print("v210_fitbit_real_sleep_normalization_api_error_classification: True")
    print("v210_fitbit_real_sleep_normalization_sleep_summary_mapping: True")
    print("v210_fitbit_real_sleep_normalization_mock_safe: True")
    print("v210_fitbit_real_sleep_normalization_real_operator_execution: False")
    print("v210_fitbit_real_sleep_normalization_release_records_changed: False")
    print("v210_fitbit_real_sleep_normalization_w3_completed_accepted: True")
    print("v210_fitbit_real_sleep_normalization_w4_current_not_completed: True")
    print("v210_fitbit_real_sleep_normalization_later_phases_planned: True")
    print("[v210-fitbit-real-sleep-normalization-check] OK")


if __name__ == "__main__":
    main()
