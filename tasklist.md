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
current small commit: M-1
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

## M-1 — post-v2.0.0 maintenance baseline

Status: CURRENT / NOT_COMPLETED

目的:

```text
- v2.0.0 RELEASEDを現在の基準点として同期する。
- v2.0.x保守作業のsource of truthを新設する。
- Public版とPrivate operator環境の境界を明文化する。
- 歴史的v2.0.0検証と今後の通常保守検証を分離する。
```

変更対象:

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/post_v200_release_baseline.md
docs/DRC_v20x_maintenance_checklist.md
docs/public_private_development_policy.md
scripts/check_v20x_maintenance_baseline.py
```

変更しない対象:

```text
docs/DRC_v200_goal_checklist_small_commit.md
release_notes/v2.0.0.md
backend runtime
Flutter runtime
provider / OAuth / health / LLM / TTS / STT / motion implementation
```

M-1完了条件:

```text
- README、roadmap、tasklist、scripts READMEがv2.0.0 RELEASED基準へ同期される。
- v2.0.x保守チェックリストが唯一の詳細source of truthとして作成される。
- v2.0.0チェックリストとリリースノートの内容が変更されていない。
- Public / Private運用境界が明文化される。
- python -m compileall -q backend scripts が通る。
- python scripts\check_v20x_maintenance_baseline.py が通る。
- 差分確認後に小コミットとして承認される。
```

M-1は、上記検証とコミット承認が終わるまで`COMPLETED`へ変更しない。

---

# 4. v2.0.x small-commit queue

```text
M-1  CURRENT  docs: establish post-v2.0.0 maintenance baseline
M-2  PLANNED  fix/test: align application version metadata
M-3  PLANNED  test: add backend mock-safe regression foundation
M-4  PLANNED  test: cover Framework fallback and voice artifact safety
M-5  PLANNED  fix: bound temporary chat sessions and TTS artifacts
M-6  PLANNED  fix: make Web CORS origins configurable
M-7  PLANNED  docs/test: clarify Fitbit current-state contract
M-8  PLANNED  test/docs: add v2.0.x aggregate maintenance readiness
M-9  PLANNED  release: build and verify a fixed patch ZIP only after scope acceptance
```

完了要件を前倒ししない。現在の小コミットが受け入れられるまで、次の項目を`CURRENT`または`COMPLETED`へ変更しない。

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
