# Daily Rhythm Companion post-v2.0.0 task list

更新日: 2026-08-03
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
current parent phase: RT-8 CURRENT / NOT_COMPLETED
current small commit: RT-8c Stage 1 PC Windows operator tooling
current implementation step: RT-8c Stage 1 credential-free preflight and strict PC manifest recorder
current implementation state: IMPLEMENTED / AWAITING_REVIEW
current implementation baseline: 4815403d4c94b05551df03678e9c2c4e1dfe754e
current implementation commit: none
last accepted small commit: RT-8b1 strict PC execution-count corrective COMPLETED / ACCEPTED / PUSHED at 4815403d4c94b05551df03678e9c2c4e1dfe754e
accepted RT-4c implementation: 72622cab2e73699adaff4f628cfbc4b14323a23a
strategic target: v3.0.0
```

v2.1.0は固定ZIP `DailyRhythmCompanion_v2.1.0_20260725_160036.zip`、annotated tag `DRC_v2.1.0`、GitHub Release、公開後SHA-256再検証まで完了している。公開済み`DRC_v2.0.0`、`DRC_v2.0.1`、`DRC_v2.1.0`を変更せず、v3.0.0の最初の小コミットRT-0aをdocs/test-onlyで完了・受け入れた。RT-0a受け入れ時点ではRT-0bはNOT_STARTEDだった。RT-0bはcompileall、RT-0a/RT-0b gate、Backend 110件、Flutter 103件、diff確認、明示的なオペレーター承認の通過後にCOMPLETED / ACCEPTEDとなった。RT-0bのv5.0.0判定`BLOCKED_FRAMEWORK_UPDATE_REQUIRED`は履歴として維持する。RT-0cもreleased Framework v5.1.0の再評価、local gate、Backend 110件、Flutter 103件、diff確認、明示的なオペレーター承認の通過後にCOMPLETED / ACCEPTEDとなった。host-app基盤は大幅に改善したが、public voice input、unified realtime、hard cancel/TTS queue/barge-in、motion adapterは未リリースのため、`BLOCKED_REALTIME_PUBLIC_CONTRACTS_MISSING`としてRT-1以降を開始しない。

その後、released FW v5.2.0〜v5.4.0のpublic boundaryを段階的に採用し、RT-1、RT-2、RT-3、RT-3d、RT-3d2、RT-3d3はCOMPLETED / ACCEPTEDとなった。RT-4aは実装コミット`235654e470f8c0cac17644ddf216ac7e6e223514`でCOMPLETED / ACCEPTED / PUSHED。RT-4bは実装コミット`7e1e10e2ca33dd76ee963fcda31c2c5f800b4901`でCOMPLETED / ACCEPTED / PUSHED。RT-4cは実装コミット`72622cab2e73699adaff4b628cfbc4b14323a23a`でbounded SSE transport、cooperative cancel、capacity/time/event limits、disconnect cleanupを実装し、commit-scoped再構成、専用gate、16 focused Backend tests、全回帰、exact diff、private scan、明示承認後にCOMPLETED / ACCEPTED / PUSHEDとなった。RT-4dは実装コミット`f713f515eef723a1d51cfbe35c1dfe16e3547420`でdefault-off FW root-public `ask_stream()` adapterを実装し、同じくcommit-scoped検証と明示承認後にCOMPLETED / ACCEPTED / PUSHEDとなった。provider-level hard cancelは主張しない。RT-4eは実装コミット`1cfe6134b0d19a4d14ebcf3ec76812ce07dac261`でFlutter stream models、injectable SSE client、ChangeNotifier controller、fake transport testsを実装し、COMPLETED / ACCEPTED / PUSHEDとなった。RT-4fはCOMPLETED / ACCEPTEDで、RT-4f1はdocs/test-only inventoryとしてCOMPLETED / ACCEPTED / PUSHED、RT-4f2はCOMPLETED / ACCEPTED / PUSHED、RT-4f3はCOMPLETED / ACCEPTED / PUSHED、RT-4f4は実装コミット`9b19e379634a718df2ab3ed5eb49bb20bfe7e240`でCOMPLETED / ACCEPTED / PUSHEDとなった。RT-5aはdocs/test-only inventoryとして実装コミット`1cf77774dca75b9875099c2b6c6c03992456d80f`でCOMPLETED / ACCEPTED / PUSHEDとなった。RT-5はCURRENT / NOT_COMPLETED。RT-5bはFlutter-only fake/in-memory実装として実装コミット`c48238256cb0b17c925f8063c3b636d3b4ccf533`でCOMPLETED / ACCEPTED / PUSHEDとなった。RT-5cは別のexact contract reviewで承認され、exact nine-file fake-only実装コミット`f00214cd7e75b28c041728bca6ffc3b180face80`がCOMPLETED / ACCEPTED / PUSHEDとなった。RT-5dは別のexact ten-file fake-only HomeScreen contractで承認され、実装コミット`eff46a3b4de771aa37a48ea9ef5959918e407200`でCOMPLETED / ACCEPTED / PUSHEDとなった。RT-5eは別のexact contract reviewで承認され、exact thirteen-file実装commit`ef5f96337b5f601277a9bcc38b9e6fedc520b0a6`がCOMPLETED / ACCEPTED / PUSHEDとなった。configured local operator acceptance、natural audible playback、explicit playback-stop、cleanup、clean-tree verificationも通過した。RT-5f0はexact seven-file docs/test-only readiness checkpointとして実装コミット`348669884e872475aaa4242a5960a6de6fb7e10b`でCOMPLETED / ACCEPTED / PUSHEDとなった。RT-5f1はexact seventeen-file実装コミット`daca3a68672eb3106e861278ebb65612380140ed`としてCOMPLETED / ACCEPTED / PUSHEDとなった。専用gate、focused Backend 12件、Backend全204件、Flutter analyze、focused Flutter 12件、Flutter全355件、exact surface、privacy review、明示承認、push、clean-tree verificationが通過した。private credential read、provider/network execution、real STT、HomeScreen wiring、operator acceptanceは実施していない。RT-5f2はimplementation `c538dc89c2aa9780cd3014aa4ba11c17a9e378e6` とcorrective `b7bd436196210f27782b64c1a094aa65d6893915`でCOMPLETED / ACCEPTED / PUSHEDとなった。Backend 204件、Flutter focused 26件、全381件、exact review、両push、clean-tree verificationが通過した。RT-5f3はexact twenty-file実装commit`75504424c37222234ea8a4314d01ce386ff92d23`でCOMPLETED / ACCEPTED / PUSHEDとなった。専用gate、Backend 204件、Flutter analyze、focused Flutter 53件、Flutter全408件、exact surface/privacy review、明示的なcommit承認、push、clean DRC working treeが通過した。real operator executionとaudible soft-barge-in acceptanceは未実施。RT-5f4はcheckpoint commit`c84617e7ce07ecb1ca1605956eda7435b797c2fe`とcorrective commit`bf17538f8b33aa504671289edda8f55c511fe77d`を通じてCOMPLETED / ACCEPTED / PUSHED。Control A〜D、repeated Stop Capture corrective、playback-time speech detection correctiveは実機で通過し、Backend 204件、Flutter analyze、Flutter全411件も通過した。RT-5fとRT-5はCOMPLETED / ACCEPTED。RT-6はCOMPLETED / ACCEPTED。RT-6aは実装コミット`cbcb218aa54d286da7515a01e899121b22d8f3fc`でCOMPLETED / ACCEPTED / PUSHED。RT-6bはexact ten-file pure-mapping implementation commit `17f0c46eb0b4e26e2fdf5ffd4090c15c69f4e594`でCOMPLETED / ACCEPTED / PUSHED。RT-6cはexact ten-file default-off root-public mock-only implementation commit `f929e8faa65a817f1ba4fed82b729438b73dbfab`でCOMPLETED / ACCEPTED / PUSHED。RT-6dはexact twelve-file Flutter-only implementation commit `0f220b792feb7ebb82c5871a794731aa1327439a`でCOMPLETED / ACCEPTED / PUSHED。RT-6eはimplementation commit `13343017738d0bb5fe23583467856233d62196fb`でCOMPLETED / ACCEPTED / PUSHED。RT-6fはexact nineteen-file implementation commit `fcdce38b9260604ea7c435c6de44fc129dc613f6`でCOMPLETED / ACCEPTED / PUSHED。dedicated gate、Backend focused 10、Backend full 289、Flutter analyze、focused Flutter 15、Flutter full 483、exact surface/privacy/diff review、configured local Controls A-E、post-push clean-treeが通過した。RT-6はCOMPLETED / ACCEPTED。RT-7はBLOCKED_REAL_LIVE2D_VTS_ADAPTER_NOT_IMPLEMENTED。 RT-7aはexact seven-file docs/static-gate implementation commit `efb139b2c0b6c7cc66912a229bd674b36df82dd7`でCOMPLETED / ACCEPTED / PUSHED。compileall、専用gate、Backend 289、Flutter analyze、Flutter 483、exact surface/privacy/diff review、明示承認、push、post-push clean-treeが通過した。RT-7bで固定FW v5.5.0 vendor readinessを受け入れた。RT-7cはexact 11-file implementation `4a2374854801791caefdf0be8cd246e5a2e9278e` とexact 4-file strict-boolean corrective `484ba17245d24a98407907984b28995b247581fa`を通じてCOMPLETED / ACCEPTED / PUSHED。dedicated gate、focused Backend 31、Backend full 320、Flutter analyze、Flutter 483、exact surface/privacy/diff review、両push、clean-tree verificationが通過した。RT-7dはexact 28-file default-off manual VTS wiring implementation `37f7ac8bedc5303f3ddf53e4e543b71f35ce2ed2`としてCOMPLETED / ACCEPTED / PUSHED。dedicated gate、Backend focused 16、Backend full 336、Dart focused format、Flutter analyze、Flutter focused 16、Flutter full 499、exact surface/privacy/diff review、明示承認、push、clean-tree verificationが通過した。RT-7e Controls A-Eと親RT-7はCOMPLETED / ACCEPTED。Control Eは追加provider/network/real-motion executionなしでcleanupと最終同期を固定した。RT-8 exact contract reviewはREADYだが、implementationはNOT_AUTHORIZED。



## RT-5f1 — App-visible provider-neutral real-STT transcript source

```text
status: COMPLETED / ACCEPTED / PUSHED
implementation commit: daca3a68672eb3106e861278ebb65612380140ed
FW: d313eb6acb643103fe25988720ebee5976a04f78
change surface: exact seventeen files
```

受け入れ済み:

- body-only staging IDの`POST /demo/voice-input/transcript`
- default-off real-STT gateとforeground opt-in
- credential/FW root/single-flight preflight-before-consume
- accepted FW root-public real executor assemblyの再利用
- single-use staged WAV cleanup
- exact final transcript response、4096 code-point bound、no-store
- Flutter provider、one-shot staged handle、redirect/size/header/key validation
- existing transcript handoff compatibility
- synthetic Backend/Flutter testsと専用source gate

受け入れ検証:

```text
compileall: passed
dedicated RT-5f1 pre-commit gate: passed
focused Backend: 12 passed
Backend full: 204 passed, 1 existing warning
Flutter analyze: passed
focused Flutter: 12 passed
Flutter full: 355 passed
exact implementation surface: 17 files
privacy review: passed
git diff --check: passed
explicit approval: accepted
implementation push: completed
post-push DRC/FW working trees: clean
```

未実施・未主張:

- private credential read、OpenAI SDK import、network、real STT
- normal main.dart/HomeScreen microphone wiring
- automatic TTS、speech activity、barge-in
- configured real-STT-to-stream operator acceptance

```text
RT-5f2: COMPLETED / ACCEPTED / PUSHED
```

## RT-5f0 — App-visible real-input and DRC-local soft-barge-in readiness

Status: COMPLETED / ACCEPTED / PUSHED

```text
RT-5e  COMPLETED / ACCEPTED / PUSHED
RT-5f0  COMPLETED / ACCEPTED / PUSHED
RT-5f1  COMPLETED / ACCEPTED / PUSHED
RT-5f2  COMPLETED / ACCEPTED / PUSHED
implementation commit: 348669884e872475aaa4242a5960a6de6fb7e10b
```

Readiness result:

```text
PARTIAL_READY_FOR_APP_VISIBLE_REAL_STT_AND_DRC_LOCAL_SOFT_BARGE_IN
```

確認済みの断線点:

```text
- RT-3d3 real transcriptはprivate operator resultだけ。
- FastAPIのapp-visible real-STT consume routeはない。
- normal main.dartはconfigured text streamとvoice outputだけを構成する。
- ProviderNeutralTranscriptResult handoffは存在するがreal providerは未接続。
- production record adapterにspeech onset / amplitude event境界はない。
- RT-5e flushはlocal playerとapp-owned queueだけを停止・無効化する。
- FW v5.4.0はreal runtime / real output flush / hard cancelをsupportしない。
```

RT-5fで許可可能な最終claimはspeech-triggered DRC-local soft barge-inに
限定する。Backend HTTP cancel、provider synthesis cancel、FW real flush、
provider hard cancelはclaimしない。

Accepted exact split:

```text
RT-5f1  app-visible provider-neutral real-STT transcript source
RT-5f2  fake-only integrated voice-turn and soft-barge-in coordinator
RT-5f3  default-off HomeScreen and production speech-activity wiring
RT-5f4  configured local real-STT→stream→TTS and audible soft-barge-in acceptance
```

受け入れ結果:

```text
implementation commit: 348669884e872475aaa4242a5960a6de6fb7e10b
compileall: passed
dedicated RT-5f0 pre-commit gate: passed
Backend full tests: 192 passed, 1 existing warning
Flutter analyze: passed
Flutter full tests: 343 passed
exact implementation surface: 7 files
changed-content privacy review: passed
git diff --check: passed
explicit operator approval: accepted
implementation push: completed
post-push working tree: clean
```

RT-5f0はdocs/test-only。runtime、既存test、dependency、private env、provider
execution、audio/transcript、version、release recordは変更していない。専用gateは
pre-commit baselineとexact seven-file候補に束縛された履歴gateとして保持し、
docs-only acceptance syncでは再実行しない。

RT-5f1は別exact contract reviewを開始できるが、実装・commit・pushは明示承認
まで行わない。詳細: `docs/v300_rt5f_readiness_and_exact_split.md`。

## RT-5b — App-owned bounded voice-output queue

Status: COMPLETED / ACCEPTED / PUSHED

```text
RT-5a  COMPLETED / ACCEPTED / PUSHED
RT-5b  COMPLETED / ACCEPTED / PUSHED
RT-5c  COMPLETED / ACCEPTED / PUSHED
```

実装境界:

```text
- Flutter-onlyのFIFO pending queue。
- pending最大8件、utterance最大4096 Unicode code points。
- active + pendingのretained text最大16384 code points。
- active claimは1件のみ。
- enqueue / claim / complete / fail / flush / disposeをtyped化。
- flushでgenerationを更新し、古いcomplete/failを拒否。
- pending clearとactive invalidationをlocal stop完了前に確定。
- concurrent flushはinjected local playback stopを1回だけ共有。
- local stop失敗でもqueue clearを戻さずtyped partial resultを返す。
- public stateへutterance textを載せず、log/persistence/UIへ保存しない。
```

No HomeScreen integration、Backend/HTTP、existing player、Framework/provider、
real audio、automatic TTS、hard cancel、barge-in変更は含めない。詳細:
`docs/v300_rt5b_voice_output_queue_contract.md`。

受け入れ結果:

```text
implementation commit: c48238256cb0b17c925f8063c3b636d3b4ccf533
dart format: passed
compileall: passed
dedicated RT-5b candidate gate: passed
Backend full tests: 192 passed, 1 existing warning
Flutter analyze: passed
focused Flutter tests: 15 passed
Flutter full tests: 293 passed
exact implementation surface: 9 files
changed-content privacy review: passed
git diff --check: passed
explicit operator approval: accepted
implementation push: completed
RT-5c at RT-5b acceptance: NOT_STARTED / NOT_AUTHORIZED
```

専用RT-5b gateはpre-commit exact nine-file候補に束縛された履歴gateとして
保持し、docs-only acceptance syncでは再実行しない。

## RT-5c — Realtime-terminal voice-output orchestration

Status: COMPLETED / ACCEPTED / PUSHED

```text
RT-5a  COMPLETED / ACCEPTED / PUSHED
RT-5b  COMPLETED / ACCEPTED / PUSHED
RT-5c  COMPLETED / ACCEPTED / PUSHED
RT-5d  NOT_STARTED / NOT_AUTHORIZED
```

実装境界:

```text
- completed terminalを明示的にenqueueする。listenerやautomatic TTSは追加しない。
- explicit processNext 1回でRT-5b FIFO itemを最大1件処理する。
- terminal整合性とprivate 32-entry duplicate windowを検証する。
- injected fake synthesisだけを呼び、audioReady / rejected / failedをtyped化する。
- opaque audio URIは最大2048 code pointsのabsolute HTTP(S)だけを受理する。
- injected fake playbackはterminal completed / failed / expired / stoppedまで待つ。
- playback completedだけqueue complete、それ以外はfixed safe codeでqueue failする。
- operation epoch/tokenとqueue generation/itemをasync境界ごとに再検証する。
- flushでlate synthesis/playbackを無効化し、新generation処理を旧Futureから解放する。
- public stateにutterance、terminal IDs、URI、payload、raw exceptionを保持しない。
```

No HomeScreen integration、Backend HTTP、existing real player、Framework/provider、
real synthesis、real audio、automatic TTS、Framework real output flush、provider
hard cancel、speech-triggered barge-in。

受け入れ結果:

```text
implementation commit: f00214cd7e75b28c041728bca6ffc3b180face80
dart format: passed
compileall: passed
dedicated RT-5c candidate gate: passed before commit
Backend full tests: 192 passed, 1 existing warning
Flutter analyze: passed
focused Flutter tests: 22 passed
Flutter full tests: 315 passed
exact implementation surface: 9 files
changed-content privacy review: passed
git diff --check: passed
explicit operator approval: accepted
implementation push: completed
RT-5d: NOT_STARTED / NOT_AUTHORIZED
```

詳細: `docs/v300_rt5c_realtime_terminal_voice_output_orchestration_contract.md`。
専用gate: `scripts/check_v300_rt5c_realtime_terminal_voice_output_orchestration_contract.py`。
専用gateはpre-commit baselineとexact nine-file候補に束縛された履歴gateとして
保持し、docs-only acceptance syncでは再実行しない。

## RT-5d — HomeScreen manual voice-output controls

Status: COMPLETED / ACCEPTED / PUSHED

```text
RT-5a  COMPLETED / ACCEPTED / PUSHED
RT-5b  COMPLETED / ACCEPTED / PUSHED
RT-5c  COMPLETED / ACCEPTED / PUSHED
RT-5d  COMPLETED / ACCEPTED / PUSHED
RT-5e  COMPLETED / ACCEPTED / PUSHED
```

実装境界:

```text
- optional HomeScreen binding factory。main.dartは変更せずdefault unconfigured。
- session-local opt-inはdefault OFF、非永続。
- completed terminalはbutton押下時だけenqueue。
- enqueueだけではprocessしない。
- process button 1回でprocessNextを1回だけ呼ぶ。
- flush buttonだけがapp queue invalidation + injected local fake stopを呼ぶ。
- flushは古いUI process sequenceを無効化し、新generation表示を保護する。
- bindingがorchestratorとbinding-owned cleanupをexactly onceでdisposeする。
- UIはphase/count/typed outcome/fixed codeのみ表示し、text/ID/URI/raw errorを複製しない。
- existing Voice Output Demo playerとは分離し、load/play/stopを呼ばない。
```

受け入れ結果:

```text
implementation commit: eff46a3b4de771aa37a48ea9ef5959918e407200
compileall: passed
dedicated RT-5d candidate gate: passed before commit
Backend full tests: 192 passed, 1 existing warning
Flutter analyze: passed
focused Flutter tests: 16 passed
Flutter full tests: 331 passed
exact implementation surface: 10 files
HomeScreen final diff: +396 / -0
changed-content privacy review: passed
git diff --check: passed
explicit operator approval: accepted
implementation push: completed
RT-5e: COMPLETED / ACCEPTED / PUSHED
```

No `main.dart`、Backend、configured runtime、existing RT-5c orchestrator、
queue、existing real player、dependency、permission、version、release record、
FW repo変更。

No Backend HTTP、Framework/provider実行、real synthesis、real audio、
automatic TTS、Framework real output flush、provider hard cancel、
speech-triggered barge-in。

詳細: `docs/v300_rt5d_home_screen_voice_output_controls.md`。
専用gate: `scripts/check_v300_rt5d_home_screen_voice_output_controls.py`。
専用gateはpre-commit baselineとexact ten-file候補に束縛された履歴gate
として保持し、docs-only acceptance syncでは再実行しない。RT-5eは後に
exact contract review、実装commit `ef5f96337b5f601277a9bcc38b9e6fedc520b0a6`、push、private operator
acceptanceまで完了した。

## RT-5e — Configured local Backend/FW one-shot synthesis and local playback-stop

Status: COMPLETED / ACCEPTED / PUSHED

```text
RT-5d  COMPLETED / ACCEPTED / PUSHED
RT-5e  COMPLETED / ACCEPTED / PUSHED
RT-5f  NOT_STARTED / BLOCKED_READINESS
implementation commit: ef5f96337b5f601277a9bcc38b9e6fedc520b0a6
FW baseline: d313eb6acb643103fe25988720ebee5976a04f78
```

受け入れ済み実装境界:

```text
- compile-time flagはdefault OFF。通常アプリはvoice-output-unconfigured。
- existing Backend /demo/voice-outputとFW v5.4.0 root-public APIだけを使用。
- process button 1回につきBackend one-shot requestを最大1回。
- exact generated contractとroot-relative opaque MP3 URLだけを再生候補にする。
- RT-5e bindingが専用local playerを所有し、existing Demo playerを共有しない。
- flushはapp-owned queue + RT-5e専用local player stopだけ。
- old synthesis/playback completionはexisting generation/epochで無効化。
```

2026-07-31 configured local operator acceptance:

```text
configured runtime: true
opt-in default off: true
stream terminal completion: confirmed
explicit enqueue: accepted
real FW root-public synthesis: accepted
natural audible playback completion: accepted
active playback before flush: confirmed
explicit flush: completed
cleared pending: 0
local playback stop requested: true
local playback stop succeeded: true
audible playback interruption: confirmed
final phase: idle
final pending: 0
final active: no
operator artifact files removed: 3
operator artifacts remaining: false
private evidence committed/pushed: false
DRC/FW working trees after cleanup: clean
```

実装検証はdedicated gate、FW root-public smoke、Backend 192、Flutter
analyze、focused Flutter 82、full Flutter 343、exact thirteen-file review、
HomeScreen semantic-only `+6/-6`、privacy review、`git diff --check`を通過。
実装commit `ef5f96337b5f601277a9bcc38b9e6fedc520b0a6` はmainへpush済み。

No Backend/FW source change、DRC provider client、FW internal import、automatic
TTS、automatic drain、Backend cancel、provider hard cancel、FW real flush、
speech-triggered barge-in、real-STT-to-TTS。

詳細: `docs/v300_rt5e_configured_local_voice_output_acceptance.md`。
専用gateはpre-commit baselineとexact thirteen-file候補に束縛された履歴
gateとして保持し、six-document acceptance syncでは再実行しない。

RT-5はCURRENT / NOT_COMPLETED。RT-5fはNOT_STARTED /
BLOCKED_READINESSのままで、未承認。

---

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
docs/v300_backend_realtime_normalization.md
scripts/check_v300_backend_realtime_normalization.py
docs/v300_microphone_permission_capture_inventory.md
scripts/check_v300_microphone_permission_capture_inventory.py
docs/v300_microphone_permission_contract.md
scripts/check_v300_microphone_permission_contract.py
docs/v300_microphone_platform_permission_wiring.md
scripts/check_v300_microphone_platform_permission_wiring.py
docs/v300_framework_v530_stt_integration_inventory.md
scripts/check_v300_framework_v530_stt_integration_inventory.py
docs/v300_host_audio_handoff_lifecycle.md
scripts/check_v300_host_audio_handoff_lifecycle.py
docs/v300_framework_real_stt_requirement_feedback.md
scripts/check_v300_framework_real_stt_requirement_feedback.py
docs/v300_framework_v540_real_stt_adoption_inventory.md
scripts/check_v300_framework_v540_real_stt_adoption_inventory.py
docs/v300_rt3d2a_framework_v540_executor_path_correction.md
scripts/check_v300_rt3d2a_framework_v540_executor_path_correction.py
docs/v300_rt3d2b_bounded_marked_fake_executor_wiring.md
scripts/check_v300_rt3d2b_bounded_marked_fake_executor_wiring.py
docs/v300_rt3d2c_guarded_real_executor_assembly_contract.md
scripts/check_v300_rt3d2c_guarded_real_executor_assembly_contract.py
docs/v300_rt4_streaming_cancel_current_behavior_inventory.md
scripts/check_v300_rt4_streaming_cancel_current_behavior_inventory.py
docs/v300_rt4_backend_stream_contract.md
scripts/check_v300_rt4_backend_stream_contract.py
docs/v300_rt4_backend_sse_transport.md
scripts/check_v300_rt4_backend_sse_transport.py
docs/v300_rt4_framework_public_streaming_adapter.md
scripts/check_v300_rt4_framework_public_streaming_adapter.py
docs/v300_rt5_tts_output_control_current_behavior_inventory.md
scripts/check_v300_rt5_tts_output_control_current_behavior_inventory.py
docs/v300_rt5b_voice_output_queue_contract.md
scripts/check_v300_rt5b_voice_output_queue_contract.py
docs/v300_rt5c_realtime_terminal_voice_output_orchestration_contract.md
scripts/check_v300_rt5c_realtime_terminal_voice_output_orchestration_contract.py
docs/v300_rt5d_home_screen_voice_output_controls.md
scripts/check_v300_rt5d_home_screen_voice_output_controls.py
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
Current parent phase: RT-2 CURRENT / NOT_COMPLETED
Current small commit: RT-2a CURRENT / NOT_COMPLETED
Completed small commit: RT-1b COMPLETED / ACCEPTED
Current authorization: RT2A_INVENTORY_IMPLEMENTED_NOT_ACCEPTED
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
- [x] accepted stateをコミットする。

RT-1aはcompileall、RT-0a/RT-0b/RT-0c/RT-1a gate、DRC `.venv`でのBackend 110件、Flutter 103件、diff review、明示承認の通過後にCOMPLETED / ACCEPTEDとなった。

次小コミットはRT-1b CURRENT / NOT_COMPLETED; NOT_STARTED。Backend-onlyでDRC所有の
realtime state/event/capability/session modelとFramework event normalizerを
追加する。API route、WebSocket/SSE、microphone、Flutter UI、provider実行は
RT-1bへ含めない。


### RT-1b — Backend realtime model and Framework-contract normalization

```text
status: COMPLETED / ACCEPTED
implementation: COMPLETED / ACCEPTED
parent RT-1: COMPLETED / ACCEPTED
```

- [x] DRC-owned realtime state enumを追加する。
- [x] DRC-owned realtime event typeとevent modelを追加する。
- [x] public/mock/realを分離したcapability modelを追加する。
- [x] DRC-owned realtime session snapshotを追加する。
- [x] Framework object/mappingを扱うnormalizerを追加する。
- [x] Framework Enumの`.value`を安全に正規化する。
- [x] session-specific v5.2.0 metadataをstale global snapshotより優先する。
- [x] unknown future eventを失敗させず保持する。
- [x] metadataのsecret/private keyをredactする。
- [x] focused Backend 6件、full Backend 116件をlocal実装検証で通す。
- [x] API route、transport、microphone、Flutter、Framework import、provider実行を追加しない。
- [x] operator環境でfocused/full Backend、Flutter 103件、diff reviewを通す。
- [x] explicit approval後にRT-1bとparent RT-1をCOMPLETED / ACCEPTEDへ同期する。
- [x] compileall、focused Backend 6件、full Backend 116件、Flutter 103件、`git diff --check`を通す。
- [x] Framework import、API route、microphone、provider execution、realtime runtime開始がないことを確認する。

RT-1bは2026-07-26にCOMPLETED / ACCEPTED。次はRT-2のguarded microphone permission/capture pathを小コミットへ分割してから着手する。real STTは引き続きFW実装待ち。

### RT-2a permission/capture inventory and split

status: COMPLETED / ACCEPTED
implementation: COMPLETED / ACCEPTED

- [x] `app/pubspec.yaml`にmicrophone/permission/capture packageがないことを確認する。
- [x] Android main manifestに`RECORD_AUDIO`がないことを確認する。
- [x] iOS `Info.plist`に`NSMicrophoneUsageDescription`がないことを確認する。
- [x] Flutter voice-input UIがmetadata-only backend requestで、録音しないことを確認する。
- [x] Backend voice-input demoがaudioを受け取らず、real STTを開始しないことを確認する。
- [x] RT-2b〜RT-2eをpermission contract、platform permission、fake capture、guarded real captureへ分割する。
- [x] always-on/background recording、raw audio default persistence、RT-3前のSTT送信を除外する。
- [x] operator環境でgate、Backend 116件、Flutter 103件、diff reviewを通す。
- [x] explicit approval後にRT-2aをCOMPLETED / ACCEPTEDへ同期する。

RT-2aは2026-07-26にCOMPLETED / ACCEPTED。compileall、RT-1b/RT-2a gate、Backend 116件、Flutter 103件、`git diff --check`、7-file diff review、explicit operator approvalが通過した。Backend/Flutter runtime、existing tests、pubspec、Android/iOS permission、version、release recordは変更していない。RT-2bはapp-owned permission contractとfake/unsupported gatewayだけに限定して開始可能。

### RT-2b app-owned permission contract and fake gateway

status: COMPLETED / ACCEPTED
implementation: COMPLETED / ACCEPTED

- [x] unknown/granted/denied/permanently-denied/restricted/unsupported/failed statesを追加する。
- [x] check/request/open-settings operationをtyped contractへ分離する。
- [x] conservativeなcanRequest/canOpenSettings判定を追加する。
- [x] safe user messageとtechnical codeを分離する。
- [x] immutable public metadataを追加する。
- [x] platform-neutral `MicrophonePermissionGateway` interfaceを追加する。
- [x] OS permissionを呼ばないdeterministic fake gatewayを追加する。
- [x] fake check/request/settings call countとrequest sequenceをtestする。
- [x] focused Flutter testsを追加する。
- [x] dependency、manifest、MethodChannel、UI、microphone、capture、Backend、Framework、provider、STTを変更しない。
- [x] operator環境でRT-2b gate、focused Flutter 9件、full Flutter 112件、Backend 116件、diff reviewを通す。
- [x] explicit approval後にRT-2bをCOMPLETED / ACCEPTEDへ同期する。

RT-2bは2026-07-26にCOMPLETED / ACCEPTED。compileall、RT-2b gate、focused Flutter 9件、full Flutter 112件、Backend 116件、`git diff --check`、9-file diff review、gate portability fixes、explicit operator approvalが通過した。RT-2c platform permission wiring without captureはCURRENT / NOT_COMPLETED、NOT_STARTED。

### RT-2c platform permission wiring without capture

status: COMPLETED / ACCEPTED
implementation: COMPLETED / ACCEPTED

- [x] `permission_handler` 12.0.3を`pubspec.yaml`へpinする。
- [x] operator環境の`flutter pub get`で`pubspec.lock`を解決する。
- [x] `permission_handler_windows`のgenerated registrant/CMake更新がplugin登録のみであることを確認する。
- [x] Android main manifestへ`RECORD_AUDIO`を1件だけ追加する。
- [x] iOS `Info.plist`へ日本語の`NSMicrophoneUsageDescription`を追加する。
- [x] app-owned gateway interfaceのAndroid/iOS実装として閉じ込める。
- [x] web/desktopはpluginを呼ばずtyped unsupportedへfail closedする。
- [x] denied/granted/restricted/permanently-deniedをDRC contractへ正規化する。
- [x] microphoneでは想定外のlimited/provisionalをfailedへ閉じる。
- [x] MissingPlugin/Unsupported/generic errorからraw errorを公開しない。
- [x] fake driver focused testsを追加し、real OS permission dialogを呼ばない。
- [x] startup、`HomeScreen`、voice-input UIへgatewayを接続しない。
- [x] microphone open、audio capture、raw audio、Backend upload、Framework/provider/STTを開始しない。
- [x] operator環境で`flutter analyze` clean、focused Flutter 13件、full Flutter 125件、Backend 116件、Android debug APK buildを通す。
- [x] Windows generated plugin filesを許可・検証する修正版RT-2c gateと16-file diff reviewを通す。
- [x] operator acceptance evidence後にRT-2cをCOMPLETED / ACCEPTEDへ同期する。

RT-2cは2026-07-27にCOMPLETED / ACCEPTED。implementation commit `fe26c3c`、`flutter pub get`、Windows generated plugin exact-marker review、`flutter analyze` clean、focused Flutter 13件、full Flutter 125件、Backend 116件、RT-2c gate、Android debug APK build、`git diff --check`、16-file review、operator acceptance evidenceが通過した。permission request、microphone access、audio capture、Backend upload、Framework/provider/STTは実行していない。

### RT-2d capture lifecycle contract and fake engine

status: COMPLETED / ACCEPTED
implementation: COMPLETED / ACCEPTED

- [x] app-owned capture lifecycle state/result/request contractを追加する。
- [x] single-active-session、bounded duration、stop/cancel/error cleanupを型で固定する。
- [x] microphoneへ触れないdeterministic fake capture engineを追加する。
- [x] permission denied/restricted/unsupported/busy/timeout/cancel/cleanup failureを分離する。
- [x] UI、platform capture plugin、real microphone、raw audio、Backend upload、STTを変更しない。

- [x] permission checkだけを使用し、permission request/settings openを実行しない。
- [x] resultからraw bytes、local path、platform handleを排除し、opaque fake idだけを返す。
- [x] RT-2d source/surface gateとfocused testを追加する。
- [x] operator環境で`flutter analyze`、focused/full Flutter、Backend regression、`git diff --check`、9-file reviewを通す。
- [x] explicit operator approval後にRT-2dをCOMPLETED / ACCEPTEDへ同期する。

RT-2dは2026-07-27にCOMPLETED / ACCEPTED。compileall、RT-2d gate、`flutter analyze` clean、focused Flutter 17件、full Flutter 142件、Backend 116件（既存warning 1件）、`git diff --check`、9-file review、explicit operator approvalが通過した。permission request、real microphone access、audio capture、raw audio exposure、Backend upload、Framework/provider/STT executionは行っていない。

### RT-2e explicitly guarded bounded real capture adapter

status: CURRENT / NOT_COMPLETED

#### RT-2e-a exact-surface and recorder-package readiness

status: COMPLETED / ACCEPTED
implementation: COMPLETED / ACCEPTED; docs/test-only

- [x] 現行Flutter/platform/permission/capture/dependency/test境界をexact HEAD archiveから再確認する。
- [x] Dart `^3.11.5`ではDart 3.12以上を要求する`record` 7.xを採用しない。
- [x] RT-2e-b候補を互換pre-7 lineの`record` 6.2.1へ固定する。
- [x] raw byte streamを公開する`startStream`をRT-2eで使用しない。
- [x] file modeはprivate temporary artifact/path boundaryの内側だけで使用する方針を固定する。
- [x] permission ownershipは既存permission gatewayに残し、recorder側のpermission APIへ委譲しない。
- [x] docs/test-only gateを追加し、dependency/runtime/platform/UI変更がないことを検証する。
- [x] operator verificationとexplicit approval後にRT-2e-aをCOMPLETED / ACCEPTEDへ同期する。

#### RT-2e-b injectable recorder adapter and private temporary artifact

status: COMPLETED / ACCEPTED
implementation: COMPLETED / ACCEPTED

- [x] `record: 6.2.1`と`path_provider: 2.1.6`をexact direct dependencyとして追加する。
- [x] operator `flutter pub get`でlockとgenerated plugin registrationを解決・reviewする。
- [x] injected driverでstart/stop/cancel/disposeをRT-2d engineへ接続する。
- [x] private temporary path/artifact registryとstop/cancel/error/dispose cleanupを実装する。
- [x] controllerはengine completionからallowlisted safe metadataだけを伝播する。
- [x] unit testsはfake driver/fake filesystemのみを使い、permission requestやreal captureを実行しない。
- [x] analyzer warning 3件を失敗経路テストへ置き換え、focused Flutter 18件、lifecycle Flutter 18件、full Flutter 161件、Backend 116件、gate、Android debug APK build、diff reviewを通す。
- [x] explicit operator approval後にRT-2e-bをCOMPLETED / ACCEPTEDへ同期する。

#### RT-2e-c explicit operator real-device capture evidence

status: CURRENT / NOT_COMPLETED

##### RT-2e-c1 operator-only harness/readiness contract

status: COMPLETED / ACCEPTED
implementation: COMPLETED / ACCEPTED; docs/test-only

- [x] accepted `5a7f814`のstartup、HomeScreen、permission、capture、record adapter、test surfaceをexact archiveから再確認する。
- [x] normal `main.dart`/`HomeScreen`を変更せず、separate `main_rt2ec_operator.dart`だけを後続harness entrypointにする。
- [x] `--dart-define=DRC_RT2EC_OPERATOR=true`とin-app acknowledgementの二重opt-inを必須にする。
- [x] permission check/request/start/stop/cancelを自動実行せず、別々のexplicit user actionにする。
- [x] granted後のみstart可能、maximum 15 seconds、WAV 16 kHz mono、single active captureを固定する。
- [x] stop完了後はopaque id経由でprivate artifactを即時discardし、path/raw bytes/audio contentをUI/log/evidenceへ出さない。
- [x] safe evidenceをstatus/code/booleans/duration/cleanupだけにallowlistし、Backend upload、Framework/provider、STTを禁止する。
- [x] docs/test-only source/surface gateを追加し、runtime/dependency/platform/UI/Backend変更とreal executionがないことを検証する。
- [x] operator verificationとexplicit approval後にRT-2e-c1をCOMPLETED / ACCEPTEDへ同期する。

##### RT-2e-c2 operator-only harness and fake/widget tests

status: COMPLETED / ACCEPTED
implementation: COMPLETED / ACCEPTED
authorization: completed-accepted-fake-widget-only

- [x] RT-2e-c1 acceptance後にseparate operator entrypointとdouble opt-in harnessを追加する。
- [x] production-capable dependenciesはcompile-time flagとin-app acknowledgement後だけ構築する。
- [x] permission check/request/start/stop/cancel、15-second bound、auto-discard、safe evidenceをfake/widget testsで検証する。
- [x] default main/HomeScreen、Backend、platform declarations、dependenciesを変更しない。
- [x] real permission request、microphone access、audio captureは実行しない。
- [x] operator verificationとexplicit approval後にRT-2e-c2をCOMPLETED / ACCEPTEDへ同期する。

##### RT-2e-c3 real Android bounded capture and cleanup evidence

status: CURRENT / NOT_COMPLETED

###### RT-2e-c3a real Android operator preflight and safe evidence contract

status: COMPLETED / ACCEPTED
implementation: COMPLETED / ACCEPTED; docs/test-only
authorization: completed-docs-test-only-preflight

- [x] accepted `b2e2adb` operator target、permission gateway、record adapter、Android manifest、safe evidence surfaceをexact archive SHA-256 `18d39ea0676bcd3213c104a71fd5ce2c096c6b96002eb7aaef7ceccd06a2fd86`から再確認する。
- [x] physical Android deviceだけを受け入れ、Web/Windows/iOS/emulatorをevidence targetにしない。
- [x] `flutter run -d <ANDROID_DEVICE_ID> --target lib/main_rt2ec_operator.dart --dart-define=DRC_RT2EC_OPERATOR=true`を唯一のoperator起動経路として固定する。
- [x] Android設定で既存microphone permissionを事前にrevoked/deniedへ戻し、in-app acknowledgement後にcheck/request/start/stopを別々に明示操作する。
- [x] non-sensitive test phraseを1回だけ、15秒未満で録音し、stop後のprivate artifact即時discardを必須にする。
- [x] marker-only evidenceをallowlisted status/code/boolean/durationへ限定し、device serial/model、private path、opaque id、raw audio、audio content、raw screenshotを除外する。
- [x] docs/test-only source/surface gateを追加し、Flutter/Backend/runtime/platform/dependency変更とreal executionがないことを検証する。
- [x] compileall、RT-2e-c3a gate、Backend 116件（既存warning 1件）、`flutter analyze`、full Flutter 171件、`git diff --check`、exact ten-file review、explicit operator approval後にCOMPLETED / ACCEPTEDへ同期した。

###### RT-2e-c3b explicit real Android bounded capture and cleanup evidence

status: COMPLETED / ACCEPTED
implementation: COMPLETED / ACCEPTED; marker-only real Android evidence
authorization: completed-accepted-explicit-real-android-bounded-capture-evidence

- [x] clean accepted RT-2e-c3a HEAD `ddae21944ac0e251cd8194bf93982bd5dc7a4ae8`からphysical Android operator targetを起動した。
- [x] permission request attempted=true、permission status=grantedをsafe evidenceで確認した。
- [x] acceptance sessionの1回のbounded completed captureでduration=4820 ms、microphone/audio=true、raw audio exposed=falseを確認した。
- [x] private artifact registered/discarded=true、cleanup succeeded=trueを確認した。
- [x] Backendを起動せず、upload、Framework/provider、STT、transcript persistenceを実行しなかった。
- [x] raw audio、private path、opaque id、device serial/model、raw screenshot、private operator pathをcommitしなかった。
- [x] `flutter run`終了後のworking treeがcleanで、source commitが変わっていないことを確認した。

最初のoperator sessionはduration markerを保持しなかったためacceptance evidenceには使用しない。後続のacceptance sessionは1回のcompleted captureだけを含み、marker-only evidenceを取得した。RT-2、RT-2e、RT-2e-c、RT-2e-c3はCOMPLETED / ACCEPTED。RT-3は`BLOCKED_REAL_STT_NOT_IMPLEMENTED`のまま。

RT-2e authorization: `authorized-explicit-opt-in-bounded-real-capture-adapter-only`。RT-2e-bは2026-07-27にCOMPLETED / ACCEPTED。operator `flutter pub get`、generated plugin review、analyzer cleanup、focused Flutter 18件、lifecycle Flutter 18件、full Flutter 161件、Backend 116件（既存warning 1件）、RT-2e-b gate、Android debug APK build、`git diff --check`、19-file review、explicit operator approvalが通過した。Kotlin incremental-cache daemonはcross-drive cache errorを報告したが、Gradle fallback後にAPK生成は成功した。real permission request、microphone access、audio capture、public raw path/bytes exposure、upload、STT executionは行っていない。RT-2e-c1はcompileall、RT-2e-c1 gate、Backend 116件（既存warning 1件）、`flutter analyze`、full Flutter 161件、`git diff --check`、exact 8-file review、explicit operator approvalの通過後にCOMPLETED / ACCEPTEDとなった。RT-2e-c2はcompileall、RT-2e-c2 gate、Backend 116件（既存warning 1件）、`flutter analyze`、focused Flutter 10件、full Flutter 171件、`git diff --check`、exact 12-file review、explicit operator approvalの通過後にCOMPLETED / ACCEPTEDとなった。separate entrypoint、compile-time flag、in-app acknowledgement後のlazy dependency construction、explicit permission/capture actions、15-second bound、opaque-id immediate discard、safe evidence allowlist、fake/widget testsを追加した。default app、dependencies、platform、Backendは変更せず、real permission request、microphone access、audio capture、upload、STT executionは行っていない。RT-2e-c3aはcompileall、RT-2e-c3a gate、Backend 116件（既存warning 1件）、`flutter analyze`、full Flutter 171件、`git diff --check`、exact ten-file review、explicit operator approvalの通過後にCOMPLETED / ACCEPTEDとなった。docs/test-onlyであり、real permission request、microphone access、audio captureは行っていない。RT-2e-c3bはphysical Androidのmarker-only evidence取得、4820 msのbounded capture、private artifact discard、cleanup、post-run clean tree確認後にCOMPLETED / ACCEPTEDとなった。RT-2、RT-2e、RT-2e-c、RT-2e-c3もCOMPLETED / ACCEPTEDで、RT-3は`BLOCKED_REAL_STT_NOT_IMPLEMENTED`のまま。


RT-2e-c3b acceptance evidence summary:

```text
source_commit: ddae21944ac0e251cd8194bf93982bd5dc7a4ae8
target_class: physical-android
permission_status: granted
permission_request_attempted: true
capture_outcome: completed
captured_duration_milliseconds: 4820
microphone_accessed: true
audio_captured: true
raw_audio_exposed: false
private_artifact_discarded: true
cleanup_succeeded: true
backend_started: false
audio_uploaded: false
stt_executed: false
post_run_working_tree_clean: true
```

## RT-3a Framework v5.3.0 STT integration inventory

Status: COMPLETED / ACCEPTED

- [x] DRC source commit `c7a6afd85f29fe07564ded02a76fa645b2fb9a69`を固定した。
- [x] vendored FW v5.3.0 public STT surfaceをsource-onlyで照合した。
- [x] public host-audio types、fake adapter、session adapter wiringを確認した。
- [x] guarded real adapterが`real_stt_not_implemented`を返し、real providerを実行しないことを確認した。
- [x] DRC voice-input APIがmetadata-onlyで、audio upload/stagingを持たないことを確認した。
- [x] DRC private capture artifactはopaque IDで解決可能だが、operator pathでは停止直後にdiscardされることを確認した。
- [x] RT-3bをapp-owned handoff lifecycle contractだけに限定した。
- [x] RT-3cをprivate backend stagingとfake FW public-session handoffだけに限定した。
- [x] RT-3d real provider evidenceをFW real provider execution実装待ちとして維持した。
- [x] operator環境でgate、Backend 116、Flutter 171、clean analyze、diff reviewを通した。
- [x] RT-3aをCOMPLETED / ACCEPTEDへ同期した。
- [x] accepted stateをコミットする。

RT-3a acceptanceではBackend/Flutter runtime、existing tests、dependencies、platform、
vendor、private env、version/release recordを変更しない。FW import、audio
read/upload、microphone access、provider execution、STT executionも行わない。


## RT-3b app-owned host-audio handoff lifecycle contract

Status: COMPLETED / ACCEPTED

Authorization: `authorized-app-owned-host-audio-lifecycle-contract-fake-only`

RT-3bはopaque capture artifactのretain/lease/consume/discard契約だけを追加する。network upload、private path公開、FW import、provider execution、STT execution、既存RT-2 operator pathのdefault変更は禁止する。

- [x] completed captureだけをretained artifactとして受け付ける。
- [x] 15秒上限、encoding、sample rate、channel countを検証する。
- [x] single retained artifactを強制する。
- [x] private pathをpublic resultへ含めず、consumer実行中だけscoped callbackを許可する。
- [x] fake consumerを追加し、audio read/upload/FW/provider/STTを行わない。
- [x] consume success/failure/exceptionでprivate artifactをdiscardする。
- [x] cancel、explicit discard、closeでcleanupする。
- [x] cleanup failure時はexplicit retry可能なleaseを維持する。
- [x] public metadata allowlistでprivate path、opaque ID、credential-like fieldを除外する。
- [x] existing RT-2 operator path、Backend、dependencies、platform、vendorを変更しない。
- [x] operator環境でfocused Flutter 21、full Flutter 192、Backend 116、clean analyze、diff reviewを通す。
- [x] cleanup-retry test order correctionを適用し、focused/full Flutterを再検証する。
- [x] RT-3bをCOMPLETED / ACCEPTEDへ同期する。
- [ ] accepted stateをコミットする。

Acceptance evidence: source gate、Backend 116（既存warning 1件）、`flutter analyze`、focused Flutter 21、full Flutter 192、exact ten-file review、cleanup-retry test correction、`git diff --check`。

## RT-3c private Backend staging and fake FW public-session handoff

Status: COMPLETED / ACCEPTED

Authorization outcome: `completed-accepted-private-backend-staging-and-fake-fw-public-session-handoff`

RT-3cはprivate Backend staging境界とfake FW public-session handoffだけを追加する。real provider execution、real STT acceptance、raw audio/public private path exposureは引き続き禁止する。


## RT-3c1 private staging and fake FW handoff readiness

```text
RT-3c1: COMPLETED / ACCEPTED
implementation: COMPLETED / ACCEPTED
RT-3c2: COMPLETED / ACCEPTED
RT-3c3: COMPLETED / ACCEPTED / COMPLETED / ACCEPTED
RT-3c3 authorization: authorized-guarded-binary-upload-route-and-flutter-scoped-staging-consumer-only
runtime changed: no
audio uploaded/staged/read: no
Framework imported/executed: no
provider/STT executed: no
```

RT-3c1 fixes the following implementation sequence before runtime changes:

```text
RT-3c2
bounded private Backend staging store/config only

