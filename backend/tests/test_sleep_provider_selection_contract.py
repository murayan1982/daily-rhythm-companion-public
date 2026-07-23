"""Mock-safe W-4a coverage for backend-owned sleep-provider selection metadata."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from app.api import sleep_provider_selection
from app.config import AppConfig
from app.services.sleep_provider_selection_service import (
    get_sleep_provider_selection_status,
)


@pytest.mark.parametrize(
    ("provider", "label", "role", "requires_real_operator"),
    [
        ("mock", "サンプルデータ", "credential_free_default", False),
        (
            "wearable_stub",
            "ウェアラブル連携サンプル",
            "deterministic_sample",
            False,
        ),
        (
            "google_health",
            "Google Health",
            "configured_real_provider",
            False,
        ),
        (
            "fitbit_stub",
            "ウェアラブル連携サンプル（旧設定）",
            "deprecated_alias",
            False,
        ),
        (
            "fitbit",
            "Fitbit（旧Web API・移行参照）",
            "legacy_migration_reference",
            False,
        ),
    ],
)
def test_selection_status_classifies_supported_providers(
    provider: str,
    label: str,
    role: str,
    requires_real_operator: bool,
) -> None:
    status = get_sleep_provider_selection_status(
        AppConfig(sleep_provider=f"  {provider.upper()}  ")
    )

    assert status.configured_provider == provider
    assert status.configured_provider_label == label
    assert status.configured_provider_role == role
    assert status.configured_provider_supported is True
    assert status.selection_mode == "backend_config"
    assert status.change_requires_backend_restart is True

    selected = next(
        item for item in status.provider_options if item.provider == provider
    )
    assert selected.real_operator_verification_required is requires_real_operator


def test_selection_status_marks_fitbit_stub_as_deprecated_alias() -> None:
    status = get_sleep_provider_selection_status(AppConfig(sleep_provider="fitbit_stub"))
    fitbit_stub = next(
        item for item in status.provider_options if item.provider == "fitbit_stub"
    )

    assert fitbit_stub.deprecated is True
    assert fitbit_stub.alias_for == "wearable_stub"


def test_selection_status_handles_unknown_provider_conservatively() -> None:
    status = get_sleep_provider_selection_status(
        AppConfig(sleep_provider="private-experimental-provider")
    )

    assert status.configured_provider == "private-experimental-provider"
    assert status.configured_provider_label == "未対応のsleep provider設定"
    assert status.configured_provider_role == "unsupported"
    assert status.configured_provider_supported is False
    assert all(
        option.provider != "private-experimental-provider"
        for option in status.provider_options
    )


def test_sleep_provider_selection_endpoint_is_read_only_and_deterministic(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        sleep_provider_selection,
        "load_config",
        lambda: AppConfig(sleep_provider="fitbit"),
    )
    test_app = FastAPI()
    test_app.include_router(sleep_provider_selection.router)

    with TestClient(test_app) as client:
        response = client.get("/sleep/providers")

    assert response.status_code == 200
    payload = response.json()
    assert payload["configured_provider"] == "fitbit"
    assert payload["configured_provider_supported"] is True
    assert payload["configured_provider_role"] == "legacy_migration_reference"
    assert payload["selection_mode"] == "backend_config"
    assert payload["change_requires_backend_restart"] is True
    assert [item["provider"] for item in payload["provider_options"]] == [
        "mock",
        "wearable_stub",
        "google_health",
        "fitbit_stub",
        "fitbit",
    ]
    assert payload["provider_options"][-1][
        "real_operator_verification_required"
    ] is False
    assert "SLEEP_PROVIDER" in payload["message"]
