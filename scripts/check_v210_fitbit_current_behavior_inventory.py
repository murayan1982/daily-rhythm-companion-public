"""Validate the accepted W-1 inventory through the accepted W-3 boundary."""

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

# Backend and stable model files outside later accepted change surfaces remain pinned to the W-1 baseline.
W1_UNCHANGED_IMPLEMENTATION_HASHES = {
    "backend/app/config.py": "063b9fdd7c1b5c3132a5885eddb56fc2b2202d45b202dda25b745393b35ccc06",
    "backend/app/api/fitbit.py": "44463bb3ce7c0e325c7a2a31602a68b0bc436cff615ef03ea70a3d4be6641b66",
    "backend/app/api/sleep.py": "80ea9be0988dee24492821990a039608be3ee7dc5a3179d758151461809e5c3a",
    "backend/app/models/sleep.py": "4fd063af3ff7cfb4f0ed1c26fe252ab60907622720081ce7cafdcb8296a72961",
    "backend/app/services/fitbit_http_client.py": "9bde5276055f9f022f6fae3c7e3868c77c8bda902f9b4c29c605e8a808ae5713",
    "backend/app/services/sleep_providers/factory.py": "b898031e0b499a00ff88e5355e3851b280436377d0d0f35263d68e481289c3e6",
    "backend/tests/test_fitbit_current_state_contract.py": "fad33f7a99f59f60903d84cccdb14b8d58c715f2666a74c97ff7dbdaae0f67bb",
    "app/lib/models/sleep_summary.dart": "f28173aeb89b996e284771243fe6cbd6e037098a634647b827ac096cef4d11e8",
    "app/test/fitbit_current_state_contract_test.dart": "d753b8163410e78dd33c354a7adfab0153358b598f741743b300b8f254e9acb0",
    "app/pubspec.yaml": "fe4921649f69a5c9a7fe9dc4caad7d41f796cdb1b6adcd8687974a89cec85f86",
}


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
    checklist = read("docs/DRC_v210_goal_checklist_small_commit.md")
    inventory = read("docs/v210_fitbit_current_behavior_inventory.md")
    w2_contract = read("docs/v210_fitbit_token_status_reconnect.md")
    w3_contract = read("docs/v210_fitbit_real_sleep_normalization.md")

    require(checklist, "W-1 state: COMPLETED / ACCEPTED", "W-1 accepted state")
    require(checklist, "W-2 state: COMPLETED / ACCEPTED", "W-2 accepted state")
    require(checklist, "W-3 state: COMPLETED / ACCEPTED", "W-3 accepted state")
    require(checklist, "Current small commit: W-4", "W-4 current state")
    require(checklist, "W-3  COMPLETED / ACCEPTED", "W-3 queue state")
    require(checklist, "W-4  CURRENT / NOT_COMPLETED", "W-4 queue state")
    for phase in ("W-5", "C-1", "T-1", "V-1", "R-1"):
        require(checklist, f"{phase}  PLANNED", f"{phase} planned state")

    require(inventory, "GET /fitbit/status", "W-1 status inventory")
    require(inventory, "FITBIT_ENABLE_REAL_TOKEN_EXCHANGE", "W-1 guarded exchange inventory")
    require(w2_contract, "token_present_unverified", "W-2 conservative state")
    require(w2_contract, "Configured real acceptance remains W-5", "W-5 boundary")
    require(w3_contract, "COMPLETED / ACCEPTED", "W-3 accepted state")
    require(w3_contract, "Configured real acceptance remains W-5", "W-3/W-5 boundary")
    read("backend/tests/test_fitbit_real_sleep_normalization.py")
    read("scripts/check_v210_fitbit_real_sleep_normalization.py")

    assert_hashes(PROTECTED_RELEASE_HASHES, "Protected release record")
    assert_hashes(W1_UNCHANGED_IMPLEMENTATION_HASHES, "W-1 non-W-2 implementation")

    for relative in (
        "README.md",
        "roadmap.md",
        "tasklist.md",
        "scripts/README.md",
        "docs/DRC_v210_goal_checklist_small_commit.md",
        "docs/v210_fitbit_current_behavior_inventory.md",
        "docs/v210_fitbit_token_status_reconnect.md",
        "docs/v210_fitbit_real_sleep_normalization.md",
    ):
        assert_no_sensitive_values(relative, read(relative))

    print("v210_fitbit_inventory_status: completed-accepted")
    print("v210_fitbit_inventory_completed_small_commit: W-1")
    print("v210_fitbit_inventory_completed_small_commit_w2: W-2")
    print("v210_fitbit_inventory_completed_small_commit_w3: W-3")
    print("v210_fitbit_inventory_current_small_commit: W-4")
    print("v210_fitbit_inventory_w2_runtime_changed: True")
    print("v210_fitbit_inventory_w2_flutter_changed: True")
    print("v210_fitbit_inventory_w4b_flutter_changed: True")
    print("v210_fitbit_inventory_w4b_tests_changed: True")
    print("v210_fitbit_inventory_release_records_changed: False")
    print("v210_fitbit_inventory_mock_safe: True")
    print("v210_fitbit_inventory_real_operator_execution: False")
    print("v210_fitbit_inventory_w2_completed_accepted: True")
    print("v210_fitbit_inventory_w3_completed_accepted: True")
    print("v210_fitbit_inventory_w3_implementation_present: True")
    print("v210_fitbit_inventory_w4_current_not_completed: True")
    print("v210_fitbit_inventory_later_phases_planned: True")
    print("[v210-fitbit-current-behavior-inventory-check] OK")


if __name__ == "__main__":
    main()