RT-3c3
guarded streamed audio/wav upload plus Flutter scoped staging consumer

RT-3c4
fake FW public VoiceInputSession handoff and single-use staged cleanup
```

Selected defaults for later implementation:

```text
content type: audio/wav or application/octet-stream
multipart: not used
maximum body: 1048576 bytes
staging TTL: 300 seconds
maximum staged artifacts: 8
audio contract: WAV / 16000 Hz / mono / <=15000 ms
public response: opaque server staging ID only; never a path
storage: backend/local_data/voice_input/staging
```

Acceptance evidence: compileall、source-only gate、Backend 116（既存warning 1件）、`flutter analyze`、full Flutter 192、exact nine-file review、`git diff --check`。

RT-3c2 acceptance evidence: compileall、four RT-3 gates、focused Backend 14、full Backend 127（既存warning 1件）、`flutter analyze`、full Flutter 192、exact 18-file surface review、`git diff --check`。

RT-3c3 acceptance evidence: compileall、five RT-3 gates、focused Backend 21、full Backend 137（既存warning 1件）、`flutter analyze`、focused Flutter 29、full Flutter 200、exact 22-file surface review、`git diff --check`。RT-3c4 and parent RT-3c are COMPLETED / ACCEPTED after compileall、six RT-3 gates、focused Backend 8、full Backend 145（既存warning 1件）、`flutter analyze`、full Flutter 200、exact 22-file surface review、`git diff --check`、explicit operator approval。RT-3d remains blocked pending accepted Framework real provider execution.


## RT-3c2 private Backend voice-input staging store

```text
RT-3c2: COMPLETED / ACCEPTED
implementation: COMPLETED / ACCEPTED
authorization at implementation: authorized-bounded-private-backend-staging-store-and-lifecycle-only
expected focused Backend: 14 passed
expected full Backend: 127 passed
expected full Flutter unchanged: 192 passed
```

- [x] Add positive-integer TTL/count/byte-limit configuration with safe defaults.
- [x] Add private `backend/local_data/voice_input/staging` ownership.
- [x] Add bounded chunked WAV staging and opaque IDs.
- [x] Keep public metadata path-free.
- [x] Add single-use scoped consume and explicit discard.
- [x] Add expiry, capacity, partial, rejection, and exception cleanup.
- [x] Add traversal and symlink safety tests.
- [x] Run local acceptance validation.
- [x] Apply acceptance sync after explicit approval.

Acceptance evidence: compileall、four RT-3 gates、focused Backend 14、full Backend 127（既存warning 1件）、`flutter analyze`、full Flutter 192、exact 18-file surface review、`git diff --check`。

RT-3c3 is COMPLETED / ACCEPTED after compileall, five RT-3 gates, focused Backend 21, full Backend 137（既存warning 1件）、`flutter analyze`、focused Flutter 29、full Flutter 200、exact 22-file surface review、`git diff --check`。No real microphone artifact, Framework import, VoiceInputSession handoff, provider execution, or STT evidence is claimed. RT-3c4 and parent RT-3c are COMPLETED / ACCEPTED under authorization `authorized-fake-fw-public-session-handoff-and-single-use-staged-artifact-cleanup-only`.


## RT-3c3 guarded binary upload and Flutter scoped staging consumer

```text
RT-3c3: COMPLETED / ACCEPTED
implementation: COMPLETED / ACCEPTED
authorization at implementation: authorized-guarded-binary-upload-route-and-flutter-scoped-staging-consumer-only
RT-3c4: COMPLETED / ACCEPTED
RT-3c4 implementation: COMPLETED / ACCEPTED
RT-3c4 authorization: authorized-fake-fw-public-session-handoff-and-single-use-staged-artifact-cleanup-only
```

- [x] Add the bounded streamed WAV upload route without multipart.
- [x] Add the Flutter consumer that reads only inside `withPrivateArtifactPath(...)`.
- [x] Return only opaque/path-free staging metadata.
- [x] Keep Framework import, VoiceInputSession, provider execution, and STT absent.
- [x] Add synthetic Backend and Flutter contract tests.
- [x] Run local acceptance validation.
- [x] Apply explicit acceptance sync after approval.

Acceptance evidence: compileall、five RT-3 gates、focused Backend 21、full Backend 137（既存warning 1件）、`flutter analyze`、focused Flutter 29、full Flutter 200、exact 22-file surface review、`git diff --check`。


## RT-3c4 fake FW public-session handoff and single-use staged cleanup

```text
RT-3c4: COMPLETED / ACCEPTED
implementation: COMPLETED / ACCEPTED
authorization: authorized-fake-fw-public-session-handoff-and-single-use-staged-artifact-cleanup-only
```

- [x] Add a Backend adapter that consumes one accepted private staged artifact.
- [x] Create only FW v5.3.0 public `VoiceInputAudioSource` / `VoiceInputSession` objects.
- [x] Use `FakeVoiceInputProviderAdapter` only.
- [x] Return a typed path-free result and guarantee single-use consume/discard cleanup.
- [x] Keep real provider execution, transcription, and STT absent.

## RT-3c4 implementation checkpoint

- [x] Add guarded fake-handoff route for one opaque Backend staging ID.
- [x] Import only the configured FW v5.3.0 public package.
- [x] Build public WAV/file-source/request/session objects.
- [x] Explicitly inject `FakeVoiceInputProviderAdapter`.
- [x] Normalize a path-free typed DRC result.
- [x] Close the FW session in `finally`.
- [x] Consume/discard the staged artifact once callback execution begins.
- [x] Preserve the staged artifact when Framework preflight fails.
- [x] Accept RT-3c4 after local gates, Backend 8/145, Flutter 200, surface review, and explicit approval.
- [ ] Implement real provider execution; RT-3d remains blocked on a future accepted FW boundary.

RT-3c4 acceptance evidence: compileall、six RT-3 gates、focused Backend 8、full Backend 145（既存warning 1件）、`flutter analyze`、full Flutter 200、exact 22-file surface review、`git diff --check`、explicit operator approval。No real microphone artifact、provider execution、real transcription、or real STT is claimed.


## RT-5 - TTS output control, queue, flush, and barge-in

Status: CURRENT / NOT_COMPLETED

```text
RT-5a  COMPLETED / ACCEPTED / PUSHED
        Current DRC/FW TTS output-control inventory, readiness classification,
        terminology separation, and exact small-commit split.
        Docs/test-only. No runtime, provider, network, audio, or existing-test change.

