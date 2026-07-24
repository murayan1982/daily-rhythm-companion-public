# Daily Rhythm Companion post-v2.0.0 task list

更新日: 2026-07-24

## 1. 現在地

```text
Public repository: murayan1982/daily-rhythm-companion-public
immutable capability baseline: v2.0.0
current released version: v2.0.1
release / annotated tag: DRC_v2.0.1
v2.0.1 status: RELEASED
completed maintenance line: v2.0.x COMPLETED / ACCEPTED
current development line: v2.1.0
current small commit: T-1c CURRENT / NOT_COMPLETED
completed phase: C-1 COMPLETED / ACCEPTED
strategic target: v3.0.0
```

v2.0.1の固定ZIP、annotated tag、GitHub Release、公開後SHA-256再検証は完了している。公開済み`DRC_v2.0.0`と`DRC_v2.0.1`を変更せず、今後の変更は新しいコミットと新しいバージョンで行う。

## 2. Source of truth

v2.1.0のauthoritative詳細タスクリスト:

```text
docs/DRC_v210_goal_checklist_small_commit.md
```

実装棚卸し:

```text
docs/v210_fitbit_current_behavior_inventory.md
```

ロードマップ:

```text
roadmap.md
```

完了済みv2.0.xの履歴source of truth:

```text
docs/DRC_v20x_maintenance_checklist.md
```

v2.0.0の完了記録:

```text
docs/DRC_v200_goal_checklist_small_commit.md
release_notes/v2.0.0.md
GitHub Release: DRC_v2.0.0
```

v2.0.0とv2.0.1の公開記録は履歴として保持し、v2.1.0の進捗管理には再利用しない。

---

# 3. 現在の小コミット

## T-1 — Flutter in-app TTS player and artifact-expiry handling

Status: CURRENT / NOT_COMPLETED

実装分割:

```text
T-1a  COMPLETED / ACCEPTED     current TTS/audio handoff inventory and implementation contract
T-1b  COMPLETED / ACCEPTED  Flutter in-app player abstraction, states, and mock-safe tests
T-1c  CURRENT / NOT_COMPLETED                 Home UI integration, expired-artifact recovery, and T-1 acceptance
```

### T-1a — Current TTS/audio handoff inventory and implementation contract

```text
- Backend artifact store/audio routeとFlutter voice-output flowを棚卸しする。
- 24時間TTL、100件上限、opaque MP3 URL、no-store/nosniffを固定する。
- 現状がexternalApplicationへのURL launchであり、in-app playerではないことを記録する。
- play / stop / replay / loading / completion / failure / expired stateが未実装であることを記録する。
- runtime、dependency、existing testsをnormalized hashで固定し、T-1aでは変更しない。
- T-1b/T-1cの責任範囲を固定し、V-1とR-1を前倒ししない。
```

詳細: `docs/v210_tts_player_current_behavior_inventory.md`

受け入れ結果:

```text
- implementation commit: 0b06378
- compileall / T-1a source-tree check: passed
- W-1〜W-5 / C-1 checks / v2.0.x guards: passed
- backend pytest: 110 passed
- Flutter test: 64 passed
- diff review / operator approval / push: passed
- Backend / Flutter runtime changed: false
- dependency / existing tests changed: false
- real Framework/TTS execution: false
- release records changed: false
```

T-1aは2026-07-24にCOMPLETED / ACCEPTEDとなった。T-1bも実装コミット`161e624`でCOMPLETED / ACCEPTEDとなり、T-1cはCURRENT / NOT_COMPLETED、親T-1はCURRENT / NOT_COMPLETEDのままである。

### T-1b — Flutter player abstraction, states, and mock-safe tests

Status: COMPLETED / ACCEPTED
Implementation state: COMPLETED / ACCEPTED

```text
- VoiceOutputAudioEngineのapp-owned interfaceを追加する。
- idle/loading/playing/stopped/completed/failed/expired stateを追加する。
- play/stop/replay/reset/markExpired/disposeをcontrollerへ追加する。
- http/https以外のsourceをengineへ渡さない。
- user-facing messageへraw URL、private path、provider exceptionを出さない。
- reset/dispose後の古いasync完了を無視する。
- fake engineだけでfocused Flutter testを追加する。
- HomeScreen、Backend、pubspec、実TTS、V-1/R-1を変更しない。
```

詳細: `docs/v210_tts_player_controller.md`

