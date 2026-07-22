# Character Selection UX Copy

Milestone: v1.4.0 Day5

This document defines the small copy surface used to make the bundled demo characters easier to understand from the character selection flow.

The goal is not to turn Daily Rhythm Companion into a large character platform. The goal is to make the existing three demo characters easier to distinguish while keeping the app-facing contract stable and testable.

## Scope

Day5 covers selection-facing copy and metadata polish only:

```text
- character card headline
- short tagline
- selection summary
- tone label
- safe expectation copy
- metadata responsibility boundaries
```

Day5 does not add new characters, introduce a custom character editor, require a real AI Character Framework checkout, call external LLM providers, or change the fixed v1.3.0 release zip.

## Stable contract vs selection copy

Stable app-facing fields remain the same:

```text
character_id
display_name
description
personality_type
speaking_style
advice_style
```

Selection UX copy is a presentation layer on top of those fields. It should be safe to revise copy wording without breaking saved DailyRecord history or DRC-to-FW mapping.

Selection copy should not become a new hidden compatibility contract unless a later version explicitly promotes it.

## Character selection copy matrix

| character_id | display name | selection headline | short tagline | tone label | selection summary |
| --- | --- | --- | --- | --- | --- |
| `gentle_mina` | ミナ | やさしく整える | 休息に寄り添う落ち着いた相棒 | 休息重視 / やさしい | 疲れ気味の日でも、無理なく整える一言をくれるキャラクター。 |
| `cheerful_sora` | ソラ | 明るく背中を押す | 前向きな勢いをくれる相棒 | 前向き / 元気 | 少し気分を上げたい日に、軽く動き出せる言葉をくれるキャラクター。 |
| `cool_rei` | レイ | 短く実用的に整理する | 落ち着いて次の一手を出す相棒 | 実用重視 / 端的 | 忙しい日でも、今できる小さな行動へ整理してくれるキャラクター。 |

## Safe expectation copy

Character selection should set expectations conservatively:

```text
- キャラごとに話し方や助言の雰囲気が変わります。
- 睡眠データや気分入力をもとに、軽い日々の振り返りを返します。
- 医療的な診断や治療の助言ではありません。
- データが不足している場合は、不足している前提で控えめに返します。
```

Do not imply that a character can provide a medical diagnosis, treatment advice, health improvement guarantees, diagnose health, improve sleep, treat symptoms, or replace professional advice.

## Metadata responsibility boundary

Backend responsibility:

```text
- provide stable character identifiers and existing profile fields
- keep character_id stable for DailyRecord history
- keep DRC-to-FW mapping explicit and testable
- avoid exposing provider-specific or FW-internal implementation details through selection copy
```

Flutter/UI responsibility:

```text
- render selection copy in a compact card or list
- avoid overloading the selection screen with long profiles
- keep the current selection obvious
- keep fallback behavior understandable when character metadata is unavailable
```

Docs/check responsibility:

```text
- keep this copy matrix aligned with docs/character_experience_inventory.md
- keep this copy matrix aligned with docs/character_advice_tone_matrix.md
- keep release cleanup checkpoint in the v1.4.0 release path
```

## Link to tone matrix

The selection copy should summarize character intent. The actual advice posture remains defined by `docs/character_advice_tone_matrix.md`.

The selection UX should make the three characters easier to choose before advice generation, while the advice tone matrix keeps generated or mock advice conservative and non-medical.


---

## Mapping note

Selection-facing copy does not change framework character routing by itself.

The current DRC character_id to AI Character Framework character mapping is documented in [docs/character_framework_mapping.md](character_framework_mapping.md). Day5 copy can make the three bundled demo characters feel different in the UI, while Day6 keeps the FW mapping explicit and testable.
