from fastapi import FastAPI

from app.api.public_advice import router as advice_router
from app.services.public_advice_startup import public_advice_lifespan


app = FastAPI(
    title="Daily Rhythm Companion Public Advice API",
    lifespan=public_advice_lifespan,
    openapi_url=None,
    docs_url=None,
    redoc_url=None,
    swagger_ui_oauth2_redirect_url=None,
    redirect_slashes=False,
)
app.include_router(advice_router)


@app.get("/health")
def health():
    return {"status": "ok"}
