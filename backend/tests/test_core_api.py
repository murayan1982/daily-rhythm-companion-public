"""Credential-free API regression coverage for core public endpoints."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api import characters, health, sleep
from app.config import AppConfig
from app.version import APP_VERSION


def _core_client(monkeypatch) -> TestClient:
    monkeypatch.setattr(
        sleep,
        "load_config",
        lambda: AppConfig(sleep_provider="mock"),
    )
    test_app = FastAPI()
    test_app.include_router(health.router)
    test_app.include_router(characters.router)
    test_app.include_router(sleep.router)
    return TestClient(test_app)


def test_health_endpoint_reports_current_version(monkeypatch) -> None:
    with _core_client(monkeypatch) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": APP_VERSION}


def test_characters_endpoint_returns_stable_presets(monkeypatch) -> None:
    with _core_client(monkeypatch) as client:
        response = client.get("/characters")

    assert response.status_code == 200
    payload = response.json()
    assert [item["character_id"] for item in payload] == [
        "gentle_mina",
        "cheerful_sora",
        "cool_rei",
    ]
    assert [item["display_name"] for item in payload] == ["ミナ", "ソラ", "レイ"]


def test_sleep_summary_endpoint_uses_deterministic_mock_provider(monkeypatch) -> None:
    with _core_client(monkeypatch) as client:
        response = client.get("/sleep/summary")

    assert response.status_code == 200
    payload = response.json()
    assert payload["source"] == "mock"
    assert payload["available"] is True
    assert payload["date"] == "2026-04-28"
    assert payload["total_sleep_minutes"] == 372
    assert payload["is_real_data"] is False
