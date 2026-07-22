# Character Framework Mapping

Milestone: v1.4.0 Day6

This document records the app-facing DRC character_id to AI Character Framework character mapping policy.

Daily Rhythm Companion currently uses a small app-level character set for demo clarity. AI Character Framework remains the framework/runtime boundary. The mapping should be explicit even when all bundled DRC characters currently route to the framework `default` character.

## Current mapping table

| DRC character_id | Display name | Current FW character | Normal source metadata | Notes |
| --- | --- | --- | --- | --- |
| `gentle_mina` | ミナ | `default` | `mapped_default` | Gentle/rest-focused DRC presentation; no dedicated FW-side character required yet. |
| `cheerful_sora` | ソラ | `default` | `mapped_default` | Cheerful/positive DRC presentation; no dedicated FW-side character required yet. |
| `cool_rei` | レイ | `default` | `mapped_default` | Cool/practical DRC presentation; no dedicated FW-side character required yet. |

The source of truth for this mapping is:

```text
backend/app/engines/character_mapping.py
```

## Source metadata

DRC exposes framework character metadata so demo operators can tell why a framework character was selected.

```text
mapped_default
configured_override
fallback_default
mapped_specific
```

Meanings:

```text
mapped_default:
  A known DRC character_id mapped through the table to the framework default character.

configured_override:
  A local/demo operator set FRAMEWORK_CHARACTER to a non-default value.
  This is useful for trying a FW-side character without changing DRC app-facing IDs.

fallback_default:
  An unknown DRC character_id fell back to the framework default character instead of crashing.

mapped_specific:
  Reserved for a future table entry that maps a known DRC character_id to a specific FW character.
```

## Local/demo override

A configured local/demo operator may set:

```env
FRAMEWORK_CHARACTER=<framework-character-name>
```

When this value is non-empty and not `default`, the framework engine should report:

```text
framework_character=<framework-character-name>
framework_character_source=configured_override
```

This does not make configured FW/LLM checks mandatory. Normal v1.4.0 checks remain mock-safe.

## Responsibility split

DRC owns:

```text
- app-facing character_id values
- display names
- selection UX copy
- character advice tone hints
- DailyRecord compatibility for saved character IDs
- explicit mapping table and source metadata
```

AI Character Framework owns:

```text
- FW-side character files or presets when they exist
- framework runtime session creation
- provider/model execution details
- provider credentials and provider-specific configuration
```

The current v1.4.0 scope does not require dedicated FW-side character files for ミナ, ソラ, or レイ. If the framework later adds matching character assets, update the mapping table, this document, and the Day6 check together.

## Safety and non-goals

Day6 mapping verification does not require a real AI Character Framework checkout.

Day6 mapping verification does not:

```text
- add new DRC characters
- require a real AI Character Framework checkout
- require provider credentials
- call external LLM providers
- call Google Health real APIs
- create release artifacts
- change the fixed v1.3.0 release zip
- make medical diagnosis, treatment advice, or health improvement guarantees
```
