# Daily Rhythm Companion post-v2.0.0 task list

更新日: 2026-07-26

## 1. 現在地

```text
Public repository: murayan1982/daily-rhythm-companion-public
immutable capability baseline: v2.0.0
current released version: v2.1.0
current released metadata: Backend 2.1.0 / Flutter 2.1.0+3 RELEASED
release / annotated tag: DRC_v2.1.0
v2.1.0 status: RELEASED / ACCEPTED
completed maintenance line: v2.0.x COMPLETED / ACCEPTED
completed development line: v2.1.0 COMPLETED / ACCEPTED
current small commit: RT-1b CURRENT / NOT_COMPLETED
current implementation step: Backend realtime model and Framework-contract normalization boundary
current implementation state: NOT_STARTED
completed small commit: RT-1a COMPLETED / ACCEPTED
strategic target: v3.0.0
```

v2.1.0は固定ZIP `DailyRhythmCompanion_v2.1.0_20260725_160036.zip`、annotated tag `DRC_v2.1.0`、GitHub Release、公開後SHA-256再検証まで完了している。公開済み`DRC_v2.0.0`、`DRC_v2.0.1`、`DRC_v2.1.0`を変更せず、v3.0.0の最初の小コミットRT-0aをdocs/test-onlyで完了・受け入れた。RT-0a受け入れ時点ではRT-0bはNOT_STARTEDだった。RT-0bはcompileall、RT-0a/RT-0b gate、Backend 110件、Flutter 103件、diff確認、明示的なオペレーター承認の通過後にCOMPLETED / ACCEPTEDとなった。RT-0bのv5.0.0判定`BLOCKED_FRAMEWORK_UPDATE_REQUIRED`は履歴として維持する。RT-0cもreleased Framework v5.1.0の再評価、local gate、Backend 110件、Flutter 103件、diff確認、明示的なオペレーター承認の通過後にCOMPLETED / ACCEPTEDとなった。host-app基盤は大幅に改善したが、public voice input、unified realtime、hard cancel/TTS queue/barge-in、motion adapterは未リリースのため、`BLOCKED_REALTIME_PUBLIC_CONTRACTS_MISSING`としてRT-1以降を開始しない。


## 2. Source of truth

v3.0.0のactive checklistとRT-0a棚卸し:

```text
docs/DRC_v300_goal_checklist_small_commit.md
docs/v300_realtime_current_behavior_inventory.md
scripts/check_v300_realtime_current_behavior_inventory.py
docs/v300_framework_realtime_contract_readiness.md
scripts/check_v300_framework_realtime_contract_readiness.py
docs/v300_framework_v510_reassessment.md
scripts/check_v300_framework_v510_reassessment.py
docs/v300_framework_v520_contract_adoption.md
scripts/check_v300_framework_v520_contract_adoption.py
```

v2.1.0のauthoritative詳細タスクリスト:

```text
docs/DRC_v210_goal_checklist_small_commit.md
```

実装棚卸し:

```text
docs/v210_fitbit_current_behavior_inventory.md
docs/v210_character_display_current_behavior_inventory.md
docs/v210_release_readiness_current_behavior_inventory.md
docs/v210_release_readiness.md
docs/v210_release_record.md
release_notes/v2.1.0.md
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


# 3. 完了したRT-0 prerequisite phase

## RT-0 — v3.0.0 prerequisite and current behavior review

Status: COMPLETED / ACCEPTED

Small-commit split:

```text
RT-0a  COMPLETED / ACCEPTED      DRC realtime current behavior inventory
RT-0b  COMPLETED / ACCEPTED      Released Framework public realtime readiness review
RT-0c  COMPLETED / ACCEPTED      Framework v5.1.0 reassessment and remaining realtime block decision
```

### RT-0a — Realtime current behavior inventory

目的:

```text
- Backend、Flutter、platform metadata、tests、roadmap、tasklistを実コードどおり棚卸しする。
- voice input / LLM / TTS / character / motionの実runtime、guarded boundary、discovery-onlyを分離する。
- v3.0.0の目的、scope、除外範囲、RT-0以降の責任分割を固定する。
- 旧R-1節のCURRENT表示をCOMPLETED / ACCEPTEDへ同期する。
- runtime、既存tests、version、release recordsを変更しない。
```

変更対象:

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v300_goal_checklist_small_commit.md
docs/v300_realtime_current_behavior_inventory.md
scripts/check_v300_realtime_current_behavior_inventory.py
```

