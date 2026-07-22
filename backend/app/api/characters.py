from fastapi import APIRouter

from app.models.character import CharacterPreset
from app.services.character_service import CharacterService

router = APIRouter()

character_service = CharacterService()


@router.get("/characters", response_model=list[CharacterPreset])
def list_characters():
    return character_service.list_presets()