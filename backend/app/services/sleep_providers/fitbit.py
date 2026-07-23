from __future__ import annotations

from collections.abc import Callable
from datetime import date

from app.models.sleep import SleepSummary
from app.services.fitbit_sleep_normalizer import (
    FITBIT_SLEEP_NORMALIZE_ERROR_INVALID_RESPONSE,
    FITBIT_SLEEP_NORMALIZE_ERROR_NO_SLEEP_DATA,
    normalize_fitbit_sleep_response,
)
from app.services.fitbit_sleep_service import (
    FITBIT_SLEEP_ERROR_API_REQUEST_FAILED,
    FITBIT_SLEEP_ERROR_INVALID_RESPONSE,
    FITBIT_SLEEP_ERROR_NO_ACCESS_TOKEN_AFTER_REFRESH,
    FITBIT_SLEEP_ERROR_NO_TOKEN,
    FITBIT_SLEEP_ERROR_PERMISSION_DENIED,
    FITBIT_SLEEP_ERROR_PROVIDER_UNAVAILABLE,
    FITBIT_SLEEP_ERROR_RATE_LIMITED,
    FITBIT_SLEEP_ERROR_RECONNECT_REQUIRED,
    FITBIT_SLEEP_ERROR_REFRESH_FAILED,
    FITBIT_SLEEP_ERROR_SCOPE_MISSING,
    FitbitSleepApiResult,
    fetch_fitbit_sleep_for_date,
)
from app.services.sleep_providers.base import SleepProvider


class FitbitSleepProvider(SleepProvider):
    """
    Fitbit sleep provider backed by the local OAuth token store.

    W-3 maps only allow-listed API/normalization states into SleepSummary. Real
    configured operator acceptance remains a separate W-5 activity.
    """

    def __init__(
        self,
        *,
        fetcher: Callable[[date], FitbitSleepApiResult] | None = None,
        date_provider: Callable[[], date] | None = None,
    ) -> None:
        self._fetcher = fetcher
        self._date_provider = date_provider or date.today

    def get_sleep_summary(self) -> SleepSummary:
        target_date = self._date_provider()
        fetcher = self._fetcher or fetch_fitbit_sleep_for_date
        sleep_result = fetcher(target_date)

        if not sleep_result.success or sleep_result.raw_data is None:
            unavailable_reason = _map_fetch_error_to_unavailable_reason(
                sleep_result.error
            )
            return _build_unavailable_sleep_summary(
                target_date=target_date,
                message=_build_unavailable_message(sleep_result.error),
                unavailable_reason=unavailable_reason,
            )

        normalize_result = normalize_fitbit_sleep_response(
            sleep_result.raw_data,
            target_date=sleep_result.date,
        )

        if not normalize_result.success or normalize_result.summary is None:
            unavailable_reason = _map_normalize_error_to_unavailable_reason(
                normalize_result.error
            )
            return _build_unavailable_sleep_summary(
                target_date=target_date,
                message=_build_normalization_unavailable_message(
                    normalize_result.error
                ),
                unavailable_reason=unavailable_reason,
            )

        summary = normalize_result.summary

        return SleepSummary(
            date=summary.date,
            total_sleep_minutes=summary.total_sleep_minutes,
            efficiency=summary.efficiency,
            deep_sleep_minutes=None,
            rem_sleep_minutes=None,
            awake_minutes=None,
            source="fitbit",
            available=True,
            message=summary.message,
            sleep_start=summary.main_sleep_start_time,
            sleep_end=summary.main_sleep_end_time,
            quality_label=summary.quality_label,
            confidence=summary.confidence,
            is_real_data=summary.is_real_data,
            unavailable_reason=None,
        )


def _build_unavailable_sleep_summary(
    *,
    target_date: date,
    message: str,
    unavailable_reason: str,
) -> SleepSummary:
    """Return a safe app-facing summary when Fitbit data is unavailable."""

    return SleepSummary(
        date=target_date.isoformat(),
        total_sleep_minutes=0,
        efficiency=None,
        deep_sleep_minutes=None,
        rem_sleep_minutes=None,
        awake_minutes=None,
        source="fitbit",
        available=False,
        message=message,
        sleep_start=None,
        sleep_end=None,
        quality_label="unavailable",
        confidence="none",
        is_real_data=False,
        unavailable_reason=unavailable_reason,
    )


