from app.models.character import CharacterPreset


class CharacterService:
    """
    Provides character presets for the app.

    For now, presets are defined in code. Later this service can be replaced
    with database-backed user character settings.
    """

    def __init__(self) -> None:
        self._presets: list[CharacterPreset] = [
            CharacterPreset(
                character_id="gentle_mina",
                display_name="ミナ",
                description="やさしく落ち着いた朝の案内役。",
                personality_type="gentle",
                speaking_style="casual",
                advice_style="rest_focused",
            ),
            CharacterPreset(
                character_id="cheerful_sora",
                display_name="ソラ",
                description="明るく元気に背中を押してくれる相棒。",
                personality_type="cheerful",
                speaking_style="casual",
                advice_style="positive",
            ),
            CharacterPreset(
                character_id="cool_rei",
                display_name="レイ",
                description="落ち着いて短く実用的に助言する秘書タイプ。",
                personality_type="cool",
                speaking_style="concise",
                advice_style="practical",
            ),
        ]

    def list_presets(self) -> list[CharacterPreset]:
        """Return available character presets."""
        return self._presets