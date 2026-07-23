# Daily Rhythm Companion post-v2.0.0 task list

更新日: 2026-07-23

## 1. 現在地

```text
Public repository: murayan1982/daily-rhythm-companion-public
immutable capability baseline: v2.0.0
current released version: v2.0.1
release / annotated tag: DRC_v2.0.1
v2.0.1 status: RELEASED
current maintenance line: v2.0.x COMPLETED
current small commit: none (M-9 accepted)
next feature release: v2.1.0
strategic target: v3.0.0
```

v2.0.1の固定ZIP、annotated tag、GitHub Release、公開後SHA-256再検証は完了している。公開済み`DRC_v2.0.0`と`DRC_v2.0.1`を変更せず、今後の変更は新しいコミットと新しいバージョンで行う。

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

現在の小コミットはない。M-1〜M-9は受け入れ済みで、v2.0.1は正式リリース済み。

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

# 4. 直近完了した小コミット

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

# 5. 直近完了した小コミット

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

# 6. v2.0.x small-commit queue

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

M-1〜M-9は受け入れ済みで、v2.0.1は正式リリース済み。次の実装source of truthは、v2.1.0 checklistが別途作成・受け入れされるまで開始しない。

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

v2.1.0とv3.0.0は計画段階であり、実装済みまたは受け入れ済みとは扱わない。
