from fastapi import APIRouter

from app.config import AppConfig, load_config
from app.engines.errors import FrameworkEngineError
from app.engines.factory import create_conversation_engine
from app.models.advice import AdviceRequest, AdviceResponse, AdviceSource
from app.models.recent_sleep_trend import RecentSleepTrend
from app.models.report_handoff import ReportHandoffContext
from app.services.advice_daily_record_saver import AdviceDailyRecordSaver
from app.services.recent_sleep_trend_service import RecentSleepTrendService


router = APIRouter()

config = load_config()
conversation_engine = create_conversation_engine(config)
mock_conversation_engine = create_conversation_engine(
    AppConfig(conversation_engine="mock")
)
daily_record_saver = AdviceDailyRecordSaver()
recent_sleep_trend_service = RecentSleepTrendService()


@router.post("/advice", response_model=AdviceResponse)
def create_advice(request: AdviceRequest):
    request_with_context = _attach_recent_sleep_trend(request)
    request_with_context = _normalize_report_handoff_context(request_with_context)
    response, engine_basis = _create_advice_with_engine_fallback(
        request_with_context
    )
    response = _with_report_handoff_source(response, request_with_context)

    daily_record_saver.save(
        request=request_with_context,
        response=response,
        advice_basis=_build_advice_basis(
            recent_sleep_trend=request_with_context.recent_sleep_trend,
            report_handoff=request_with_context.report_handoff,
            engine_basis=engine_basis,
        ),
    )

    return response


def _create_advice_with_engine_fallback(
    request: AdviceRequest,
) -> tuple[AdviceResponse, str]:
    """
    Create advice through the configured engine.

    Framework mode falls back to the mock engine when the framework adapter is
    unavailable. The fallback response keeps the same source metadata contract,
    but marks the engine as ``framework_fallback`` so the app can explain it.
    """

    configured_engine = _engine_basis_label(config.conversation_engine)

    try:
        response = conversation_engine.create_advice(request)
    except FrameworkEngineError:
        if configured_engine != "framework":
            raise

        response = mock_conversation_engine.create_advice(request)
        return _with_fallback_source(response, request), "framework_fallback"

    return response, configured_engine


def _with_fallback_source(
    response: AdviceResponse,
    request: AdviceRequest,
) -> AdviceResponse:
    """Replace mock source metadata with framework fallback metadata."""

    return response.model_copy(
        update={
            "source": AdviceSource(
                engine="framework_fallback",
                drc_character_id=request.character.character_id,
                drc_character_name=request.character.display_name,
            )
        }
    )


def _with_report_handoff_source(
    response: AdviceResponse,
    request: AdviceRequest,
) -> AdviceResponse:
    """Attach safe report handoff metadata to the app-facing source block."""

    report_handoff = request.report_handoff
    if not _uses_report_handoff(report_handoff):
        return response

    source = response.source or AdviceSource(
        engine=_engine_basis_label(config.conversation_engine),
        drc_character_id=request.character.character_id,
        drc_character_name=request.character.display_name,
    )

    return response.model_copy(
        update={
            "source": source.model_copy(
                update={"report_handoff": report_handoff}
            )
        }
    )


def _normalize_report_handoff_context(request: AdviceRequest) -> AdviceRequest:
    """Keep only report context that may safely inform advice."""

    if _uses_report_handoff(request.report_handoff):
        return request

    return request.model_copy(update={"report_handoff": None})


def _attach_recent_sleep_trend(request: AdviceRequest) -> AdviceRequest:
    """Attach server-side recent sleep trend context only for unavailable sleep."""

    if request.sleep.available:
        return request.model_copy(update={"recent_sleep_trend": None})

    trend = recent_sleep_trend_service.summarize_for_unavailable_today(
        current_sleep=request.sleep,
    )

    return request.model_copy(update={"recent_sleep_trend": trend})


def _build_advice_basis(
    recent_sleep_trend: RecentSleepTrend | None,
    report_handoff: ReportHandoffContext | None,
    engine_basis: str,
) -> str:
    """Return the basis label stored in DailyRecord history."""

    if _uses_report_handoff(report_handoff):
        base_basis = f"{report_handoff.advice_basis_prefix}+mood+character"
    elif _uses_recent_sleep_trend(recent_sleep_trend):
        base_basis = "recent_sleep_trend+mood+character"
    else:
        base_basis = "sleep+mood+character"

    return f"{base_basis}+{engine_basis}"


def _engine_basis_label(engine_name: str) -> str:
    normalized = engine_name.strip().lower()

    if normalized == "framework":
        return "framework"

    if normalized == "mock":
        return "mock"

    return normalized


def _uses_report_handoff(report_handoff: ReportHandoffContext | None) -> bool:
    return (
        report_handoff is not None
        and not report_handoff.is_medical_advice
        and report_handoff.should_inform_advice
        and report_handoff.advice_basis_prefix != "none"
    )


def _uses_recent_sleep_trend(recent_sleep_trend: RecentSleepTrend | None) -> bool:
    return (
        recent_sleep_trend is not None
        and recent_sleep_trend.label != "insufficient_data"
    )
