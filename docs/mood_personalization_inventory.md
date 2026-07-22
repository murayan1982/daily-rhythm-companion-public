# Mood personalization inventory

## Position

This document records the current Daily Rhythm Companion mood input surface before v1.5.0 changes it.

v1.5.0 should make the daily advice loop feel more personal, but the first implementation boundary stays small:

```text
stable mood IDs + presentation labels + optional lightweight preference hints
```

The current app already passes mood through the advice loop and stores it in DailyRecord history. Day2 documents that contract so later work can add character-aware mood labels and user-adjusted labels without breaking mock-safe behavior or saved records.

## Current stable mood IDs

Current app-facing mood IDs:

```text
energetic
normal
tired
```

Current default:

```text
normal
```

These IDs are stable internal values for the advice contract. They are not the same thing as display copy.

Current Japanese display labels:

```text
energetic -> 元気
normal -> ふつう
tired -> だるい
```

## Current Flutter mood surface

Current UI source:

```text
app/lib/screens/home_screen.dart
```

Current responsibilities:

```text
- holds _selectedMood with the default value normal
- renders three ChoiceChip options for energetic / normal / tired
- formats display labels through _formatMoodLabel
- explains advice posture through _formatMoodSupportMessage
- shows a compact advice focus through _formatMoodAdviceIntent
- passes the selected mood to BackendApiClient.createAdvice
- shows mood in Daily Loop overview, advice readiness, advice result, and save preview
```

Current API client source:

```text
app/lib/services/backend_api_client.dart
```

Current responsibilities:

```text
- includes mood in the /advice request body
- keeps mood as a simple string field
```

Current Flutter history source:

```text
app/lib/models/daily_record.dart
```

Current responsibilities:

```text
- preserves the saved mood ID from DailyRecord
- maps known mood IDs to display labels through displayMood
- falls back to the raw value for unknown future-compatible mood IDs
```

## Current backend mood surface

Current request model:

```text
backend/app/models/advice.py
```

Current contract:

```text
AdviceRequest.mood: str
```

Current prompt builder source:

```text
backend/app/services/advice_prompt_builder.py
```

Current responsibilities:

```text
- defines MOOD_LABELS for energetic / normal / tired
- treats mood values as stable internal IDs
- includes User mood in the advice prompt
- adjusts advice guidance by sleep availability, sleep quality, recent trend, and mood
- keeps health wording non-diagnostic and conservative
```

Current mock engine source:

```text
backend/app/engines/mock_engine.py
```

Current responsibilities:

```text
- creates deterministic mock advice from normalized sleep, mood, and character context
- converts mood IDs into Japanese user-facing labels
- varies advice for energetic / normal / tired
- does not invent sleep details when current sleep is unavailable
```

Current DailyRecord sources:

```text
backend/app/models/daily_record.py
backend/app/services/advice_daily_record_saver.py
backend/app/services/daily_record_store.py
```

Current responsibilities:

```text
- store mood as a required string
- include mood in the saved DailyRecord
- preserve advice_basis values such as sleep+mood+character and recent_sleep_trend+mood+character
```

## Current advice basis behavior

Mood is already part of the advice basis.

Current expected basis values include:

```text
sleep+mood+character+mock
sleep+mood+character+framework
sleep+mood+character+framework_fallback
recent_sleep_trend+mood+character+mock
recent_sleep_trend+mood+character+framework
recent_sleep_trend+mood+character+framework_fallback
```

The important point for v1.5.0 is that personalization should extend this context carefully, not replace or obscure the existing source/basis labels.

## Day2 boundary decisions

### Stable contract

Keep these stable for now:

```text
- AdviceRequest.mood remains a string ID.
- energetic / normal / tired remain the current recognized mood IDs.
- normal remains the default mood.
- DailyRecord.mood continues storing the stable mood ID.
- mock advice remains deterministic and testable.
```

### Presentation layer

Allowed v1.5.0 direction:

```text
- character-aware mood choice copy
- character-aware support text around the same mood IDs
- user-adjusted mood labels that map back to stable mood IDs
- small advice-focus wording changes that do not change the saved ID contract
```

Display copy can become more personal, but the request and history contract should still depend on stable IDs.

### Lightweight personalization layer

Possible future fields, if needed:

```text
preferred_advice_tone
preferred_daily_focus
mood_label_overrides
short_profile_hint
```

These should stay lightweight, optional, and app-facing. They should not become a hidden medical profile, a large personal-data store, or a source of diagnostic claims.

### Safety boundary

Mood and personalization must not introduce:

```text
- medical diagnosis
- treatment advice
- health improvement guarantees
- alarmist sleep interpretation
- hidden real API calls
- hidden provider-backed LLM calls
- raw provider payloads or secrets in logs, responses, docs, or release packages
```

History-derived trend or preference context must not be presented as today's measured sleep state.

## Proposed Day3 direction

Day3 can define the first character-aware mood choice copy matrix.

Suggested Day3 scope:

```text
- keep mood IDs unchanged: energetic / normal / tired
- add character-specific labels or subtitles for gentle_mina, cheerful_sora, and cool_rei
- keep user-adjusted labels as a documented future extension, not necessarily implemented yet
- verify copy stays non-medical and does not imply diagnosis
- keep mock-safe checks source-tree only
```
