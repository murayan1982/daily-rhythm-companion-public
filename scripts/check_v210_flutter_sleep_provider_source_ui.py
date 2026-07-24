"""Validate the mock-safe W-4b Flutter provider/source-label UI boundary."""

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

ACCEPTED_BACKEND_HASHES = {
    "backend/app/main.py": "6ead9b1570b1453d7029496db3b554156b0e6752b1cb2369053e9341a81d3c27",
    "backend/app/api/sleep_provider_selection.py": "7f5569e46be04ca199233b5035b90c348348268618635656fe36b5d6b4e9805d",
    "backend/app/models/sleep_provider_selection.py": "b1fda1bfdf2755007f6dfc25e09dbef414d6b4529ef5faba948c835a9dfe46eb",
    "backend/app/services/sleep_provider_selection_service.py": "10904eadd11bf90409c9604cbaa7e1f3c6b19b3c43ffc5f78286d3a2ce58ddb5",
    "backend/tests/test_sleep_provider_selection_contract.py": "b173c7a164b24a45e4f00276eb298c3effade8af82286d484c89326d248bc472",
    "backend/app/api/sleep.py": "80ea9be0988dee24492821990a039608be3ee7dc5a3179d758151461809e5c3a",
    "backend/app/models/sleep.py": "4fd063af3ff7cfb4f0ed1c26fe252ab60907622720081ce7cafdcb8296a72961",
    "backend/app/services/sleep_providers/factory.py": "b898031e0b499a00ff88e5355e3851b280436377d0d0f35263d68e481289c3e6",
    "backend/app/services/fitbit_api_client.py": "34a613eeda3d20adbae0a7a4fd0e21a7dd5e68c210d21372548424e1a4aef54b",
    "backend/app/services/fitbit_sleep_service.py": "5d62b006f760278d2f8501f2f32d95deeb99437e7004e35c5388662c686d9e89",
    "backend/app/services/fitbit_sleep_normalizer.py": "c0acb09ad59c89be97d64eaf2e1b410cd3bad3efed1a52a790049f16ac410c2d",
    "backend/app/services/sleep_providers/fitbit.py": "41f48c65245515ac429ad4380f00052ca9010258782eb90e15e04dafc065f356",
    "backend/tests/test_fitbit_real_sleep_normalization.py": "ebbf3edd6ec135ad7ec10b3125e82f842acf28088952c06a6f35682abf45c7ce",
}

