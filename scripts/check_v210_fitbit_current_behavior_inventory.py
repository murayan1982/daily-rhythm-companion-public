"""Validate the W-1 v2.1.0 Fitbit implementation inventory.

This check is source-tree only. It reads public files, compares normalized
hashes, and verifies stable implementation markers. It does not load local
environment files, inspect backend/local_data, call external providers, open an
OAuth browser, build release artifacts, or modify the repository.
"""

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

INSPECTED_IMPLEMENTATION_HASHES = {
    "backend/app/config.py": "063b9fdd7c1b5c3132a5885eddb56fc2b2202d45b202dda25b745393b35ccc06",
    "backend/app/api/fitbit.py": "44463bb3ce7c0e325c7a2a31602a68b0bc436cff615ef03ea70a3d4be6641b66",
    "backend/app/api/sleep.py": "80ea9be0988dee24492821990a039608be3ee7dc5a3179d758151461809e5c3a",
    "backend/app/models/fitbit.py": "92bfbdbe3d2ace42bb2e0c18f4b79e7e283f25acbe713140a6e0f3e56092e7d3",
    "backend/app/models/sleep.py": "4fd063af3ff7cfb4f0ed1c26fe252ab60907622720081ce7cafdcb8296a72961",
    "backend/app/services/fitbit_service.py": "fa1089b7ce7836e4aa5a43a2709cf8aa3125c307c62775b5b4715b94d13679b5",
    "backend/app/services/fitbit_oauth_state_store.py": "ffa2faf86411e0df48b5720b9a98ba5dc2aad67a088c1b1452508334085a8595",
    "backend/app/services/fitbit_token_exchange.py": "34ad7b0f8c2217f6a3e974b97d8d7ddbebb7a0aaf3f20079d44bc6e8ff21b88e",
    "backend/app/services/fitbit_token_store.py": "5d795a3e44f369af3b89fd123946b13ae1d58851ae59339fb39051f49a11d73e",
    "backend/app/services/fitbit_api_client.py": "3b296b544c77e66f7213f91f2269eb279ad94a0c4feaea06ac181eaec0a0c3e0",
    "backend/app/services/fitbit_http_client.py": "9bde5276055f9f022f6fae3c7e3868c77c8bda902f9b4c29c605e8a808ae5713",
    "backend/app/services/fitbit_sleep_service.py": "9bc7fe4df3f2fc0d7b261faac21604d2be66ce5685f62411178fe0048aa63c3e",
    "backend/app/services/fitbit_sleep_normalizer.py": "940ec681a914c1791fc5dd6bb73e37196312fe7a127a0cb6662f592ecd0b380c",
    "backend/app/services/sleep_providers/factory.py": "b898031e0b499a00ff88e5355e3851b280436377d0d0f35263d68e481289c3e6",
    "backend/app/services/sleep_providers/fitbit.py": "7ebf9d1f5e12e1080cfac36e9d528ce56433b83b023a8e6bd04376247366b5e4",
    "backend/tests/test_fitbit_current_state_contract.py": "fad33f7a99f59f60903d84cccdb14b8d58c715f2666a74c97ff7dbdaae0f67bb",
    "app/lib/models/fitbit_status.dart": "e59b2f7cec18c78275c8604ade984cd057681c20e355592c2cdaa45510395b47",
    "app/lib/models/fitbit_connect_response.dart": "727b434269afc102c954b41f45ba99cbe38b59db69bb3f120d3c3aba967d4f84",
    "app/lib/models/sleep_summary.dart": "f28173aeb89b996e284771243fe6cbd6e037098a634647b827ac096cef4d11e8",
    "app/lib/services/backend_api_client.dart": "98bbd40caef0c6a55892dfd9d9a146d524e3427f0a2cfe3ce71cc36eb34fab25",
    "app/lib/screens/home_screen.dart": "344ec16c252448ed89087818a66432522b5e162b2f58c52c3b5660bb33847e90",
    "app/test/fitbit_current_state_contract_test.dart": "d753b8163410e78dd33c354a7adfab0153358b598f741743b300b8f254e9acb0",
    "app/pubspec.yaml": "fe4921649f69a5c9a7fe9dc4caad7d41f796cdb1b6adcd8687974a89cec85f86",
}