RT-5b  COMPLETED / ACCEPTED / PUSHED
        App-owned bounded TTS utterance queue and local playback-flush lifecycle.

RT-5c  COMPLETED / ACCEPTED / PUSHED
        Explicit completed-terminal to RT-5b queue, injected fake synthesis,
        bounded opaque URI, and injected fake terminal playback orchestration.

RT-5d  NOT_STARTED / NOT_AUTHORIZED
        HomeScreen presentation and explicit opt-in enqueue/play/flush controls.
        Automatic TTS remains default-off.

RT-5e  NOT_STARTED
        Configured local Backend/FW one-shot synthesis, sequential playback,
        pending app-queue clear, and local playback-stop operator acceptance.

RT-5f  NOT_STARTED / BLOCKED_READINESS
        Speech-triggered real barge-in and real-STT-to-TTS acceptance only after
        a separately reviewed app-visible real input source and sufficient public
        FW execution capability exist.
```

RT-5a documents that local playback stop exists, while DRC app-owned TTS queue,
Backend synthesis cancel, DRC output flush endpoint, automatic stream-to-TTS,
real speech-triggered barge-in, provider hard cancel, and FW real queue flush
were not implemented at RT-5a. RT-5b is now accepted, and RT-5c is implemented under a separately authorized exact fake-only contract but remains awaiting patch review.

Detailed inventory: `docs/v300_rt5_tts_output_control_current_behavior_inventory.md`.
Dedicated candidate gate: `scripts/check_v300_rt5_tts_output_control_current_behavior_inventory.py`.

RT-5a acceptance passed on 2026-07-30 at implementation commit `1cf77774dca75b9875099c2b6c6c03992456d80f`
after compileall, the dedicated candidate gate, Backend 192 passed with one
existing warning, Flutter analyze, Flutter 278 passed, exact seven-file review,
privacy scan, `git diff --check`, explicit operator approval, commit, and push.

## RT-3d0 Framework real STT requirement feedback

Status: `COMPLETED / ACCEPTED`

FW v5.3.0 remains the latest released and accepted DRC public Voice Input
baseline. RT-3c4 proves only the fake public-session handoff. Concrete
real-provider execution remains absent, so RT-3d stays
`BLOCKED_FRAMEWORK_REAL_PROVIDER_EXECUTION_NOT_IMPLEMENTED`.

The additional FW requirement must be handled in the FW development thread.
This checkpoint does not select the next FW version or provider and changes no
runtime, dependency, version, audio, provider, or release surface. Acceptance
passed with the six clean-baseline RT-3 gates, the dedicated RT-3d0 gate,
Backend 145, clean Flutter analysis, Flutter 200, exact seven-file review,
`git diff --check`, and explicit operator approval.


## RT-3d1 Framework v5.4.0 real STT adoption inventory

Status: `COMPLETED / ACCEPTED`

The FW v5.4.0 released public real-STT surface is verified. RT-3d remains
`BLOCKED_DRC_V540_REAL_STT_WIRING_AND_OPERATOR_ACCEPTANCE_PENDING`.
No DRC runtime, audio, credential, provider, network, or release execution
occurs in RT-3d1. Acceptance passed with the dedicated source-only gate, Backend 145, clean Flutter analysis, Flutter 200, exact seven-file review, `git diff --check`, and explicit operator approval.


## RT-3d2a FW v5.4.0 executor-path correction

Status: `COMPLETED / ACCEPTED`

The released Voice Input session is data-only. RT-3d2b must use the public bounded marked-fake executor in normal tests. The public real-provider executor is reserved for guarded assembly and private operator acceptance. RT-3d remains `BLOCKED_DRC_V540_REAL_STT_WIRING_AND_OPERATOR_ACCEPTANCE_PENDING`.

RT-3d2a acceptance passed after FW executor distinction checks, safe FW smokes, Backend 145, Flutter analyze, Flutter 200, exact eight-file review, `git diff --check`, and explicit operator approval. RT-3d2b is `AUTHORIZED / NOT_STARTED`.

## RT-3d2b bounded marked-fake executor wiring

Status: `COMPLETED / ACCEPTED`

The Backend now has a separate guarded marked-fake executor path that performs
bounded staged-WAV reading through FW v5.4.0 public contracts, returns a
path-free typed result, and enforces single-use cleanup. It does not read
credentials, import the OpenAI SDK, create a real provider client, access a
microphone, or execute the network.

RT-3d2b acceptance passed with the implementation commit `044f978`, FW safe
marked-fake verification, focused Backend 8, full Backend 153, Flutter analyze,
Flutter 200, exact thirteen-file implementation review, `git diff --check`, and
explicit operator approval.

RT-3d2c authorization: AUTHORIZED / NOT_STARTED.

## RT-3d2c guarded real-executor assembly contract

Status: `COMPLETED / ACCEPTED`

The Backend now has a separate assembly-only service for the released FW v5.4.0
real OpenAI executor path. It requires complete explicit opt-in before Framework
public import or private credential-object preparation.

The service constructs the public execution configuration, real policy, real
client factory, OpenAI adapter, and real provider executor, then returns only a
safe assembly snapshot plus an opaque private executor handle. It does not call
the client factory or executor.

Focused Backend result: `5 passed`. No credential value was read by DRC, no
OpenAI SDK was imported, no provider client or network request was created, and
no staging artifact, audio, microphone, path, payload, transcript, or real STT
was used.

RT-3d2c acceptance passed with implementation commit `12a9d35`, the dedicated
gate, focused Backend 5, full Backend 158 with one existing warning, clean
Flutter analysis, Flutter 200, exact nine-file implementation review,
acceptance-only seven-file review, `git diff --check`, and explicit operator
approval.

RT-3d3 is `AUTHORIZED / NOT_STARTED`. Private credential use, provider client
creation, network execution, transcript evidence, and real STT acceptance remain
separate explicit work. Additional Framework development requirement: `False`.

## RT-3d3 private real-STT operator boundary

```text
Implementation: DONE
Synthetic focused tests: PASS
Non-provider regression: PASS
Dedicated implementation gate: PENDING
Exact nine-file review: PENDING
Actual real-provider execution: NOT_RUN
Private operator acceptance: PENDING
Commit approval: PENDING
Push approval: PENDING
```

Do not place credential values, private paths, raw audio, provider payloads,
transcripts, screenshots, LAN addresses, or operator evidence in the
repository. Actual provider execution requires a new explicit operator opt-in.
RT-3d remains
`BLOCKED_DRC_V540_REAL_STT_WIRING_AND_OPERATOR_ACCEPTANCE_PENDING`.

## RT-3d3 real operator execution checkpoint

```text
RT-3d3: COMPLETED / ACCEPTED
RT-3d2: COMPLETED / ACCEPTED
RT-3d: COMPLETED / ACCEPTED
FW baseline: clean v5.4.0
Transport response status: 200
Transcript nonempty: True
Expected phrase match: True
Staged artifact cleanup complete: True
Provider payload exposed: False
Private path exposed: False
Raw audio exposed: False
Transcript exposed: False
Private operator evidence committed: False
Explicit operator approval: ACCEPTED
Implementation commit: 5f7c7a682b5d52de2ba3ff9592d253f9bbb3341c
```

The deterministic private operator run used the released FW v5.4.0 public
real-STT boundary and completed without changing the repository during
execution. Only fixed public-safe markers are synchronized here.

# 5. Current RT-4 phase

## RT-4 — Streaming LLM, DRC event consumption, and cooperative cancellation

Status: COMPLETED / ACCEPTED

```text
RT-4a  COMPLETED / ACCEPTED  Current behavior inventory and small-commit split
RT-4b  COMPLETED / ACCEPTED  Backend provider-neutral stream lifecycle and fake-only tests
RT-4c  COMPLETED / ACCEPTED / PUSHED  Bounded Backend SSE transport and cancel request boundary
RT-4d  COMPLETED / ACCEPTED / PUSHED  FW v5.4.0 root-public streaming adapter and cooperative cancel
RT-4e  COMPLETED / ACCEPTED / PUSHED  Flutter stream client/controller without HomeScreen integration
RT-4f  COMPLETED / ACCEPTED  UI integration and configured streaming/cancel acceptance
  RT-4f1  COMPLETED / ACCEPTED / PUSHED  Current behavior inventory and exact small-commit split
  RT-4f2  COMPLETED / ACCEPTED / PUSHED  HomeScreen stream presentation and fake controller lifecycle wiring
  RT-4f3  COMPLETED / ACCEPTED / PUSHED  App-owned provider-neutral transcript handoff boundary
  RT-4f4  COMPLETED / ACCEPTED / PUSHED  Configured local Backend/FW streaming and cancel acceptance
