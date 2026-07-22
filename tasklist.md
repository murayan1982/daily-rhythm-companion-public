# Daily Rhythm Companion v2.0.0

## 最終Publicリリース前 課題一覧・タスクリスト

更新日: 2026-07-22

## 1. 現在地

```text
current released baseline: v1.10.0
current target: v2.0.0
v2.0.0 status: NOT_RELEASED

capability evidence: ACCEPTED
accepted private evidence manifest: ACCEPTED

Public repository: created
Public-P4: completed
Public-P5: completed
Public-P6: completed

final Public fixed ZIP: not-built
final artifact record: not-recorded
DRC_v2.0.0 annotated tag: not-created
GitHub Release: not-created
```

重要な区別:

```text
Day82 / Day83の検証機構・契約実装
    = completed

最終Public mainから一度だけ作るZIPに対する
Day82 / Day83の実受け入れ
    = not completed
```

既存のPrivateリポジトリ候補ZIP、Private側タグ、手動作成ZIPは、最終Publicリリースには使用しない。

---

# 2. 最終ビルド前に解決する課題

## 課題A — Day82／Day83が証拠JSONなしでも成功できる

優先度: P0・リリースブロッカー

現状の疑い:

```text
--release-zip のみ指定
--evidence-json なし
```

でもZIP構造検査後に成功終了できる。

この状態では、正式builder由来か確認できないZIPや、Day80／Day81の受け入れ証拠が結び付いていないZIPでも、Day82／Day83の `OK` と誤解される可能性がある。

### 必要な修正

* 実受け入れモードでは `--release-zip` と `--evidence-json` を必須セットにする。
* ZIPのみの検査は「パッケージ構造検査」に限定する。
* ZIPのみの実行でDay82／Day83 acceptanceを名乗らない。
* source-tree契約スモークは引き続きcredential-freeで実行可能にする。
* Day82／Day83の実受け入れと、契約実装チェックを出力上でも明確に分ける。

### 変更対象候補

```text
scripts/smoke_framework_v200_fixed_release_zip_with_web_evidence_verification.py
scripts/smoke_framework_v200_final_release_readiness_fixed_zip_with_web_evidence.py

backend/app/services/
  framework_v200_fixed_release_zip_with_web_evidence_verification.py

docs/operator_evidence_templates/
  v200_fixed_release_zip_with_web_evidence_day82.example.json

docs/DRC_v200_goal_checklist_small_commit.md
```

### 完了条件

* evidence JSONを省略した実受け入れコマンドが非成功になる。
* ZIP単体の構造検査は別モードとして実行できる。
* 正しいZIPと正しい証拠JSONの組み合わせだけが受け入れ成功になる。
* fixed ZIP、tag、Releaseは未完了のまま維持される。

### 小コミット案

```text
test: require evidence-backed Day82 and Day83 acceptance
```

---

## 課題B — Day81／ZIPビルド／Day82の順序が循環している

優先度: P0・リリースブロッカー

現在の説明には、次の循環が生じる可能性がある。

```text
Day81:
fixed ZIPの存在・検証を要求

Day82 evidence:
Day81通過後にZIPを作ったことを要求
```

これでは、どちらを先に実行すべきか確定できない。

### 正しい実行順として固定する案

```text
1. Day80 accepted manifestを確認
2. 最終Publicソースをcommit
3. Public mainへpush
4. HEAD == origin/mainを確認
5. ソースをfreeze
6. fixed ZIPを一度だけbuild
7. そのZIPでDay81
8. 同じZIPでDay82
9. 同じZIPでDay83
10. 同じZIPのartifact recordを検証
11. annotated tagを作成
12. 同じZIPをGitHub Releaseへ添付
```

### 必要な修正

* `release_zip_built_once_after_day81` のような循環するマーカーを廃止する。
* 次のような意味へ変更する。

```text
release_zip_built_once_from_final_committed_public_source
release_zip_built_once_before_day82
same_fixed_zip_used_for_day81_day82_day83
```

### 変更対象候補

```text
backend/app/services/
  framework_v200_fixed_release_zip_with_web_evidence_verification.py

scripts/smoke_framework_v200_fixed_release_zip_with_web_evidence_verification.py
scripts/smoke_framework_v200_final_release_readiness_fixed_zip_with_web_evidence.py

docs/operator_evidence_templates/
  v200_fixed_release_zip_with_web_evidence_day82.example.json

docs/v200_fixed_release_zip_with_web_evidence_verification.md
docs/v200_final_release_readiness_fixed_zip_with_web_evidence.md
docs/DRC_v200_goal_checklist_small_commit.md
```

