"""Mock-safe regression coverage for configurable Web CORS origins."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient
from httpx import Response

from app.config import AppConfig, load_config


def _cors_client(config: AppConfig) -> TestClient:
    test_app = FastAPI()
    test_app.add_middleware(
        CORSMiddleware,
        allow_origins=list(config.web_cors_origins),
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @test_app.get("/probe")
    def probe() -> dict[str, str]:
        return {"status": "ok"}

    return TestClient(test_app)


def _preflight(client: TestClient, origin: str) -> Response:
    return client.options(
        "/probe",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "GET",
        },
    )


def test_web_cors_default_preserves_local_demo_wildcard(monkeypatch) -> None:
    monkeypatch.delenv("WEB_CORS_ORIGINS", raising=False)

    config = load_config()

    assert config.web_cors_origins == ("*",)


def test_web_cors_origins_can_be_explicitly_restricted(monkeypatch) -> None:
    monkeypatch.setenv(
        "WEB_CORS_ORIGINS",
        "http://localhost:3000, http://127.0.0.1:8080",
    )

    config = load_config()

    assert config.web_cors_origins == (
        "http://localhost:3000",
        "http://127.0.0.1:8080",
    )


def test_web_cors_separator_only_value_uses_local_demo_default(monkeypatch) -> None:
    monkeypatch.setenv("WEB_CORS_ORIGINS", ", ,")

    config = load_config()

    assert config.web_cors_origins == ("*",)


def test_local_demo_wildcard_accepts_any_preflight_origin() -> None:
    with _cors_client(AppConfig()) as client:
        response = _preflight(client, "http://demo-device.local:7357")

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "*"


def test_restricted_origins_allow_configured_and_reject_other_preflight() -> None:
    config = AppConfig(
        web_cors_origins=(
            "http://localhost:3000",
            "http://127.0.0.1:8080",
        )
    )

    with _cors_client(config) as client:
        allowed = _preflight(client, "http://localhost:3000")
        rejected = _preflight(client, "https://untrusted.example")

    assert allowed.status_code == 200
    assert allowed.headers["access-control-allow-origin"] == "http://localhost:3000"
    assert rejected.status_code == 400
    assert "access-control-allow-origin" not in rejected.headers
