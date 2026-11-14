# DRC v4.1.0 GP-2 Local Advice Migration Corrective R1

## Control metadata

```text
Task: DRC_V410_GP2_LOCAL_ADVICE_MIGRATION_CORRECTIVE_R1
Baseline: 2beb34d57ded8a9d7c67e5a39b7729944fd77e58
Surface: exact M10 A4 D0
Stage / commit / push: NOT_AUTHORIZED
Corrective implementation and product/test copy correction: AUTHORIZED
```

## User-approved local-only beta decision

The user selected `LOCAL_ONLY_DETERMINISTIC_ADVICE` and
`NO_REMOTE_PRODUCTION_BACKEND` on 2026-11-13 for the v4.1.0 GitHub Android
Public Beta. GP0-D03 is approved only for this active local-only track. A future
Cloud Backend remains `DEFERRED / NOT_CANCELLED` and requires a new decision
and implementation authorization.

## Approved scope

This slice derives one daily message from the accepted ephemeral mood and
character selections. It changes only the exact ten-path surface recorded by
this Control. It does not persist either selection and performs no asynchronous
or external operation.

## Exact nine-message matrix

| Character | Mood | Message |
| --- | --- | --- |
| gentle_mina | energetic | 今日は調子がよさそうですね。無理に予定を増やさず、気持ちよいペースを保っていきましょう。 |
| gentle_mina | normal | いつもの調子を大切に、ひとつずつ進めてみましょう。少し疲れたら、早めに休憩して大丈夫です。 |
| gentle_mina | tired | 今日は無理に頑張りすぎなくて大丈夫です。まずは短い休憩と、できることをひとつだけにしましょう。 |
| cheerful_sora | energetic | いい調子ですね！今の勢いを使って、やりたいことをひとつ始めてみましょう。 |
| cheerful_sora | normal | 今日は小さく動き出せれば十分です。まずは気軽にひとつ、始めてみましょう！ |
| cheerful_sora | tired | 疲れている日は小さな一歩でOKです。水分をとって、負担の少ないことから始めましょう。 |
| cool_rei | energetic | 調子は良好です。優先することを一つ決め、終えたら次へ進みましょう。 |
| cool_rei | normal | 今日の優先事項を一つ決めましょう。終えたら短い休憩を入れてください。 |
| cool_rei | tired | 今日はタスクを増やさない方がよいでしょう。必要なことを一つに絞り、終えたら休みましょう。 |

## Pure Dart deterministic model

`production_local_advice.dart` imports only the production mood and character
models. Its exhaustive record-pattern lookup returns an immutable result that
contains the selected mood, selected character, and exact message. It has no
Flutter, random, clock, locale, network, storage, service, legacy model,
provider, medical-diagnosis, treatment, or outcome-guarantee dependency.

## Ephemeral state flow

`ProductionJourneyOverview` receives the existing Mood Check-in and Character
Selection callbacks, holds nullable selections only in widget state, and passes
them to step 4. Advice updates synchronously after either selection changes.
Nothing is saved or restored after app restart.

## User-visible copy alignment

Mood and Character selection copy now states that the selection is reflected
immediately in this screen's local message. Persistence and app-restart
restoration remain unimplemented. The stale statement that both saving and
advice reflection were still being prepared has been removed from production
journey source. This Corrective does not alter the exact nine-message matrix or
the ephemeral state flow.

## UI and accessibility contract

Step 4 represents both-unselected, mood-only, character-only, and ready states.
The ready state exposes the character name, mood, and fixed message. Permanent
copy explains local fixed rules, no AI/external-server transmission, and the
non-medical boundary. Semantics expose readiness and ready content without
button actions. The layout supports a 320-by-568 viewport and 2.0 text scale.

## Source and import boundary

There is no Backend, HTTP/HTTPS, URL, endpoint, credential, API key, network,
persistence, DailyRecord, AI/LLM generation, AI Character Framework runtime
routing, provider/model selection, health, sleep, analytics, or platform access.
Accepted Mood and Character source/tests remain unchanged.

## Verification commands

From `app`:

```text
flutter analyze --no-pub
flutter test --no-pub test/production_local_advice_test.dart
flutter test --no-pub test/production_mood_check_in_test.dart
flutter test --no-pub test/production_character_selection_test.dart
flutter test --no-pub test/production_journey_shell_test.dart
flutter test --no-pub test/production_composition_boundary_test.dart
flutter test --no-pub test/production_core_scope_boundary_test.dart
flutter test --no-pub test/widget_test.dart
```

## D03 update

GP0-D03 approved value is
`V410_GITHUB_BETA_LOCAL_ONLY_NO_REMOTE_BACKEND`, with user evidence recorded
2026-11-13 and implementation authorization limited to this task. D08 remains
`NOT_DECIDED`; D11 remains `APPROVED`.

## Explicit non-claims and deferred work

This slice does not claim Cloud Backend, deployment, connectivity, endpoint,
domain, credential, AI-generated advice, Framework routing, persistence,
restart restoration, health/Fitbit integration, permissions, analytics, text
chat, history, artifact exclusion proof, public APK readiness, Privacy Policy,
D08 closure, GP-2 completion, or GP-3 completion. Cloud/AI/Framework work is
`DEFERRED / NOT_CANCELLED`.

## Remaining GP-2 / GP-3 work and Corrective R1 stop boundary

Mood persistence, character-aware mood-copy decisions, remaining Core-flow
migration, artifact exclusion proof, and GP-3 refinement remain open. Stop
after the Corrective R1 required verification and review handoff. Do not stage, commit, push,
build, sign, tag, publish a Release/asset, or expand the implementation surface.
