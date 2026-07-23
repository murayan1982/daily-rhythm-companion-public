"""Mock-safe W-3 coverage for Fitbit sleep API and normalization semantics."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

import httpx
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api import sleep
from app.config import AppConfig
from app.services import sleep_summary_service
from app.services.fitbit_api_client import (
    FITBIT_API_ERROR_INVALID_RESPONSE,
    FITBIT_API_ERROR_PERMISSION_DENIED,
    FITBIT_API_ERROR_REQUEST_FAILED,
    FITBIT_API_ERROR_PROVIDER_UNAVAILABLE,
    FITBIT_API_ERROR_RATE_LIMITED,
    FITBIT_API_ERROR_SCOPE_MISSING,
    FITBIT_API_ERROR_UNAUTHORIZED,
    FitbitApiClientError,
    get_fitbit_json,
)
from app.services.fitbit_http_client import FitbitHttpResponse
from app.services.fitbit_sleep_normalizer import (
    FITBIT_SLEEP_NORMALIZE_ERROR_INVALID_RESPONSE,
    FITBIT_SLEEP_NORMALIZE_ERROR_NO_SLEEP_DATA,
    normalize_fitbit_sleep_response,
)
from app.services.fitbit_sleep_service import (
    FITBIT_SLEEP_ERROR_INVALID_RESPONSE,
    FITBIT_SLEEP_ERROR_PERMISSION_DENIED,
    FITBIT_SLEEP_ERROR_PROVIDER_UNAVAILABLE,
    FITBIT_SLEEP_ERROR_RATE_LIMITED,
    FITBIT_SLEEP_ERROR_RECONNECT_REQUIRED,
    FITBIT_SLEEP_ERROR_SCOPE_MISSING,
    FitbitSleepApiResult,
    fetch_fitbit_sleep_for_date,
)
from app.services.fitbit_token_store import FitbitTokenStore
from app.services.sleep_providers.fitbit import FitbitSleepProvider


FIXED_DATE = date(2026, 7, 20)
PUBLIC_SAFE_ACCESS_TOKEN = "public-safe-fitbit-access"


@dataclass
class _FakeResponse:
    status_code: int
    payload: Any
    content: bytes = b"{}"

    def json(self) -> Any:
        return self.payload


def _write_future_token(path: Path) -> FitbitTokenStore:
    path.write_text(
        json.dumps(
            {
                "access_token": PUBLIC_SAFE_ACCESS_TOKEN,
                "refresh_token": "public-safe-fitbit-refresh",
                "expires_at": "2099-01-01T00:00:00+00:00",
                "scope": "sleep",
            }
        ),
        encoding="utf-8",
    )
    return FitbitTokenStore(path)


def _main_sleep_payload() -> dict[str, Any]:
    return {
        "sleep": [
            {
                "isMainSleep": False,
                "minutesAsleep": 40,
                "startTime": "2026-07-20T13:00:00.000",
                "endTime": "2026-07-20T13:40:00.000",
            },
            {
                "isMainSleep": True,
                "minutesAsleep": 425,
                "timeInBed": 470,
                "efficiency": 91,
                "startTime": "2026-07-19T23:10:00.000",
                "endTime": "2026-07-20T07:00:00.000",
            },
        ],
        "summary": {"totalMinutesAsleep": 465},
    }


def _api_result(
    *,
    success: bool,
    raw_data: dict[str, Any] | None = None,
    error: str | None = None,
) -> FitbitSleepApiResult:
    return FitbitSleepApiResult(
        attempted=True,
        success=success,
        date=FIXED_DATE.isoformat(),
        raw_data=raw_data,
        error=error,
        message="public-safe fixture result",
    )


def test_api_client_classifies_401_without_exposing_payload() -> None:
    private_marker = "private-provider-detail-must-not-escape"

    def fake_get(*args: object, **kwargs: object) -> _FakeResponse:
        return _FakeResponse(
            status_code=401,
            payload={"errors": [{"errorType": "expired_token", "message": private_marker}]},
        )

    with pytest.raises(FitbitApiClientError) as exc_info:
        get_fitbit_json(
            endpoint="https://example.invalid/sleep",
            access_token=PUBLIC_SAFE_ACCESS_TOKEN,
            http_get=fake_get,
        )

    assert exc_info.value.code == FITBIT_API_ERROR_UNAUTHORIZED
    assert exc_info.value.status_code == 401
    assert private_marker not in str(exc_info.value)
    assert PUBLIC_SAFE_ACCESS_TOKEN not in str(exc_info.value)


def test_api_client_classifies_network_and_invalid_success_response_safely() -> None:
    private_marker = "private-network-detail-must-not-escape"

    def network_get(*args: object, **kwargs: object) -> _FakeResponse:
        request = httpx.Request("GET", "https://example.invalid/sleep")
        raise httpx.ConnectError(private_marker, request=request)

    with pytest.raises(FitbitApiClientError) as network_error:
        get_fitbit_json(
            endpoint="https://example.invalid/sleep",
            access_token=PUBLIC_SAFE_ACCESS_TOKEN,
            http_get=network_get,
        )

    assert network_error.value.code == FITBIT_API_ERROR_REQUEST_FAILED
    assert private_marker not in str(network_error.value)

    class _InvalidJsonResponse(_FakeResponse):
        def json(self) -> Any:
            raise ValueError("private-invalid-json-detail")

    def invalid_json_get(*args: object, **kwargs: object) -> _FakeResponse:
        return _InvalidJsonResponse(status_code=200, payload=None)

    with pytest.raises(FitbitApiClientError) as invalid_error:
        get_fitbit_json(
            endpoint="https://example.invalid/sleep",
            access_token=PUBLIC_SAFE_ACCESS_TOKEN,
            http_get=invalid_json_get,
        )

    assert invalid_error.value.code == FITBIT_API_ERROR_INVALID_RESPONSE
    assert "private-invalid-json-detail" not in str(invalid_error.value)


def test_api_client_classifies_scope_and_permission_403() -> None:
    def scope_get(*args: object, **kwargs: object) -> _FakeResponse:
        return _FakeResponse(
            status_code=403,
            payload={"errors": [{"errorType": "insufficient_scope"}]},
        )

    with pytest.raises(FitbitApiClientError) as scope_error:
        get_fitbit_json(
            endpoint="https://example.invalid/sleep",
            access_token=PUBLIC_SAFE_ACCESS_TOKEN,
            http_get=scope_get,
        )
    assert scope_error.value.code == FITBIT_API_ERROR_SCOPE_MISSING

    def permission_get(*args: object, **kwargs: object) -> _FakeResponse:
        return _FakeResponse(
            status_code=403,
            payload={"errors": [{"errorType": "insufficient_permissions"}]},
        )

    with pytest.raises(FitbitApiClientError) as permission_error:
        get_fitbit_json(
            endpoint="https://example.invalid/sleep",
            access_token=PUBLIC_SAFE_ACCESS_TOKEN,
            http_get=permission_get,
        )
    assert permission_error.value.code == FITBIT_API_ERROR_PERMISSION_DENIED


@pytest.mark.parametrize(
    ("status_code", "expected_code"),
    [
        (429, FITBIT_API_ERROR_RATE_LIMITED),
        (503, FITBIT_API_ERROR_PROVIDER_UNAVAILABLE),
    ],
)
def test_api_client_classifies_rate_limit_and_provider_outage(
    status_code: int,
    expected_code: str,
) -> None:
    def fake_get(*args: object, **kwargs: object) -> _FakeResponse:
        return _FakeResponse(status_code=status_code, payload={"errors": []})

    with pytest.raises(FitbitApiClientError) as exc_info:
        get_fitbit_json(
            endpoint="https://example.invalid/sleep",
            access_token=PUBLIC_SAFE_ACCESS_TOKEN,
            http_get=fake_get,
        )

    assert exc_info.value.code == expected_code


@pytest.mark.parametrize(
    ("client_code", "expected_sleep_error"),
    [
        (FITBIT_API_ERROR_UNAUTHORIZED, FITBIT_SLEEP_ERROR_RECONNECT_REQUIRED),
        (FITBIT_API_ERROR_PERMISSION_DENIED, FITBIT_SLEEP_ERROR_PERMISSION_DENIED),
        (FITBIT_API_ERROR_SCOPE_MISSING, FITBIT_SLEEP_ERROR_SCOPE_MISSING),
        (FITBIT_API_ERROR_RATE_LIMITED, FITBIT_SLEEP_ERROR_RATE_LIMITED),
        (
            FITBIT_API_ERROR_PROVIDER_UNAVAILABLE,
            FITBIT_SLEEP_ERROR_PROVIDER_UNAVAILABLE,
        ),
    ],
)
def test_sleep_service_maps_safe_api_errors(
    tmp_path: Path,
    client_code: str,
    expected_sleep_error: str,
) -> None:
    store = _write_future_token(tmp_path / "tokens.json")

    def fake_api_get(**kwargs: object) -> FitbitHttpResponse:
        raise FitbitApiClientError(client_code, status_code=503)

    result = fetch_fitbit_sleep_for_date(
        FIXED_DATE,
        token_store=store,
        api_get=fake_api_get,
    )

    assert result.attempted is True
    assert result.success is False
    assert result.raw_data is None
    assert result.error == expected_sleep_error
    assert PUBLIC_SAFE_ACCESS_TOKEN not in (result.message or "")


def test_normalizer_prefers_main_sleep_and_maps_real_fields() -> None:
    result = normalize_fitbit_sleep_response(
        _main_sleep_payload(),
        target_date=FIXED_DATE.isoformat(),
    )

    assert result.success is True
    assert result.summary is not None
    assert result.summary.total_sleep_minutes == 425
    assert result.summary.time_in_bed_minutes == 470
    assert result.summary.efficiency == 91
    assert result.summary.main_sleep_start_time == "2026-07-19T23:10:00.000"
    assert result.summary.main_sleep_end_time == "2026-07-20T07:00:00.000"
    assert result.summary.quality_label == "good"
    assert result.summary.confidence == "high"
    assert result.summary.is_real_data is True


def test_normalizer_uses_summary_total_as_medium_confidence_fallback() -> None:
    result = normalize_fitbit_sleep_response(
        {"sleep": [], "summary": {"totalMinutesAsleep": "365"}},
        target_date=FIXED_DATE.isoformat(),
    )

    assert result.success is True
    assert result.summary is not None
    assert result.summary.total_sleep_minutes == 365
    assert result.summary.main_sleep_start_time is None
    assert result.summary.main_sleep_end_time is None
    assert result.summary.quality_label == "fair"
    assert result.summary.confidence == "medium"
    assert result.summary.is_real_data is True


@pytest.mark.parametrize(
    "payload",
    [
        {"sleep": [], "summary": {"totalMinutesAsleep": 0}},
        {"sleep": [], "summary": {}},
        {},
    ],
)
def test_normalizer_rejects_missing_or_zero_usable_sleep(payload: dict[str, Any]) -> None:
    result = normalize_fitbit_sleep_response(
        payload,
        target_date=FIXED_DATE.isoformat(),
    )

    assert result.success is False
    assert result.summary is None
    assert result.error == FITBIT_SLEEP_NORMALIZE_ERROR_NO_SLEEP_DATA


@pytest.mark.parametrize(
    "payload",
    [
        {"sleep": "not-a-list", "summary": {}},
        {"sleep": [], "summary": "not-an-object"},
        {"sleep": [{"isMainSleep": True, "minutesAsleep": -1}]},
        {"sleep": [], "summary": {"totalMinutesAsleep": "not-a-number"}},
    ],
)
def test_normalizer_rejects_invalid_response_shapes(payload: dict[str, Any]) -> None:
    result = normalize_fitbit_sleep_response(
        payload,
        target_date=FIXED_DATE.isoformat(),
    )

    assert result.success is False
    assert result.summary is None
    assert result.error == FITBIT_SLEEP_NORMALIZE_ERROR_INVALID_RESPONSE


def test_provider_maps_normalized_fitbit_data_into_sleep_summary() -> None:
    provider = FitbitSleepProvider(
        fetcher=lambda target_date: _api_result(
            success=True,
            raw_data=_main_sleep_payload(),
        ),
        date_provider=lambda: FIXED_DATE,
    )

    summary = provider.get_sleep_summary()

    assert summary.date == FIXED_DATE.isoformat()
    assert summary.source == "fitbit"
    assert summary.available is True
    assert summary.total_sleep_minutes == 425
    assert summary.sleep_start == "2026-07-19T23:10:00.000"
    assert summary.sleep_end == "2026-07-20T07:00:00.000"
    assert summary.quality_label == "good"
    assert summary.confidence == "high"
    assert summary.is_real_data is True
    assert summary.unavailable_reason is None


@pytest.mark.parametrize(
    ("error", "expected_reason"),
    [
        (FITBIT_SLEEP_ERROR_RECONNECT_REQUIRED, "reconnect_required"),
        (FITBIT_SLEEP_ERROR_PERMISSION_DENIED, "permission_denied"),
        (FITBIT_SLEEP_ERROR_SCOPE_MISSING, "scope_missing"),
        (FITBIT_SLEEP_ERROR_RATE_LIMITED, "rate_limited"),
        (FITBIT_SLEEP_ERROR_PROVIDER_UNAVAILABLE, "provider_unavailable"),
        (FITBIT_SLEEP_ERROR_INVALID_RESPONSE, "invalid_response"),
    ],
)
def test_provider_maps_failures_into_safe_unavailable_summary(
    error: str,
    expected_reason: str,
) -> None:
    provider = FitbitSleepProvider(
        fetcher=lambda target_date: _api_result(success=False, error=error),
        date_provider=lambda: FIXED_DATE,
    )

    summary = provider.get_sleep_summary()

    assert summary.source == "fitbit"
    assert summary.available is False
    assert summary.total_sleep_minutes == 0
    assert summary.quality_label == "unavailable"
    assert summary.confidence == "none"
    assert summary.is_real_data is False
    assert summary.unavailable_reason == expected_reason
    assert "public-safe fixture result" not in (summary.message or "")


def test_sleep_summary_api_returns_w3_real_data_semantics(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider = FitbitSleepProvider(
        fetcher=lambda target_date: _api_result(
            success=True,
            raw_data=_main_sleep_payload(),
        ),
        date_provider=lambda: FIXED_DATE,
    )
    monkeypatch.setattr(
        sleep,
        "load_config",
        lambda: AppConfig(sleep_provider="fitbit"),
    )
    monkeypatch.setattr(
        sleep_summary_service,
        "create_sleep_provider",
        lambda config: provider,
    )

    test_app = FastAPI()
    test_app.include_router(sleep.router)
    with TestClient(test_app) as client:
        response = client.get("/sleep/summary")

    assert response.status_code == 200
    payload = response.json()
    assert payload["source"] == "fitbit"
    assert payload["available"] is True
    assert payload["sleep_start"] == "2026-07-19T23:10:00.000"
    assert payload["sleep_end"] == "2026-07-20T07:00:00.000"
    assert payload["quality_label"] == "good"
    assert payload["confidence"] == "high"
    assert payload["is_real_data"] is True
    assert payload["unavailable_reason"] is None
    assert "sleep" not in payload
    assert PUBLIC_SAFE_ACCESS_TOKEN not in response.text
