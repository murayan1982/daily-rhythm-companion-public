from datetime import date

from fastapi import APIRouter, Query

from app.config import load_config
from app.models.google_health import (
    GoogleHealthCallbackResponse,
    GoogleHealthConnectResponse,
    GoogleHealthStatusResponse,
    GoogleHealthDiagnosticsResponse,
    GoogleHealthSelfCheckResponse,
    GoogleHealthPreflightResponse,
    GoogleHealthTokenRefreshCheckResponse,
    GoogleHealthScopeCheckResponse,
    GoogleHealthPermissionRetestReadinessResponse,
    GoogleHealthProjectAccessReadinessResponse,
    GoogleHealthCodelabExerciseCheckResponse,
    GoogleHealthConnectionChecklistResponse,
    GoogleHealthConnectionUxResponse,
)
from app.services.google_health_service import (
    build_google_health_connect_response,
    get_google_health_status,
    handle_google_health_callback_stub,
)
from app.services.google_health_diagnostics import get_google_health_diagnostics
from app.services.google_health_self_check import run_google_health_self_check
from app.services.google_health_preflight import get_google_health_preflight
from app.services.google_health_refresh_check import (
    run_google_health_token_refresh_check,
)
from app.services.google_health_scope_check import get_google_health_scope_check
from app.services.google_health_permission_retest_readiness import (
    get_google_health_permission_retest_readiness,
)
from app.services.google_health_project_access_readiness import (
    get_google_health_project_access_readiness,
)
from app.services.google_health_codelab_exercise_check import (
    run_google_health_codelab_exercise_check,
)
from app.services.google_health_connection_checklist import (
    get_google_health_connection_checklist,
)
from app.services.google_health_connection_ux import get_google_health_connection_ux

router = APIRouter(prefix="/google-health", tags=["google-health"])


@router.get("/status", response_model=GoogleHealthStatusResponse)
def read_google_health_status() -> GoogleHealthStatusResponse:
    config = load_config()
    return get_google_health_status(config)


@router.get("/diagnostics", response_model=GoogleHealthDiagnosticsResponse)
def read_google_health_diagnostics() -> GoogleHealthDiagnosticsResponse:
    config = load_config()
    return get_google_health_diagnostics(config)


@router.get("/self-check", response_model=GoogleHealthSelfCheckResponse)
def read_google_health_self_check(
    target_date: date | None = Query(default=None),
) -> GoogleHealthSelfCheckResponse:
    config = load_config()
    return run_google_health_self_check(
        config=config,
        target_date=target_date,
    )


@router.get("/preflight", response_model=GoogleHealthPreflightResponse)
def read_google_health_preflight() -> GoogleHealthPreflightResponse:
    config = load_config()
    return get_google_health_preflight(config)


@router.get("/token-refresh-check", response_model=GoogleHealthTokenRefreshCheckResponse)
def read_google_health_token_refresh_check() -> GoogleHealthTokenRefreshCheckResponse:
    config = load_config()
    return run_google_health_token_refresh_check(config=config)


@router.get("/scope-check", response_model=GoogleHealthScopeCheckResponse)
def read_google_health_scope_check() -> GoogleHealthScopeCheckResponse:
    config = load_config()
    return get_google_health_scope_check(config=config)


@router.get(
    "/permission-retest-readiness",
    response_model=GoogleHealthPermissionRetestReadinessResponse,
)
def read_google_health_permission_retest_readiness() -> GoogleHealthPermissionRetestReadinessResponse:
    config = load_config()
    return get_google_health_permission_retest_readiness(config=config)


@router.get(
    "/project-access-readiness",
    response_model=GoogleHealthProjectAccessReadinessResponse,
)
def read_google_health_project_access_readiness() -> GoogleHealthProjectAccessReadinessResponse:
    config = load_config()
    return get_google_health_project_access_readiness(config=config)


@router.get(
    "/codelab-exercise-check",
    response_model=GoogleHealthCodelabExerciseCheckResponse,
)
def read_google_health_codelab_exercise_check() -> GoogleHealthCodelabExerciseCheckResponse:
    config = load_config()
    return run_google_health_codelab_exercise_check(config=config)


@router.get(
    "/connection-checklist",
    response_model=GoogleHealthConnectionChecklistResponse,
)
def read_google_health_connection_checklist() -> GoogleHealthConnectionChecklistResponse:
    config = load_config()
    return get_google_health_connection_checklist(config=config)


@router.get(
    "/connection-ux",
    response_model=GoogleHealthConnectionUxResponse,
)
def read_google_health_connection_ux() -> GoogleHealthConnectionUxResponse:
    config = load_config()
    return get_google_health_connection_ux(config=config)


@router.get("/connect", response_model=GoogleHealthConnectResponse)
def connect_google_health() -> GoogleHealthConnectResponse:
    config = load_config()
    return build_google_health_connect_response(config)


@router.get("/callback", response_model=GoogleHealthCallbackResponse)
def google_health_callback(
    code: str | None = Query(default=None),
    state: str | None = Query(default=None),
    error: str | None = Query(default=None),
    error_description: str | None = Query(default=None),
) -> GoogleHealthCallbackResponse:
    config = load_config()

    return handle_google_health_callback_stub(
        config=config,
        code=code,
        state=state,
        error=error,
        error_description=error_description,
    )