受け入れ結果:

```text
- implementation commit: 161e624
- compileall / T-1a / T-1b source-tree checks: passed
- W-1〜W-5 / C-1 checks / v2.0.x guards: passed
- focused Flutter test: 10 passed
- backend pytest: 110 passed
- Flutter test: 74 passed
- diff review / operator approval / push: passed
- Backend runtime / HomeScreen changed: false
- dependency changed: false
- real Framework/TTS execution: false
- release records changed: false
```

T-1bは2026-07-24にCOMPLETED / ACCEPTEDとなった。T-1cはCURRENT / NOT_COMPLETED、親T-1はCURRENT / NOT_COMPLETEDのままである。

---

## C-1 — Post-advice chat lifecycle and UI-state hardening

Status: COMPLETED / ACCEPTED

実装分割:

```text
C-1a  COMPLETED / ACCEPTED     current behavior inventory and implementation contract
C-1b  COMPLETED / ACCEPTED     backend lifecycle outcomes, bounded turns, and tests
C-1c  COMPLETED / ACCEPTED     Flutter lifecycle state, recovery UI, and C-1 acceptance
```

### C-1a — Current behavior inventory and implementation contract

```text
- accepted chat/session boundariesをBackendとFlutterの両方で棚卸しする。
- 既存の30分idle TTL、100 session上限、LRU境界を固定する。
- turn limit未実装、missing-session 404一律、Flutter stale-session recovery不足を記録する。
- Framework outcomeとnormal-user UI stateの契約差を記録する。
- runtime/testファイルをnormalized hashで固定し、C-1aでは変更しない。
- C-1b/C-1cの責任範囲を固定する。
- T-1、V-1、R-1を前倒ししない。
```

詳細: `docs/v210_post_advice_chat_current_behavior_inventory.md`

受け入れ結果:

```text
- implementation commit: a4263ca
- compileall / C-1a source-tree check: passed
- W-1〜W-5 checks / v2.0.x guards: passed
- backend pytest: 100 passed
- Flutter test: 57 passed
- diff review / operator approval: passed
- Backend runtime changed: false
- Flutter runtime changed: false
- existing tests changed: false
- real Framework execution: false
- release records changed: false
```

C-1aは2026-07-24にCOMPLETED / ACCEPTEDとなった。C-1b、C-1c、親C-1も同日にCOMPLETED / ACCEPTEDとなり、T-1がCURRENT / NOT_COMPLETEDである。

### C-1b — Backend lifecycle outcomes, bounded turns, and tests

Status: COMPLETED / ACCEPTED

```text
- accepted 1800秒TTL、100 session、LRUを維持する。
- POST_ADVICE_CHAT_MAX_TURNS=8を追加する。
- ChatLifecycle / ChatOutcome / ChatSessionProblemを追加する。
- expired / evicted / unknownをstructured HTTP 404で区別する。
- turn limit後の送信をrestartable HTTP 409にする。
- removed session本文を保持せず、terminal reason cacheを100件以内に制限する。
- deterministic clock / fake adapterだけでmock-safe回帰を追加する。
- Flutter runtimeとC-1c、T-1、V-1、R-1を前倒ししない。
```

詳細: `docs/v210_post_advice_chat_backend_lifecycle.md`

受け入れ結果:

```text
- implementation commit: 3055995
- C-1a / C-1b source-tree checks: passed
- focused Backend tests: 17 passed
- backend pytest: 110 passed
- Flutter test: 57 passed
- diff review / operator approval: passed
- Flutter runtime changed by C-1b: false
- real Framework execution: false
- release records changed: false
```

C-1bは2026-07-24にCOMPLETED / ACCEPTEDとなった。C-1cと親C-1も同日にCOMPLETED / ACCEPTEDとなり、T-1がCURRENT / NOT_COMPLETEDである。

### C-1c — Flutter lifecycle state, recovery UI, and C-1 acceptance

Status: COMPLETED / ACCEPTED

```text
- ChatLifecycle / ChatOutcome / ChatSessionProblemをFlutterでparseする。
- lifecycle/outcomeなしの旧payloadも安全に読み込む。
- structured HTTP problemをtyped exceptionへ変換する。
- 会話状態、turn進捗、mock/configured/fallback/unavailable/blocked/skippedを表示する。
- terminal stateでは送信欄を閉じ、期限切れ・evicted・unknown・turn limitから直接再開できるようにする。
- normal-user copyとdeveloper detailsを分離する。
- Backend runtime、T-1、V-1、R-1、release recordsを変更しない。
```