### 完了条件

* ビルドからDay83までの順序が一意に読める。
* Day81とDay82の相互依存がない。
* 同じZIPを使い続ける契約が維持される。
* ZIP作成後のソースコミット禁止が維持される。

この修正は課題Aと同じ小コミットに含めてよい。

---

## 課題C — 手動ZIPに未追跡Flutter生成ファイルが混入しても通る

優先度: P0・リリースブロッカー

調査対象ZIPでは、Gitで無視されるFlutter生成ファイルが含まれていた。

```text
app/android/app/src/main/java/io/flutter/plugins/
  GeneratedPluginRegistrant.java

app/ios/Runner/
  GeneratedPluginRegistrant.h
  GeneratedPluginRegistrant.m

app/linux/flutter/
  generated_plugin_registrant.cc
  generated_plugin_registrant.h
  generated_plugins.cmake

app/windows/flutter/
  generated_plugin_registrant.cc
  generated_plugin_registrant.h
  generated_plugins.cmake
```

正式builderはcommitted HEADのdetached worktreeを使用するため、これらの未追跡生成物は本来入らない。

現行検査でこれらが明示的に拒否されなければ、作業フォルダを手動圧縮したZIPが正式成果物に見える可能性がある。

### 必要な修正

* fixed ZIPの禁止エントリへFlutter生成registrantを追加する。
* Windows、Linux、iOS、Androidの対象をすべて検査する。
* generated registrantを含むテストZIPが拒否されるnegative testを追加する。
* 正式builderのdetached worktree方針を文書化する。
* 手動ZIPは最終成果物にならないことを明記する。

### 変更対象候補

```text
backend/app/services/framework_v200_public_distribution_readiness.py
scripts/smoke_framework_v200_public_distribution_readiness.py
scripts/check_release_package.py
docs/v200_public_distribution_readiness.md
docs/DRC_v200_goal_checklist_small_commit.md
```

### 完了条件

* 9個のFlutter生成ファイルのいずれかを含むZIPが拒否される。
* 通常のFlutterソースや必要な設定ファイルは誤って拒否されない。
* 正式builderによるZIP検査は通る。
* source-tree検査とfixed-ZIP検査の役割が区別される。

### 小コミット案

```text
test: reject untracked Flutter generated release entries
```

---

## 課題D — Public main-only契約と旧main/develop文言が混在

優先度: P1・最終ビルド前に必須

Public-P4以降の正式契約は次のとおり。

```text
clean-history Public repository
branch: main
HEAD == origin/main
one root commit
Private git history excluded
develop ref is not part of the final artifact record
```

一方、一部のDay82／Day83文書やscripts READMEには旧G-7時代の以下の文言が残っている。

```text
main and develop point to the same HEAD
matching main and develop refs
```

### 必要な修正

* 現在の操作手順から `develop` を削除する。
* 旧G-7説明を残す場合は、historical／supersededと明記する。
* 現行手順を次に統一する。

```text
Public main HEAD
==
origin/main
==
artifact source_head
==
annotated tag target
```

### 変更対象候補

```text
docs/v200_fixed_release_zip_with_web_evidence_verification.md
docs/v200_final_release_readiness_fixed_zip_with_web_evidence.md
scripts/README.md
scripts/smoke_framework_v200_final_release_artifact_record.py
```

### 完了条件

* active手順に `develop` 必須条件が存在しない。
* artifact record実装と文書が一致する。
* historical説明とcurrent procedureが区別される。
* `develop_head`を最終Public recordへ入れた場合は引き続き拒否される。

---

## 課題E — builderのDay80 manifest依存に関する記録が不正確

優先度: P1

実builderは、Publicリポジトリ外に置いたaccepted Day80 manifestを明示指定する設計になっている。

```text
ManifestPath is required
manifest must remain outside the Public repository
```

一方、タスクリストの説明には、Private manifest dependencyそのものを削除したように読める記述がある。

実際に削除されたのは、Publicリポジトリ内部のignored manifestへの暗黙依存であり、外部Day80 manifestによるpreflightは残っている。

### 必要な修正

次のように意味を分ける。

```text
builder_repository_local_private_manifest_dependency:
  removed

builder_external_day80_manifest_preflight:
  required
```

