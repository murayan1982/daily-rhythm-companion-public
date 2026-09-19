# DRC v4.1.0 GP-2 Production Journey Shell

## Control metadata

```text
Task: DRC_V410_GP2_PRODUCTION_JOURNEY_SHELL_CORRECTIVE_R1
Baseline: 438b8e82c2fb66181289a0a5a60897993effe62f
Development line: DRC v4.1.0
Phase: GP-2
Implementation: APPROVED
Stage / commit / push: NOT_AUTHORIZED
```

## Closed prerequisites

- Control A closed at `e0e7e8434e49f812735b9d4a510997ad0108d174`.
- Control B closed at `45d6a543165321e30757808095a545b0d9bc9ec1`.
- The Backend/privacy decision control closed at
  `438b8e82c2fb66181289a0a5a60897993effe62f`.
- GP0-D03 and GP0-D08 remain `NOT_DECIDED`.

## Approved scope

GP2-S01 approves `TEXT_CORE_PLUS_CHAT`. Control C represents that scope as this
exact local sequence:

| Order | Journey step | Production capability | State |
| --- | --- | --- | --- |
| 1 | 睡眠を確認 | `sleepHealthConnection` | Health/provider decision pending |
| 2 | 気分を記録 | `moodCheckIn` | Static planned step |
| 3 | キャラクターを選択 | `characterSelection` | Static planned step |
| 4 | 今日のアドバイス | `dailyAdvice` | Static planned step |
| 5 | 会話を続ける | `optionalTextChat` | Static planned, optional step |
| 6 | 履歴を振り返る | `history` | Static planned step |

## Local-only UI boundary

The production home screen renders the six items from an immutable typed model.
It makes no connection, reads no live data, accepts no user input, and exposes no
button, gesture action, navigation, permission request, or platform call. The
sleep step says that connection preparation is in progress; it does not name or
imply a provider. The production Backend remains unwired.

## Accessibility and responsive contract

- Visual and semantic order are both 1 through 6.
- Each semantic item includes its order, user-facing title, optional state when applicable, and user-facing description or preparation state.
- Text chat is visibly and semantically marked optional.
- Cards have flexible height and Material text styles.
- The home shell scrolls vertically, uses horizontal padding, and limits content
  width on large displays.
- Focused tests cover a 320 by 568 viewport and 2.0 text scaling without overflow
  or framework exceptions.

## Source and import boundary

`production_journey_step.dart` imports only the existing production capability
model. `production_journey_overview.dart` imports Flutter Material and the local
journey model. `production_home_screen.dart` imports Flutter Material and the
local component. No legacy screen, service, model, widget, operator, network
client, URL, endpoint, credential, or transport configuration is introduced.
The existing directive parser, adversarial guard, and recursive exclusion tests
remain active.

## Verification commands

Run from `app/`:

```text
flutter analyze --no-pub
flutter test --no-pub test/production_journey_shell_test.dart
flutter test --no-pub test/production_composition_boundary_test.dart
flutter test --no-pub test/production_core_scope_boundary_test.dart
flutter test --no-pub test/widget_test.dart
```

Static verification also checks the exact ten-file surface, empty index,
encoding and EOF LF, protected hashes, import and transport exclusions,
undecided D03/D08 state, and immutable v4.0.0 release tuple.

## Non-claims

This control does not claim working health connection, provider selection,
runtime permission, mood or character input, advice generation, text chat,
history retrieval, Backend connectivity, route expansion, Android release
wiring, artifact exclusion, policy completion, GP-2 completion, GP-3 completion,
or production readiness.

## Remaining work

- GP-2: complete production separation, non-product Backend boundary, authorized
  core-flow migration, route decisions, and artifact exclusion proof.
- GP-3: implement and verify the usable daily journey and its states.
- GP-4: wire the approved release entrypoint, identity, signing, and production
  configuration under separate authorization.
- GP-5: reconcile implemented behavior with privacy, deletion, Data safety, and
  Health Apps declarations after D03/D08 decisions.

## Rollback and stop boundary

Stop without staging or committing if the baseline changes, the surface exceeds
exact M6 A4 D0, a protected file changes, a production import crosses the
allowlist, an interactive/network/platform behavior appears, or required
verification fails. Rollback or expansion requires separate authorization; this
control does not use reset, checkout, or revert.
