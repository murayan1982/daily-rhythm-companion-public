from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.config import load_config
from app.models.voice_output_demo import (
    VoiceOutputDemoRequest,
    VoiceOutputDemoRequestResponse,
    VoiceOutputDemoStatusResponse,
)
from app.services.voice_output_artifact_store import VoiceOutputArtifactStore
from app.services.voice_output_demo_service import VoiceOutputDemoService

router = APIRouter()


@router.get("/demo/voice-output/status", response_model=VoiceOutputDemoStatusResponse)
def get_voice_output_demo_status():
    """Return the guarded voice output demo boundary status."""

    return VoiceOutputDemoService(load_config()).build_status()


@router.post("/demo/voice-output", response_model=VoiceOutputDemoRequestResponse)
def create_voice_output_demo_request(request: VoiceOutputDemoRequest):
    """Accept a metadata-only voice output demo request.

    This endpoint remains guarded by default. It calls the AI Character
    Framework public voice-output boundary only when explicit real TTS opt-in
    is enabled; otherwise it returns a safe not-started result.
    """

    return VoiceOutputDemoService(load_config()).submit_request(request)


@router.get("/demo/voice-output/audio/{artifact_id}", response_class=FileResponse)
def get_voice_output_demo_audio(artifact_id: str):
    """Serve one DRC-managed local MP3 through an opaque artifact ID."""

    artifact_store = VoiceOutputArtifactStore()
    artifact_path = artifact_store.resolve_public_artifact(artifact_id)
    if artifact_path is None:
        raise HTTPException(
            status_code=404,
            detail="Voice output audio artifact was not found.",
        )

    media_type = artifact_store.media_type_for(artifact_path)
    if media_type is None:
        raise HTTPException(
            status_code=404,
            detail="Voice output audio artifact was not found.",
        )

    return FileResponse(
        path=artifact_path,
        media_type=media_type,
        headers={
            "Cache-Control": "no-store",
            "X-Content-Type-Options": "nosniff",
        },
    )
