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
current small commit: M-2
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

## M-2 — application version metadata alignment

Status: CURRENT / NOT_COMPLETED

目的:

```text
- 現在の保守ソースをv2.0.1へ進める。
- backend APP_VERSION、FastAPI、/health、Flutter package versionを整合させる。
- Webと各platformはpubspec継承とし、重複した固定バージョンを増やさない。
- Backend status欄にAPI versionを表示し、旧backendのversion無し応答も維持する。
```

変更対象:

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
backend/app/version.py
backend/app/main.py
backend/app/api/health.py
app/pubspec.yaml
app/lib/services/backend_api_client.dart
app/test/widget_test.dart
docs/v20x_application_version_metadata.md
docs/DRC_v20x_maintenance_checklist.md
scripts/check_v20x_maintenance_baseline.py
scripts/check_v20x_application_version_metadata.py
```

変更しない対象:

```text
docs/DRC_v200_goal_checklist_small_commit.md
release_notes/v2.0.0.md
provider / OAuth / health-data / LLM / TTS / STT / motion execution
persistence schema
release ZIP / tag / GitHub Release
```

M-2完了条件:

```text
- backend APP_VERSION、FastAPI version、/health versionが2.0.1で一致する。
- Flutter package versionが2.0.1+2になる。
- Flutter UIがAPI v2.0.1を表示し、version無しの旧応答も処理できる。
- Web sourceに別の固定versionを追加しない。
- M-3以降をPLANNEDのまま維持する。
- compileall、M-1 baseline check、M-2 metadata check、flutter testが通る。
- 差分確認後に小コミットとして承認される。
```

M-2は上記検証とコミット承認が終わるまで`COMPLETED`へ変更しない。M-2ではv2.0.1をリリースしない。

---

# 4. v2.0.x small-commit queue

```text
M-1  COMPLETED  docs: establish post-v2.0.0 maintenance baseline
M-2  CURRENT    fix/test: align application version metadata
M-3  PLANNED    test: add backend mock-safe regression foundation
M-4  PLANNED    test: cover Framework fallback and voice artifact safety
M-5  PLANNED    fix: bound temporary chat sessions and TTS artifacts
M-6  PLANNED    fix: make Web CORS origins configurable
M-7  PLANNED    docs/test: clarify Fitbit current-state contract
M-8  PLANNED    test/docs: add v2.0.x aggregate maintenance readiness
M-9  PLANNED    release: build and verify a fixed patch ZIP only after scope acceptance
```

完了要件を前倒ししない。M-2が受け入れられるまでM-3以降を`CURRENT`または`COMPLETED`へ変更しない。

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
