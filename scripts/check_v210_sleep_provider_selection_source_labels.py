"""Validate the mock-safe W-4a sleep-provider selection status contract."""

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

W3_ACCEPTED_BOUNDARY_HASHES = {
    "backend/app/api/sleep.py": "80ea9be0988dee24492821990a039608be3ee7dc5a3179d758151461809e5c3a",
    "backend/app/models/sleep.py": "4fd063af3ff7cfb4f0ed1c26fe252ab60907622720081ce7cafdcb8296a72961",
    "backend/app/services/sleep_providers/factory.py": "b898031e0b499a00ff88e5355e3851b280436377d0d0f35263d68e481289c3e6",
    "backend/app/services/fitbit_api_client.py": "34a613eeda3d20adbae0a7a4fd0e21a7dd5e68c210d21372548424e1a4aef54b",
    "backend/app/services/fitbit_sleep_service.py": "5d62b006f760278d2f8501f2f32d95deeb99437e7004e35c5388662c686d9e89",
    "backend/app/services/fitbit_sleep_normalizer.py": "c0acb09ad59c89be97d64eaf2e1b410cd3bad3efed1a52a790049f16ac410c2d",
    "backend/app/services/sleep_providers/fitbit.py": "41f48c65245515ac429ad4380f00052ca9010258782eb90e15e04dafc065f356",
    "backend/tests/test_fitbit_real_sleep_normalization.py": "ebbf3edd6ec135ad7ec10b3125e82f842acf28088952c06a6f35682abf45c7ce",
}

W4A_FILES = (
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v210_goal_checklist_small_commit.md",
    "docs/v210_sleep_provider_selection_source_labels.md",
    "backend/app/main.py",
    "backend/app/api/sleep_provider_selection.py",
    "backend/app/models/sleep_provider_selection.py",
    "backend/app/services/sleep_provider_selection_service.py",
    "backend/tests/test_sleep_provider_selection_contract.py",
    "scripts/check_v210_sleep_provider_selection_source_labels.py",
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
    files = {relative: read(relative) for relative in W4A_FILES}

    checklist = files["docs/DRC_v210_goal_checklist_small_commit.md"]
    require(checklist, "Current small commit: W-5b1", "W-5 current commit")
    require(checklist, "W-5a  COMPLETED / ACCEPTED", "W-5a accepted state")
    require(checklist, "Current small-commit state: CURRENT / NOT_COMPLETED", "W-5 current state")
    require(checklist, "W-4  COMPLETED / ACCEPTED", "W-4 phase state")
    require(checklist, "W-4a  COMPLETED / ACCEPTED", "W-4a accepted state")
    require(checklist, "W-4b  COMPLETED / ACCEPTED", "W-4b accepted state")
    require(checklist, "W-5  CURRENT / NOT_COMPLETED", "W-5 current state")
    for phase in ("C-1", "T-1", "V-1", "R-1"):
        require(checklist, f"{phase}  PLANNED", f"{phase} planned state")

    model = files["backend/app/models/sleep_provider_selection.py"]
    for marker in (
        "class SleepProviderOption",
        "class SleepProviderSelectionStatus",
        "configured_provider_supported",
        "change_requires_backend_restart",
        "real_operator_verification_required",
    ):
        require(model, marker, "selection response model")

    service = files["backend/app/services/sleep_provider_selection_service.py"]
    for marker in (
        'provider="mock"',
        'provider="wearable_stub"',
        'provider="google_health"',
        'provider="fitbit_stub"',
        'alias_for="wearable_stub"',
        'provider="fitbit"',
        'role="legacy_migration_reference"',
        "real_operator_verification_required=False",
        'configured_role = "unsupported"',
        "get_sleep_provider_selection_status",
    ):
        require(service, marker, "provider selection classification")
    for forbidden in (
        "create_sleep_provider",
        "FitbitTokenStore",
        "GoogleHealthTokenStore",
        "httpx",
        "requests",
    ):
        if forbidden in service:
            raise AssertionError(f"W-4a service must remain metadata-only: {forbidden}")

    api = files["backend/app/api/sleep_provider_selection.py"]
    require(api, '@router.get("/sleep/providers"', "read-only provider endpoint")
    require(api, "get_sleep_provider_selection_status(load_config())", "metadata-only route")

    main_source = files["backend/app/main.py"]
    require(main_source, "sleep_provider_selection,", "provider router import")
    require(main_source, "app.include_router(sleep_provider_selection.router)", "provider router binding")

    tests = files["backend/tests/test_sleep_provider_selection_contract.py"]
    for marker in (
        "test_selection_status_classifies_supported_providers",
        "test_selection_status_marks_fitbit_stub_as_deprecated_alias",
        "test_selection_status_handles_unknown_provider_conservatively",
        "test_sleep_provider_selection_endpoint_is_read_only_and_deterministic",
    ):
        require(tests, marker, "W-4a backend regression")

    contract = files["docs/v210_sleep_provider_selection_source_labels.md"]
    require(contract, "Status: COMPLETED / ACCEPTED", "accepted state")
    require(contract, "W-5b1 correction", "W-5 boundary")
    require(contract, "W-5b1 correction", "parent W-5 boundary")

    assert_hashes(PROTECTED_RELEASE_HASHES, "Protected release record")
    assert_hashes(W3_ACCEPTED_BOUNDARY_HASHES, "Accepted W-3 runtime boundary")

    for relative, text in files.items():
        assert_no_sensitive_values(relative, text)

    print("v210_sleep_provider_selection_status: completed-accepted")
    print("v210_sleep_provider_selection_completed_small_commit: W-4a")
    print("v210_sleep_provider_selection_current_small_commit: W-5b1")
    print("v210_sleep_provider_selection_parent_phase: W-4-completed-accepted")
    print("v210_sleep_provider_selection_real_operator_execution: false")
    print("v210_sleep_provider_selection_release_records_changed: false")
    print("v210_sleep_provider_selection_w5a_completed_accepted: True")
    print("[v210-sleep-provider-selection-source-labels-check] OK")


if __name__ == "__main__":
    main()
