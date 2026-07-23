# Daily Rhythm Companion post-v2.0.0 task list

更新日: 2026-07-23

## 1. 現在地

```text
Public repository: murayan1982/daily-rhythm-companion-public
immutable capability baseline: v2.0.0
current released version: v2.0.1
release / annotated tag: DRC_v2.0.1
v2.0.1 status: RELEASED
completed maintenance line: v2.0.x COMPLETED / ACCEPTED
current development line: v2.1.0
current small commit: W-4a CURRENT / NOT_COMPLETED
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

## W-4 — Sleep-provider selection and source-label UI

Status: CURRENT / NOT_COMPLETED

実装分割:

```text
W-4a  CURRENT / NOT_COMPLETED  read-only sleep-provider selection status contract
W-4b  PLANNED                 Flutter provider/source-label UI and simplified
                               Google Health user UX with retained diagnostics
```

### W-4a — Read-only sleep-provider selection status contract

Implementation state: IMPLEMENTED / NOT_ACCEPTED

目的:

```text
- backendのSLEEP_PROVIDER選択状態をread-only APIで公開する。
- configured providerとSleepSummary.sourceを別概念として固定する。
- credentials、OAuth、token refresh、sleep取得をendpointから実行しない。
- W-3で受け入れたFitbit backend normalization/API contractを変更しない。
- Flutter UI変更やconfigured real Fitbit実行を完了扱いしない。
```

変更対象:

```text
backend/app/main.py
backend/app/api/sleep_provider_selection.py
backend/app/models/sleep_provider_selection.py
backend/app/services/sleep_provider_selection_service.py
backend/tests/test_sleep_provider_selection_contract.py
docs/v210_sleep_provider_selection_source_labels.md
docs/DRC_v210_goal_checklist_small_commit.md
scripts/check_v210_sleep_provider_selection_source_labels.py
README.md
roadmap.md
tasklist.md
scripts/README.md
```

変更しない対象:

```text
backend/app/api/sleep.py
backend/app/models/sleep.py
backend/app/services/sleep_providers/factory.py
W-3 Fitbit API / normalization / provider mapping / regression files
app/lib/**
app/test/**
version metadata
v2.0.0 / v2.0.1 tag、GitHub Release、固定ZIP、公開後記録
```

W-4aのsource実装だけでは受け入れない。compileall、W-1/W-2/W-3 check、W-4a check、v2.0.x guards、backend pytest、Flutter test、差分確認、オペレーター承認が必要である。W-4a受け入れ後もW-4はCURRENT / NOT_COMPLETEDで、W-4bがprovider/source-label UIとGoogle Health通常UXを担当する。configured real Fitbit operator verificationはW-5まで未完了である。

---

# 4. 直近完了した小コミット

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

# 6. 完了済みv2.0.x記録

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

M-1〜M-9は受け入れ済みで、v2.0.1は正式リリース済み。W-1、W-2、W-3も受け入れ済みで、Fitbit inventory、token/status/reconnect、sleep normalization/API regression境界が確立された。次の実装変更はW-4の別小コミットとして進める。

---

# 7. Later version boundaries

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

v2.1.0はW-1、W-2、W-3を受け入れ済みで、W-4がCURRENT / NOT_COMPLETEDである。W-4aのread-only provider selection status contractは実装済みだが未受け入れで、Flutter provider/source-label UIとGoogle Health通常UX整理はW-4bでこれから着手する。configured real Fitbit実利用、chat、TTS、character、release readinessは未実装・未受け入れで、v3.0.0は計画段階である。
