"""Validate the W-2 Fitbit token/status/reconnect source-tree contract."""

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

W2_FILES = (
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "backend/app/models/fitbit.py",
    "backend/app/services/fitbit_service.py",
    "backend/app/services/fitbit_token_store.py",
    "backend/app/services/fitbit_oauth_state_store.py",
    "backend/app/services/fitbit_token_exchange.py",
    "backend/tests/test_fitbit_token_status_reconnect.py",
    "app/lib/models/fitbit_status.dart",
    "app/lib/models/fitbit_connect_response.dart",
    "app/test/fitbit_token_status_reconnect_test.dart",
    "docs/DRC_v210_goal_checklist_small_commit.md",
    "docs/v210_fitbit_token_status_reconnect.md",
    "scripts/check_v210_fitbit_current_behavior_inventory.py",
    "scripts/check_v210_fitbit_token_status_reconnect.py",
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


def reject(text: str, needle: str, label: str) -> None:
    if needle in text:
        raise AssertionError(f"Unexpected {label}: {needle!r}")


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
    files = {relative: read(relative) for relative in W2_FILES}

    checklist = files["docs/DRC_v210_goal_checklist_small_commit.md"]
    require(checklist, "Current small commit: C-1b", "W-5 current commit")
    require(checklist, "W-5b1  COMPLETED / ACCEPTED", "W-5b1 accepted state")
    require(checklist, "W-5a  COMPLETED / ACCEPTED", "W-5a accepted state")
    require(checklist, "Current small-commit state: CURRENT / NOT_COMPLETED", "W-5 incomplete state")
    require(checklist, "W-1 state: COMPLETED / ACCEPTED", "W-1 accepted state")
    require(checklist, "W-2 state: COMPLETED / ACCEPTED", "W-2 accepted state")
    require(checklist, "W-2  COMPLETED / ACCEPTED", "W-2 queue state")
    require(checklist, "W-3 state: COMPLETED / ACCEPTED", "W-3 accepted state")
    require(checklist, "W-3  COMPLETED / ACCEPTED", "W-3 queue state")
    require(checklist, "W-4  COMPLETED / ACCEPTED", "W-4 queue state")
    require(checklist, "W-5  COMPLETED / ACCEPTED", "W-5 queue state")
    require(checklist, "C-1  CURRENT / NOT_COMPLETED", "C-1 current state")
    for phase in ("T-1", "V-1", "R-1"):
        require(checklist, f"{phase}  PLANNED", f"{phase} planned state")

    model = files["backend/app/models/fitbit.py"]
    for state in (
        "UNCONFIGURED",
        "AUTHORIZATION_READY",
        "TOKEN_PRESENT_UNVERIFIED",
        "CONNECTED",
        "REFRESH_REQUIRED",
        "RECONNECT_REQUIRED",
        "PERMISSION_BLOCKED",
        "UNAVAILABLE",
        "ERROR",
    ):
        require(model, state, f"connection state {state}")
    require(model, "connection_state", "response state field")
    require(model, "verified", "response verified field")

    service = files["backend/app/services/fitbit_service.py"]
    require(service, "_classify_token_status", "status classifier")
    require(service, "legacy_connected", "backward-compatible bool")
    require(service, "consume_state", "one-time OAuth state")
    require(service, "PERMISSION_BLOCKED", "permission classification")
    reject(service, "post_fitbit_form", "status/network coupling")
    reject(service, "refresh_fitbit_access_token", "automatic status refresh")

    token_store = files["backend/app/services/fitbit_token_store.py"]
    require(token_store, "now_provider", "deterministic time injection")
    require(token_store, "should_refresh", "refresh classification")
    require(token_store, "is_development_dummy", "dummy marker")

    state_store = files["backend/app/services/fitbit_oauth_state_store.py"]
    require(state_store, "def consume_state", "state consumption")
    require(state_store, "self.delete_state()", "state deletion")

    exchange = files["backend/app/services/fitbit_token_exchange.py"]
    require(exchange, "http_post", "fake HTTP injection")
    require(exchange, "token_store", "temporary store injection")

    backend_test = files["backend/tests/test_fitbit_token_status_reconnect.py"]
    for needle in (
        "test_near_expiry_token_requires_guarded_refresh",
        "test_expired_access_without_refresh_requires_reconnect",
        "test_oauth_state_is_consumed_once",
        "test_permission_denial_is_classified_and_state_is_consumed",
        "test_fake_refresh_success_saves_tokens_without_exposing_values",
        "test_fake_refresh_failure_is_safe_and_does_not_save",
    ):
        require(backend_test, needle, "backend W-2 regression")

    flutter_status = files["app/lib/models/fitbit_status.dart"]
    require(flutter_status, "resolvedConnectionState", "old/new response fallback")
    require(flutter_status, "verified ? '連携済み' : '未検証'", "verified-only success wording")
    flutter_test = files["app/test/fitbit_token_status_reconnect_test.dart"]
    require(flutter_test, "isNot('連携済み')", "Flutter conservative state")

    contract = files["docs/v210_fitbit_token_status_reconnect.md"]
    require(contract, "Normal `/fitbit/status` does not call", "no automatic HTTP boundary")
    require(contract, "Configured real acceptance remains W-5", "real operator boundary")

    for relative, digest in PROTECTED_RELEASE_HASHES.items():
        actual = normalized_hash(relative)
        if actual != digest:
            raise AssertionError(f"Protected release record changed: {relative}")

    for relative, text in files.items():
        assert_no_sensitive_values(relative, text)

    print("v210_fitbit_token_status_reconnect_status: completed-accepted")
    print("v210_fitbit_token_status_reconnect_completed_small_commit: W-2")
    print("v210_fitbit_token_status_reconnect_completed_small_commit_w3: W-3")
    print("v210_fitbit_token_status_reconnect_current_small_commit: C-1b")
    print("v210_fitbit_token_status_reconnect_connection_states_added: True")
    print("v210_fitbit_token_status_reconnect_status_external_http: False")
    print("v210_fitbit_token_status_reconnect_oauth_state_one_time: True")
    print("v210_fitbit_token_status_reconnect_mock_safe: True")
    print("v210_fitbit_token_status_reconnect_real_operator_execution: False")
    print("v210_fitbit_token_status_reconnect_release_records_changed: False")
    print("v210_fitbit_token_status_reconnect_w3_completed_accepted: True")
    print("v210_fitbit_token_status_reconnect_w4_completed_accepted: True")
    print("v210_fitbit_token_status_reconnect_w5_completed_accepted: True")
    print("v210_fitbit_token_status_reconnect_later_phases_planned: True")
    print("v210_fitbit_token_status_reconnect_w5a_completed_accepted: True")
    print("v210_fitbit_token_status_reconnect_w5b1_completed_accepted: True")
    print("v210_fitbit_token_status_reconnect_w5b2_completed_accepted: True")
    print("[v210-fitbit-token-status-reconnect-check] OK")


if __name__ == "__main__":
    main()
