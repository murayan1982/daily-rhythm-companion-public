"""Verify the accepted M-6 configurable Web CORS origin boundary."""

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
        entries.append((path.relative_to(local_data).as_posix(), stat.st_size, stat.st_mtime_ns))
    return tuple(entries)


def assert_historical_hashes() -> None:
    for relative, expected in HISTORICAL_HASHES.items():
        normalized = (ROOT / relative).read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
        actual = sha256(normalized).hexdigest()
        if actual != expected:
            raise AssertionError(f"Historical release record changed: {relative}: {actual} != {expected}")


def run_check(relative: str) -> None:
    subprocess.run([sys.executable, str(ROOT / relative)], cwd=ROOT, check=True)


def run_m6_pytest() -> None:
    subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "backend/tests/test_web_cors_config.py"],
        cwd=ROOT,
        check=True,
    )


def main() -> None:
    local_data_before = snapshot_local_data()

    config = read("backend/app/config.py")
    for needle in (
        'WEB_CORS_DEFAULT_ORIGINS = ("*",)',
        "web_cors_origins: tuple[str, ...] = WEB_CORS_DEFAULT_ORIGINS",
        '_env_csv_tuple("WEB_CORS_ORIGINS", WEB_CORS_DEFAULT_ORIGINS)',
        "or WEB_CORS_DEFAULT_ORIGINS",
    ):
        require(config, needle, "Web CORS configuration")

    main_source = read("backend/app/main.py")
    for needle in (
        "from app.config import load_config",
        "config = load_config()",
        "allow_origins=list(config.web_cors_origins)",
        "allow_credentials=False",
        'allow_methods=["*"]',
        'allow_headers=["*"]',
    ):
        require(main_source, needle, "FastAPI CORS binding")
    reject(main_source, 'allow_origins=["*"]', "hard-coded CORS origin list")

    for relative in ("backend/.env.example", "backend/env_profiles/mock_safe.env"):
        require(read(relative), "WEB_CORS_ORIGINS=*", f"{relative} local-demo default")

    tests = read("backend/tests/test_web_cors_config.py")
    for needle in (
        "test_web_cors_default_preserves_local_demo_wildcard",
        "test_web_cors_origins_can_be_explicitly_restricted",
        "test_web_cors_separator_only_value_uses_local_demo_default",
        "test_local_demo_wildcard_accepts_any_preflight_origin",
        "test_restricted_origins_allow_configured_and_reject_other_preflight",
        '"Access-Control-Request-Method": "GET"',
        'rejected.status_code == 400',
    ):
        require(tests, needle, "M-6 regression coverage")
    for forbidden in (
        "from app.main import",
        "backend/local_data",
        "requests.get(",
        "requests.post(",
        "time.sleep(",
        "OPENAI_API_KEY",
        "GEMINI_API_KEY",
    ):
        reject(tests, forbidden, "non-mock-safe test dependency")

    documentation = read("docs/v20x_web_cors_origins.md")
    for needle in (
        "Status: COMPLETED / ACCEPTED",
        "WEB_CORS_ORIGINS=*",
        "allow_credentials remains False",
        "do not import the full production `app.main`",
        "M-6 was accepted on 2026-07-23",
    ):
        require(documentation, needle, "M-6 documentation")

    checklist = read("docs/DRC_v20x_maintenance_checklist.md")
    require(checklist, "Current small commit: none (M-8 accepted; M-9 planned)", "M-6 checklist accepted state")
    m5 = checklist.split("# M-5", 1)[1].split("# M-6", 1)[0]
    require(m5, "Status: COMPLETED", "M-5 accepted state")
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
    require(m9, "Status: PLANNED", "M-9 planned state")

    assert_historical_hashes()
    run_check("scripts/check_v20x_temporary_lifecycle_limits.py")
    run_m6_pytest()

    if snapshot_local_data() != local_data_before:
        raise AssertionError("Normal M-6 checks must not create or modify backend/local_data")

    print("v20x_web_cors_origins_status: m6-completed-accepted")
    print("v20x_web_cors_origins_local_demo_default: wildcard")
    print("v20x_web_cors_origins_explicit_restrictions: True")
    print("v20x_web_cors_origins_credentials_allowed: False")
    print("v20x_web_cors_origins_credentials_required: False")
    print("v20x_web_cors_origins_release_created: False")
    print("[v20x-web-cors-origins-check] OK")


if __name__ == "__main__":
    main()