def _map_fetch_error_to_unavailable_reason(error: str | None) -> str:
    if error == FITBIT_SLEEP_ERROR_NO_TOKEN:
        return "not_connected"
    if error in {
        FITBIT_SLEEP_ERROR_REFRESH_FAILED,
        FITBIT_SLEEP_ERROR_NO_ACCESS_TOKEN_AFTER_REFRESH,
        FITBIT_SLEEP_ERROR_RECONNECT_REQUIRED,
    }:
        return FITBIT_SLEEP_ERROR_RECONNECT_REQUIRED
    if error == FITBIT_SLEEP_ERROR_PERMISSION_DENIED:
        return FITBIT_SLEEP_ERROR_PERMISSION_DENIED
    if error == FITBIT_SLEEP_ERROR_SCOPE_MISSING:
        return FITBIT_SLEEP_ERROR_SCOPE_MISSING
    if error == FITBIT_SLEEP_ERROR_RATE_LIMITED:
        return FITBIT_SLEEP_ERROR_RATE_LIMITED
    if error == FITBIT_SLEEP_ERROR_PROVIDER_UNAVAILABLE:
        return FITBIT_SLEEP_ERROR_PROVIDER_UNAVAILABLE
    if error == FITBIT_SLEEP_ERROR_INVALID_RESPONSE:
        return FITBIT_SLEEP_ERROR_INVALID_RESPONSE
    return FITBIT_SLEEP_ERROR_API_REQUEST_FAILED


def _map_normalize_error_to_unavailable_reason(error: str | None) -> str:
    if error == FITBIT_SLEEP_NORMALIZE_ERROR_NO_SLEEP_DATA:
        return FITBIT_SLEEP_NORMALIZE_ERROR_NO_SLEEP_DATA
    if error == FITBIT_SLEEP_NORMALIZE_ERROR_INVALID_RESPONSE:
        return FITBIT_SLEEP_ERROR_INVALID_RESPONSE
    return FITBIT_SLEEP_ERROR_INVALID_RESPONSE


def _build_unavailable_message(error: str | None) -> str:
    """Return a conservative user-facing unavailable sleep message."""

    if error == FITBIT_SLEEP_ERROR_NO_TOKEN:
        return (
            "睡眠データはまだ連携されていません。今日は気分をもとに、"
            "軽めのアドバイスを作ります。"
        )

    if error in {
        FITBIT_SLEEP_ERROR_REFRESH_FAILED,
        FITBIT_SLEEP_ERROR_NO_ACCESS_TOKEN_AFTER_REFRESH,
        FITBIT_SLEEP_ERROR_RECONNECT_REQUIRED,
    }:
        return (
            "Fitbitとの再連携が必要です。今日は気分をもとに、"
            "無理のない過ごし方を提案します。"
        )

    if error == FITBIT_SLEEP_ERROR_PERMISSION_DENIED:
        return (
            "Fitbitの睡眠データ利用が許可されていません。今日は気分をもとに、"
            "できる範囲のアドバイスを作ります。"
        )

    if error == FITBIT_SLEEP_ERROR_SCOPE_MISSING:
        return (
            "Fitbitの睡眠権限を確認できませんでした。今日は気分をもとに、"
            "できる範囲のアドバイスを作ります。"
        )

    if error == FITBIT_SLEEP_ERROR_RATE_LIMITED:
        return (
            "Fitbitへのアクセスが一時的に制限されています。今日は気分をもとに、"
            "無理のない過ごし方を提案します。"
        )

    if error == FITBIT_SLEEP_ERROR_PROVIDER_UNAVAILABLE:
        return (
            "Fitbitの睡眠サービスを一時的に利用できません。今日は気分をもとに、"
            "無理のない過ごし方を提案します。"
        )

    if error == FITBIT_SLEEP_ERROR_INVALID_RESPONSE:
        return (
            "Fitbitの睡眠データ形式を確認できませんでした。今日は気分をもとに、"
            "無理のない過ごし方を提案します。"
        )

    return (
        "睡眠データを取得できませんでした。今日は気分をもとに、"
        "できる範囲のアドバイスを作ります。"
    )


def _build_normalization_unavailable_message(error: str | None) -> str:
    if error == FITBIT_SLEEP_NORMALIZE_ERROR_NO_SLEEP_DATA:
        return (
            "指定日のFitbit睡眠データがありません。今日は気分をもとに、"
            "無理のない過ごし方を提案します。"
        )

    return (
        "Fitbitの睡眠データ形式を確認できませんでした。今日は気分をもとに、"
        "無理のない過ごし方を提案します。"
    )
