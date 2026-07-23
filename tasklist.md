# Daily Rhythm Companion post-v2.0.0 task list

更新日: 2026-07-22

## 1. 現在地

```text
Public repository: murayan1982/daily-rhythm-companion-public
released baseline: v2.0.0
release / annotated tag: DRC_v2.0.0
v2.0.0 status: RELEASED
current maintenance line: v2.0.x
current patch target: v2.0.1
current small commit: none (M-5 accepted; M-6 planned)
next feature release: v2.1.0
strategic target: v3.0.0
```

v2.0.0の固定ZIP、annotated tag、GitHub Release、公開後SHA-256再検証は完了している。公開済み`DRC_v2.0.0`を変更せず、今後の変更は新しいコミットと新しいバージョンで行う。

## 2. Source of truth

現在の詳細タスクリスト:

```text
docs/DRC_v20x_maintenance_checklist.md
```

ロードマップ:

```text
roadmap.md
```

v2.0.0の完了記録:

```text
docs/DRC_v200_goal_checklist_small_commit.md
release_notes/v2.0.0.md
GitHub Release: DRC_v2.0.0
```

v2.0.0の記録は履歴として保持し、v2.0.xの進捗管理には再利用しない。

---

# 3. 最新の完了小コミット

## M-5 — temporary chat sessions and TTS artifacts lifecycle limits

Status: COMPLETED

目的:

```text
- post-advice chat sessionをidle TTLとLRU件数上限で制限する。
- DRC-managed TTS staging/public artifactをTTLと件数上限で制限する。
- background workerやcleanup APIを追加せず、lazy cleanupを実装する。
- 既存API model、route、opaque URL、404契約を維持する。
- clock injectionとpytest tmp_pathでmock-safeな決定的回帰テストを追加する。
```

既定値:

```text
POST_ADVICE_CHAT_TTL_SECONDS=1800
POST_ADVICE_CHAT_MAX_SESSIONS=100
VOICE_OUTPUT_ARTIFACT_TTL_SECONDS=86400
VOICE_OUTPUT_ARTIFACT_MAX_COUNT=100
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
backend/app/services/post_advice_chat_service.py
backend/app/services/voice_output_artifact_store.py
backend/app/services/voice_output_demo_service.py
backend/tests/test_post_advice_chat_lifecycle.py
backend/tests/test_temporary_lifecycle_config.py
backend/tests/test_voice_output_artifact_store.py
docs/DRC_v20x_maintenance_checklist.md
docs/v20x_framework_fallback_voice_artifact_regression.md
docs/v20x_temporary_lifecycle_limits.md
scripts/check_v20x_maintenance_baseline.py
scripts/check_v20x_application_version_metadata.py
scripts/check_v20x_backend_mock_safe_regression.py
scripts/check_v20x_framework_fallback_voice_artifact_regression.py
scripts/check_v20x_temporary_lifecycle_limits.py
```

確認したが変更しない対象:

```text
backend/app/api/voice_output_demo.py
backend/app/api/chat.py
backend/app/models/chat.py
backend/app/models/voice_output_demo.py
```

audio resolverの既存`VoiceOutputArtifactStore()`引数なし生成は、fake store差し替え互換性のため維持する。active lifecycle configはstore内部で読む。

変更しない対象:

```text
docs/DRC_v200_goal_checklist_small_commit.md
release_notes/v2.0.0.md
chat/voice API modelとroute
Framework provider implementation
real LLM / TTS / STT / health / OAuth / motion execution
Flutter behavior
persistence schema
release ZIP / tag / GitHub Release
```

M-5完了条件:

```text
- configの4値がpositive integerとして安全に読み込まれる。
- chat sessionが最終成功利用からexpiryし、LRU順でcapacity evictionされる。
- chat cleanup後も既存404契約を維持する。
- TTS public artifactが公開時刻からexpiryし、resolveで延命されない。
- staging/public artifactがTTLと件数上限でcleanupされる。
- symlink、outside path、unsupported format、traversal、不正IDを安全に扱う。
- VoiceOutputDemoServiceはactive AppConfigを渡し、audio resolverは既存の引数なしstore生成を維持しつつstore内部でactive configを読む。
- M-6以降をPLANNEDのまま維持する。
- compileall、M-1〜M-5 check、backend pytest、flutter testが通る。
- 差分確認後に小コミットとして承認される。
```

M-5は上記検証、Flutter 39件、差分確認、オペレーター承認を完了し、2026-07-22に受け入れられた。M-5ではv2.0.1 releaseや公開済みv2.0.0資産を変更していない。

---

# 4. v2.0.x small-commit queue

```text
M-1  COMPLETED  docs: establish post-v2.0.0 maintenance baseline
M-2  COMPLETED  fix/test: align application version metadata
M-3  COMPLETED  test: add backend mock-safe regression foundation
M-4  COMPLETED  test: cover Framework fallback and voice artifact safety
M-5  COMPLETED  fix/test: bound temporary chat sessions and TTS artifacts
M-6  PLANNED    fix: make Web CORS origins configurable
M-7  PLANNED    docs/test: clarify Fitbit current-state contract
M-8  PLANNED    test/docs: add v2.0.x aggregate maintenance readiness
M-9  PLANNED    release: build and verify a fixed patch ZIP only after scope acceptance
```

完了要件を前倒ししない。M-5は受け入れ済みで、M-6以降は正式着手まで`PLANNED`を維持する。

---

# 5. Later version boundaries

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

v2.1.0とv3.0.0は計画段階であり、実装済みまたは受け入れ済みとは扱わない。
