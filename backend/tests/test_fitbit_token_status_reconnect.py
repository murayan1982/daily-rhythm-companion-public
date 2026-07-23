"""Mock-safe W-2 coverage for Fitbit token/status/reconnect behavior."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from app.config import AppConfig
from app.models.fitbit import FitbitConnectionState
from app.services.fitbit_http_client import FitbitHttpClientError, FitbitHttpResponse
from app.services.fitbit_oauth_state_store import FitbitOAuthStateStore
from app.services.fitbit_service import (
    build_fitbit_connect_response,
    get_fitbit_status,
    handle_fitbit_callback_stub,
)
from app.services.fitbit_token_exchange import (
    TOKEN_EXCHANGE_ERROR_HTTP_REQUEST_FAILED,
    refresh_fitbit_access_token,
)
from app.services.fitbit_token_store import FitbitTokenStore


FIXED_NOW = datetime(2026, 7, 23, 6, 0, tzinfo=timezone.utc)


def _config(**overrides: object) -> AppConfig:
    values: dict[str, object] = {
        "fitbit_client_id": "public-test-client",
        "fitbit_client_secret": "public-test-secret",
        "fitbit_redirect_uri": "http://127.0.0.1:8000/fitbit/callback",
    }
    values.update(overrides)
    return AppConfig(**values)


def _write_token_file(path: Path, **values: object) -> FitbitTokenStore:
    path.write_text(json.dumps(values), encoding="utf-8")
    return FitbitTokenStore(path, now_provider=lambda: FIXED_NOW)


def _response_text(response: object) -> str:
    if hasattr(response, "model_dump_json"):
        return response.model_dump_json()  # type: ignore[attr-defined]
    return response.json()  # type: ignore[attr-defined]


def test_unconfigured_status_is_explicit() -> None:
    status = get_fitbit_status(AppConfig())

    assert status.connected is False
    assert status.verified is False
    assert status.connection_state == FitbitConnectionState.UNCONFIGURED


def test_configured_without_token_is_authorization_ready(tmp_path: Path) -> None:
    store = FitbitTokenStore(tmp_path / "missing.json", now_provider=lambda: FIXED_NOW)

    status = get_fitbit_status(_config(), token_store=store)

    assert status.connected is False
    assert status.connection_state == FitbitConnectionState.AUTHORIZATION_READY
    assert status.verified is False


def test_future_access_and_refresh_tokens_are_present_but_unverified(tmp_path: Path) -> None:
    store = _write_token_file(
        tmp_path / "tokens.json",
        access_token="public-safe-access-value",
        refresh_token="public-safe-refresh-value",
        expires_at=(FIXED_NOW + timedelta(hours=1)).isoformat(),
        source="fitbit_oauth_token_exchange",
    )

    status = get_fitbit_status(_config(), token_store=store)

    assert status.connected is True  # backward-compatible legacy bool
    assert status.verified is False
    assert status.connection_state == FitbitConnectionState.TOKEN_PRESENT_UNVERIFIED
    assert "Real token validation is not implemented yet" in status.message


def test_near_expiry_token_requires_guarded_refresh(tmp_path: Path) -> None:
    store = _write_token_file(
        tmp_path / "tokens.json",
        access_token="public-safe-access-value",
        refresh_token="public-safe-refresh-value",
        expires_at=(FIXED_NOW + timedelta(minutes=4)).isoformat(),
    )

    status = get_fitbit_status(_config(), token_store=store)

    assert status.connected is True
    assert status.connection_state == FitbitConnectionState.REFRESH_REQUIRED
    assert "guarded refresh path" in status.message
    assert "not verified by status" in status.message


def test_missing_access_with_refresh_requires_refresh(tmp_path: Path) -> None:
    store = _write_token_file(
        tmp_path / "tokens.json",
        refresh_token="public-safe-refresh-value",
    )

    status = get_fitbit_status(_config(), token_store=store)

    assert status.connected is False
    assert status.connection_state == FitbitConnectionState.REFRESH_REQUIRED


def test_expired_access_without_refresh_requires_reconnect(tmp_path: Path) -> None:
    store = _write_token_file(
        tmp_path / "tokens.json",
        access_token="public-safe-access-value",
        expires_at=(FIXED_NOW - timedelta(minutes=1)).isoformat(),
    )

    status = get_fitbit_status(_config(), token_store=store)

    assert status.connected is False
    assert status.connection_state == FitbitConnectionState.RECONNECT_REQUIRED
    assert "Start the authorization flow again" in status.message


def test_malformed_token_file_is_error_not_connected(tmp_path: Path) -> None:
    token_file = tmp_path / "tokens.json"
    token_file.write_text("{not-json", encoding="utf-8")
    store = FitbitTokenStore(token_file, now_provider=lambda: FIXED_NOW)

    status = get_fitbit_status(_config(), token_store=store)

    assert status.connected is False
    assert status.connection_state == FitbitConnectionState.ERROR
    assert status.verified is False



def test_non_object_token_file_is_error_not_connected(tmp_path: Path) -> None:
    token_file = tmp_path / "tokens.json"
    token_file.write_text("[]", encoding="utf-8")
    store = FitbitTokenStore(token_file, now_provider=lambda: FIXED_NOW)

    status = get_fitbit_status(_config(), token_store=store)

    assert status.connected is False
    assert status.connection_state == FitbitConnectionState.ERROR


def test_dummy_token_is_never_reported_as_real_connection(tmp_path: Path) -> None:
    store = FitbitTokenStore(
        tmp_path / "tokens.json",
        now_provider=lambda: FIXED_NOW,
    )
    store.save_dummy_tokens_for_development(
        authorization_code="public-safe-code",
        state="public-safe-state",
    )

    status = get_fitbit_status(_config(), token_store=store)

    assert status.connection_state == FitbitConnectionState.TOKEN_PRESENT_UNVERIFIED
    assert status.verified is False
    assert "dummy token" in status.message


def test_status_response_does_not_expose_token_values(tmp_path: Path) -> None:
    access_token = "fixture-access-token-value"
    refresh_token = "fixture-refresh-token-value"
    store = _write_token_file(
        tmp_path / "tokens.json",
        access_token=access_token,
        refresh_token=refresh_token,
        expires_at=(FIXED_NOW + timedelta(hours=1)).isoformat(),
    )

    response_text = _response_text(get_fitbit_status(_config(), token_store=store))

    assert access_token not in response_text
    assert refresh_token not in response_text


def test_oauth_state_is_consumed_once(tmp_path: Path) -> None:
    state_store = FitbitOAuthStateStore(
        tmp_path / "state.json",
        now_provider=lambda: FIXED_NOW,
    )
    state = state_store.create_and_save_state()

    first = state_store.consume_state(state, ttl_seconds=600)
    second = state_store.consume_state(state, ttl_seconds=600)

    assert first.matched is True
    assert first.expired is False
    assert first.consumed is True
    assert second.matched is False
    assert second.consumed is False
    assert state_store.state_file.exists() is False


def test_expired_oauth_state_is_removed_and_requires_reconnect(tmp_path: Path) -> None:
    state_file = tmp_path / "state.json"
    state_file.write_text(
        json.dumps(
            {
                "state": "expired-state",
                "created_at": (FIXED_NOW - timedelta(minutes=20)).isoformat(),
            }
        ),
        encoding="utf-8",
    )
    state_store = FitbitOAuthStateStore(
        state_file,
        now_provider=lambda: FIXED_NOW,
    )

    result = state_store.consume_state("expired-state", ttl_seconds=600)

    assert result.matched is True
    assert result.expired is True
    assert result.consumed is False
    assert state_file.exists() is False


def test_permission_denial_is_classified_and_state_is_consumed(tmp_path: Path) -> None:
    state_store = FitbitOAuthStateStore(
        tmp_path / "state.json",
        now_provider=lambda: FIXED_NOW,
    )
    state = state_store.create_and_save_state()

    response = handle_fitbit_callback_stub(
        _config(),
        state=state,
        error="access_denied",
        error_description="public-safe denial",
        state_store=state_store,
    )

    assert response.connection_state == FitbitConnectionState.PERMISSION_BLOCKED
    assert response.state_valid is True
    assert response.verified is False
    assert state_store.state_file.exists() is False


def test_invalid_callback_state_requires_reconnect_without_consuming_saved_state(
    tmp_path: Path,
) -> None:
    state_store = FitbitOAuthStateStore(
        tmp_path / "state.json",
        now_provider=lambda: FIXED_NOW,
    )
    state_store.create_and_save_state()

    response = handle_fitbit_callback_stub(
        _config(),
        code="public-safe-code",
        state="wrong-state",
        state_store=state_store,
    )

    assert response.connection_state == FitbitConnectionState.RECONNECT_REQUIRED
    assert response.error == "invalid_state"
    assert state_store.state_file.exists() is True



def test_expired_callback_state_returns_reconnect_and_is_removed(tmp_path: Path) -> None:
    state_file = tmp_path / "state.json"
    state_file.write_text(
        json.dumps(
            {
                "state": "expired-callback-state",
                "created_at": (FIXED_NOW - timedelta(minutes=20)).isoformat(),
            }
        ),
        encoding="utf-8",
    )
    state_store = FitbitOAuthStateStore(
        state_file,
        now_provider=lambda: FIXED_NOW,
    )

    response = handle_fitbit_callback_stub(
        _config(),
        code="public-safe-code",
        state="expired-callback-state",
        state_store=state_store,
    )

    assert response.connection_state == FitbitConnectionState.RECONNECT_REQUIRED
    assert response.state_expired is True
    assert response.error == "invalid_state_expired"
    assert state_file.exists() is False


def test_callback_state_replay_is_rejected_after_first_use(tmp_path: Path) -> None:
    state_store = FitbitOAuthStateStore(
        tmp_path / "state.json",
        now_provider=lambda: FIXED_NOW,
    )
    state = state_store.create_and_save_state()

    first = handle_fitbit_callback_stub(
        _config(),
        code="public-safe-code",
        state=state,
        state_store=state_store,
    )
    second = handle_fitbit_callback_stub(
        _config(),
        code="public-safe-code",
        state=state,
        state_store=state_store,
    )

    assert first.state_valid is True
    assert first.connection_state == FitbitConnectionState.RECONNECT_REQUIRED
    assert second.state_valid is False
    assert second.error == "invalid_state"
    assert second.connection_state == FitbitConnectionState.RECONNECT_REQUIRED


def test_connect_response_marks_authorization_ready(tmp_path: Path) -> None:
    state_store = FitbitOAuthStateStore(
        tmp_path / "state.json",
        now_provider=lambda: FIXED_NOW,
    )

    response = build_fitbit_connect_response(_config(), state_store=state_store)

    assert response.ready is True
    assert response.connection_state == FitbitConnectionState.AUTHORIZATION_READY
    assert response.verified is False
    assert response.connect_url is not None


def test_fake_refresh_success_saves_tokens_without_exposing_values(tmp_path: Path) -> None:
    store = FitbitTokenStore(
        tmp_path / "tokens.json",
        now_provider=lambda: FIXED_NOW,
    )
    captured: dict[str, object] = {}

    def fake_post(**kwargs: object) -> FitbitHttpResponse:
        captured.update(kwargs)
        return FitbitHttpResponse(
            status_code=200,
            data={
                "access_token": "new-fixture-access-value",
                "refresh_token": "new-fixture-refresh-value",
                "token_type": "Bearer",
                "expires_in": 3600,
                "scope": "sleep",
                "user_id": "public-safe-user",
            },
        )

    result = refresh_fitbit_access_token(
        _config(fitbit_enable_real_token_exchange=True),
        "old-fixture-refresh-value",
        token_store=store,
        http_post=fake_post,
    )

    assert result.saved is True
    assert result.error is None
    assert result.request_preview is not None
    assert result.request_preview.has_refresh_token is True
    assert "old-fixture-refresh-value" not in str(result)
    assert "new-fixture-access-value" not in str(result)
    assert captured["endpoint"] == "https://api.fitbit.com/oauth2/token"
    assert store.get_status().has_access_token is True


def test_fake_refresh_failure_is_safe_and_does_not_save(tmp_path: Path) -> None:
    store = FitbitTokenStore(
        tmp_path / "tokens.json",
        now_provider=lambda: FIXED_NOW,
    )

    def failing_post(**_: object) -> FitbitHttpResponse:
        raise FitbitHttpClientError("public-safe-http-failure", status_code=401)

    result = refresh_fitbit_access_token(
        _config(fitbit_enable_real_token_exchange=True),
        "fixture-refresh-value",
        token_store=store,
        http_post=failing_post,
    )

    assert result.saved is False
    assert result.error == TOKEN_EXCHANGE_ERROR_HTTP_REQUEST_FAILED
    assert "fixture-refresh-value" not in str(result)
    assert store.token_file.exists() is False
