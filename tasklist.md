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
current small commit: M-4
next feature release: v2.1.0
strategic target: v3.0.0
```

v2.0.0の固定ZIP、annotated tag、GitHub Release、公開後SHA-256再検証は完了している。
公開済み`DRC_v2.0.0`を変更せず、今後の変更は新しいコミットと新しいバージョンで行う。

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

# 3. 現在の小コミット

## M-4 — Framework fallback and voice artifact safety regression

Status: CURRENT / NOT_COMPLETED

目的:

```text
- configured Framework advice成功経路を一時fake packageで通常回帰確認する。
- FrameworkEngineError時のframework_fallback表示契約を通常回帰確認する。
- DRC-managed voice artifactのopaque URL、managed boundary、format、ID検証を通常回帰確認する。
- 実Framework、provider、network、real TTSを呼ばずに境界契約を固定する。
```

変更対象:

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
backend/tests/test_framework_advice.py
backend/tests/test_voice_output_artifact_store.py
docs/DRC_v20x_maintenance_checklist.md
docs/v20x_backend_mock_safe_regression.md
docs/v20x_framework_fallback_voice_artifact_regression.md
scripts/check_v20x_maintenance_baseline.py
scripts/check_v20x_application_version_metadata.py
scripts/check_v20x_backend_mock_safe_regression.py
scripts/check_v20x_framework_fallback_voice_artifact_regression.py
```

変更しない対象:

```text
backend runtime implementation
FrameworkConversationEngine implementation
/advice fallback implementation
VoiceOutputArtifactStore implementation
provider / OAuth / health-data real execution
real LLM / TTS / STT / motion execution
chat session or TTS artifact lifecycle limits
release ZIP / tag / GitHub Release
```

M-4完了条件:

```text
- fake framework packageがpublic create_text_chat_session境界からadviceを返す。
- framework source metadataとcharacter mapping metadataを確認する。
- empty FW responseがFrameworkEngineErrorになる。
- FW failureがframework_fallbackとして明示される。
- voice artifact storeがmanaged staging内MP3だけをopaque URLへ移す。
- local absolute pathをAPI-facing URLへ含めない。
- outside path、unsupported format、traversal、不正IDを拒否する。
- backend/local_dataを作成・参照しない。
- M-5以降をPLANNEDのまま維持する。
- compileall、M-1〜M-4 check、backend pytest、flutter testが通る。
- 差分確認後に小コミットとして承認される。
```

M-4は上記検証とコミット承認が終わるまで`COMPLETED`へ変更しない。M-4ではbackend runtime、v2.0.1 release、公開済みv2.0.0資産を変更しない。

---

# 4. v2.0.x small-commit queue

```text
M-1  COMPLETED  docs: establish post-v2.0.0 maintenance baseline
M-2  COMPLETED  fix/test: align application version metadata
M-3  COMPLETED  test: add backend mock-safe regression foundation
M-4  CURRENT    test: cover Framework fallback and voice artifact safety
M-5  PLANNED    fix: bound temporary chat sessions and TTS artifacts
M-6  PLANNED    fix: make Web CORS origins configurable
M-7  PLANNED    docs/test: clarify Fitbit current-state contract
M-8  PLANNED    test/docs: add v2.0.x aggregate maintenance readiness
M-9  PLANNED    release: build and verify a fixed patch ZIP only after scope acceptance
```

完了要件を前倒ししない。M-4が受け入れられるまでM-5以降を`CURRENT`または`COMPLETED`へ変更しない。

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
