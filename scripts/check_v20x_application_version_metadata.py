"""Verify M-2 application version metadata alignment.

This credential-free check imports only the local health/version boundary, reads
source metadata, and validates Flutter/Web source contracts. It does not call
external services, create release artifacts, or modify the repository.
"""

from __future__ import annotations

from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = ROOT / "backend"
EXPECTED_VERSION = "2.0.1"
EXPECTED_FLUTTER_VERSION = "2.0.1+2"


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


def run_baseline_check() -> None:
    subprocess.run(
        [sys.executable, str(ROOT / "scripts/check_v20x_maintenance_baseline.py")],
        cwd=ROOT,
        check=True,
    )


def main() -> None:
    if not re.fullmatch(r"\d+\.\d+\.\d+", EXPECTED_VERSION):
        raise AssertionError(f"Invalid expected semantic version: {EXPECTED_VERSION}")

    sys.path.insert(0, str(BACKEND_ROOT))
    from app.api.health import health  # noqa: PLC0415
    from app.version import APP_VERSION  # noqa: PLC0415

    if APP_VERSION != EXPECTED_VERSION:
        raise AssertionError(f"APP_VERSION mismatch: {APP_VERSION}")

    health_payload = health()
    if health_payload != {"status": "ok", "version": APP_VERSION}:
        raise AssertionError(f"Unexpected /health payload: {health_payload!r}")

    version_source = read("backend/app/version.py")
    require(version_source, 'APP_VERSION = "2.0.1"', "backend version constant")
    if len(re.findall(r"^APP_VERSION\s*=", version_source, flags=re.MULTILINE)) != 1:
        raise AssertionError("backend/app/version.py must define APP_VERSION exactly once")

    main_source = read("backend/app/main.py")
    require(main_source, "from app.version import APP_VERSION", "FastAPI version import")
    require(main_source, "version=APP_VERSION", "FastAPI version binding")
    reject(main_source, 'version="0.15.0"', "legacy FastAPI version")

    health_source = read("backend/app/api/health.py")
    require(health_source, 'return {"status": "ok", "version": APP_VERSION}', "health version response")

    pubspec = read("app/pubspec.yaml")
    match = re.search(r"^version:\s*([^\s]+)\s*$", pubspec, flags=re.MULTILINE)
    if not match:
        raise AssertionError("Missing Flutter pubspec version")
    flutter_version = match.group(1)
    if flutter_version != EXPECTED_FLUTTER_VERSION:
        raise AssertionError(f"Flutter version mismatch: {flutter_version}")
    flutter_semantic_version, build_number = flutter_version.split("+", 1)
    if flutter_semantic_version != APP_VERSION:
        raise AssertionError(
            f"Flutter/backend semantic version mismatch: {flutter_semantic_version} != {APP_VERSION}"
        )
    if build_number != "2":
        raise AssertionError(f"Unexpected Flutter build number: {build_number}")

    client = read("app/lib/services/backend_api_client.dart")
    for needle in (
        "static String formatHealthStatus",
        "final version = body['version']?.toString().trim() ?? '';",
        "return '$status / API v$version';",
        "return formatHealthStatus(body);",
    ):
        require(client, needle, "Flutter health version formatting")

    widget_test = read("app/test/widget_test.dart")
    for needle in (
        "BackendApiClient formats versioned and legacy health payloads",
        "ok / API v2.0.1",
        "Backend status: ok / API v2.0.1",
    ):
        require(widget_test, needle, "Flutter version regression test")

    for relative in ("app/web/index.html", "app/web/manifest.json"):
        web_source = read(relative)
        require(web_source, "Daily Rhythm Companion", f"{relative} product identity")
        for forbidden in ("2.0.1", "2.0.0+1", "0.15.0"):
            reject(web_source, forbidden, f"{relative} duplicate version")

    inventory = read("docs/v20x_application_version_metadata.md")
    for needle in (
        "Backend/API semantic version: backend/app/version.py",
        "Flutter package version/build: app/pubspec.yaml",
        "Backend/API: 2.0.1",
        "Flutter package: 2.0.1+2",
        "M-2 does not create a tag, fixed ZIP, or GitHub Release",
    ):
        require(inventory, needle, "M-2 version inventory")

    checklist = read("docs/DRC_v20x_maintenance_checklist.md")
    require(checklist, "Current small commit: none (M-8 accepted; M-9 planned)", "active checklist current state")
    m2 = checklist.split("# M-2", 1)[1].split("# M-3", 1)[0]
    require(m2, "Status: COMPLETED", "M-2 completed state")
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
    require(m9, "Status: PLANNED", "M-9 planned state")

    run_baseline_check()

    print("v20x_application_version_metadata_status: m2-completed")
    print(f"v20x_application_version_metadata_backend_version: {APP_VERSION}")
    print(f"v20x_application_version_metadata_flutter_version: {flutter_version}")
    print("v20x_application_version_metadata_health_runtime_surface: True")
    print("v20x_application_version_metadata_flutter_legacy_fallback: True")
    print("v20x_application_version_metadata_web_duplicate_constant: False")
    print("v20x_application_version_metadata_release_created: False")
    print("[v20x-application-version-metadata-check] OK")


if __name__ == "__main__":
    main()
