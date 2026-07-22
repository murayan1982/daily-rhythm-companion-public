# Personalization profile boundary

## Position

This document records the v1.5.0 Day6 boundary for lightweight personalization profile fields.

Day6 keeps the normal development path mock-safe.

v1.5.0 has already made mood choices feel less generic by adding character-aware mood display copy while preserving the stable mood ID contract.

Day6 defines what kind of future profile/preferences are allowed before any persistence, backend schema, or account-level profile work is introduced.

Core rule:

```text
personalization can adjust presentation and advice focus hints, but it must not become medical profiling, diagnosis, or a heavy account/profile system.
```

## Current stable contracts remain unchanged

Day6 does not change the existing app/backend contract.

Stable mood IDs remain:

```text
energetic
normal
tired
```

These contracts remain unchanged:

```text
AdviceRequest.mood
DailyRecord.mood
sleep+mood+character
recent_sleep_trend+mood+character
```

Character-aware labels remain a presentation layer that maps back to the stable mood IDs.

## Allowed lightweight profile candidates

The following fields are allowed as future candidates, but are not implemented by Day6:

```text
nickname
preferred_mood_labels
advice_focus_preference
tone_preference
```

Intended meaning:

```text
nickname:
  Optional display-only name used in local UI copy.

preferred_mood_labels:
  Optional user-adjusted display labels that still map to energetic / normal / tired.

advice_focus_preference:
  Optional lightweight preference for advice framing, such as rest_first, small_step, or rhythm_keep.

tone_preference:
  Optional lightweight preference for presentation tone, such as gentle, cheerful, concise, or default.
```

These fields should be treated as app-level hints, not health records.

## Explicit non-goals

Day6 explicitly does not introduce:

```text
- profile persistence
- account sync
- authentication
- cloud profile storage
- backend user-profile endpoints
- DailyRecord schema changes
- AdviceRequest schema changes
- profile-driven medical claims
- diagnosis or treatment logic
- provider-specific LLM personalization memory
- raw health-data profiling
```

## Safety boundaries

Future profile/preference fields must avoid storing or exposing:

```text
- secrets, tokens, API keys, or authorization headers
- raw provider payloads
- local token file paths
- private absolute machine paths
- medical diagnosis, treatment, medication, or condition fields
- precise location
- sensitive identity attributes
```

If a future feature needs any sensitive or long-lived personal data, it should be designed as a separate explicit opt-in milestone, not smuggled into v1.5.0 mood personalization.

## Mapping rule

User-adjusted mood labels must never replace stable mood IDs.

Allowed shape:

```text
user label: "今日はゆるめ"
stable mood ID: tired
```

Not allowed:

```text
mood: "今日はゆるめ"
```

The backend and DailyRecord history should continue to receive and store stable mood IDs unless a future schema migration is explicitly designed and verified.

## Conservative wording rule

Profile-aware wording can make advice feel warmer or more relevant, but it must stay conservative:

```text
- no diagnosis
- no treatment claims
- no guaranteed improvement
- no alarmist health language
- no pretending history-derived trend is today's measured sleep state
```

## Verification

Day6 is verified by:

```powershell
python scripts\check_v150_mood_personalization_day6.py
```

The Day6 check verifies this boundary document, the Day6 internal note, roadmap/README/script inventory, previous Day5 coverage, and the unchanged backend mood contracts.

Day6 does not implement profile persistence, call external LLM providers, require AI Character Framework checkout, call Google Health real APIs, create release artifacts, rebuild release artifacts, or change the fixed v1.4.0 release zip.
