from fastapi import APIRouter

from app.config import load_config
from app.models.voice_input_demo import (
    VoiceInputDemoRequest,
    VoiceInputDemoRequestResponse,
    VoiceInputDemoStatusResponse,
)
from app.services.voice_input_demo_service import VoiceInputDemoService

router = APIRouter()


@router.get("/demo/voice-input/status", response_model=VoiceInputDemoStatusResponse)
def get_voice_input_demo_status():
    """Return the guarded v0.34.0 voice input demo boundary status."""

    return VoiceInputDemoService(load_config()).build_status()


@router.post("/demo/voice-input", response_model=VoiceInputDemoRequestResponse)
def create_voice_input_demo_request(request: VoiceInputDemoRequest):
    """Accept a metadata-only voice input demo request.

    This endpoint is intentionally a safe contract placeholder. It does not
    process audio yet; it returns the current capability status and a clear
    not-started result for the future Flutter voice trigger flow.
    """

    return VoiceInputDemoService(load_config()).submit_request(request)