詳細: `docs/v210_post_advice_chat_flutter_lifecycle.md`

受け入れ結果:

```text
- implementation commit: c856374
- C-1a / C-1b / C-1c source-tree checks: passed
- focused Flutter tests: 7 passed
- backend pytest: 110 passed
- Flutter test: 64 passed
- diff review / operator approval: passed
- Backend runtime changed by C-1c: false
- Flutter runtime changed by C-1c: true
- real Framework execution: false
- release records changed: false
```

C-1cと親C-1は2026-07-24にCOMPLETED / ACCEPTEDとなった。T-1はCURRENT / NOT_COMPLETED、V-1とR-1はPLANNEDである。

---

## W-5 — Wearable migration correction and configured Google Health verification

Status: COMPLETED / ACCEPTED

実装分割:

```text
W-5a  COMPLETED / ACCEPTED   Fitbit real operator contract and preflight
W-5b1  COMPLETED / ACCEPTED   Google Health API migration audit and legacy Fitbit execution retirement
W-5b2  COMPLETED / ACCEPTED   Configured Google Health API operator verification
```

### W-5a — Fitbit real operator contract and preflight

目的:

```text
- dedicatedなignored Fitbit operator env templateを追加する。
- env値を表示しないnetwork-free preflightを追加する。
- backend/.env上書きを無効化するValidateOnly対応ランチャーを追加する。
- --allow-real-request必須の安全なbackend execution smokeを準備する。
- W-5bのreal OAuth/token/sleep/smartphone Web手順と非公開境界を固定する。
```

変更対象:

```text
backend/env_profiles/fitbit_real_operator.env.example
backend/scripts/run_fitbit_real_operator.ps1
docs/v210_fitbit_real_operator_runbook.md
scripts/smoke_v210_fitbit_real_operator_preflight.py
scripts/smoke_v210_fitbit_real_operator_execution.py
scripts/check_v210_fitbit_real_operator_contract.py
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v210_goal_checklist_small_commit.md
既存v2.1.0 check scriptsのcurrent-state同期
```

W-5a境界:

```text
- real operator executionはまだ実施しない。
- Fitbit backend/Flutter runtime、response model、W-2/W-3/W-4 semanticsを変更しない。
- token、authorization code、OAuth state、raw payload、raw screenshot、
  正確な私的睡眠値、private path、LAN URLはPublicへ記録しない。
- preflight成功やValidateOnly成功だけではW-5完了にならない。
- W-5bとC-1以降の完了要件を前倒ししない。
```

詳細契約: `docs/v210_fitbit_real_operator_runbook.md`

受け入れ結果:

```text
- implementation commit: 7f84980
- default/example network-free preflight: passed
- W-1〜W-5a check: passed
- v2.0.x guards: passed
- backend pytest: 92 passed
- Flutter test: 57 passed
- diff review / operator approval: passed
- real operator execution: false
- release records changed: false
```

W-5aは2026-07-24にCOMPLETED / ACCEPTEDとなった。その後W-5b1とW-5b2も完了し、親W-5はCOMPLETED / ACCEPTEDとなった。

### W-5b1 — Google Health API migration audit and legacy Fitbit execution retirement

Status: COMPLETED / ACCEPTED

```text
- Google公式のFitbit Web APIからGoogle Health APIへの移行方針を固定する。
- 現在のgoogle_health実装がv4 endpoint/scope/filter/sleep schemaを使うことをmock-safeに確認する。
- 旧Fitbit Web APIの新規OAuth/operator executionを停止する。
- Backendのprovider_optionsとFlutter parserの契約ずれを修正する。
- Fitbit表示を旧Web API・移行参照へ変更し、通常UIから旧OAuth導線を外す。
- real Google Health OAuth/API/smartphone Web確認はW-5b2へ残す。
```

詳細契約: `docs/v210_google_health_migration_audit.md`

受け入れ結果:

```text
- implementation commit: 081cfdd
- legacy Fitbit execution: retired before network
- Google Health v4 focused tests: 8 passed
- provider selection + migration focused tests: 16 passed
- backend pytest: 100 passed
- Flutter test: 57 passed
- W-1〜W-5b1 checks / v2.0.x guards: passed
- diff review / operator approval: passed
- real Google Health operator execution: false
- release records changed: false
```

