from __future__ import annotations

from datetime import date

from app.models.sleep import SleepSummary
from app.services.fitbit_sleep_normalizer import (
    normalize_fitbit_sleep_response,
)
from app.services.fitbit_sleep_service import (
    FITBIT_SLEEP_ERROR_API_REQUEST_FAILED,
    FITBIT_SLEEP_ERROR_NO_TOKEN,
    FITBIT_SLEEP_ERROR_REFRESH_FAILED,
    fetch_fitbit_sleep_for_date,
)
from app.services.sleep_providers.base import SleepProvider


class FitbitSleepProvider(SleepProvider):
    """
    Legacy Fitbit sleep provider backed by the local OAuth token store.

    This provider is kept as a migration/reference boundary. It returns the
    app-facing SleepSummary shape and keeps raw Fitbit payloads inside the
    service boundary.
    """

    def get_sleep_summary(self) -> SleepSummary:
        target_date = date.today()
        sleep_result = fetch_fitbit_sleep_for_date(target_date)

        if not sleep_result.success or sleep_result.raw_data is None:
            return _build_unavailable_sleep_summary(
                target_date=target_date,
                message=_build_unavailable_message(sleep_result.error),
            )

        normalize_result = normalize_fitbit_sleep_response(
            sleep_result.raw_data,
            target_date=sleep_result.date,
        )

        if not normalize_result.success or normalize_result.summary is None:
            return _build_unavailable_sleep_summary(
                target_date=target_date,
                message=(
                    "睡眠データの形式を確認できませんでした。今日は気分をもとに、"
                    "無理のない過ごし方を提案します。"
                ),
            )

        summary = normalize_result.summary

        return SleepSummary(
            date=summary.date,
            total_sleep_minutes=summary.total_sleep_minutes or 0,
            efficiency=summary.efficiency,
            deep_sleep_minutes=None,
            rem_sleep_minutes=None,
            awake_minutes=None,
            source="fitbit",
            available=True,
            message=summary.message,
        )


def _build_unavailable_sleep_summary(
    *,
    target_date: date,
    message: str,
) -> SleepSummary:
    """Return a safe app-facing summary when sleep data is unavailable."""

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
    )


def _build_unavailable_message(
    error: str | None,
) -> str:
    """Return a user-facing unavailable sleep message."""

    if error == FITBIT_SLEEP_ERROR_NO_TOKEN:
        return (
            "睡眠データはまだ連携されていません。今日は気分をもとに、"
            "軽めのアドバイスを作ります。"
        )

    if error == FITBIT_SLEEP_ERROR_REFRESH_FAILED:
        return (
            "睡眠データの連携を更新できませんでした。今日は気分をもとに、"
            "無理のない過ごし方を提案します。"
        )

    if error == FITBIT_SLEEP_ERROR_API_REQUEST_FAILED:
        return (
            "睡眠データを取得できませんでした。今日は気分をもとに、"
            "できる範囲のアドバイスを作ります。"
        )

    return (
        "睡眠データは現在利用できません。今日は気分をもとに、"
        "無理のない過ごし方を提案します。"
    )