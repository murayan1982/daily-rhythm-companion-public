# Mood choice copy matrix

## Position

This document defines the v1.5.0 Day3 character-aware mood choice copy matrix.

Day3 intentionally changes documentation and validation only. It does not change the app-facing mood request contract, saved DailyRecord shape, or backend advice behavior yet.

Core boundary:

```text
stable mood IDs stay the same; character-aware mood choice copy is presentation-layer copy.
```

## Stable mood IDs

The current stable mood IDs remain:

```text
energetic
normal
tired
```

Current default remains:

```text
normal
```

These IDs are the values passed through `AdviceRequest.mood` and saved in `DailyRecord.mood`.

Character-aware labels, subtitles, support messages, and advice focus text must map back to these stable mood IDs instead of becoming new stored values.

## Characters covered

The matrix covers the current bundled demo characters:

```text
gentle_mina / ミナ
cheerful_sora / ソラ
cool_rei / レイ
```

The goal is to make the mood input feel less generic while keeping the DRC character contract small and testable.

## Copy responsibilities

The mood choice copy can have three presentation parts:

```text
label: short chip-facing text
subtitle: compact helper text near the selected mood
advice_focus: short phrase used before advice generation
```

These are presentation fields only. They do not change:

```text
- AdviceRequest.mood
- DailyRecord.mood
- advice_basis source labels
- Framework character mapping
- mock-safe default behavior
```

## Character-aware mood copy matrix

### gentle_mina / ミナ

ミナはやさしく休息寄り。選択コピーは、安心感と無理しない方向に寄せる。

| stable mood ID | label | subtitle | advice_focus |
| --- | --- | --- | --- |
| energetic | いい感じ | 調子がよさそう。がんばりすぎず、いい流れを保つ提案にするね。 | いい流れを保つ |
| normal | いつも通り | 今日は落ち着いていけそう。生活リズムを崩さない提案にするね。 | 穏やかに整える |
| tired | ちょっと休みたい | 今日は回復優先で大丈夫。負担を減らす提案にするね。 | 回復を優先する |

### cheerful_sora / ソラ

ソラは明るく前向き。選択コピーは、軽い背中押しとポジティブさに寄せる。

| stable mood ID | label | subtitle | advice_focus |
| --- | --- | --- | --- |
| energetic | いけそう！ | 今日は勢いがありそう。楽しく進めつつ、使いすぎない提案にするよ。 | 楽しく進める |
| normal | ぼちぼち | いつもの調子でいけそう。小さく前に進める提案にするよ。 | 小さく進める |
| tired | 省エネで | 今日は省エネでOK。元気を取り戻しやすい提案にするよ。 | 省エネで整える |

### cool_rei / レイ

レイは落ち着いて実用寄り。選択コピーは、短く判断しやすい言葉に寄せる。

| stable mood ID | label | subtitle | advice_focus |
| --- | --- | --- | --- |
| energetic | 高め | 活動量を上げられる状態。優先度を絞って進める提案にします。 | 優先度を絞って進める |
| normal | 標準 | 通常運転。リズム維持を中心に提案します。 | リズムを維持する |
| tired | 低め | 回復優先。今日は負荷を抑える提案にします。 | 負荷を抑える |

## User-adjusted mood labels

user-adjusted mood labels remain a future extension after Day3.

Allowed future direction:

```text
- user can adjust display labels for the existing stable mood IDs
- adjusted labels map back to energetic / normal / tired
- saved DailyRecord.mood still stores the stable ID
- history can display the stable ID through the label available at render time
```

Do not treat user-adjusted labels as new mood IDs until a later explicit contract change exists.

## Safety wording boundary

Character-aware mood copy must remain conservative, non-medical, and non-diagnostic.

Allowed:

```text
- lightweight preference and mood framing
- gentle energy-level language
- practical rest/activity suggestions
- clear fallback when sleep data is unavailable
```

Avoid:

```text
- medical diagnosis
- treatment advice
- health improvement guarantees
- alarmist interpretation of sleep or mood
- claiming mood data is measured health data
- pretending history-derived trends are today's measured sleep state
```

## Implementation boundary after Day3

Day3 does not implement Flutter UI changes yet.

A later implementation day can use this matrix to update `app/lib/screens/home_screen.dart` while preserving:

```text
- _selectedMood stores stable IDs
- _buildMoodChoiceChip receives stable IDs
- _formatMoodLabel remains a safe fallback path
- advice creation still sends mood: _selectedMood
- DailyRecord history still stores mood as a string ID
```

Day3 is mock-safe and source-tree only. It does not call external LLM providers, require AI Character Framework checkout, call Google Health real APIs, run Flutter, create release artifacts, or rebuild release artifacts.
