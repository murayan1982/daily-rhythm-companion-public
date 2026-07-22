from pydantic import BaseModel


class CharacterContext(BaseModel):
    character_id: str
    display_name: str
    personality_type: str
    speaking_style: str
    advice_style: str


class CharacterPreset(BaseModel):
    character_id: str
    display_name: str
    description: str
    personality_type: str
    speaking_style: str
    advice_style: str