### 変更対象候補

```text
docs/DRC_v200_goal_checklist_small_commit.md
docs/v200_public_repository_migration.md
README.md
roadmap.md
```

builder実装は、現在の外部manifest必須方針が意図どおりなら変更しない。

### 完了条件

* checklistとbuilder実装が同じ意味を示す。
* private manifestをリポジトリへ入れない方針が維持される。
* raw evidenceやprivate pathを公開メタデータへコピーしない。
* accepted public-safe markerだけで実証拠を代替したとは説明しない。

---

## 課題F — Public-P6後の状態文書が同期されていない

優先度: P1

状態説明の一部がPublic-P5時点で止まっている。

### 同期対象

```text
README.md
roadmap.md
docs/v200_public_repository_migration.md
docs/DRC_v200_goal_checklist_small_commit.md
```

### 必要な修正

* Public-P6完了を反映する。
* 今回のpre-build follow-up完了後の状態を追記する。
* 次の未完了状態は変更しない。

```text
final_fixed_release_zip: not-built
public_fixed_release_zip: not-built
DRC_v2.0.0_tag: not-created
public_DRC_v2.0.0_tag: not-created
public_github_release: not-created
release_status: NOT_RELEASED
```

### 完了条件

* README、roadmap、migration、checklistの現在地が一致する。
* ZIP、tag、Releaseを完了扱いにしない。
* 実行していないDay82／Day83受け入れにチェックを付けない。
* 「validator実装完了」と「最終artifact検証完了」を区別する。

---

## 課題G — Public distribution validatorのnext_focusが古い

優先度: P1

validator出力のnext focusが、すでに完了したPublic-P3／Publicリポジトリ初期化を案内している。

### 必要な修正

現在の次工程へ更新する。

```text
Resolve final Public pre-build gate issues.
Commit and push final Public source.
Verify clean Public main.
Freeze source.
Build one fixed ZIP.
Run Day81, Day82 and Day83 against that same ZIP.
```

### 変更対象候補

```text
backend/app/services/framework_v200_public_distribution_readiness.py
scripts/smoke_framework_v200_public_distribution_readiness.py
docs/v200_public_distribution_readiness.md
```

### 完了条件

* validator出力が完了済みPublic-P3を案内しない。
* fixed ZIPをまだ作成していない状態を正しく案内する。
* 出力更新に対する回帰テストがある。

課題Cと同じ小コミットへ含めてよい。

---

## 課題H — tracked files 576とZIP内586ファイルの差

優先度: P1・Public実チェックアウトで確認

roadmap上の記録:

```text
public_repository_tracked_files: 576
```

調査ZIP:

```text
physical files: 586
```

9ファイルはFlutter生成registrantとして特定済み。

残り1ファイルは、ZIPにGitメタデータがないため追跡／未追跡を断定できない。

### 確認コマンド

```powershell
git status --short --untracked-files=all
git ls-files | Measure-Object

git ls-files |
    Sort-Object |
    Set-Content tracked_files.txt
```

必要に応じて、展開ZIPのファイル一覧と `git ls-files` を比較する。

### 完了条件

* Public実チェックアウトがclean。
* 追跡ファイル数を再確認。
* ZIPに含まれる全ファイルがbuilderの想定内。
* 不明な10個目のファイルを特定。
* 生成物や未追跡物がある状態ではbuilderを実行しない。

この確認だけのためにコミットは作成しない。

---

# 3. 推奨する小コミット順

## Commit 1 — Day82／Day83受け入れ契約修正

```text
test: require evidence-backed Day82 and Day83 acceptance
```

対象課題:

```text
A. evidence JSONなし成功
B. Day81／ビルド／Day82順序の循環
```

このコミットでは以下を行わない。

```text
- fixed ZIP作成
- tag作成
- GitHub Release作成
- capability acceptanceの変更
```

---

## Commit 2 — ZIP生成物ガード強化

```text
test: reject untracked Flutter generated release entries
```

対象課題:

```text
C. ignored Flutter生成ファイル
G. public distribution next_focus
```

このコミットでは正式ZIPを作成しない。

---

## Commit 3 — Public最終手順・状態同期

```text
docs: synchronize final Public release sequence
```

対象課題:

```text
D. main/develop旧文言
E. manifest依存説明
F. Public-P6後の状態同期
```

必要に応じて課題A〜Cの結果もsource of truthへ記録する。