W-5b1は2026-07-24にCOMPLETED / ACCEPTEDとなった。W-5b2も同日に受け入れられ、configured Google Health API、PC/スマートフォンWeb、operator-confirmed Fitbit Versa 2由来をpublic-safe markerで記録した。

### W-5b2 — Configured Google Health API operator verification

Status: COMPLETED / ACCEPTED

```text
- ignoredなGoogle Health operator環境を使用する。
- Google OAuth 2.0のconfigured接続を明示操作で確認する。
- Google Health API v4からreal sleepを取得する。
- Fitbit-origin sleepが利用可能な場合はsourceを確認する。
- normalized SleepSummaryとFlutter Webのprovider/source/data-kind表示を確認する。
- private token、raw payload、正確な睡眠値、private path、LAN URL、raw screenshotはGitへ入れない。
- public-safe markerだけを受け入れ記録へ同期する。
```

受け入れ結果:

```text
- execution-record commit: ed50d9e
- operator env preflight / ValidateOnly: passed
- token refresh: succeeded
- real Google Health HTTP status: 200
- normalized SleepSummary: confirmed
- PC Web / smartphone Web: passed
- Fitbit-origin device model: operator-confirmed Fitbit Versa 2
- W-1〜W-5b2 checks / v2.0.x guards: passed
- backend pytest: 100 passed
- Flutter test: 57 passed
- diff review / operator approval: passed
- raw screenshot committed: false
- release records changed: false
```

W-5b2と親W-5は2026-07-24にCOMPLETED / ACCEPTEDとなった。C-1もCOMPLETED / ACCEPTEDとなり、T-1はCURRENT / NOT_COMPLETED、V-1とR-1はPLANNEDである。

詳細記録: `docs/v210_google_health_real_operator_verification.md`

```text
operator env validation: accepted
token refresh: succeeded
real Google Health HTTP: 200
normalized SleepSummary: confirmed
PC Web display: confirmed
smartphone Web display: confirmed
raw screenshot committed: false
release records changed: false
```

---

# 4. 直近完了した小コミット

## W-4 — Sleep-provider selection and source-label UI

Status: COMPLETED / ACCEPTED

実装分割:

```text
W-4a  COMPLETED / ACCEPTED   read-only sleep-provider selection status contract
W-4b  COMPLETED / ACCEPTED   Flutter provider/source-label UI and simplified
                              Google Health user UX with retained diagnostics
```

受け入れ結果:

```text
- W-4a implementation commit: 1619b0b
- W-4b implementation commit: 1fbea58
- configured providerとactual SleepSummary source/data kindを別表示する。
- mock providerではFitbit statusを呼ばない。
- Google Health通常UXを簡潔にし、operator detailsをAdvancedへ維持する。
- Fitbit表示はW-5実利用検証待ちを明示する。
- compileall、W-1/W-2/W-3/W-4a/W-4b checks、v2.0.x guardsが通過した。
- focused Flutter model 4件、widget 35件、backend 92件、Flutter全体57件が通過した。
- 差分確認とオペレーター承認が通過した。
- real Fitbit operator executionとrelease作業は行っていない。
```

詳細契約:

```text
docs/v210_sleep_provider_selection_source_labels.md
docs/v210_flutter_sleep_provider_source_ui.md
```

---

# 6. 以前に完了した小コミット

## W-3 — Fitbit real sleep normalization and API regression tests

Status: COMPLETED / ACCEPTED

目的:

```text
- Fitbit APIエラーをraw payload非公開のまま保守的に分類する。
- 正規化済みsleep fieldsをSleepSummaryへ接続する。
- accepted real-data semanticsをmock-safe fixtureで回帰テストする。
- Public fixtureへprivate raw Fitbit payloadや正確な私的睡眠値を入れない。
- configured real sleep retrievalを完了扱いしない。
```

受け入れ状態: COMPLETED / ACCEPTED

変更対象:

```text
backend/app/services/fitbit_api_client.py
backend/app/services/fitbit_sleep_service.py
backend/app/services/fitbit_sleep_normalizer.py
backend/app/services/sleep_providers/fitbit.py
backend/tests/test_fitbit_real_sleep_normalization.py
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v210_goal_checklist_small_commit.md
docs/v210_fitbit_real_sleep_normalization.md
scripts/check_v210_fitbit_current_behavior_inventory.py
scripts/check_v210_fitbit_real_sleep_normalization.py
```

