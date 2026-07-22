from datetime import date as Date

from fastapi import APIRouter, HTTPException, Query

from app.models.daily_record import (
    DailyRecordCreateRequest,
    DailyRecordResponse,
)
from app.models.recent_sleep_trend import RecentSleepTrend
from app.models.rhythm_report import RhythmReport, RhythmReportPeriod
from app.models.weekly_sleep_summary import WeeklySleepSummary
from app.services.daily_record_store import DailyRecordStore
from app.services.recent_sleep_trend_service import RecentSleepTrendService
from app.services.rhythm_report_service import RhythmReportService
from app.services.weekly_sleep_summary_service import WeeklySleepSummaryService

router = APIRouter(prefix="/daily-records", tags=["daily-records"])

store = DailyRecordStore()
recent_sleep_trend_service = RecentSleepTrendService(store)
weekly_sleep_summary_service = WeeklySleepSummaryService(store)
rhythm_report_service = RhythmReportService(store)


@router.post("", response_model=DailyRecordResponse)
def save_daily_record(
    request: DailyRecordCreateRequest,
) -> DailyRecordResponse:
    return store.upsert(request)


@router.get("", response_model=list[DailyRecordResponse])
def list_daily_records(
    limit: int = Query(default=30, ge=1, le=365),
) -> list[DailyRecordResponse]:
    return store.list_recent(limit=limit)


@router.get("/recent-sleep-trend", response_model=RecentSleepTrend)
def read_recent_sleep_trend(
    reference_date: str | None = Query(default=None, min_length=1),
    days: int = Query(default=7, ge=1, le=30),
) -> RecentSleepTrend:
    """Return a conservative recent-history sleep trend label for History UI."""

    normalized_reference_date = reference_date or Date.today().isoformat()

    return recent_sleep_trend_service.summarize_recent_history(
        reference_date=normalized_reference_date,
        days=days,
    )


@router.get("/weekly-summary", response_model=WeeklySleepSummary)
def read_weekly_sleep_summary(
    reference_date: str | None = Query(default=None, min_length=1),
    days: int = Query(default=7, ge=1, le=30),
) -> WeeklySleepSummary:
    """Return a conservative weekly History recap built from DailyRecords."""

    normalized_reference_date = reference_date or Date.today().isoformat()

    return weekly_sleep_summary_service.summarize_weekly_history(
        reference_date=normalized_reference_date,
        days=days,
    )


@router.get("/rhythm-report", response_model=RhythmReport)
def read_rhythm_report(
    period: RhythmReportPeriod = Query(default="weekly"),
    reference_date: str | None = Query(default=None, min_length=1),
) -> RhythmReport:
    """Return a conservative weekly/monthly report built from DailyRecords."""

    normalized_reference_date = reference_date or Date.today().isoformat()

    return rhythm_report_service.build_report(
        period=period,
        reference_date=normalized_reference_date,
    )


@router.get("/{date}", response_model=DailyRecordResponse)
def read_daily_record(date: str) -> DailyRecordResponse:
    record = store.get(date)

    if record is None:
        raise HTTPException(status_code=404, detail="Daily record not found.")

    return record
