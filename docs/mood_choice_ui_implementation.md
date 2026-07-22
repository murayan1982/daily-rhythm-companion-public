# Mood choice UI implementation

## Position

This document records the v1.5.0 Day4 implementation of character-aware mood choice display copy in the Flutter home screen.

Day4 implements the Day3 copy matrix in the UI presentation layer only. It is presentation-layer copy, not a stored mood value change.

Core boundary:

```text
stable mood IDs stay the same; character-aware labels are display copy only.
```

## What changed

Day4 updates:

```text
app/lib/screens/home_screen.dart
```

The UI now resolves mood display copy from the selected character when the character is one of the bundled DRC demo characters:

```text
gentle_mina
cheerful_sora
cool_rei
```

The existing fallback/default labels remain available for unknown or test characters:

```text
energetic -> 元気
normal -> ふつう
tired -> だるい
```

## Character-aware display behavior

When a bundled DRC character is selected, the Mood section, Daily Loop overview, pre-advice confirmation, and advice status chips can display character-aware labels and advice focus text.

The stable mood IDs remain:

```text
energetic
normal
tired
```

The selected mood state remains:

```text
String _selectedMood = 'normal';
```

Advice creation still sends:

```text
mood: _selectedMood
```

## Copy source in Flutter

The Flutter implementation uses a small private presentation model:

```text
_MoodChoiceCopy
_defaultMoodChoiceCopy
_characterAwareMoodChoiceCopy
_resolveMoodChoiceCopy
```

This keeps character-aware labels close to the home screen presentation layer for now.
It does not introduce a profile database, settings persistence, or a custom character authoring system.

## Preserved API and persistence contract

Day4 does not change:

```text
- backend/app/models/advice.py AdviceRequest.mood
- backend/app/models/daily_record.py DailyRecord.mood
- advice_basis labels such as sleep+mood+character
- backend prompt contract
- mock advice engine behavior
- Framework character mapping
- release artifacts
```

User-adjusted mood labels remain a future extension. When added later, they should still map back to the stable IDs unless a separate explicit contract change is introduced.

## Safety wording boundary

Day4 UI copy remains conservative, lightweight, non-medical, and non-diagnostic.

Allowed:

```text
- energy-level framing
- rest/activity preference framing
- character-flavored display labels
- fallback display copy for unknown characters
```

Avoid:

```text
- diagnosis
- treatment advice
- medical claims
- health improvement guarantees
- interpreting mood as measured health data
- presenting history-derived trends as today's measured sleep state
```

## Verification

Day4 is verified by:

```powershell
python scripts\check_v150_mood_personalization_day4.py
```

The check is source-tree and mock-safe. It does not run Flutter, call external LLM providers, require AI Character Framework checkout, call Google Health real APIs, create release artifacts, or rebuild release artifacts.
