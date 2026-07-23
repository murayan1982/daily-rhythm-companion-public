"""Mock-safe regression coverage for the v2.0.x Fitbit current-state contract."""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import parse_qs, urlparse

import pytest

from app.config import AppConfig
from app.services import fitbit_service
from app.services.fitbit_token_store import FitbitTokenStatus
from app.services.sleep_providers.factory import (
    DEPRECATED_SLEEP_PROVIDER_ALIASES,
    LEGACY_SLEEP_PROVIDERS,
    RECOMMENDED_SLEEP_PROVIDERS,
    create_sleep_provider,
)
from app.services.fitbit_sleep_service import (
    FITBIT_SLEEP_ERROR_NO_TOKEN,
    FitbitSleepApiResult,
)
from app.services.sleep_providers import fitbit as fitbit_provider_module
from app.services.sleep_providers.fitbit import FitbitSleepProvider
from app.services.sleep_providers.fitbit_stub import FitbitStubSleepProvider
from app.services.sleep_providers.wearable_stub import WearableStubSleepProvider


@dataclass
class _FakeTokenStore:
    status: FitbitTokenStatus

    def get_status(self) -> FitbitTokenStatus:
        return self.status


class _FakeStateStore:
    def create_and_save_state(self) -> str:
        return "mock-safe-state"


def _patch_token_status(
    monkeypatch: pytest.MonkeyPatch,
    *,
    exists: bool,
    access: bool,
    refresh: bool,
) -> None:
    fake_store = _FakeTokenStore(
        FitbitTokenStatus(
            exists=exists,
            has_access_token=access,
            has_refresh_token=refresh,
        )
    )
    monkeypatch.setattr(fitbit_service, "FitbitTokenStore", lambda: fake_store)


def test_provider_inventory_keeps_recommended_stub_and_legacy_roles_explicit() -> None:
    assert RECOMMENDED_SLEEP_PROVIDERS == (
        "mock",
        "wearable_stub",
        "google_health",
    )
    assert DEPRECATED_SLEEP_PROVIDER_ALIASES == {"fitbit_stub": "wearable_stub"}
    assert LEGACY_SLEEP_PROVIDERS == ("fitbit",)

    assert isinstance(
        create_sleep_provider(AppConfig(sleep_provider="wearable_stub")),
        WearableStubSleepProvider,
    )
    assert isinstance(
        create_sleep_provider(AppConfig(sleep_provider="fitbit_stub")),
        FitbitStubSleepProvider,
    )
    assert isinstance(
        create_sleep_provider(AppConfig(sleep_provider="fitbit")),
        FitbitSleepProvider,
    )


def test_fitbit_stub_is_deterministic_compatibility_data_not_real_data() -> None:
    summary = FitbitStubSleepProvider().get_sleep_summary()

    assert summary.available is True
    assert summary.source == "fitbit_stub"
    assert "Deprecated sleep provider alias" in (summary.message or "")
    assert "wearable_stub" in (summary.message or "")


def test_legacy_fitbit_provider_returns_safe_unavailable_summary(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        fitbit_provider_module,
        "fetch_fitbit_sleep_for_date",
        lambda target_date: FitbitSleepApiResult(
            attempted=False,
            success=False,
            date=target_date.isoformat(),
            error=FITBIT_SLEEP_ERROR_NO_TOKEN,
            message="mock-safe no-token state",
        ),
    )

    summary = FitbitSleepProvider().get_sleep_summary()

    assert summary.available is False
    assert summary.source == "fitbit"
    assert summary.total_sleep_minutes == 0
    assert "まだ連携されていません" in (summary.message or "")


def test_status_without_legacy_configuration_is_unavailable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_token_status(
        monkeypatch,
        exists=False,
        access=False,
        refresh=False,
    )

    status = fitbit_service.get_fitbit_status(AppConfig())

    assert status.connected is False
    assert status.provider == "fitbit"
    assert status.message == "Fitbit integration is not configured yet."


def test_configured_credentials_without_tokens_are_not_connected(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_token_status(
        monkeypatch,
        exists=False,
        access=False,
        refresh=False,
    )
    config = AppConfig(
        fitbit_client_id="public-test-client",
        fitbit_client_secret="public-test-secret",
        fitbit_redirect_uri="http://127.0.0.1:8000/fitbit/callback",
    )

    status = fitbit_service.get_fitbit_status(config)

    assert status.connected is False
    assert "credentials are configured" in status.message
    assert "token data is not available" in status.message


def test_local_token_presence_does_not_claim_real_validation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_token_status(
        monkeypatch,
        exists=True,
        access=True,
        refresh=True,
    )
    config = AppConfig(
        fitbit_client_id="public-test-client",
        fitbit_client_secret="public-test-secret",
        fitbit_redirect_uri="http://127.0.0.1:8000/fitbit/callback",
    )

    status = fitbit_service.get_fitbit_status(config)

    # Backward compatibility preserves connected=True for the legacy route,
    # but the message must keep the real-validation limitation explicit.
    assert status.connected is True
    assert "appears to be connected" in status.message
    assert "Real token validation is not implemented yet" in status.message


def test_connect_ready_only_means_authorization_url_was_prepared(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(fitbit_service, "FitbitOAuthStateStore", _FakeStateStore)
    config = AppConfig(
        fitbit_client_id="public-test-client",
        fitbit_redirect_uri="http://127.0.0.1:8000/fitbit/callback",
    )

    response = fitbit_service.build_fitbit_connect_response(config)

    assert response.ready is True
    assert response.connect_url is not None
    assert response.message == (
        "Fitbit OAuth connect URL is ready. Open the URL to continue."
    )

    parsed = urlparse(response.connect_url)
    query = parse_qs(parsed.query)
    assert parsed.scheme == "https"
    assert parsed.netloc == "www.fitbit.com"
    assert query["client_id"] == ["public-test-client"]
    assert query["scope"] == ["sleep"]
    assert query["state"] == ["mock-safe-state"]
