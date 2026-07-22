# Mood choice Flutter test policy

## Position

This document records the v1.5.0 Day5 Flutter test coverage for character-aware mood choice display copy.

Day4 implemented character-aware display labels in the Flutter Home screen. Day5 adds test coverage to prove that this presentation change does not change the app-facing mood ID contract.

Core boundary:

```text
character-aware mood labels are UI copy; saved/API mood values remain stable IDs.
```

## What Day5 verifies

Day5 adds widget-test coverage for the bundled DRC characters:

```text
gentle_mina / ミナ
cheerful_sora / ソラ
cool_rei / レイ
```

The test verifies that the Home screen displays character-aware mood labels:

```text
ミナ: いい感じ / いつも通り / ちょっと休みたい
ソラ: いけそう！ / ぼちぼち / 省エネで
レイ: 高め / 標準 / 低め
```

It also verifies that selecting a character-aware mood still sends the stable mood ID to advice creation:

```text
energetic
normal
tired
```

## Preserved contract

Day5 does not change:

```text
- AdviceRequest.mood
- DailyRecord.mood
- advice_basis values such as sleep+mood+character
- backend prompt contract
- mock advice engine behavior
- Framework character mapping
- release artifacts
```

The Flutter UI can show character-aware labels, but the selected value remains `_selectedMood`, and advice creation continues to call:

```text
mood: _selectedMood
```

## Test coverage added

Day5 updates:

```text
app/test/widget_test.dart
```

The new widget test uses a dedicated fake backend client that exposes all three bundled demo characters and records the mood value passed to `createAdvice`.

The test path is intentionally app-side only:

```text
- render HomeScreen
- confirm ミナ mood copy
- switch to ソラ and confirm ソラ mood copy
- switch to レイ and confirm レイ mood copy
- select レイ's tired label
- create advice
- assert the recorded mood value is tired
- assert the recorded character ID is cool_rei
```


## Day5 marker summary

```text
Flutter widget-test stable mood IDs
gentle_mina cheerful_sora cool_rei
いい感じ / 省エネで / 低め
mood: _selectedMood
AdviceRequest.mood
DailyRecord.mood
mock-safe
```

## Verification

Day5 is verified by:

```powershell
python scripts\check_v150_mood_personalization_day5.py
```

The Day5 check runs the Day4 source-tree check and `flutter test` from the `app/` directory.

Day5 does not call external LLM providers, require AI Character Framework checkout, call Google Health real APIs, create release artifacts, rebuild release artifacts, or change the fixed v1.4.0 release zip.
