# Character Experience Inventory

Updated: 2026-05-21  
Milestone: v1.4.0 Day2

## Purpose

This document records the current Daily Rhythm Companion character experience before adding or refining character-facing behavior in v1.4.0.

v1.4.0 should make the bundled demo characters easier to distinguish while keeping the app small, mock-safe, and useful as an AI Character Framework demo application.

## Current bundled characters

| DRC character ID | Display name | Personality type | Speaking style | Advice style | Current role |
| --- | --- | --- | --- | --- | --- |
| `gentle_mina` | ミナ | `gentle` | `casual` | `rest_focused` | A gentle morning companion that prioritizes rest and low-pressure pacing. |
| `cheerful_sora` | ソラ | `cheerful` | `casual` | `positive` | A bright companion that turns the user's mood into simple forward momentum. |
| `cool_rei` | レイ | `cool` | `concise` | `practical` | A calm secretary-like companion that gives short, practical next steps. |

The current inventory is intentionally small. v1.4.0 may refine these characters, but it should not turn DRC into a large character platform yet.

## Stable app-facing character contract

These fields are stable app-facing contract fields and should remain explicit:

```text
character_id
display_name
description
personality_type
speaking_style
advice_style
```

Compatibility notes:

```text
- character_id should remain stable because DailyRecord history and FW mapping can depend on it.
- display_name is user-facing and may appear in advice and History.
- description is user-facing selection UX copy.
- personality_type, speaking_style, and advice_style are compact tone hints used by backend prompt/mock logic and Flutter display.
```

## Tone-hint fields

The current tone-hint fields are not a full personality system. They are intentionally small labels that help the backend and UI distinguish characters.

Current labels:

```text
personality_type: gentle | cheerful | cool
speaking_style: casual | concise
advice_style: rest_focused | positive | practical
```

v1.4.0 may clarify or extend the meaning of these labels, but it should avoid adding broad profile fields that are not needed for the current demo.

## Current backend surfaces

Current backend character surfaces:

```text
backend/app/models/character.py
backend/app/services/character_service.py
backend/app/engines/character_mapping.py
backend/app/services/advice_prompt_builder.py
backend/app/engines/mock_engine.py
```

Important behavior:

```text
- /characters returns the bundled CharacterPreset list.
- /advice receives CharacterContext with stable character fields.
- mock advice uses character display name and personality_type to produce deterministic character-facing copy.
- the LLM prompt includes character_id, display_name, personality_type, speaking_style, and advice_style.
```

## Current Flutter surfaces

Current Flutter character surfaces:

```text
app/lib/models/character_preset.dart
app/lib/screens/home_screen.dart
```

Important behavior:

```text
- Flutter parses the same character contract returned by /characters.
- Character Choice displays display_name, description, personality_type, speaking_style, and advice_style.
- Today's Loop and advice readiness reflect the selected character.
- Voice output and motion demo requests can carry the selected character_id as demo metadata.
```

## Framework mapping policy

The current DRC-to-FW character mapping remains explicit:

```text
gentle_mina -> default
cheerful_sora -> default
cool_rei -> default
```

This is acceptable for v1.4.0 Day2 because the app-level character contract still carries DRC character identity and tone hints. Future FW-side character-specific mapping can be added deliberately, but should remain explicit and testable.

Mapping source labels remain important:

```text
mapped_default
mapped_specific
configured_override
fallback_default
```

## Safe wording policy

Character experience improvements must preserve conservative wording:

```text
- no medical diagnosis
- no treatment advice
- no health improvement guarantees
- no alarmist sleep interpretation
- recent history must not be presented as today's sleep
- unavailable sleep data must not be invented
```

## Day2 conclusion

v1.4.0 can safely continue from the existing three-character inventory.

Day3 extension:

```text
Define a small character tone matrix for advice: docs/character_advice_tone_matrix.md defines a small character tone matrix for the Day3 tone matrix without requiring real LLM credentials.
```


## Day5 selection UX copy link

`docs/character_selection_ux_copy.md` defines compact selection-facing copy for the existing three characters. It keeps stable contract fields separate from presentation copy and stays aligned with `docs/character_advice_tone_matrix.md` without requiring real LLM credentials.

docs/character_selection_ux_copy.md defines compact selection-facing copy for the existing three characters. It keeps stable contract fields separate from presentation copy without requiring real LLM credentials.


---

## Framework mapping reference

Day6 keeps DRC-to-FW character mapping explicit in [docs/character_framework_mapping.md](character_framework_mapping.md).

The current v1.4.0 mapping is intentionally conservative: `gentle_mina`, `cheerful_sora`, and `cool_rei` map to the framework `default` character unless a configured local/demo operator uses `FRAMEWORK_CHARACTER` as an explicit override. This preserves mock-safe operation and avoids requiring FW-side character assets during character UX polish.

This keeps Day6 mapping verification explicit without requiring FW-side character assets.