W4B_FILES = (
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v210_goal_checklist_small_commit.md",
    "docs/v210_flutter_sleep_provider_source_ui.md",
    "app/lib/models/sleep_provider_selection.dart",
    "app/lib/services/backend_api_client.dart",
    "app/lib/screens/home_screen.dart",
    "app/test/sleep_provider_selection_test.dart",
    "app/test/widget_test.dart",
    "scripts/check_v210_fitbit_current_behavior_inventory.py",
    "scripts/check_v210_fitbit_token_status_reconnect.py",
    "scripts/check_v210_fitbit_real_sleep_normalization.py",
    "scripts/check_v210_sleep_provider_selection_source_labels.py",
    "scripts/check_v210_flutter_sleep_provider_source_ui.py",
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
    files = {relative: read(relative) for relative in W4B_FILES}

    checklist = files["docs/DRC_v210_goal_checklist_small_commit.md"]
    require(checklist, "Current small commit: C-1a", "W-5 current commit")
    require(checklist, "W-5b1  COMPLETED / ACCEPTED", "W-5b1 accepted state")
    require(checklist, "W-5a  COMPLETED / ACCEPTED", "W-5a accepted state")
    require(checklist, "Current small-commit state: CURRENT / NOT_COMPLETED", "W-5 current state")
    require(checklist, "W-4  COMPLETED / ACCEPTED", "W-4 parent state")
    require(checklist, "W-4a  COMPLETED / ACCEPTED", "W-4a accepted state")
    require(checklist, "W-4b  COMPLETED / ACCEPTED", "W-4b state")
    require(checklist, "W-5  COMPLETED / ACCEPTED", "W-5 current state")
    require(checklist, "C-1  CURRENT / NOT_COMPLETED", "C-1 current state")
    for phase in ("T-1", "V-1", "R-1"):
        require(checklist, f"{phase}  PLANNED", f"{phase} planned state")

    model = files["app/lib/models/sleep_provider_selection.dart"]
    for marker in (
        "class SleepProviderOption",
        "class SleepProviderSelectionStatus",
        "configuredProviderLabel",
        "changeRequiresBackendRestart",
        "requiresRealOperatorVerification",
        "displayConfiguredState",
    ):
        require(model, marker, "Flutter provider model")

    client = files["app/lib/services/backend_api_client.dart"]
    require(client, "fetchSleepProviderSelectionStatus", "Flutter API method")
    require(client, "$baseUrl/sleep/providers", "provider metadata route")

    home = files["app/lib/screens/home_screen.dart"]
    for marker in (
        "fetchSleepProviderSelectionStatus",
        "providerSelectionStatus?.isFitbit == true",
        "Sleep Data Source",
        "sleep-data-source-section",
        "設定中のprovider:",
        "今回のデータ元:",
        "Google Health Operator Connection Details",
        "google-health-operator-details",
        "Fitbit Operator Status",
        "新しい実利用経路にはGoogle Health",
    ):
        require(home, marker, "W-4b Home UI")
    if "final fitbitStatus = await widget.apiClient.fetchFitbitStatus();" in home:
        raise AssertionError("W-4b must not fetch Fitbit status unconditionally")

    model_tests = files["app/test/sleep_provider_selection_test.dart"]
    for marker in (
        "parses backend-owned provider selection metadata",
        "marks legacy Fitbit as migration reference",
        "marks deprecated compatibility aliases conservatively",
        "reports unsupported selection without inventing availability",
    ):
        require(model_tests, marker, "provider model regression")

    widget_tests = files["app/test/widget_test.dart"]
    for marker in (
        "Google Health user UX stays concise in sleep data source card",
        "Google Health operator details remain under advanced tools",
        "Mock provider stays credential-free and skips Fitbit status",
        "Fitbit UI retires legacy OAuth guidance",
        "Mock provider must not query Fitbit status.",
    ):
        require(widget_tests, marker, "provider/source widget regression")

    contract = files["docs/v210_flutter_sleep_provider_source_ui.md"]
    require(contract, "Status: COMPLETED / ACCEPTED", "W-4b contract state")
    require(contract, "Parent phase: W-4 COMPLETED / ACCEPTED", "W-4 parent state")
    require(contract, "W-5b1 correction", "W-5 boundary")

    assert_hashes(PROTECTED_RELEASE_HASHES, "Protected release record")
    assert_hashes(ACCEPTED_BACKEND_HASHES, "Accepted backend boundary")

    for relative, text in files.items():
        assert_no_sensitive_values(relative, text)

    print("v210_flutter_sleep_provider_source_ui_status: completed-accepted")
    print("v210_flutter_sleep_provider_source_ui_completed_small_commit: W-4b")
    print("v210_flutter_sleep_provider_source_ui_current_small_commit: C-1a")
    print("v210_flutter_sleep_provider_source_ui_parent_phase: W-4-completed-accepted")
    print("v210_flutter_sleep_provider_source_ui_real_operator_execution: false")
    print("v210_flutter_sleep_provider_source_ui_release_records_changed: false")
    print("v210_flutter_sleep_provider_source_ui_w5a_completed_accepted: True")
    print("v210_flutter_sleep_provider_source_ui_w5b1_completed_accepted: True")
    print("v210_flutter_sleep_provider_source_ui_w5b2_completed_accepted: True")
    print("[v210-flutter-sleep-provider-source-ui-check] OK")


if __name__ == "__main__":
    main()