このコミットでも次は未完了のままとする。

```text
final fixed ZIP
Day81 actual fixed-ZIP acceptance
Day82 actual fixed-ZIP acceptance
Day83 actual fixed-ZIP acceptance
artifact record
annotated tag
GitHub Release
```

---

# 4. 各コミット後の検証

## 共通Python検証

```powershell
python -m compileall -q backend scripts

python scripts\smoke_framework_v200_public_distribution_readiness.py
python scripts\smoke_framework_v200_accepted_web_evidence_manifest_acceptance_sync.py
python scripts\smoke_framework_v200_accepted_web_evidence_manifest_aggregate.py
python scripts\smoke_framework_v200_final_release_artifact_record.py
python scripts\smoke_framework_v200_fixed_release_zip_with_web_evidence_verification.py
python scripts\smoke_framework_v200_final_release_readiness_fixed_zip_with_web_evidence.py
python scripts\smoke_framework_v200_final_release_readiness_with_web_evidence.py
```

## Flutter検証

```powershell
cd app
flutter test
cd ..
```

## Public Git状態確認

```powershell
git status --short --untracked-files=all
git branch --show-current
git rev-parse HEAD
git rev-parse refs/remotes/origin/main
git rev-list --max-parents=0 HEAD
git tag --list DRC_v2.0.0
git remote get-url origin
git ls-files | Measure-Object
```

期待値:

```text
working tree: clean
branch: main
HEAD == origin/main
root commit count: 1
DRC_v2.0.0 tag: absent
origin: official Public repository
```

---

# 5. 最終ビルド開始条件

以下がすべて満たされるまではbuilderを実行しない。

```text
[ ] Commit 1が完了
[ ] Commit 1のテストが通過
[ ] Commit 2が完了
[ ] Commit 2のnegative ZIP testが通過
[ ] Commit 3が完了
[ ] source of truthと状態文書が同期
[ ] compileall通過
[ ] 全関連スモーク通過
[ ] flutter test通過
[ ] Public working treeがclean
[ ] branchがmain
[ ] HEAD == origin/main
[ ] root commit count == 1
[ ] official Public origin確認
[ ] DRC_v2.0.0 tagが存在しない
[ ] tracked／untrackedファイル差分を確認
[ ] accepted Day80 manifestがPublic repository外に存在
[ ] これ以上ソース修正が不要と判断
```

---

# 6. 最終ビルド後のタスクリスト

このセクションは、前項の全条件を満たした後だけ実行する。

```text
[ ] 最終Public mainのHEADを記録
[ ] builderを一度だけ実行
[ ] fixed ZIPの絶対パスまたは安全な記録用パスを保持
[ ] ZIP basenameを記録
[ ] ZIP byte sizeを記録
[ ] ZIP SHA-256を記録
[ ] ZIPの更新時刻を記録
[ ] 同じZIPでDay81を実行
[ ] 同じZIPと証拠JSONでDay82を実行
[ ] ZIPのhashとサイズが変わっていないことを確認
[ ] 同じZIPと証拠JSONでDay83を実行
[ ] ZIPのhashとサイズが変わっていないことを再確認
[ ] final artifact recordを検証
[ ] source HEADとtag target候補が一致することを確認
[ ] annotated DRC_v2.0.0 tagを作成
[ ] tagをpush
[ ] 同じZIPをGitHub Releaseへ添付
[ ] artifact recordをtag messageとRelease bodyへ同一内容で記載
[ ] GitHub Releaseを公開
[ ] v2.0.0 release完了を確認
```

最終ZIP作成後は禁止:

```text
- ソース変更
- 文書変更
- コミット追加
- ZIP再構築
- ZIP内容変更
- 別ZIPへの差し替え
```

変更が必要になった場合:

```text
1. 旧ZIPを不採用にする
2. ソースを修正してcommit/push
3. 全pre-build検証をやり直す
4. 新しいHEADから一度だけ新ZIPを作る
5. Day81以降を最初からやり直す
```

---

# 7. 今回の作業範囲

当面の作業対象:

```text
Commit 1
→ Commit 2
→ Commit 3
→ Public実チェックアウトで全検証
```

今回まだ実行しないもの:

```text
- 最終fixed ZIP作成
- Day81／Day82／Day83の最終artifact受け入れ
- final artifact record作成
- annotated tag作成
- GitHub Release公開
- v2.0.0 release完了更新
```
