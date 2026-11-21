from collections.abc import Awaitable, Callable
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.models.advice import PublicAdviceProblem, PublicAdviceRequest, PublicAdviceResponse
from app.services.public_advice import PublicAdviceRuntime


_NO_STORE = {"Cache-Control": "no-store"}


def _invalid_request() -> JSONResponse:
    return JSONResponse(
        status_code=422, content={"detail": "invalid_request"}, headers=_NO_STORE
    )


class PublicAdviceRoute(APIRoute):
    def get_route_handler(self) -> Callable[[Request], Awaitable[Response]]:
        handler = super().get_route_handler()

        async def safe_handler(request: Request) -> Response:
            if request.query_params:
                return _invalid_request()
            try:
                return await handler(request)
            except RequestValidationError:
                # Validation details can contain arbitrary client-supplied keys and values.
                return _invalid_request()

        return safe_handler


router = APIRouter(prefix="/v1", route_class=PublicAdviceRoute)
bearer = HTTPBearer(auto_error=False)


def get_public_advice_runtime(request: Request) -> PublicAdviceRuntime | None:
    return getattr(request.app.state, "public_advice_runtime", None)


@router.post(
    "/advice",
    response_model=PublicAdviceResponse,
    responses={code: {"model": PublicAdviceProblem} for code in (401, 422, 429, 502, 503)},
)
def create_public_advice(
    request: PublicAdviceRequest,
    response: Response,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
    runtime: Annotated[PublicAdviceRuntime | None, Depends(get_public_advice_runtime)],
) -> PublicAdviceResponse:
    if runtime is None:
        raise HTTPException(503, "advice_unavailable", headers=_NO_STORE)

    try:
        user_id = runtime.authenticate(credentials.credentials) if credentials else None
    except Exception:
        raise HTTPException(503, "advice_unavailable", headers=_NO_STORE) from None
    if not user_id:
        raise HTTPException(
            401, "authentication_required", headers={**_NO_STORE, "WWW-Authenticate": "Bearer"}
        )

    try:
        exceeded = runtime.quota.reserve(user_id)
    except Exception:
        raise HTTPException(503, "advice_unavailable", headers=_NO_STORE) from None
    if exceeded is not None:
        raise HTTPException(429, exceeded, headers=_NO_STORE)

    try:
        reply = PublicAdviceResponse(
            message=runtime.generate(mood=request.mood, character_id=request.character_id)
        )
    except Exception:
        raise HTTPException(502, "upstream_failure", headers=_NO_STORE) from None

    response.headers.update(_NO_STORE)
    return reply