W1_FILES = (
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v210_goal_checklist_small_commit.md",
    "docs/v210_fitbit_current_behavior_inventory.md",
    "scripts/check_v210_fitbit_current_behavior_inventory.py",
)


def read(relative: str) -> str:
    path = ROOT / relative
    if not path.is_file():
        raise AssertionError(f"Missing required file: {relative}")
    return path.read_text(encoding="utf-8")


def normalized_hash(relative: str) -> str:
    path = ROOT / relative
    if not path.is_file():
        raise AssertionError(f"Missing protected file: {relative}")
    normalized = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return sha256(normalized).hexdigest()


def require(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise AssertionError(f"Missing {label}: {needle!r}")


def reject(text: str, needle: str, label: str) -> None:
    if needle in text:
        raise AssertionError(f"Unexpected {label}: {needle!r}")


def assert_hashes(expected_hashes: dict[str, str], label: str) -> None:
    for relative, expected in expected_hashes.items():
        actual = normalized_hash(relative)
        if actual != expected:
            raise AssertionError(
                f"{label} changed: {relative}: {actual} != {expected}"
            )


def assert_no_sensitive_values(relative: str, text: str) -> None:
    patterns = (
        r"sk-[A-Za-z0-9_\-]{12,}",
        r"xai-[A-Za-z0-9_\-]{12,}",
        r"AIza[0-9A-Za-z_\-]{20,}",
        r"Bearer\s+[A-Za-z0-9_\-.]{16,}",
        r"(?:access|refresh)_token\s*[:=]\s*['\"][^'\"]+",
        r"authorization_code\s*[:=]\s*['\"][^'\"]+",
        r"client_secret\s*[:=]\s*['\"][^'\"]+",
        r"[A-Za-z]:\\Users\\[^<\r\n]+",
        r"192\.168\.\d{1,3}\.\d{1,3}",
    )
    for pattern in patterns:
        if re.search(pattern, text, flags=re.IGNORECASE):
            raise AssertionError(f"Sensitive-looking value in {relative}: {pattern}")


def main() -> None:
    files = {relative: read(relative) for relative in W1_FILES}

    for relative in ("README.md", "roadmap.md", "tasklist.md", "scripts/README.md"):
        require(files[relative], "v2.0.1", f"{relative} released version")
        require(files[relative], "W-1", f"{relative} W-1 state")
        require(
            files[relative],
            "docs/DRC_v210_goal_checklist_small_commit.md",
            f"{relative} active checklist",
        )

    checklist = files["docs/DRC_v210_goal_checklist_small_commit.md"]
    require(checklist, "Current small commit: W-2", "W-2 current small commit")
    require(checklist, "Current small-commit state: CURRENT / NOT_COMPLETED", "W-2 current state")
    require(checklist, "W-1 state: COMPLETED / ACCEPTED", "W-1 accepted top state")
    require(checklist, "W-1  COMPLETED / ACCEPTED", "W-1 accepted queue state")
    require(checklist, "W-2  CURRENT / NOT_COMPLETED", "W-2 current queue state")
    w1_section = checklist.split("# W-1 —", 1)[1].split("# W-2 —", 1)[0]
    require(w1_section, "Status: COMPLETED / ACCEPTED", "W-1 accepted section state")
    w2_section = checklist.split("# W-2 —", 1)[1].split("# W-3 —", 1)[0]
    require(w2_section, "Status: CURRENT / NOT_COMPLETED", "W-2 current section state")
    for phase in ("W-3", "W-4", "W-5", "C-1", "T-1", "V-1", "R-1"):
        require(checklist, f"{phase}  PLANNED", f"{phase} planned queue state")
        section = checklist.split(f"# {phase} —", 1)[1]
        require(section, "Status: PLANNED", f"{phase} planned section state")

    for needle in (
        "Local token presence does not prove live token validity.",
        "OAuth URL preparation does not prove connection success.",
        "Mock-safe verification does not substitute for explicit real operator verification.",
        "R-1 completion requirements must not be imported into W-1",
    ):
        require(checklist, needle, "W-1 non-advancement rule")

    inventory = files["docs/v210_fitbit_current_behavior_inventory.md"]
    for needle in (
        "GET /fitbit/status",
        "GET /fitbit/connect",
        "GET /fitbit/callback",
        "FITBIT_ENABLE_REAL_TOKEN_EXCHANGE",
        "is_real_data (default false)",
        "W-5: PLANNED — explicit configured real OAuth/token/permission/sleep/UI operator acceptance",
    ):
        require(inventory, needle, "Fitbit inventory contract")

    factory = read("backend/app/services/sleep_providers/factory.py")
    for needle in (
        'RECOMMENDED_SLEEP_PROVIDERS = ("mock", "wearable_stub", "google_health")',
        'DEPRECATED_SLEEP_PROVIDER_ALIASES = {"fitbit_stub": "wearable_stub"}',
        'LEGACY_SLEEP_PROVIDERS = ("fitbit",)',
    ):
        require(factory, needle, "provider classification")

    api = read("backend/app/api/fitbit.py")
    for needle in (
        '@router.get("/status", response_model=FitbitStatusResponse)',
        '@router.get("/connect", response_model=FitbitConnectResponse)',
        '@router.get("/callback", response_model=FitbitCallbackResponse)',
    ):
        require(api, needle, "Fitbit route")

    service = read("backend/app/services/fitbit_service.py")
    require(service, "has_config and has_tokens", "local configuration/token status gate")
    require(service, "Real token validation is not implemented yet.", "unverified status wording")
    require(service, "Fitbit OAuth connect URL is ready.", "authorization-ready wording")

    token_exchange = read("backend/app/services/fitbit_token_exchange.py")
    require(token_exchange, "fitbit_enable_real_token_exchange", "real exchange guard")
    require(token_exchange, "refresh_fitbit_access_token", "refresh boundary")

    sleep_service = read("backend/app/services/fitbit_sleep_service.py")
    require(sleep_service, "refresh_fitbit_access_token", "sleep refresh path")
    require(sleep_service, "get_fitbit_json", "sleep API path")

    normalizer = read("backend/app/services/fitbit_sleep_normalizer.py")
    require(normalizer, 'main_sleep_start_time=_optional_string(main_sleep or {}, "startTime")', "normalized start time")
    require(normalizer, 'main_sleep_end_time=_optional_string(main_sleep or {}, "endTime")', "normalized end time")

    fitbit_provider = read("backend/app/services/sleep_providers/fitbit.py")
    require(fitbit_provider, 'source="fitbit"', "Fitbit SleepSummary source")
    reject(fitbit_provider, "is_real_data=True", "early real-data mapping")
    reject(fitbit_provider, "sleep_start=summary.main_sleep_start_time", "early sleep-start mapping")
    reject(fitbit_provider, "sleep_end=summary.main_sleep_end_time", "early sleep-end mapping")

    flutter_status = read("app/lib/models/fitbit_status.dart")
    require(flutter_status, "ローカルトークン検出", "Flutter conservative token wording")
    flutter_connect = read("app/lib/models/fitbit_connect_response.dart")
    require(flutter_connect, "確認完了を意味しません", "Flutter authorization-ready warning")
    flutter_test = read("app/test/fitbit_current_state_contract_test.dart")
    require(flutter_test, "isNot('連携済み')", "Flutter non-success regression")

    assert_hashes(PROTECTED_RELEASE_HASHES, "Protected release record")
    assert_hashes(INSPECTED_IMPLEMENTATION_HASHES, "W-1 inspected implementation")

    for relative, text in files.items():
        assert_no_sensitive_values(relative, text)

    print("v210_fitbit_inventory_status: completed-accepted")
    print("v210_fitbit_inventory_completed_small_commit: W-1")
    print("v210_fitbit_inventory_current_small_commit: W-2")
    print("v210_fitbit_inventory_runtime_changed: False")
    print("v210_fitbit_inventory_flutter_changed: False")
    print("v210_fitbit_inventory_existing_tests_changed: False")
    print("v210_fitbit_inventory_release_records_changed: False")
    print("v210_fitbit_inventory_mock_safe: True")
    print("v210_fitbit_inventory_real_operator_execution: False")
    print("v210_fitbit_inventory_w2_current_not_completed: True")
    print("v210_fitbit_inventory_later_phases_planned: True")
    print("[v210-fitbit-current-behavior-inventory-check] OK")


if __name__ == "__main__":
    main()
