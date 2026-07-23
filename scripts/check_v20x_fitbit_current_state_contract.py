"""Verify the accepted M-7 Fitbit current-state contract."""

from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
HISTORICAL_HASHES = {
    "docs/DRC_v200_goal_checklist_small_commit.md": "4c043837986c626c6fc44e4f84f73b019b2c8c21da7531a3f029554006b7eb63",
    "release_notes/v2.0.0.md": "d2e13041ae51b9fef330a01a0d9124ccbfb6fb0850a0c2a29966baf96be3417b",
}


def read(relative: str) -> str:
    path = ROOT / relative
    if not path.is_file():
        raise AssertionError(f"Missing required file: {relative}")
    return path.read_text(encoding="utf-8")


def require(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise AssertionError(f"Missing {label}: {needle!r}")


def reject(text: str, needle: str, label: str) -> None:
    if needle in text:
        raise AssertionError(f"Unexpected {label}: {needle!r}")


def snapshot_local_data() -> tuple[tuple[str, int, int], ...] | None:
    local_data = ROOT / "backend/local_data"
    if not local_data.exists():
        return None
    entries: list[tuple[str, int, int]] = []
    for path in sorted(local_data.rglob("*")):
        stat = path.lstat()
        entries.append(
            (
                path.relative_to(local_data).as_posix(),
                stat.st_size,
                stat.st_mtime_ns,
            )
        )
    return tuple(entries)


def assert_historical_hashes() -> None:
    for relative, expected in HISTORICAL_HASHES.items():
        normalized = (
            (ROOT / relative)
            .read_bytes()
            .replace(b"\r\n", b"\n")
            .replace(b"\r", b"\n")
        )
        actual = sha256(normalized).hexdigest()
        if actual != expected:
            raise AssertionError(
                f"Historical release record changed: {relative}: {actual} != {expected}"
            )


def run_check(relative: str) -> None:
    subprocess.run([sys.executable, str(ROOT / relative)], cwd=ROOT, check=True)


def run_m7_pytest() -> None:
    subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "backend/tests/test_fitbit_current_state_contract.py",
        ],
        cwd=ROOT,
        check=True,
    )


