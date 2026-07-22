from __future__ import annotations

from dataclasses import dataclass


DEFAULT_FRAMEWORK_CHARACTER_NAME = "default"

DRC_TO_FRAMEWORK_CHARACTER_NAME = {
    "gentle_mina": DEFAULT_FRAMEWORK_CHARACTER_NAME,
    "cheerful_sora": DEFAULT_FRAMEWORK_CHARACTER_NAME,
    "cool_rei": DEFAULT_FRAMEWORK_CHARACTER_NAME,
}


@dataclass(frozen=True)
class FrameworkCharacterMapping:
    """
    Resolved framework-side character selection for one DRC character.

    ``framework_character_source`` is app-facing debug metadata. It lets DRC
    explain whether a framework character was selected by the default v0.32
    mapping, a future specific mapping, a local override, or a fallback.
    """

    drc_character_id: str
    framework_character: str
    framework_character_source: str


def resolve_framework_character_mapping(
    character_id: str,
    *,
    configured_character: str | None = None,
) -> FrameworkCharacterMapping:
    """
    Resolve a DRC character_id to a framework character plus source metadata.

    v0.32.0 starts with the same safe mapping as v0.31.0: all bundled DRC
    characters map to the framework ``default`` character. An explicit
    FRAMEWORK_CHARACTER value can still override this for local demo testing.
    """

    normalized_configured = (configured_character or "").strip()
    if (
        normalized_configured
        and normalized_configured != DEFAULT_FRAMEWORK_CHARACTER_NAME
    ):
        return FrameworkCharacterMapping(
            drc_character_id=character_id,
            framework_character=normalized_configured,
            framework_character_source="configured_override",
        )

    if character_id in DRC_TO_FRAMEWORK_CHARACTER_NAME:
        framework_character = DRC_TO_FRAMEWORK_CHARACTER_NAME[character_id]
        source = (
            "mapped_default"
            if framework_character == DEFAULT_FRAMEWORK_CHARACTER_NAME
            else "mapped_specific"
        )

        return FrameworkCharacterMapping(
            drc_character_id=character_id,
            framework_character=framework_character,
            framework_character_source=source,
        )

    return FrameworkCharacterMapping(
        drc_character_id=character_id,
        framework_character=DEFAULT_FRAMEWORK_CHARACTER_NAME,
        framework_character_source="fallback_default",
    )


def resolve_framework_character_name(character_id: str) -> str:
    """
    Backward-compatible helper for older v0.31 checks and scripts.

    New v0.32 code should prefer ``resolve_framework_character_mapping`` so it
    can expose framework character source metadata to the app/debug contract.
    """

    return resolve_framework_character_mapping(character_id).framework_character
