from fastapi import APIRouter

from app.version import APP_VERSION

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok", "version": APP_VERSION}