実装済み境界:

```text
- HTTP/API失敗をallow-list済みreasonへ分類する。
- raw payload、provider message、token、Authorization headerを公開しない。
- 正のsleep durationがある場合だけnormalization成功とする。
- main sleepとsummary fallbackを決定的に扱う。
- sleep_start / sleep_end / quality_label / confidence / is_real_data /
  unavailable_reasonをSleepSummaryへ接続する。
- fake HTTP、synthetic fixture、provider、API responseをmock-safeに回帰テストする。
```

受け入れ結果:

```text
- allow-list済みFitbit sleep API error分類を追加した。
- 正のsleep durationをreal-data成功の必須条件にした。
- sleep_start / sleep_end / quality_label / confidence / is_real_data /
  unavailable_reasonをSleepSummaryへ接続した。
- fake HTTP、synthetic fixture、provider mapping、/sleep/summary responseを回帰テストした。
- compileall、W-1/W-2/W-3 check、v2.0.x guards、backend pytest 84件、
  Flutter test 50件、差分確認、オペレーター承認が通過した。
- real Fitbit execution、provider選択UI、smartphone Web受け入れ、release作業は行っていない。
```

詳細契約は`docs/v210_fitbit_real_sleep_normalization.md`。W-3は2026-07-23にCOMPLETED / ACCEPTEDとなった。configured real Fitbit acceptanceはW-5まで未完了である。

---

# 5. それ以前に完了した小コミット

## W-2 — Fitbit token/status/reconnect hardening

Status: COMPLETED / ACCEPTED

目的:

```text
- connected/provider/messageを維持し、connection_state/verifiedを追加する。
- token存在、期限、refresh必要、reconnect必要、permission拒否、破損を区別する。
- matching OAuth stateを一度だけconsumeし、replayを拒否する。
- fake HTTPと一時token/state storeでrefresh境界を回帰テストする。
- normal /fitbit/statusでは外部HTTPやrefreshを実行しない。
```

変更対象:

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
backend/app/models/fitbit.py
backend/app/services/fitbit_service.py
backend/app/services/fitbit_token_store.py
backend/app/services/fitbit_oauth_state_store.py
backend/app/services/fitbit_token_exchange.py
backend/tests/test_fitbit_token_status_reconnect.py
app/lib/models/fitbit_status.dart
app/lib/models/fitbit_connect_response.dart
app/test/fitbit_token_status_reconnect_test.dart
docs/DRC_v210_goal_checklist_small_commit.md
docs/v210_fitbit_token_status_reconnect.md
scripts/check_v210_fitbit_current_behavior_inventory.py
scripts/check_v210_fitbit_token_status_reconnect.py
```

変更しない対象:

```text
Fitbit API route
Fitbit sleep API/error/normalization/provider実装
SleepSummary real-data mapping
Flutter home_screen / backend_api_client / provider選択UI
既存M-7 backend / Flutter回帰テスト
version metadata
v2.0.0 / v2.0.1 tag、GitHub Release、固定ZIP、公開後記録
```

受け入れ結果:

```text
- connection_state / verifiedを追加し、connected/provider/message互換を維持した。
- token期限、refresh必要、reconnect必要、permission拒否、破損をmock-safeに分類した。
- normal /fitbit/statusは外部HTTPや自動refreshを実行しない。
- matching OAuth stateを一度だけconsumeし、replayを拒否した。
- fake HTTPと一時storeだけでrefresh成功・失敗を回帰テストした。
- 旧Flutter responseの「未検証」表示と新状態表示を両立した。
- compileall、W-1/W-2 check、v2.0.x guard、backend pytest 57件、Flutter test 50件、差分確認、オペレーター承認が通過した。
- real Fitbit executionとrelease作業は行っていない。
```

詳細契約: `docs/v210_fitbit_token_status_reconnect.md`

real OAuth、real token exchange/refresh、permission、実sleep取得、smartphone Web受け入れはW-5まで完了扱いしない。W-2は2026-07-23にCOMPLETED / ACCEPTEDとなった。

---

## W-1 — Fitbit current behavior inventory and contract

Status: COMPLETED / ACCEPTED

Commit title:

```text
docs/test: establish v2.1.0 Fitbit current behavior inventory
```

目的:

```text
- v2.1.0のactive checklistを新設する。
- M-7から引き継いだFitbit実コードを正確に棚卸しする。
- ソース存在、ローカルトークン検出、認証URL準備、mock-safe成功、
  configured real Fitbit成功を別の状態として固定する。