```

### RT-4a — Current behavior inventory and small-commit split

Purpose:

```text
- Read the accepted RT-3 DRC implementation and clean FW v5.4.0 public surface.
- Separate existing full-response chat from new incremental streaming work.
- Freeze cooperative cancel versus provider-level hard cancel semantics.
- Fix the RT-4b through RT-4f responsibility split before runtime changes.
- Keep RT-5 TTS queue/flush/barge-in work out of RT-4.
```

Current source facts:

```text
- DRC configured chat calls TextChatSession.ask() and returns one full response.
- POST /chat/sessions/{session_id}/messages is a normal response-model route.
- DRC realtime models have lifecycle/event normalization but no text chunk model.
- Backend has no StreamingResponse, text/event-stream route, or WebSocket route.
- Flutter has no EventSource/WebSocket stream client or stream controller.
- RT-3 real STT returns one completed transcript; it is not yet connected to LLM streaming.
- FW v5.4.0 ask_stream()/events/interrupt() are root-public.
- FW interrupt is cooperative soft cancel, not provider-level hard cancel.
- FW root RealtimeSession real orchestration and TTS queue flush remain unsupported.
```

Exact RT-4a change surface:

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v300_goal_checklist_small_commit.md
docs/v300_rt4_streaming_cancel_current_behavior_inventory.md
scripts/check_v300_rt4_streaming_cancel_current_behavior_inventory.py
```

