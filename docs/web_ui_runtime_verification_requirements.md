# Web UI runtime verification requirements

DRC verification must include browser/smartphone UI-visible results, not only direct API responses.

## Core rule

```text
API success alone does not satisfy the smartphone Web demo requirement.
```

The operator must be able to see the relevant result, status, or fallback state in the Web UI.

## Required UI-visible surfaces

The Web UI verification path should cover:

```text
- Home advice result
- character list and selected character
- sleep summary or safe unavailable state
- mood selection
- DailyRecord save result
- History review result
- report-informed advice/reflection state when used
- capability status for LLM / STT / TTS / Live2D-VTS
```

## Capability evidence expectations

For each configured FW capability:

```text
LLM:
- UI shows generated or fallback advice result.
- source/fallback state is understandable.

STT:
- UI shows recognized text or a safe unavailable/skipped state.

TTS:
- UI shows voice output attempt/status, success, unavailable, skipped, or fallback.

Live2D/VTS:
- UI shows motion trigger/status, connected/unavailable/skipped/fallback state.
```

## Manual evidence

Manual smartphone Web smoke documentation should record:

```text
- device/browser used
- Web UI URL shape
- backend API base URL shape
- selected character
- selected mood
- capability mode
- visible UI result
- fallback/unavailable state if applicable
```

Do not paste secrets, tokens, local credential paths, or raw provider payloads into shared logs.
