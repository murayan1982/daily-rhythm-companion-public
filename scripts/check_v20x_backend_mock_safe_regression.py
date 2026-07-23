"""Verify M-3 backend mock-safe regression foundation.

This check validates the credential-free test layout and runs the focused backend
pytest suite. It does not call external services, use real credentials, build
release artifacts, or modify the repository.
"""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


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


def run_check(relative: str) -> None:
    subprocess.run([sys.executable, str(ROOT / relative)], cwd=ROOT, check=True)


def run_pytest() -> None:
    subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "backend/tests/test_core_api.py",
            "backend/tests/test_mock_advice.py",
            "backend/tests/test_daily_record_store.py",
        ],
        cwd=ROOT,
        check=True,
    )


def main() -> None:
    requirements = read("backend/requirements-dev.txt")
    require(requirements, "-r requirements.txt", "production requirements include")
    require(requirements, "pytest>=8,<10", "bounded pytest dependency")
    reject(read("backend/requirements.txt"), "pytest", "pytest production dependency")

    tests = {
        "backend/tests/conftest.py": read("backend/tests/conftest.py"),
        "backend/tests/test_core_api.py": read("backend/tests/test_core_api.py"),
        "backend/tests/test_mock_advice.py": read("backend/tests/test_mock_advice.py"),
        "backend/tests/test_daily_record_store.py": read("backend/tests/test_daily_record_store.py"),
    }

    conftest = tests["backend/tests/conftest.py"]
    for needle in (
        'os.environ["DRC_SKIP_BACKEND_DOTENV"] = "1"',
        'os.environ["CONVERSATION_ENGINE"] = "mock"',
        'os.environ["SLEEP_PROVIDER"] = "mock"',
        'monkeypatch.delenv(key, raising=False)',
    ):
        require(conftest, needle, "mock-safe fixture")

    core_api = tests["backend/tests/test_core_api.py"]
    for needle in (
        'client.get("/health")',
        'client.get("/characters")',
        'client.get("/sleep/summary")',
        'lambda: AppConfig(sleep_provider="mock")',
        '"gentle_mina"',
        '"cheerful_sora"',
        '"cool_rei"',
    ):
        require(core_api, needle, "core API regression")

    advice = tests["backend/tests/test_mock_advice.py"]
    for needle in (
        "MockConversationEngine().create_advice(request)",
        'response.source.engine == "mock"',
        '"0時間0分" not in response.message',
    ):
        require(advice, needle, "mock advice regression")

    daily_record = tests["backend/tests/test_daily_record_store.py"]
    require(daily_record, 'DailyRecordStore(tmp_path / "daily_records.sqlite3")', "temporary DailyRecord database")
    require(daily_record, "store.upsert", "DailyRecord upsert coverage")
    require(daily_record, "store.get", "DailyRecord read coverage")

    combined = "\n".join(tests.values())
    for forbidden in (
        "from app.main import app",
        "backend/local_data",
        "requests.get(",
        "requests.post(",
        "http://",
        "https://",
    ):
        reject(combined, forbidden, "external or production-app test dependency")

    documentation = read("docs/v20x_backend_mock_safe_regression.md")
    for needle in (
        "backend/requirements-dev.txt",
        "backend/tests/**",
        "Framework success/fallback regression: M-4",
        "DailyRecord tests use pytest tmp_path",
        "M-3 does not create a fixed ZIP, tag, GitHub Release, or v2.0.1 release",
    ):
        require(documentation, needle, "M-3 documentation")

    checklist = read("docs/DRC_v20x_maintenance_checklist.md")
    require(checklist, "Current small commit: M-9 (patch release preparation)", "active checklist current state")
    m3 = checklist.split("# M-3", 1)[1].split("# M-4", 1)[0]
    require(m3, "Status: COMPLETED", "M-3 completed state")
    m4 = checklist.split("# M-4", 1)[1].split("# M-5", 1)[0]
    require(m4, "Status: COMPLETED", "M-4 completed state")
    m5 = checklist.split("# M-5", 1)[1].split("# M-6", 1)[0]
    require(m5, "Status: COMPLETED", "M-5 completed state")
    m6 = checklist.split("# M-6", 1)[1].split("# Planned queue", 1)[0]
    require(m6, "Status: COMPLETED / ACCEPTED", "M-6 accepted state")
    require(m6, "M-6 was accepted on 2026-07-23", "M-6 acceptance record")
    m7 = checklist.split("## M-7", 1)[1].split("## M-8", 1)[0]
    require(m7, "Status: COMPLETED / ACCEPTED", "M-7 accepted state")
    require(m7, "M-7 was accepted on 2026-07-23", "M-7 acceptance record")
    m8 = checklist.split("## M-8", 1)[1].split("\n## M-9 — Patch release", 1)[0]
    require(m8, "Status: COMPLETED / ACCEPTED", "M-8 accepted state")
    require(m8, "M-8 was accepted on 2026-07-23", "M-8 acceptance record")
    m9 = checklist.split("\n## M-9 — Patch release", 1)[1].split("# Future-version boundary", 1)[0]
    require(m9, "Status: CURRENT / NOT_COMPLETED", "M-9 current state")

    run_check("scripts/check_v20x_application_version_metadata.py")
    run_pytest()

    print("v20x_backend_mock_safe_regression_status: m3-completed")
    print("v20x_backend_mock_safe_regression_test_modules: 3")
    print("v20x_backend_mock_safe_regression_credentials_required: False")
    print("v20x_backend_mock_safe_regression_real_execution: False")
    print("v20x_backend_mock_safe_regression_runtime_change: False")
    print("v20x_backend_mock_safe_regression_release_created: False")
    print("[v20x-backend-mock-safe-regression-check] OK")


if __name__ == "__main__":
    main()