実コード確認結果:

```text
- Backendは通常HTTP request/responseで、WebSocket/SSE/realtime sessionは未実装。
- voice inputはmetadata-onlyでaccepted=false / not_started / transcript=null。
- Framework text chatはfull-response ask()で、DRC streaming/cancel orchestrationは未実装。
- TTSは単発artifact生成とFlutter内再生で、queue/生成cancel/barge-inは未実装。
- character activityはidle/loading/speakingのみ。
- motionはprobe/simulatorでmotion_sent=false / vts_connection_used=false。
- microphone dependency、Android RECORD_AUDIO、iOS microphone usage descriptionは未追加。
- HomeScreen 4,161行、widget_test.dart 2,753行で、realtime追加前の抽出が必要。
```

詳細:

```text
docs/v300_realtime_current_behavior_inventory.md
```

検証:

```powershell
python -m compileall -q backend scripts
python scripts\check_v300_realtime_current_behavior_inventory.py
python -m pytest -q backend/tests

cd app
flutter test
cd ..

git diff --check
```

受け入れ結果:

```text
implementation: COMPLETED / ACCEPTED
compileall: passed
RT-0a source-tree gate: passed
Backend pytest: 110 passed
Flutter test: 103 passed
git diff --check: passed
runtime changed: false
existing tests changed: false
real provider execution: false
microphone used: false
realtime session started: false
diff review / explicit operator approval: passed
RT-1 authorization: BLOCKED pending RT-0b and RT-0c
```

Stop rule:

```text
RT-0a実装中にはRT-0bを開始しない。RT-0a受け入れ後、RT-0bを次のCURRENT小コミットとして開始する。
Frameworkを変更しない。
microphone、realtime transport、STT、streaming、cancel、TTS queue、barge-in、motion executionを追加しない。
RT-0aはローカル検証、diff確認、明示的なオペレーター承認の通過後にCOMPLETED / ACCEPTEDへ同期した。
```

---

### RT-0b — Released Framework public realtime readiness review

Status: COMPLETED / ACCEPTED
Implementation state: COMPLETED / ACCEPTED

目的:

```text
- released AI Character Framework v5.0.0のpublic host-app surfaceを確認する。
- public export、session lifecycle、streaming、cancel、TTS queue、voice input、motion、capabilityを分類する。
- v2.1.0で動作したtext chat / one-shot voice outputを壊れた扱いにせず、v3 realtime不足と分離する。
- DRC実アプリ統合で得たFW-F1〜FW-F8と、realtime向けFW-F9〜FW-F12を固定する。
- DRC/FW runtime、既存tests、dependency、version、release recordを変更しない。
```

確認したreleased Framework snapshot:

```text
repository: murayan1982/ai-character-framework
released line: v5.0.0
inspected public-source commit: 6494da306015c4f714f869b43e773ba51a2478a2
release implementation commit: a2df57e2e8ed226b7c9e9c72ed68a79c8a48b6db
```

public export確認:

```text
available:
- create_text_chat_session
- create_voice_output_session
- TextChatSession / TextChatSessionInfo / events
- VoiceOutputSession / VoiceOutputRequest / VoiceOutputResult

not released at root public boundary:
- voice-input/STT session
- unified realtime session/events/capabilities
- motion-event/Live2D/VTS session
```

readiness結果:

```text
READY_CURRENT_USE:
- v2.1.0のfull-response text chat
- one-shot voice outputとopaque handoff

PARTIAL_BLOCKING:
- text streaming/events
- typed result/error
- capability reporting
- project-root-independent factory
- provider config responsibility
- session close/dispose

MISSING_BLOCKING:
- installable SDK metadata
- public voice-input/STT
- unified realtime lifecycle
- provider-level hard cancellation
- TTS queue/cancel/flush/barge-in acknowledgement
- public motion/VTS adapter

DEFECT_BLOCKING:
- READMEはsession.speak(...)を記載するが、実装はcreate_output(...)でspeak()なし
```

判定:

```text
Framework public readiness: BLOCKED_FRAMEWORK_UPDATE_REQUIRED
RT-1 authorization: BLOCKED pending RT-0c and a released Framework update
DRC runtime changed: false
Framework runtime changed: false
real provider execution: false
```