def main() -> None:
    local_data_before = snapshot_local_data()

    factory = read("backend/app/services/sleep_providers/factory.py")
    for needle in (
        'RECOMMENDED_SLEEP_PROVIDERS = ("mock", "wearable_stub", "google_health")',
        'DEPRECATED_SLEEP_PROVIDER_ALIASES = {"fitbit_stub": "wearable_stub"}',
        'LEGACY_SLEEP_PROVIDERS = ("fitbit",)',
        'if provider_name == "fitbit_stub"',
        'if provider_name == "fitbit"',
    ):
        require(factory, needle, "sleep provider classification")

    api = read("backend/app/api/fitbit.py")
    for needle in (
        '@router.get("/status", response_model=FitbitStatusResponse)',
        '@router.get("/connect", response_model=FitbitConnectResponse)',
        '@router.get("/callback", response_model=FitbitCallbackResponse)',
    ):
        require(api, needle, "legacy Fitbit route compatibility")

    models = read("backend/app/models/fitbit.py")
    for needle in (
        "class FitbitStatusResponse(BaseModel):",
        "connected: bool",
        "provider: str",
        "message: str",
        "class FitbitConnectResponse(BaseModel):",
        "ready: bool",
        "connect_url: str | None = None",
    ):
        require(models, needle, "legacy response-model compatibility")

    service = read("backend/app/services/fitbit_service.py")
    for needle in (
        "Fitbit appears to be connected using local development",
        "Real token validation is not implemented yet.",
        "Fitbit OAuth connect URL is ready. Open the URL to continue.",
    ):
        require(service, needle, "legacy backend limitation wording")

    status_model = read("app/lib/models/fitbit_status.dart")
    for needle in (
        "bool get isLegacyFitbitRoute => provider == 'fitbit';",
        "ウェアラブル連携（互換経路）",
        "ローカルトークン検出",
        "受け入れ確認は未完了です。",
    ):
        require(status_model, needle, "conservative Flutter status wording")
    reject(
        status_model,
        "case 'fitbit':\n        return 'ウェアラブル連携';",
        "unqualified legacy provider wording",
    )

    connect_model = read("app/lib/models/fitbit_connect_response.dart")
    for needle in (
        "互換用ウェアラブル認証URLを準備しました。",
        "確認完了を意味しません。",
    ):
        require(connect_model, needle, "conservative Flutter connect wording")

    backend_tests = read("backend/tests/test_fitbit_current_state_contract.py")
    for needle in (
        "test_provider_inventory_keeps_recommended_stub_and_legacy_roles_explicit",
        "test_fitbit_stub_is_deterministic_compatibility_data_not_real_data",
        "test_legacy_fitbit_provider_returns_safe_unavailable_summary",
        "test_local_token_presence_does_not_claim_real_validation",
        "test_connect_ready_only_means_authorization_url_was_prepared",
    ):
        require(backend_tests, needle, "M-7 backend regression coverage")
    for forbidden in (
        "requests.get(",
        "requests.post(",
        "httpx.",
        "backend/local_data",
        "time.sleep(",
        "FITBIT_CLIENT_SECRET",
    ):
        reject(backend_tests, forbidden, "non-mock-safe backend test dependency")

    flutter_tests = read("app/test/fitbit_current_state_contract_test.dart")
    for needle in (
        "legacy token presence is not displayed as verified connection",
        "legacy configured state without token remains unverified",
        "verified non-legacy providers keep the existing connected wording",
        "prepared legacy authorization URL is not shown as connection success",
    ):
        require(flutter_tests, needle, "M-7 Flutter regression coverage")

    documentation = read("docs/v20x_fitbit_current_state_contract.md")
    for needle in (
        "Status: COMPLETED / ACCEPTED",
        "Fitbit source boundaries present: yes",
        "Configured real Fitbit operator acceptance: no",
        "Fitbit real-use completion: deferred to v2.1.0",
        "M-7 was accepted on 2026-07-23",
    ):
        require(documentation, needle, "M-7 documentation")

    require(
        read("docs/fitbit_integration_plan.md"),
        "The active Fitbit status contract is `docs/v20x_fitbit_current_state_contract.md`",
        "historical Fitbit plan handoff",
    )
    require(
        read("docs/legacy_fitbit_cleanup_plan.md"),
        "M-7 clarified and accepted their current maintenance state",
        "legacy cleanup plan handoff",
    )

    checklist = read("docs/DRC_v20x_maintenance_checklist.md")
    require(
        checklist,
        "Current small commit: none (M-9 accepted; v2.0.1 released)",
        "M-7 checklist accepted state",
    )
    m6 = checklist.split("# M-6", 1)[1].split("# Planned queue", 1)[0]
    require(m6, "Status: COMPLETED / ACCEPTED", "M-6 accepted state")
    m7 = checklist.split("## M-7", 1)[1].split("## M-8", 1)[0]
    require(m7, "Status: COMPLETED / ACCEPTED", "M-7 accepted state")
    require(m7, "M-7 was accepted on 2026-07-23", "M-7 acceptance record")
    m8 = checklist.split("## M-8", 1)[1].split("\n## M-9 — Patch release", 1)[0]
    require(m8, "Status: COMPLETED / ACCEPTED", "M-8 accepted state")
    require(m8, "M-8 was accepted on 2026-07-23", "M-8 acceptance record")
    m9 = checklist.split("\n## M-9 — Patch release", 1)[1].split("# Future-version boundary", 1)[0]
    require(m9, "Status: COMPLETED / ACCEPTED", "M-9 accepted state")

    assert_historical_hashes()
    run_check("scripts/check_v20x_web_cors_origins.py")
    run_check("scripts/check_legacy_fitbit_boundary.py")
    run_m7_pytest()

    if snapshot_local_data() != local_data_before:
        raise AssertionError("Normal M-7 checks must not create or modify backend/local_data")

    print("v20x_fitbit_current_state_status: m7-completed-accepted")
    print("v20x_fitbit_current_state_mock_safe: True")
    print("v20x_fitbit_current_state_legacy_routes_preserved: True")
    print("v20x_fitbit_current_state_real_operator_acceptance: False")
    print("v20x_fitbit_current_state_v210_handoff: True")
    print("v20x_fitbit_current_state_release_created: False")
    print("[v20x-fitbit-current-state-contract-check] OK")


if __name__ == "__main__":
    main()