- W-2〜W-5と後続C-1 / T-1 / V-1 / R-1の責任範囲を固定する。
- runtime、API、response model、Flutter動作、version metadataを変更しない。
```

変更対象:

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v210_goal_checklist_small_commit.md
docs/v210_fitbit_current_behavior_inventory.md
scripts/check_v210_fitbit_current_behavior_inventory.py
```

変更しない対象:

```text
backend/app/**
backend/tests/**
app/lib/**
app/test/**
app/pubspec.yaml
backend/.env.example
backend/env_profiles/**
docs/DRC_v200_goal_checklist_small_commit.md
release_notes/v2.0.0.md
docs/DRC_v20x_maintenance_checklist.md
docs/v20x_patch_release.md
docs/v201_patch_release_record.md
release_notes/v2.0.1.md
build_v200_final_fixed_release_zip_from_head.ps1
build_v201_fixed_release_zip_from_head.ps1
scripts/check_v20x_patch_release.py
DRC_v2.0.0 / DRC_v2.0.1 tags
v2.0.0 / v2.0.1 GitHub Releases and fixed ZIPs
```

受け入れ結果:

```text
- v2.1.0 checklistとFitbit current behavior inventoryを作成した。
- Fitbit route、OAuth state、token exchange guard、refresh、sleep API、
  normalization、SleepSummary mapping、Flutter presentationを実コードどおり記録した。
- connected=trueとlive token validation、ready=trueとconnection successを分離した。
- Fitbit SleepSummaryのis_real_data等の未接続項目を完了扱いしていない。
- runtime、Flutter、既存テスト、version metadata、公開済みリリース記録のhashは不変だった。
- compileall、W-1 source-tree check、backend pytest 38件、Flutter test 43件が通過した。
- real Fitbit API/OAuthを実行せず、差分確認とオペレーター承認が通過した。
```

mock-safe境界:

```text
- source-treeと正規化hashの確認のみ。
- credential、backend/local_data、network、OAuth browser、real token、raw payloadを使わない。
- 既存pytestはfake、一時ファイル、deterministic fixtureだけを使用する。
```

real operator境界:

```text
- real OAuth、token exchange、refresh、scope/permission確認、sleep取得、
  smartphone Web表示はW-5まで受け入れない。
- W-1のsource-tree成功はconfigured real Fitbit成功を意味しない。
- token、authorization code、OAuth state、raw payload、private path、LAN URL、
  raw screenshot、正確な私的睡眠値はPublicへ記録しない。
```

実行候補:

```powershell
python -m compileall -q backend scripts
python scripts\check_v210_fitbit_current_behavior_inventory.py
python -m pytest -q backend/tests

cd app
flutter test
cd ..
```

W-1は2026-07-23にCOMPLETED / ACCEPTEDとなった。W-1の受け入れはconfigured real Fitbit成功を意味せず、W-2以降の完了要件を前倒ししていない。

---

# 7. 完了済みv2.0.x記録

## M-9 — v2.0.1 patch release

Status: COMPLETED / ACCEPTED

公開記録:

```text
source HEAD: 3e4c9f6186ef7195045a445307e14f412924bc26
annotated tag: DRC_v2.0.1
GitHub Release: published
fixed ZIP: DailyRhythmCompanion_20260723_143447.zip
fixed ZIP size: 1493130 bytes
fixed ZIP SHA-256: ac24378da3a0dcd7227591f8cbaa8bca010dda219a404c3723ae2f7d2716c1d1
builder invocation count: 1
same-ZIP verification without rebuilding: passed
post-publication downloaded-asset SHA-256 verification: passed
v2.0.0 historical records: unchanged
```

M-9は2026-07-23に、final committed-source gate、backend pytest 38件、Flutter test 43件、one-time fixed ZIP build、同一ZIP検証、明示的な最終承認、annotated tag、GitHub Release、公開後SHA-256再検証の通過後に受け入れ済みとなった。

---

## M-7 — Fitbit current-state contract

Status: COMPLETED / ACCEPTED

目的:

```text
- 実コード上のmock / wearable_stub / fitbit_stub / fitbitの役割を固定する。
- ローカルトークン検出や認証URL準備を実連携成功と表示しない。
- route / response model / OAuth-token-sleep実装の互換性は維持する。
- mock-safeなbackend / Flutter回帰テストを追加する。
- 実Fitbit完了をv2.1.0へ明確に引き渡す。
```

M-7は2026-07-23に、compileall、M-1〜M-7 check、backend pytest 38件、Flutter test 43件、差分確認、オペレーター承認を通過して受け入れ済み。v2.0.1のリリースは実施していない。

---

## M-6 — Web CORS origins configuration

Status: COMPLETED / ACCEPTED

目的:

```text
- 現在のWeb CORS全origin許可を設定可能にする。
- ローカルデモ向けの既定動作は維持する。
- 明示指定時だけoriginを制限する。
- configとCORS API boundaryをmock-safeに回帰テストする。
```

設定契約:

```text
WEB_CORS_ORIGINS=*

# 制限例
WEB_CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:8080
```

変更対象:

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
backend/.env.example
backend/env_profiles/mock_safe.env
backend/app/config.py
backend/app/main.py
backend/tests/test_web_cors_config.py
docs/v20x_web_cors_origins.md
docs/DRC_v20x_maintenance_checklist.md
scripts/check_v20x_maintenance_baseline.py
scripts/check_v20x_application_version_metadata.py
scripts/check_v20x_backend_mock_safe_regression.py
scripts/check_v20x_framework_fallback_voice_artifact_regression.py
scripts/check_v20x_temporary_lifecycle_limits.py
scripts/check_v20x_web_cors_origins.py
```

変更しない対象:

```text
docs/DRC_v200_goal_checklist_small_commit.md
release_notes/v2.0.0.md
既存API route / response model
Flutter application behavior
認証、production hosting、reverse proxy、TLS設定
real LLM / TTS / STT / health / OAuth / motion execution
release ZIP / tag / GitHub Release
```

M-6完了条件:

```text
- WEB_CORS_ORIGINS未指定時は既存の全origin許可を維持する。
- 明示originリストがFastAPI CORSMiddlewareへ反映される。
- 許可originのpreflightは成功し、未許可originは拒否される。
- allow_credentials=Falseと既存method/header設定を維持する。
- compileall、M-1〜M-6 check、backend pytest、flutter testが通る。
- v2.0.0履歴ファイルの正規化hashが変わらない。
- 差分確認後にオペレーターが小コミットを承認する。
```

M-6は2026-07-23に、compileall、M-1〜M-6 check、backend pytest 31件、Flutter test 39件、差分確認、オペレーター承認を通過して受け入れ済み。v2.0.1のリリースは実施していない。

---

## v2.0.x small-commit queue

```text
M-1  COMPLETED  docs: establish post-v2.0.0 maintenance baseline
M-2  COMPLETED  fix/test: align application version metadata
M-3  COMPLETED  test: add backend mock-safe regression foundation
M-4  COMPLETED  test: cover Framework fallback and voice artifact safety
M-5  COMPLETED  fix/test: bound temporary chat sessions and TTS artifacts
M-6  COMPLETED  fix/test: make Web CORS origins configurable
M-7  COMPLETED  docs/test: clarify Fitbit current-state contract
M-8  COMPLETED  test/docs: add v2.0.x aggregate maintenance readiness
M-9  COMPLETED  release: fixed-ZIP verification and v2.0.1 patch release record
```

M-1〜M-9は受け入れ済みで、v2.0.1は正式リリース済み。W-1〜W-5は受け入れ済みで、Google Health API経由のreal provider executionとPC/スマートフォンWeb確認まで完了した。現在はC-1を進める。

---

# 8. Later version boundaries

## v2.1.0

```text
Primary theme: Real wearable daily loop
Primary new capability: Fitbit real-use completion
Secondary work: provider selection, LLM chat lifecycle, in-app TTS playback, static character-state polish
```

## v3.0.0

```text
Primary theme: Realtime multimodal character runtime
Large changes: real STT, microphone capture, streaming/cancel, TTS interruption, Live2D/VTS real execution, runtime orchestration
```

v2.1.0はW-1からW-5まで受け入れ済みで、Google Health API経由のFitbit Versa 2-origin sleepとPC/スマートフォンWeb表示が確認済みである。現在はC-1がCURRENT / NOT_COMPLETED。TTS、character、release readinessは未実装・未受け入れで、v3.0.0は計画段階である。
