from fastapi import FastAPI

from app.api.public_advice import router as advice_router
from app.services.public_advice_startup import public_advice_lifespan


def health():
    return {"status": "ok"}


def create_public_advice_app(*, lifespan=None) -> FastAPI:
    app = FastAPI(
        title="Daily Rhythm Companion Public Advice API",
        lifespan=lifespan,
        openapi_url=None,
        docs_url=None,
        redoc_url=None,
        swagger_ui_oauth2_redirect_url=None,
        redirect_slashes=False,
    )
    app.include_router(advice_router)
    app.add_api_route("/health", health, methods=["GET"])
    return app


app = create_public_advice_app(lifespan=public_advice_lifespan)