変更対象:

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v300_goal_checklist_small_commit.md
docs/v300_framework_realtime_contract_readiness.md
scripts/check_v300_framework_realtime_contract_readiness.py
```

変更しない対象:

```text
backend/app/**
backend/tests/**
app/lib/**
app/test/**
app/pubspec.yaml
app/android/**
app/ios/**
docs/v300_realtime_current_behavior_inventory.md
scripts/check_v300_realtime_current_behavior_inventory.py
release_notes/**
AI Character Framework runtime/repository
v2.x release records/tags/fixed ZIPs
```

検証:

```powershell
python -m compileall -q backend scripts
python scripts\check_v300_realtime_current_behavior_inventory.py
python scripts\check_v300_framework_realtime_contract_readiness.py
python -m pytest -q backend/tests

cd app
flutter test
cd ..

git diff --check
git status --short
```

詳細:

```text
docs/v300_framework_realtime_contract_readiness.md
```

Stop rule:

```text
RT-0bではFrameworkを変更しない。
missing public contractをDRC internal/provider-specific implementationで代替しない。
realtime向けに新しいfactory/method probeやsys.path/CWD workaroundを追加しない。
RT-0b受け入れ後もRT-1は開始せず、RT-0cでhandoff境界を受け入れる。
```

### RT-0c — Released Framework v5.1.0 reassessment and remaining block decision

Status: COMPLETED / ACCEPTED
Implementation state: COMPLETED / ACCEPTED

目的:

```text
- accepted RT-0b v5.0.0 reviewを履歴として維持する。
- released tag v5.1.0のpublic export、typed result、capability、lifecycle、artifact、package importを再確認する。
- FW-F1〜FW-F12をRESOLVED_V510 / PARTIAL_V510 / MISSING_REALTIME_BLOCKERへ再分類する。
- v5.1.0で解消した統合コストと、引き続きDRC realtimeを止める不足を分離する。
- DRC/FW runtime、既存tests、version、release recordを変更しない。
```

確認したrelease:

```text
released tag: v5.1.0
tag commit: b68c62b5e80328b8c50f9eeef98164f6ae2a3b0f
post-tag release-note commit: c08c7539e2109a3a9a77be1c54a02f6e3bf06c30
fixed ZIP SHA-256: 137f9f85602957b068881d8d26e34570bafa8e000c4a624fc19871b313612545
```

再分類:

```text
RESOLVED_V510:
- FW-F4 capability snapshot
- FW-F5 provider config ownership
- FW-F7 opaque VoiceArtifactRef
- FW-F8 public contract conformance gate

PARTIAL_V510:
- FW-F1 package-like import（wheel公開は未実施）
- FW-F2 stable factory/method（text factory/project_rootはtransition）
- FW-F3 typed result/error（Text Chat中心、全session統一ではない）
- FW-F6 close/dispose（real resource cleanupは未接続）

MISSING_REALTIME_BLOCKER:
- FW-F9 public voice-input/STT
- FW-F10 unified realtime lifecycle/events
- FW-F11 hard cancel/TTS queue/flush/barge-in
- FW-F12 public motion/Live2D/VTS adapter
```

判定:

```text
Host-app foundation: SUBSTANTIALLY_READY_WITH_TRANSITION_GAPS
Realtime readiness: BLOCKED_REALTIME_PUBLIC_CONTRACTS_MISSING
RT-1 through RT-5: BLOCKED pending released voice-input/realtime/cancel contracts
RT-6 through RT-7: BLOCKED pending released motion contract
```

変更対象:

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v300_goal_checklist_small_commit.md
docs/v300_framework_v510_reassessment.md
scripts/check_v300_framework_v510_reassessment.py
```

検証:

```powershell
python -m compileall -q backend scripts
python scripts\check_v300_realtime_current_behavior_inventory.py
python scripts\check_v300_framework_realtime_contract_readiness.py
python scripts\check_v300_framework_v510_reassessment.py
python -m pytest -q backend/tests

cd app
flutter test
cd ..

git diff --check
```

Stop rule:

```text
RT-0cでDRC/FW runtimeを変更しない。
package-like PYTHONPATH検証をwheel install完了と表現しない。
missing realtime contractをDRC internal/provider-specific実装で代替しない。
新しいsys.path/CWD/module-cache workaroundを追加しない。
RT-0c受け入れ後も、required Framework public contractのrelease前にRT-1を開始しない。
```

---


# 4. 直近完了した小コミット

## R-1 — v2.1.0 aggregate readiness and release preparation

Status: COMPLETED / ACCEPTED

```text
R-1a  COMPLETED / ACCEPTED   Release/readiness current behavior inventory
R-1b  COMPLETED / ACCEPTED   Aggregate source-tree/test gate and v2.1.0 candidate metadata
R-1c  COMPLETED / ACCEPTED   Final smartphone Web evidence aggregate
R-1d  COMPLETED / ACCEPTED   One-time fixed ZIP build and same-artifact verification
R-1e  COMPLETED / ACCEPTED   Explicit approval, publication, and post-publication verification
```

R-1eと親R-1はCOMPLETED / ACCEPTED。v2.1.0は固定ZIP、annotated tag、GitHub Release、公開後SHA-256再検証まで完了している。R-1の詳細な履歴source of truthは`docs/DRC_v210_goal_checklist_small_commit.md`、`docs/v210_release_readiness.md`、`docs/v210_release_record.md`、`release_notes/v2.1.0.md`に保持する。

```text
historical v2.1.0 terminal state: current small commit: none
```

---

## V-1 — Character display extraction and deterministic states

Status: COMPLETED / ACCEPTED

実装分割:

```text
V-1a  COMPLETED / ACCEPTED         current behavior inventory and implementation contract
V-1b  COMPLETED / ACCEPTED         deterministic presentation model and standalone widget
V-1c  COMPLETED / ACCEPTED       HomeScreen extraction and integration
```

### V-1a — Current behavior inventory and implementation contract

```text
- 4,195行のHomeScreenがcharacter選択、静的画像、mood、advice、TTS再生状態、
  Advanced Motion Demoを同時に所有している現状を固定する。
- CharacterPresetの6項目と、3 character画像・2背景・1 fallback assetを固定する。
- mood / advice / loading / speaking / fallbackが通常character表示へ未統合であることを記録する。
- Motion Demo simulatorと通常日次ループのcharacter表示を分離する。
- 既存widget_test.dart 2,669行と関連テスト範囲をnormalized hashで固定する。
- V-1b / V-1cの責任範囲を固定し、R-1を前倒ししない。
- Flutter runtime、Backend、既存テスト、dependency、asset、release recordsを変更しない。
```

詳細: `docs/v210_character_display_current_behavior_inventory.md`

V-1aは実装コミット`1602b2f`でCOMPLETED / ACCEPTED。compileall、全`check_v210_*.py`、v2.0.x compatibility / maintenance guards、Backend pytest 110件、Flutter test 84件、diff確認、明示的なオペレーター承認が通過した。Flutter runtime、Backend runtime、既存テスト、dependencies/assets、real provider/motion execution、release recordsは変更していない。V-1b、V-1c、親V-1もCOMPLETED / ACCEPTEDであり、その後R-1eと親R-1もCOMPLETED / ACCEPTEDとなってv2.1.0を公開済み。

### V-1b — Deterministic presentation model and standalone widget

Status: COMPLETED / ACCEPTED

```text
- CharacterDisplayPresentationでcontent stateをmood / advice / fallbackとして解決する。
- character unavailable → asset unavailable → framework fallback → advice → moodの順で決定する。
- activity stateをspeaking → loading → idleの優先順で決定する。
- CharacterDisplayCardで静的画像、状態chip、copy、CharacterPreset profileを表示する。
- model 9件・widget 4件のfocused Flutter testsを追加する。
- HomeScreen接続、fallback asset再試行、既存widget_test変更はV-1cへ残す。
- Backend、Motion Demo、dependency、asset、release recordsを変更しない。
```

詳細: `docs/v210_character_display_state_contract.md`

V-1bは実装コミット`e1f8d6f`でCOMPLETED / ACCEPTED。compileall、全`check_v210_*.py`、v2.0.x compatibility / maintenance guards、Backend pytest 110件、focused model 9件、focused widget 4件、Flutter test 97件、diff確認、明示的なオペレーター承認が通過した。HomeScreen、Backend、Motion Demo、dependency、asset、real provider/motion execution、release recordsは変更していない。V-1cはCOMPLETED / ACCEPTED。

### V-1c — HomeScreen extraction and integration

Status: COMPLETED / ACCEPTED
Implementation state: COMPLETED / ACCEPTED

```text
- HomeScreenからcharacter display renderingを抽出済みwidgetへ接続する。
- HomeScreenはデータ取得、選択callback、advice/TTS controlを保持する。
- static repository-safe fallback assetを先に使い、generic placeholderを最終fallbackにする。
- focused HomeScreen integration testsを追加する。
- Live2D/VTS実接続、Backend変更、asset追加、R-1を含めない。
```

V-1cは実装コミット`995145d`でCOMPLETED / ACCEPTED。全`check_v210_*.py`、v2.0.x compatibility / maintenance guards、Backend pytest 110件、focused model 9件、focused card 5件、focused HomeScreen 5件、Flutter test 103件、Web/Windows build、diff確認、明示的なオペレーター承認が通過した。Backend、Motion Demo、dependencies、static assets、real motion execution、release recordsは変更していない。親V-1もCOMPLETED / ACCEPTED。詳細: `docs/v210_character_display_home_integration.md`。

---

## T-1 — Flutter in-app TTS player and artifact-expiry handling

Status: COMPLETED / ACCEPTED

実装分割:

```text
T-1a  COMPLETED / ACCEPTED     current TTS/audio handoff inventory and implementation contract
T-1b  COMPLETED / ACCEPTED  Flutter in-app player abstraction, states, and mock-safe tests
T-1c  COMPLETED / ACCEPTED                 Home UI integration, expired-artifact recovery, and T-1 acceptance
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

T-1aは2026-07-24にCOMPLETED / ACCEPTEDとなった。T-1bも実装コミット`161e624`でCOMPLETED / ACCEPTEDとなり、T-1cと親T-1もCOMPLETED / ACCEPTEDとなった。V-1はCURRENT / NOT_COMPLETEDである。

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

T-1bは2026-07-24にCOMPLETED / ACCEPTEDとなった。T-1cと親T-1もCOMPLETED / ACCEPTEDとなり、V-1がCURRENT / NOT_COMPLETEDである。

### T-1c — Home UI integration, expired-artifact recovery, and T-1 acceptance

Status: COMPLETED / ACCEPTED

```text
- audioplayers ^6.7.1をapp-owned engineの内側へ追加する。
- Backendのopaque MP3をHTTPで読み込み、404/410をexpiredへ変換する。
- HomeScreenへplay / stop / replay / regenerate UIを統合する。
- raw URL、private path、provider exceptionを通常UIへ表示しない。
- fake driver / fake engineだけでengine/widget回帰を追加する。
- Windows CMake policyをVisual Studio 2026向けに3.15へ更新する。
- Backend、Framework/TTS provider、V-1、R-1、release recordsを変更しない。
```

詳細: `docs/v210_tts_player_home_integration.md`

受け入れ結果:

```text
- implementation commit: 4d3d5d5
- desktop plugin registrant follow-up: 9771f76
- compileall / T-1a / T-1b / T-1c source-tree checks: passed
- focused Flutter tests: 20 passed
- backend pytest: 110 passed
- Flutter test: 84 passed
- Flutter Web / Windows build: passed
- PC / smartphone audible playback・stop・replay・completion: passed
- expired mapping・PC / smartphone regenerate recovery: passed
- raw URL / private path hidden: passed
- real Framework/TTS execution: true
- Backend runtime / release records changed: false
- diff review / operator approval: passed
```

T-1cと親T-1はCOMPLETED / ACCEPTED。V-1はCURRENT / NOT_COMPLETED、R-1はPLANNED。

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

M-1〜M-9は受け入れ済みで、v2.0.1は正式リリース済み。W-1〜W-5、C-1、T-1、V-1、R-1a〜R-1eと親R-1も受け入れ済みで、Google Health API経由のreal provider execution、PC/スマートフォンWeb、アプリ内TTS再生、決定論的character表示、固定ZIP、公開、公開後検証まで確認済み。v2.1.0は正式リリース済みである。

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
Current parent phase: RT-1 CURRENT / NOT_COMPLETED
Current small commit: RT-1b CURRENT / NOT_COMPLETED; NOT_STARTED
Completed small commit: RT-1a COMPLETED / ACCEPTED
Current authorization: RT1_MOCK_CONTRACT_INTEGRATION_AUTHORIZED
```

RT-0aは現行実コードの棚卸し、目的、scope、除外範囲、変更/非変更面を固定するdocs/test-only小コミットとしてCOMPLETED / ACCEPTEDとなった。RT-0a受け入れ時点のRT-0bはNOT_STARTED。RT-0bはCOMPLETED / ACCEPTEDで、released Framework v5.0.0 public readinessをBLOCKED_FRAMEWORK_UPDATE_REQUIREDと判定した。RT-0cでreleased Framework v5.1.0の再評価、DRC-to-FW handoff境界、進行順を受け入れた。required Framework public contractのrelease前にRT-1以降を開始しない。

- [x] T-1c: pin audioplayers 6.7.1 for Flutter 3.41.7
- [x] T-1c: restore missing Windows Flutter CMake scaffold locally
- [x] T-1c: add bounded Visual Studio 18 coroutine compatibility definition
- [x] T-1c: rerun Windows build after the compatibility correction
- [x] T-1c: commit implementation only after all tests/builds pass
- [x] Restore and track `app/windows/flutter/CMakeLists.txt`; scope the root SDK ignore to `/flutter/`.

R-1cはCOMPLETED / ACCEPTED。cleanな`main == origin/main`の実装commit `1e922e68685dadfc1008f1119d0ce492584e8f19`に対してignored private manifestがvalidateされ、Google Health実データ、Framework daily advice、live post-advice chat、実TTS再生、character表示、final integrated reviewの6項目をPC/スマートフォンWebで確認済み。raw screenshot/audio/health値/token/path/LAN IP/operator evidenceはGit外。R-1dはCOMPLETED / ACCEPTED。固定ZIP `DailyRhythmCompanion_v2.1.0_20260725_160036.zip` はsource `6e7af31f85eb6ee7887df3e184ac6a58142d6fec` / 1747337 bytes / SHA-256 `55bf584592b1824948ec847205132582a436f2c521feb593bac914a4904074e5` のexact tupleで受け入れ済み。R-1eと親R-1もCOMPLETED / ACCEPTEDで、tag、GitHub Release、公開後検証まで完了。


## Historical R-1d implementation handoff

```text
implementation: build_v210_fixed_release_zip_from_head.ps1
verification: scripts/check_v210_fixed_release_zip.py
fixed ZIP built: false
same-artifact verification: not run
DRC_v2.1.0 tag at that historical checkpoint: not created
GitHub Release at that historical checkpoint: not created
```

Historical handoff instruction: commit and push this implementation first, then run the builder once from clean synchronized official `main`. This step is already completed and must not be repeated for the released artifact.

## R-1d accepted fixed-ZIP handoff

```text
status: COMPLETED / ACCEPTED
release source HEAD: 6e7af31f85eb6ee7887df3e184ac6a58142d6fec
fixed ZIP basename: DailyRhythmCompanion_v2.1.0_20260725_160036.zip
fixed ZIP size bytes: 1747337
fixed ZIP SHA-256: 55bf584592b1824948ec847205132582a436f2c521feb593bac914a4904074e5
accepted-candidate build invocation count: 1
same-artifact verification: passed
DRC_v2.1.0 tag at that historical checkpoint: not created
GitHub Release at that historical checkpoint: not created
```

The exact fixed ZIP must remain unchanged in `release/`. R-1e is completed/accepted after explicit approval for this tuple, publication, and downloaded-asset verification.

### RT-1a — Released Framework v5.2.0 public-contract adoption gate

```text
status: COMPLETED / ACCEPTED
implementation: COMPLETED / ACCEPTED
Framework snapshot: v5.2.0@c2e247064987c94bf735a359700f0462439b8286
decision: RT1_MOCK_CONTRACT_INTEGRATION_AUTHORIZED
```

- [x] released v5.2.0 tag/commitを固定する。
- [x] public Voice Input / Realtime / interrupt-output-control / Motion exportsを確認する。
- [x] real runtimeが未実装であることを別状態として記録する。
- [x] global capability snapshotのv5.1 schema残存を記録する。
- [x] RT-1をmock-contract-onlyで開始可能と判定する。
- [x] RT-3/RT-4/RT-5/RT-7のreal-runtime blockを維持する。
- [x] Backend/Flutter runtimeと既存testsを変更しないsource-tree gateを追加する。
- [x] local gate、Backend 110件、Flutter 103件、diff review、明示承認を通す。
- [x] acceptance syncでRT-1aをCOMPLETED / ACCEPTEDへ更新する。
- [ ] accepted stateをコミットする。

RT-1aはcompileall、RT-0a/RT-0b/RT-0c/RT-1a gate、DRC `.venv`でのBackend 110件、Flutter 103件、diff review、明示承認の通過後にCOMPLETED / ACCEPTEDとなった。

次小コミットはRT-1b CURRENT / NOT_COMPLETED; NOT_STARTED。Backend-onlyでDRC所有の
realtime state/event/capability/session modelとFramework event normalizerを
追加する。API route、WebSocket/SSE、microphone、Flutter UI、provider実行は
RT-1bへ含めない。