Acceptance result:

- [x] actual DRC source read before planning
- [x] exact FW v5.4.0 root-public surface identified
- [x] RT-4 small-commit split fixed
- [x] docs/test-only implementation prepared
- [x] compileall passed
- [x] dedicated RT-4a gate passed against clean FW v5.4.0
- [x] Backend 163 passed
- [x] Flutter analyze and Flutter 200 passed
- [x] exact seven-file diff review and changed-content private scan passed
- [x] `git diff --check` passed
- [x] explicit operator approval, commit, and push completed

RT-4a implementation commit: `235654e470f8c0cac17644ddf216ac7e6e223514`.

### RT-4b — Backend provider-neutral stream lifecycle and fake-only tests

Purpose:

```text
- Add DRC-owned stream session, turn, chunk, event, and terminal models.
- Enforce monotonic event sequence and bounded chunk/aggregate text.
- Represent completed, cancelled, failed, and closed terminal outcomes.
- Record cooperative cancellation without claiming provider-level hard cancel.
- Reject active-turn replacement, late chunks, stale turns, and post-close callbacks.
- Use deterministic fake callbacks only.
```

Exact RT-4b change surface:

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v300_goal_checklist_small_commit.md
backend/app/models/realtime_text_stream.py
backend/app/services/realtime_text_stream_service.py
backend/tests/test_realtime_text_stream_service.py
docs/v300_rt4_backend_stream_contract.md
scripts/check_v300_rt4_backend_stream_contract.py
```

Candidate acceptance:

- [x] models/service/focused tests implemented
- [x] no route, Framework import, provider execution, dependency, or Flutter change
- [ ] compileall passes
- [ ] dedicated RT-4b gate passes
- [ ] focused Backend tests pass
- [ ] full Backend tests pass
- [ ] Flutter analyze and full Flutter tests pass
- [ ] exact ten-file review and changed-content private scan pass
- [ ] `git diff --check` passes
- [ ] explicit operator approval received

RT-4b acceptance passed and was pushed. RT-4c is COMPLETED / ACCEPTED / PUSHED at `72622cab2e73699adaff4b628cfbc4b14323a23a`. RT-4d is COMPLETED / ACCEPTED / PUSHED at `f713f515eef723a1d51cfbe35c1dfe16e3547420` with root-public FW `ask_stream()` wiring and cooperative interrupt semantics. RT-4e is COMPLETED / ACCEPTED / PUSHED at `1cfe6134b0d19a4d14ebcf3ec76812ce07dac261` with Flutter-only stream client/controller primitives, incremental UTF-8 SSE parsing, CRLF/LF chunk-boundary handling, same-origin path enforcement, monotonic sequence/session/turn validation, event type/state/payload/terminal validation, Unicode code-point bounds, cooperative cancel only, `hard_cancel_supported=false`, subscription cleanup, active-stream replacement and simultaneous start rejection, delayed `streamStarted` preserving local `cancelRequested`, fake/in-memory tests only, no HomeScreen integration, no STT transcript handoff, no real Backend/Framework/provider execution, and no TTS queue/flush/barge-in work. Verification passed: compileall, dedicated RT-4e gate, Backend 192 with one existing warning, Flutter analyze, focused Flutter RT-4e 33, Flutter full 233, exact twelve-file review, changed-content private scan, `git diff --check`, explicit operator approval, commit, and push. RT-4f is COMPLETED / ACCEPTED; RT-4f1 is COMPLETED / ACCEPTED / PUSHED at `f54e8638f0255b28e015702bc64b624a6d4a36af` as docs/test-only current behavior inventory and split. RT-4f2 is COMPLETED / ACCEPTED / PUSHED at `1e1a4b27a0fe7c105eec344bfde39afe6a077f8a` with HomeScreen fake streaming presentation, optional owned controller factory wiring, bounded manual input, fake/in-memory widget tests, no real Backend/Framework/provider execution, no STT transcript handoff, and no automatic TTS. RT-4f3 is COMPLETED / ACCEPTED / PUSHED at `d651a00be8713a70be3a46524f33c787299bbe9c` with an app-owned provider-neutral transcript-to-stream handoff boundary, injected/fake transcript results, fake/in-memory stream dependencies, independent in-flight exactly-once guard, no VoiceInputDemo transcript wiring, no real Backend/Framework/provider/STT execution, no real transcript source, and no automatic TTS. RT-4f4 is COMPLETED / ACCEPTED / PUSHED at `9b19e379634a718df2ab3ed5eb49bb20bfe7e240` with default-off configured Flutter runtime wiring, configured local Backend/FW stream completion, accepted real incremental streaming, accepted cooperative cancel, manual bounded input only, no real transcript source, no real-STT-to-stream execution or acceptance, no provider-level hard-cancel claim, and no automatic TTS. RT-4 and RT-4f are COMPLETED / ACCEPTED. RT-5 is NOT_STARTED / NOT_AUTHORIZED and TTS queue/flush/barge-in remains excluded.

## RT-5f2 — Fake-only integrated voice-turn and soft-barge-in coordinator

```text
status: COMPLETED / ACCEPTED / PUSHED
implementation commit: c538dc89c2aa9780cd3014aa4ba11c17a9e378e6
corrective commit: b7bd436196210f27782b64c1a094aa65d6893915
original surface: exact nine files
corrective surface: exact four files
RT-5f3: COMPLETED / ACCEPTED / PUSHED
```

受け入れ済み:

- fake capture→staging→final transcript→stream→terminal→TTSの合成
- operation epochによるlate completion無効化
- confirmed/foreground speech event、ID上限128、記憶上限32
- cooperative stream cancelとRT-5c local flush/stopの再利用
- local stop失敗後のretry-required blocking
- capture前・enqueue前・同期phase listener後のqueue exclusivity
- enqueue/process itemの`itemId`/`generation`一致
- public state privacy、dispose後の全late completion無効化

```text
Backend full: 204 passed, 1 existing warning
Flutter analyze: no issues
focused Flutter: 26 passed
Flutter full: 381 passed
exact surfaces/privacy/fake-only review: passed
git diff --check: passed
implementation and corrective pushes: completed
post-push DRC/FW working trees: clean
```

RT-5f3はexact twenty-file実装commit`75504424c37222234ea8a4314d01ce386ff92d23`でCOMPLETED / ACCEPTED / PUSHED。RT-5f4はcheckpoint`c84617e7ce07ecb1ca1605956eda7435b797c2fe`とcorrective`bf17538f8b33aa504671289edda8f55c511fe77d`でCOMPLETED / ACCEPTED / PUSHED。RT-5fとRT-5もCOMPLETED / ACCEPTED。RT-6は別のexact contract reviewのみ開始可能で、実装・commit・pushはNOT_AUTHORIZED。


## RT-5f3 — Default-off HomeScreen and production speech activity

```text
status: COMPLETED / ACCEPTED / PUSHED
implementation baseline: 888814d09fad75039733a4a94719454e0a69db63
implementation commit: 75504424c37222234ea8a4314d01ce386ff92d23
FW v5.4.0: d313eb6acb643103fe25988720ebee5976a04f78
exact implementation surface: 20 files
acceptance sync surface: exact seven files
real operator acceptance: NOT_EXECUTED / NOT_CLAIMED
RT-5 at RT-5f3 acceptance: CURRENT / NOT_COMPLETED
RT-5f4: COMPLETED / ACCEPTED / PUSHED
```

受け入れ済み:

- [x] `DRC_RT5F3_ENABLE_CONFIGURED_VOICE_TURN`をdefault falseで追加
- [x] RT-4/RT-5 prerequisite gate、mobile platform、valid Backend URLを要求
- [x] session-local opt-inと明示Start/Stop captureをHomeScreenへ追加
- [x] manual RT-4f4/RT-5eと非共有のstream/TTS ownershipを構成
- [x] `record: 6.2.1`でPCM16をdrain/dropしdBFSのみ検出へ渡す
- [x] 100 ms / -24 dBFS / 3 consecutive / 90 s / one event per generationを固定
- [x] capture中disarmed、staging/STT/stream/TTS中のみforeground arm
- [x] opt-out/background/event/disposeでdisarm
- [x] metadata-only UIとprivate sentinel非表示testを追加
- [x] focused synthetic testsとexact gateを追加
- [x] real DRC repositoryで専用gateを実行
- [x] Backend 204件を通過
- [x] Flutter analyzeを通過
- [x] focused Flutter 53件を通過
- [x] full Flutter 408件を通過
- [x] exact diff/privacy reviewと`git diff --check`を通過
- [x] explicit commit approvalを取得
- [x] exact twenty-file実装をcommit/push
- [x] post-push DRC working tree cleanを確認

未実施・未主張:

- real microphone-to-STT-to-stream-to-TTS operator acceptance
- real audible soft-barge-in、threshold品質、echo cancellation品質
- provider hard cancel、FW real queue flush、release readiness

Detailed accepted contract:
`docs/v300_rt5f3_default_off_home_screen_speech_activity_contract.md`.
Historical acceptance-sync gate:
`scripts/check_v300_rt5f3_default_off_home_screen_speech_activity_contract.py`.


## RT-5f4 — Configured local end-to-end and audible soft-barge-in acceptance

```text
status: COMPLETED / ACCEPTED / PUSHED
checkpoint baseline: ec6844c63b89803041e0b4e064d45c924e2d0438
checkpoint commit: c84617e7ce07ecb1ca1605956eda7435b797c2fe
corrective commit / accepted HEAD: bf17538f8b33aa504671289edda8f55c511fe77d
FW: d313eb6acb643103fe25988720ebee5976a04f78
checkpoint surface: exact seven docs/static-gate files
corrective surface: exact five Flutter runtime/test files
acceptance sync surface: exact seven files
private operator execution: COMPLETED / ACCEPTED
acceptance-sync commit/push: COMPLETED / PUSHED at ca1bd17ed32aba1e6b7d4dfd4f8eea3f10652ef7
RT-5f: COMPLETED / ACCEPTED
RT-5: COMPLETED / ACCEPTED
RT-6: NOT_STARTED / READY_FOR_EXACT_CONTRACT_REVIEW / NOT_AUTHORIZED
```

受け入れ済み:

- [x] Control A natural full-turn: PASS / ACCEPTED.
- [x] Control B silent-playback negative control: PASS / ACCEPTED.
- [x] Control C real user-speech interruption: PASS / ACCEPTED.
- [x] Control D recovery turn: PASS / ACCEPTED.
- [x] repeated Stop Capture corrective: REAL-DEVICE PASS.
- [x] playback-time speech detection corrective: REAL-DEVICE PASS.
- [x] Backend full: 204 passed, 1 existing warning.
- [x] Flutter analyze: No issues found.
- [x] Flutter full: 411 passed.
- [x] Keep the accepted claim limited to DRC-local soft barge-in.
- [x] Keep provider hard cancel, Backend hard cancel, provider TTS cancel, FW real queue flush, universal acoustic quality, iOS/PC acceptance, Live2D/VTS execution, and release readiness as non-claims.
- [x] Keep private values, text, audio, IDs, paths, addresses, screenshots, raw logs, and evidence outside commits.
- [ ] Review the exact seven-file acceptance sync.
- [x] Obtain explicit commit approval for the acceptance sync.
- [x] Commit and push the acceptance sync only after approval.
- [x] Start RT-6 exact contract review separately; RT-6a is now the active docs/static-gate candidate.


## RT-6a — Character-motion mapping readiness and exact split

```text
status: COMPLETED / ACCEPTED / PUSHED
implementation baseline: ca1bd17ed32aba1e6b7d4dfd4f8eea3f10652ef7
implementation commit: cbcb218aa54d286da7515a01e899121b22d8f3fc
FW v5.4.0: d313eb6acb643103fe25988720ebee5976a04f78
exact implementation surface: seven docs/static-gate files
Backend full: 204 passed, 3 dependency warnings
Flutter analyze: No issues found
Flutter full: 411 passed
DRC post-push working tree: clean
FW working tree: clean
RT-6b: NOT_STARTED / READY_FOR_EXACT_CONTRACT_REVIEW / NOT_AUTHORIZED
RT-6c through RT-6f: NOT_STARTED / NOT_AUTHORIZED
RT-7: BLOCKED_REAL_LIVE2D_VTS_ADAPTER_NOT_IMPLEMENTED
acceptance-sync commit/push: NOT_AUTHORIZED
```

受け入れ完了:

- [x] RT-5f4 acceptance sync `ca1bd17...` をbaselineとして固定
- [x] 既存Backend motion-demo route/service/modelを棚卸し
- [x] `accepted=false` / `not_started` / `motion_sent=false` を固定
- [x] `vts_connection_used=false` と実VTS未接続を固定
- [x] DRC独自motion vocabularyを固定
- [x] Flutter static character presentationとidle/loading/speakingを固定
- [x] realtime lifecycle-to-motion mapping/controller不在を固定
- [x] FW root-public mock motion contractを固定
- [x] FW real Live2D/VTS adapter未実装を固定
- [x] RT-6b〜RT-6fのexact ownershipを分離
- [x] exact seven-file candidate gateを追加
- [x] private/network/provider/audio non-actionを固定
- [x] real DRC/FW checkoutで専用gateを実行
- [x] Backend 204件を通過
- [x] Flutter analyzeを通過
- [x] Flutter 411件を通過
- [x] exact diff/privacy reviewと`git diff --check`を通過
- [x] explicit commit approvalを取得
- [x] commit/push後clean-treeを確認
- [x] RT-6aをCOMPLETED / ACCEPTED / PUSHEDとして記録
- [x] RT-6b exact contract reviewを別工程で実施
- [x] RT-6b実装を明示承認する

RT-6a acceptance syncではBackend/Flutter runtime、既存test、dependency、
route、asset、configuration、version、release metadata、FW source、
network/provider、VTS WebSocket/token、Live2D runtime、
microphone/audio/STT/LLM/TTSを変更・実行しない。


## RT-6b — App-owned provider-neutral character-motion mapping

```text
status: COMPLETED / ACCEPTED / PUSHED
baseline: 6ed5f2252c6c6f47fc8c50f577c4f20b7fa0cb68
implementation commit: 17f0c46eb0b4e26e2fdf5ffd4090c15c69f4e594
implementation surface: exact 10 files
acceptance-sync surface: exact 7 docs/static-gate files
RT-6c: NOT_STARTED / READY_FOR_EXACT_CONTRACT_REVIEW / NOT_AUTHORIZED
```

- [x] app-owned lifecycle fact enumを追加
- [x] existing motion-demo compatible cue enumを追加
- [x] provider-neutral command intentを追加
- [x] input/command/planをbounded Pydantic modelとして追加
- [x] arbitrary metadataを禁止
- [x] exact lifecycle mapping tableを実装
- [x] `motion_active`の再帰plan生成を禁止
- [x] `unknown`をfail-closed ignoredとする
- [x] existing `RealtimeState`全値の変換を実装
- [x] mapperをstateless/deterministicに維持
- [x] FW import、route、network、provider、VTS、Live2D実行を追加しない
- [x] focused Backend 37件を通過
- [x] Backend全241件を通過
- [x] real checkout dedicated gateを通過
- [x] Flutter analyze / 411 testsを通過
- [x] exact ten-file/privacy reviewを完了
- [x] 明示的なcommit承認を取得
- [x] commit/push後clean-treeを確認
- [x] RT-6bをCOMPLETED / ACCEPTED / PUSHEDとして記録
- [x] RT-6cをexact contract review readyに移行
- [ ] RT-6c exact contractを別工程でレビュー
- [ ] RT-6c実装を別途明示承認

受入結果:

```text
compileall: PASS
dedicated gate: PASS
focused Backend: 37 passed
Backend full: 241 passed, 3 dependency warnings
Flutter analyze: No issues found
Flutter full: 411 passed
DRC/FW post-push clean: true
```

詳細: `docs/v300_rt6b_provider_neutral_motion_mapping.md`

## RT-6c — Guarded FW root-public mock motion-session adapter

```text
RT-6: CURRENT / NOT_COMPLETED
RT-6c: COMPLETED / ACCEPTED / PUSHED
implementation baseline: 9442f511f9e41d18f64a65cf7fa44a375e7a67ce
implementation commit: f929e8faa65a817f1ba4fed82b729438b73dbfab
implementation surface: exact 10 files
acceptance-sync surface: exact 7 documentation/static-gate files
FW baseline version: 5.4.0
FW canonical reference commit: d313eb6acb643103fe25988720ebee5976a04f78
FW local source mode: external-vendored-snapshot
FW vendor Git identity required: false
root-public contract/mock smoke: PASS
focused Backend: 38 passed
Backend full: 279 passed, 3 dependency warnings
Flutter analyze: No issues found
Flutter full: 411 passed
RT-6d: IMPLEMENTED / AWAITING_REVIEW
RT-6d commit/push: NOT_AUTHORIZED
```

- [x] DRC-owned bounded adapter result modelsを追加
- [x] Default-off root-public-only mock session adapterを追加
- [x] Missing root / ignored plan / disabled pathをpre-importで停止
- [x] `adapter=mock`, real disabled, provider disallowedを固定
- [x] All five RT-6b command intentsをFW public requestへ変換
- [x] Maximum three synchronous apply callsとfail-fastを固定
- [x] Session close ownershipとfixed safe exception normalizationを追加
- [x] Event retentionをtype-only maximum twelveに限定
- [x] Raw FW objects/IDs/metadata/private detailsを返さない
- [x] Existing RT-6b/API/config/Flutter/FW/dependenciesを変更しない
- [x] FW v5.4.0 / canonical reference commitを小コミット記録へ固定
- [x] External vendor root-public contract/mock smokeを通過
- [x] Focused Backend 38件を通過
- [x] Backend全279件を通過
- [x] Flutter analyze / 411 testsを通過
- [x] Exact ten-file surface/privacy reviewを通過
- [x] 明示的なcommit承認を取得
- [x] Implementation commit/pushを完了
- [x] Post-push DRC clean-treeを確認
- [x] RT-6cをCOMPLETED / ACCEPTED / PUSHEDとして記録
- [x] RT-6dをexact contract review readyへ移行
- [x] RT-6d exact contractを別工程でレビュー
- [x] RT-6d実装を別途明示承認

詳細: `docs/v300_rt6c_framework_mock_motion_session_adapter.md`。


## RT-6d — Flutter motion presentation model/client/controller

```text
RT-6d: COMPLETED / ACCEPTED / PUSHED
baseline: cd423fa2236ce16a7635f0c67460f2fa2fd210e9
implementation commit: 0f220b792feb7ebb82c5871a794731aa1327439a
implementation surface: exact 12 files
acceptance-sync surface: exact 7 documentation/static-gate files
Flutter runtime: 3 files
focused tests: 2 files
focused Flutter: 41 passed
Flutter full: 452 passed
Backend full: 279 passed, 3 dependency warnings
FW baseline: 5.4.0 / d313eb6acb643103fe25988720ebee5976a04f78
FW source mode: external-vendored-snapshot
FW execution: false
RT-6e: NOT_STARTED / READY_FOR_EXACT_CONTRACT_REVIEW / NOT_AUTHORIZED
RT-6f authorization: false
RT-7 real adapter: blocked
acceptance-sync commit/push: NOT_AUTHORIZED
```

- [x] immutable provider-neutral motion presentation modelを追加
- [x] RT-6b lifecycle/cue/intent vocabularyをFlutter側で固定
- [x] RT-6c normalized mock resultをstrict parse
- [x] 最大3 command、最大12 event type、bounded public-safe textを検証
- [x] mock-only safety flagsを強制
- [x] injected fake/in-memory transport clientを追加
- [x] single-active-request ChangeNotifier controllerを追加
- [x] reset/close/dispose後のstale completionを無視
- [x] raw transport exception/responseをpublic stateへ保持しない
- [x] client/controller focused testsを追加
- [x] HomeScreen/main.dart/Backend/dependency/vendorを非変更
- [x] exact twelve-file static gateを追加
- [x] real checkoutでcompileallとdedicated gateを実行
- [x] Backend full 279件を通過
- [x] Dart formatとFlutter analyzeを通過
- [x] focused Flutter 41件を通過
- [x] Flutter full 452件を通過
- [x] exact surface/privacy/CRLF-aware diffをレビュー
- [x] 明示的なcommit承認を取得
- [x] implementation commit/pushを完了
- [x] post-push clean-treeを確認
- [x] RT-6dをCOMPLETED / ACCEPTED / PUSHEDとして記録
- [x] RT-6eをexact contract review readyへ移行
- [x] RT-6e exact contractを別工程でレビュー
- [x] RT-6e実装を別途明示承認
- [ ] exact ten-file候補を検証して受け入れる
- [ ] commit/pushは明示承認後のみ実行
- [ ] acceptance-sync commit/pushは別途承認後のみ実行

詳細: `docs/v300_rt6d_flutter_motion_presentation.md`。

## RT-6e — Default-off HomeScreen character-motion wiring

```text
RT-6e: COMPLETED / ACCEPTED / PUSHED
baseline: 8d69b539e974ba71fde5d9b15dd951d0c670b7ff
implementation commit: 13343017738d0bb5fe23583467856233d62196fb
implementation surface: exact 10 files
acceptance-sync surface: exact 7 documentation/static-gate files
Flutter runtime: 2 files
focused tests: 1 file
focused Flutter: 16 passed
Flutter full: 468 passed
Backend full: 279 passed, 3 dependency warnings
FW baseline: 5.4.0 / d313eb6acb643103fe25988720ebee5976a04f78
FW source mode: external-vendored-snapshot
FW execution: false
RT-6f: NOT_STARTED / READY_FOR_EXACT_CONTRACT_REVIEW / NOT_AUTHORIZED
RT-7 real adapter: blocked
acceptance-sync commit/push: NOT_AUTHORIZED
```

- [x] optional HomeScreen controller factoryを追加
- [x] factory未注入時をunconfiguredに維持
- [x] session-local opt-inをdefault off / non-persistentに維持
- [x] opt-in単独でtransport 0回を確認
- [x] explicit apply 1操作あたり最大1 requestを実装
- [x] fixed `home_screen_manual_motion`とno session/turn IDsを維持
- [x] reset/opt-outをlocal-onlyに維持
- [x] stale completionをopt-out/dispose後に無視
- [x] bounded aggregate mock stateだけをpanel表示
- [x] raw IDs/commands/events/response/exceptionを非表示
- [x] static character baselineを維持
- [x] main.dart/Backend/RT-6d runtime/dependency/vendorを非変更
- [x] exact ten-file gateを追加
- [x] lifecycle dropdown test correctiveをexact surface内で適用
- [x] Backend 279件を通過
- [x] Dart format / Flutter analyzeを通過
- [x] focused Flutter 16件を通過
- [x] Flutter full 468件を通過
- [x] exact surface/privacy/CRLF-aware diffをレビュー
- [x] 明示的なcommit承認を取得
- [x] implementation commit/pushを完了
- [x] post-push clean-treeを確認
- [x] RT-6eをCOMPLETED / ACCEPTED / PUSHEDとして記録
- [x] RT-6fをexact contract review readyへ移行
- [x] RT-6f exact contractを別工程でレビュー
- [x] RT-6f実装をexact nineteen-file契約で明示承認
- [ ] exact nineteen-file候補を検証して受け入れる
- [ ] commit/pushは別途明示承認後のみ実行
- [ ] acceptance-sync commit/pushは別途承認後のみ実行

詳細: `docs/v300_rt6e_home_screen_character_motion_wiring.md`。

## RT-6f — Configured local mock-motion presentation acceptance

```text
RT-6: COMPLETED / ACCEPTED
RT-6f: COMPLETED / ACCEPTED / PUSHED
baseline: e1d4f63d71c2de485b05fbfc5dad6811b81b31fc
implementation commit: fcdce38b9260604ea7c435c6de44fc129dc613f6
change surface: exact 19 files
acceptance-sync surface: exact 7 documentation/static-gate files
focused Backend: 10 passed
Backend full: 289 passed, 1 dependency deprecation warning
Flutter analyze: passed
focused Flutter: 15 passed
Flutter full: 483 passed
configured local Controls A-E: passed
DRC/FW post-push working trees: clean
acceptance-sync commit/push: NOT_AUTHORIZED
RT-7 real adapter: blocked
```

- [x] BackendとFlutterの二重default-off flagを追加
- [x] strict `POST /demo/character-motion/presentation`を追加
- [x] fixed `home_screen_manual_motion` / null session・turn IDsを強制
- [x] accepted RT-6b mapperからaccepted RT-6c mock adapterへ接続
- [x] disabled/unavailable/ignored/completedをtyped responseで維持
- [x] FW sessionをmock / real adapter false / provider execution falseに固定
- [x] Flutter HTTPをHTTP 200 / JSON object / 65536 bytes / whole-response 10 secondsへ制限
- [x] redirect、wrong content type、malformed bodyをgeneric failureへ正規化
- [x] controller-owned HTTP clientをdisposeでclose
- [x] main.dartからoptional controller factoryのみ注入
- [x] RT-6e HomeScreen/model/client/controller/panelを非変更
- [x] Dart format / compileall / dedicated gate / Flutter analyze
- [x] Backend focused 10 / Backend full 289
- [x] Flutter focused 15 / Flutter full 483
- [x] exact surface / privacy / CRLF-aware diff review
- [x] Control A default-off unconfigured
- [x] Control B configured idle / opt-in off
- [x] Control C speaking / completed / cue speaking / 2 of 2 / mock-only
- [x] Control D unknown / ignored / 0 of 0 / pre-import stop
- [x] Control E reset / opt-out / idle / off
- [x] implementation commit/push `fcdce38b9260604ea7c435c6de44fc129dc613f6`
- [x] post-push DRC/FW clean-tree確認
- [x] parent RT-6をCOMPLETED / ACCEPTEDへ移行
- [ ] acceptance-sync commit/pushは別途承認後のみ実行
- [ ] RT-7 real Live2D/VTS adapterは未実装のためblockedを維持

詳細: `docs/v300_rt6f_configured_local_mock_motion_presentation_acceptance.md`。

## RT-7a — Real motion adapter prerequisite and Framework requirement inventory

```text
RT-6: COMPLETED / ACCEPTED / PUSHED
RT-7: CURRENT / NOT_COMPLETED / BLOCKED_FRAMEWORK_REAL_MOTION_ADAPTER_RELEASE_REQUIRED
RT-7a: COMPLETED / ACCEPTED / PUSHED
baseline: c3c78316fd2bcd4f9939dcaadc32134a704374cf
implementation commit: efb139b2c0b6c7cc66912a229bd674b36df82dd7
implementation surface: exact 7 documentation/static-gate files
acceptance-sync surface: exact 7 documentation/static-gate files
Framework version: 5.4.0
Framework reference commit: d313eb6acb643103fe25988720ebee5976a04f78
acceptance-sync commit/push: NOT_AUTHORIZED
```

- [x] accepted RT-6 mock-motion execution and presentation pathをfreeze
- [x] FW v5.4.0 root-public motion exportsをinventory
- [x] `real_adapter_supported=false`とtyped `not_implemented`を確認
- [x] VTS WebSocket/token/private model/Live2D runtime/provider SDK未使用を記録
- [x] DRCのFW internal/provider importと独自VTS/provider bypass禁止を維持
- [x] FW real adapterに必要なminimum root-public contractを定義
- [x] released FW update前のDRC runtime実装stop ruleを固定
- [x] exact seven-file docs/static-gate implementationを追加
- [x] compileallとdedicated gateを実checkoutで通過
- [x] Backend full 289 passed / 1 dependency warning
- [x] Flutter analyze / Flutter full 483 passed
- [x] exact surface/privacy/CRLF-aware diff reviewを通過
- [x] 明示的なcommit承認を取得
- [x] implementation commit/push `efb139b2c0b6c7cc66912a229bd674b36df82dd7`を完了
- [x] post-push DRC/FW clean-treeを確認
- [x] RT-7aをCOMPLETED / ACCEPTED / PUSHEDとして記録
- [ ] acceptance-sync commit/pushは別途承認後のみ実行
- [ ] RT-7 real runtimeはreleased Framework adapterまでblockedを維持

詳細: `docs/v300_rt7a_real_motion_adapter_readiness.md`。
Historical acceptance-sync gate:
`scripts/check_v300_rt7a_real_motion_adapter_readiness.py`。

<!-- RT-7b-VENDORED-FW-v5.5.0:BEGIN -->
## RT-7b — vendored FW v5.5.0 readiness acceptance

```text
status: COMPLETED / ACCEPTED / PUSHED
implementation commit: c766610ce66a539efaabf4e4026a7c12ad2887c9
Framework local source: vendor/ai-character-framework-5.5.0
official release ZIP SHA-256: d6603003ea33abd5d543d85d4437f71e00571a86a9ed06a902506e6be3a9b5fe
official release ZIP files: 328
implementation surface: exact 8 files
acceptance-sync surface: exact 7 files
```

受け入れ済み:

- 公式v5.5.0 ZIPとsidecarのdigest、size、integrity、duplicate不在を確認
- 公式ZIPとvendorの328ファイルmembershipおよび全byte一致を確認
- Framework root-public import originをvendor配下へ固定
- motion API 5.5.0、root-public exports、mock motionを確認
- closed provider guardが`provider_execution_not_allowed`で停止
- `pyvts` import、network、real motion、private artifact readなし
- Backend 289、Flutter analyze、Flutter 483、exact surface、diff review通過
- implementation commit `c766610ce66a539efaabf4e4026a7c12ad2887c9` をmainへpush
- post-push HEAD / origin/main一致、DRC working tree clean

未承認:

- RT-7c runtime composition
- private VTS configuration handoff
- provider executionおよびreal VTube Studio motion
- acceptance-sync commit / push
<!-- RT-7b-VENDORED-FW-v5.5.0:END -->

<!-- RT-7c-GUARDED-VENDORED-FW-v5.5.0-VTS:BEGIN -->
## RT-7c — guarded vendored FW v5.5.0 VTS session adapter acceptance

```text
status: COMPLETED / ACCEPTED / PUSHED
implementation baseline: 35582f06ca037401b2cef8d97cfc5fc26cd40654
implementation commit: 4a2374854801791caefdf0be8cd246e5a2e9278e
corrective commit: 484ba17245d24a98407907984b28995b247581fa
Framework local source: vendor/ai-character-framework-5.5.0
implementation surface: exact 11 files
corrective surface: exact 4 files
acceptance-sync surface: exact 7 documentation/static-gate files
RT-7d exact contract review: READY
RT-7d implementation: NOT_AUTHORIZED
RT-7e: NOT_AUTHORIZED
real VTube Studio execution: NOT_AUTHORIZED
acceptance-sync commit / push: NOT_AUTHORIZED
```

受け入れ済み:

- RT-6 mock-specific model/adapter/routeをprotected non-changeとして維持
- fixed vendor root-public package origin検証
- Framework development checkout/CWD/sys.path fallback不使用
- explicit private VTS configuration value object
- disabled/provider-disallowedの二重closed guard
- expression / emotion / gesture / reset_expression required
- stop_motion unsupportedのoptional safe skip
- speaking_state / idle_motion / look_at拒否
- preflight-before-applyとintent別capability確認
- bounded allowlist result/event/boolean normalization
- created sessionの全経路close
- raw exception/private endpoint/token/hotkey/ID/payload非露出
- `pyvts==0.3.3` / `websockets==16.0` exact pin
- strict literal-boolean config/capability/retryable corrective
- implementation exact 11 files / corrective exact 4 files
- compileall、dedicated gate before/after regression
- focused Backend 31、Backend full 320 / 1 existing warning
- Flutter analyze、Flutter full 483
- exact surface/privacy/CRLF-aware diff review
- implementation `4a2374854801791caefdf0be8cd246e5a2e9278e` とcorrective `484ba17245d24a98407907984b28995b247581fa` のcommit/push
- post-push HEAD / origin/main一致、working tree clean

未承認:

- RT-7d implementationおよびBackend/API/Flutter configured wiring
- private VTS operator configuration/evidence
- RT-7e provider executionおよびreal VTube Studio motion
- acceptance-sync commit / push

詳細:
`docs/v300_rt7c_guarded_vendored_fw_v550_vts_session_adapter.md`。
Historical acceptance-sync gate:
`scripts/check_v300_rt7c_guarded_vendored_fw_v550_vts_session_adapter.py`。
<!-- RT-7c-GUARDED-VENDORED-FW-v5.5.0-VTS:END -->


<!-- RT-7d-DEFAULT-OFF-CONFIGURED-VTS:BEGIN -->
## RT-7d default-off configured VTS manual wiring acceptance

RT-7d is **COMPLETED / ACCEPTED / PUSHED** at implementation commit
`37f7ac8bedc5303f3ddf53e4e543b71f35ce2ed2` against baseline
`2a5e3b035bcfdd273a7d056d59af01235e2459f5` under the exact 28-file contract.

Accepted verification:

```text
compileall: PASS
dedicated RT-7d gate: PASS before and after regressions
focused Backend: 16 passed, 1 existing dependency warning
Backend full: 336 passed, 1 existing dependency warning
Dart focused format: PASS
Flutter analyze: No issues found
focused Flutter: 16 passed
Flutter full: 499 passed
exact implementation surface: 28 files
CRLF-aware git diff --check: PASS
provider execution attempted: false
network execution attempted: false
real motion executed: false
implementation commit / push: COMPLETED
post-push HEAD / origin/main: 37f7ac8bedc5303f3ddf53e4e543b71f35ce2ed2
post-push working tree: clean
```

The accepted wiring keeps the RT-6 mock route unchanged and adds a separate
one-command manual VTS route. Flutter compile-time enablement, HomeScreen
session-local opt-in, Backend adapter enablement, and Backend provider opt-in
remain independently default off. Startup, construction, opt-in, opt-out,
reset, and disposal perform no transport or motion execution.

```text
RT-7: CURRENT / NOT_COMPLETED
RT-7c: COMPLETED / ACCEPTED / PUSHED
RT-7d: COMPLETED / ACCEPTED / PUSHED
implementation baseline: 2a5e3b035bcfdd273a7d056d59af01235e2459f5
implementation commit: 37f7ac8bedc5303f3ddf53e4e543b71f35ce2ed2
implementation surface: exact 28 files
acceptance-sync surface: exact 7 documentation/static-gate files
existing RT-6 route preserved: true
one-command manual boundary: true
Flutter default off: true
Backend default off: true
session opt-in default off: true
Framework development checkout referenced: false
Framework internal import: false
pyvts direct import: false
websockets direct import: false
provider/network/real motion execution: false
RT-7e exact contract review: READY
RT-7e implementation: NOT_AUTHORIZED
real VTube Studio execution: NOT_AUTHORIZED
acceptance-sync commit / push: NOT_AUTHORIZED
```

Run the historical acceptance-sync gate from the DRC repository root while the
exact seven files are modified against implementation commit `37f7ac8bedc5303f3ddf53e4e543b71f35ce2ed2`:

```powershell
python -m compileall -q backend scripts
python scripts\check_v300_rt7d_default_off_configured_vts_manual_wiring.py
git -c core.whitespace=cr-at-eol diff --check
git status --short
git diff --name-only
```

The gate rechecks the exact 28-file implementation history, the current exact
7-file acceptance-sync surface, default-off Backend and Flutter boundaries,
one-command manual request contract, preserved RT-6 route, fixed-vendor
root-public adapter path, and closed provider/network/real-motion markers. It
reads no private VTS configuration, imports no `pyvts`, opens no WebSocket, and
executes no real motion.

Detailed accepted contract:
`docs/v300_rt7d_default_off_configured_vts_manual_wiring.md`.
Historical acceptance-sync gate:
`scripts/check_v300_rt7d_default_off_configured_vts_manual_wiring.py`.
<!-- RT-7d-DEFAULT-OFF-CONFIGURED-VTS:END -->

## RT-7e — configured local VTS operator acceptance

```text
RT-7: COMPLETED / ACCEPTED
RT-7e: COMPLETED / ACCEPTED / PUSHED
Stage 1 commit: c4455fb6d14d5a6e31f2ff782e364c0eb92d2f4f
operator corrective commit: 84429683d5ea26e5480bff17f5e29ad201b6ee71
Control C contract corrective commit: a26d027fcd40d6734cb8919059a4683c322f55da
Control D docs/test-only corrective commit: ddd392c24907eae4d8c91850d84b31a7b84e760f
Control A: PASS / ACCEPTED
Control B: PASS / ACCEPTED
Control C: PASS / ACCEPTED
Control D: PASS / ACCEPTED
Control E: PASS / ACCEPTED
Backend / Flutter real_motion_executed: false
operator-visible physical motion confirmed: true
Control E additional execution: false
RT-8 exact contract review: READY
RT-8 implementation: NOT_AUTHORIZED
```

受け入れ済み境界:

```text
- defaultではoperator runner request zero。
- Control Bはexactly-one POSTとoperator-visible gestureを受け入れた。
- Control Cのfirst attemptはFAILED / NOT_ACCEPTEDとして保持した。
- private selector corrective後のretryはexactly-one Flutter ApplyでPASS。
- Backend/Flutterのreal_motion_executedはfalseを維持した。
- visible physical motionはoperator evidenceだけで受け入れた。
- Control DはReset、opt-in OFF、disposeがlocal-onlyであることを固定した。
- Control Eは追加request/provider/network/visible motionを実行していない。
- private process values、execution flags、local processes、working tree cleanupを確認した。
```

変更禁止境界:

```text
backend/app/**
backend/tests/**
app/lib/**
app/test/**
vendor/**
dependencies
version metadata
release artifacts / tags / GitHub Releases
private environment/token/hotkey/model/evidence files
```

次はRT-8 exact contract review。実装、実機証跡取得、commit/pushは別承認まで開始しない。

<!-- RT-8a-PC-ANDROID-READINESS:BEGIN -->
## RT-8a PC/Android realtime acceptance readiness

```text
RT-7: COMPLETED / ACCEPTED
RT-7e Control E commit: 0440aa28fa7d1f49a8e15fd056de8735c83ce2ae
RT-8: CURRENT / NOT_COMPLETED
RT-8a: IMPLEMENTED / AWAITING_REVIEW
RT-8a baseline: 0440aa28fa7d1f49a8e15fd056de8735c83ce2ae
RT-8a surface: exact 7 documentation/static-gate files
readiness: READY_FOR_PLATFORM_APPROPRIATE_PC_WINDOWS_AND_ANDROID_REALTIME_ACCEPTANCE
PC Windows integrated real voice turn supported: false
Android integrated real voice turn supported: true
identical cross-platform voice-runtime claim: false
automatic voice/stream/TTS-to-VTS synchronization claim: false
RT-8b exact contract review: BLOCKED_PENDING_RT8A_ACCEPTANCE
RT-8b implementation: NOT_AUTHORIZED
RT-9: BLOCKED_PENDING_RT8
private configuration read: false
provider execution attempted: false
microphone used: false
network execution attempted: false
real motion executed: false
commit / push: NOT_AUTHORIZED
```

RT-8a is a docs/static-gate-only readiness checkpoint. It freezes a
platform-appropriate final-evidence matrix instead of requiring an identical
voice runtime on PC and smartphone.

```text
PC Windows candidate evidence:
- configured manual incremental text streaming and completed terminal;
- cooperative stream cancellation, not provider-level hard cancel;
- explicit real TTS synthesis, audible local playback, and explicit local flush;
- explicit app-owned motion presentation;
- explicit manual VTS Apply and operator-visible physical motion.

Android smartphone candidate evidence:
- bounded real microphone capture and private staging cleanup;
- Framework root-public real STT and provider-neutral transcript handoff;
- incremental text stream and completed terminal-to-TTS handoff;
- real TTS, audible local playback, silent negative control, and DRC-local soft interruption;
- inert old work and a completed explicit recovery turn;
- explicit manual VTS Apply and operator-visible physical motion.
```

The mobile integrated voice runtime remains native Android/iOS only. RT-8 does
not claim PC microphone/STT/soft-barge-in, identical cross-platform voice
support, automatic voice-to-motion synchronization, provider-level hard
cancellation, Framework unified realtime runtime, or release readiness.

Accepted exact split:

```text
RT-8a  readiness inventory and exact split; docs/static-gate only
RT-8b  private operator manifest, validator, and runbook; no real execution
RT-8c  configured PC Windows acceptance
RT-8d  configured Android smartphone acceptance
RT-8e  aggregate cleanup and RT-8 acceptance synchronization
```

Exact RT-8a surface:

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v300_goal_checklist_small_commit.md
docs/v300_rt8_pc_android_realtime_acceptance_readiness.md
scripts/check_v300_rt8_pc_android_realtime_acceptance_readiness.py
```

Protected and unchanged:

```text
backend/**
app/lib/**
app/test/**
vendor/**
dependencies and lockfiles
platform declarations and generated registration
assets
version metadata
release/**
release_notes/**
fixed ZIPs, tags, and GitHub Releases
Framework development checkout
private environment/token/endpoint/hotkey/model/evidence files
```

RT-8a performs no Backend/Flutter startup, microphone permission or capture,
audio staging, STT, LLM, TTS, playback, HTTP/provider/network/WebSocket/VTS
operation, screenshot capture, private-manifest creation, or physical motion.
RT-8b remains blocked until RT-8a passes verification, exact diff review,
privacy review, explicit approval, commit, push, and clean-tree verification.

Detailed candidate contract:
`docs/v300_rt8_pc_android_realtime_acceptance_readiness.md`.
Dedicated candidate gate:
`scripts/check_v300_rt8_pc_android_realtime_acceptance_readiness.py`.
<!-- RT-8a-PC-ANDROID-READINESS:END -->

<!-- RT-8b-PRIVATE-OPERATOR-MANIFEST:BEGIN -->
## RT-8b private operator manifest, validator, and runbook

```text
RT-8: CURRENT / NOT_COMPLETED
RT-8a: COMPLETED / ACCEPTED / PUSHED
RT-8a commit: a3af4fae002c1425fdfb61b46f66e35e2443ad17
RT-8b: IMPLEMENTED / AWAITING_REVIEW
RT-8b baseline: a3af4fae002c1425fdfb61b46f66e35e2443ad17
RT-8b surface: exact 10 files
readiness: READY_FOR_BOUNDED_PRIVATE_RT8_OPERATOR_MANIFEST_AND_NETWORK_FREE_VALIDATION
RT-8c exact contract review: READY_AFTER_RT8B_ACCEPTANCE
RT-8c implementation: NOT_AUTHORIZED
RT-8d implementation: NOT_AUTHORIZED
RT-8e implementation: NOT_AUTHORIZED
private manifest created: false
private manifest read: false
private configuration read: false
provider/network/microphone/TTS/VTS execution: false
commit / push: NOT_AUTHORIZED
```

RT-8b adds a strict JSON validator, an intentionally rejected public example,
focused credential-free tests, a source preflight gate, and a fixed operator
runbook. A real manifest must remain under ignored `operator_evidence/`; RT-8b
does not create or read one.

```text
schema: drc.v3.rt8-platform-acceptance.1
stages: example / pc_windows / android / aggregate
maximum private manifest size: 65536 bytes
unknown, missing, and duplicate JSON keys: rejected
free-form text and private-looking values: rejected
public example status: example_not_accepted
```

Exact RT-8b surface:

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v300_goal_checklist_small_commit.md
docs/v300_rt8b_private_operator_manifest_and_runbook.md
docs/operator_evidence_templates/v300_rt8_pc_android_realtime_acceptance.example.json
scripts/validate_v300_rt8_private_operator_manifest.py
scripts/check_v300_rt8b_private_operator_manifest_and_runbook.py
backend/tests/test_v300_rt8_private_operator_manifest.py
```

Protected and unchanged are `.gitignore`, Backend/Flutter runtime, all existing
tests, dependencies, platform declarations, fixed vendor Framework, versions,
release records, historical RT-8a files, and all private configuration or
evidence. RT-8c, RT-8d, RT-8e, RT-9, and every configured real execution remain
separately unauthorized.

Detailed candidate contract:
`docs/v300_rt8b_private_operator_manifest_and_runbook.md`.
Validator:
`scripts/validate_v300_rt8_private_operator_manifest.py`.
Dedicated candidate gate:
`scripts/check_v300_rt8b_private_operator_manifest_and_runbook.py`.
<!-- RT-8b-PRIVATE-OPERATOR-MANIFEST:END -->

<!-- RT-8b1-STRICT-PC-COUNT-CORRECTIVE:BEGIN -->
## RT-8b1 strict PC execution-count contract corrective

```text
RT-8: CURRENT / NOT_COMPLETED
RT-8a: COMPLETED / ACCEPTED / PUSHED
RT-8b: COMPLETED / ACCEPTED / PUSHED
RT-8b commit: eedc32a6293b99435d1d2e60b4a4a6e7c519c8d5
RT-8b1: IMPLEMENTED / AWAITING_REVIEW
RT-8b1 baseline: eedc32a6293b99435d1d2e60b4a4a6e7c519c8d5
RT-8b1 surface: exact 10 files
schema: drc.v3.rt8-platform-acceptance.2
RT-8c: BLOCKED_PENDING_RT8B1_ACCEPTANCE / NOT_AUTHORIZED
private manifest created: false
private manifest read: false
private configuration read: false
provider execution attempted: false
network execution attempted: false
microphone used: false
real TTS executed: false
real motion executed: false
commit / push: NOT_AUTHORIZED
```

RT-8b1 corrects only the strict PC execution-count schema before any configured
PC run. The bounded PC sequence requires three manual stream starts: two
completed terminals and one cancelled terminal. The two completed terminals
feed two explicit TTS enqueue/process actions; the second playback is stopped by
one explicit local flush.

```text
manual_stream_start_count: 3
completed_stream_terminal_count: 2
cancelled_stream_terminal_count: 1
cooperative_cancel_request_count: 1
explicit_tts_enqueue_count: 2
explicit_tts_process_count: 2
explicit_flush_count: 1
app_owned_motion_presentation_count: 1
manual_vts_apply_count: 1
```

The public example remains `example_not_accepted`. RT-8b1 creates and reads no
private manifest and performs no Backend, Flutter, provider, network,
microphone, STT, TTS, playback, VTS, or physical-motion operation.
<!-- RT-8b1-STRICT-PC-COUNT-CORRECTIVE:END -->

<!-- RT-8c-STAGE1-PC-WINDOWS-TOOLING:BEGIN -->
## RT-8c Stage 1 PC Windows operator tooling candidate

```text
RT-8b1: COMPLETED / ACCEPTED / PUSHED
RT-8b1 commit: 4815403d4c94b05551df03678e9c2c4e1dfe754e
RT-8c Stage 1: IMPLEMENTED / AWAITING_REVIEW
RT-8c Stage 1 surface: exact 9 files
RT-8c Stage 2: BLOCKED_PENDING_STAGE1_ACCEPTANCE / NOT_AUTHORIZED
RT-8c Stage 3: BLOCKED_PENDING_PC_CONTROLS_A_H / NOT_AUTHORIZED
schema: drc.v3.rt8-platform-acceptance.2
private manifest created: false
private manifest read: false
private configuration read: false
Backend / Flutter started: false
provider / network execution attempted: false
real TTS / playback / VTS executed: false
commit / push: NOT_AUTHORIZED
```

Stage 1 adds an inert-by-default runner, exact twelve credential-free tests, a
fixed PC runbook, and a dedicated source gate. The later PC chronology is
`A -> B -> D -> C -> E -> F -> G -> H`, with three stream starts, two completed
terminals, one cancelled terminal, two explicit TTS enqueue/process actions,
one flush, one mock-motion Apply, and one real VTS Apply.

Detailed contract:
`docs/v300_rt8c_configured_pc_windows_realtime_acceptance.md`.
Dedicated gate:
`scripts/check_v300_rt8c_configured_pc_windows_realtime_acceptance.py`.
Operator runner:
`scripts/run_v300_rt8c_private_pc_windows_operator.py`.
<!-- RT-8c-STAGE1-PC-WINDOWS-TOOLING:END -->
