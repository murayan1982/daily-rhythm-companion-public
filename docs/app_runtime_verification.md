# App runtime verification

This document defines the app-side release verification checkpoint for Daily Rhythm Companion.

The source-tree and fixed-zip release checks protect package hygiene, documentation inventory, backend scripts, and compatibility gates. They do not replace Flutter-side verification. Before writing release notes for v1.4.0, run a dedicated Flutter / Chrome checkpoint.

## v1.4.0 Day11 automated checkpoint

Use the same fixed release zip that passed Day9 and Day10.

```powershell
$zip = "release\DailyRhythmCompanion_20260521_194931.zip"

python -m compileall -q backend scripts
python scripts\check_v140_character_experience_day11.py $zip
```

The Day11 check must not rebuild the release zip.

It verifies:

```text
- Day10 final release readiness still passes against the same fixed zip.
- Flutter is available on PATH.
- `flutter test` passes from the app directory.
- `flutter devices` reports Chrome as an available web device.
```

## Manual Chrome smoke path

The automated Day11 check confirms Flutter tests and Chrome availability. A full browser session is still an operator smoke check because `flutter run -d chrome` is long-running and needs a backend process.

For a local mock-safe Chrome smoke:

Terminal 1:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Terminal 2:

```powershell
cd app
flutter run -d chrome
```

In the Chrome window, verify the lightweight demo path:

```text
- the app opens without a red error screen.
- Daily Rhythm Companion title renders.
- sleep/context area renders with mock-safe data or clear unavailable wording.
- character selection is visible.
- gentle_mina / ミナ, cheerful_sora / ソラ, and cool_rei / レイ can be distinguished.
- advice generation does not require real LLM credentials in mock-safe mode.
- History / DailyRecord flow remains reachable.
```

## Fixed zip handling

If Day11 passes without source changes, keep using the same fixed release zip.

If Day11 reveals an app issue that requires code changes, do not pretend the old fixed zip is still final. Instead:

```text
1. Fix the source tree.
2. Rerun Day8 cleanup.
3. Build one new fixed release zip.
4. Rerun Day9 fixed zip verification.
5. Rerun Day10 final release readiness.
6. Rerun Day11 app-side verification.
7. Write release notes against the new fixed zip.
```

## Non-goals

Day11 does not require:

```text
- real AI Character Framework checkout
- provider-backed LLM credentials
- Google Health real API access
- microphone or TTS runtime
- Live2D / VTS runtime
- App Store / Google Play packaging
```

Day11 also does not make medical, diagnostic, or production-health claims.


## v1.5.0 Day11 Flutter / Chrome app-side verification

v1.5.0 Day11 reuses the fixed release zip and verifies the app side without rebuilding release artifacts.

```powershell
$zip = "release\DailyRhythmCompanion_20260521_221101.zip"

python scripts\check_v150_mood_personalization_day11.py $zip
```

The automated check runs `flutter test`, runs `flutter devices`, and verifies that Chrome is detected as a Flutter web device.

The manual Chrome smoke path remains a separate operator action with the backend running.

## v1.6.0 Day11 Flutter / Chrome app-side verification

v1.6.0 Day11 reused the fixed release zip and verified the app side without rebuilding release artifacts.

```powershell
$zip = "release\DailyRhythmCompanion_20260522_195600.zip"

python scripts\check_v160_rhythm_reports_day11.py $zip
```

The automated check ran `flutter test`, ran `flutter devices`, and verified that Chrome was detected as a Flutter web device.

The manual Chrome smoke path remains a separate operator action with the backend running.

## v1.7.0 Day6 Manual Chrome rhythm report smoke

v1.7.0 Day6 adds a manual Chrome smoke checklist for the polished History screen rhythm report UX.

This checklist is for local/demo verification. It does not replace automated checks, and it does not rebuild any release artifact. Keep the v1.6.0 fixed zip unchanged:

```text
release\DailyRhythmCompanion_20260522_195600.zip
```

Before the manual smoke, run the current source-tree check:

```powershell
python -m compileall -q backend scripts
python scripts\check_v170_rhythm_report_polish_day6.py
```

### Start the mock-safe backend

Terminal 1:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Expected backend preflight:

```text
- GET /health returns status ok.
- mock-safe mode works without external LLM provider credentials.
- no real Google Health API access is required.
```

### Start the Flutter Chrome app

Terminal 2:

```powershell
cd app
flutter run -d chrome
```

Expected app preflight:

```text
- the app opens without a red error screen.
- Daily Rhythm Companion title renders.
- the backend-connected app can load the normal demo surfaces.
```

### History screen rhythm report smoke checklist

Open the History screen and verify the polished rhythm report cards.

```text
- Weekly Rhythm Report is visible.
- Monthly Rhythm Report is visible.
- each visible report card explains its record state with 記録状態.
- each visible report card explains the report range with レポート範囲.
- each visible report card explains saved-record coverage with 保存記録 and 睡眠つき記録.
- each visible report card explains data source with データ元.
- each visible report card explains aggregation scope with 集計範囲.
- weekly reports use 週次の保存履歴 wording.
- monthly reports use 月次の保存履歴 wording.
- sparse or partial data remains conservative and does not imply diagnosis or guaranteed improvement.
```

Also verify that polished cards do not expose raw/debug-style payload labels as the main user-facing explanation:

```text
- raw Quality: labels should not appear in the polished report cards.
- raw Source: labels should not appear in the polished report cards.
- raw Scope: labels should not appear in the polished report cards.
- raw weekly_history values should not appear in the polished report cards.
- raw monthly_history values should not appear in the polished report cards.
```

### Fallback-state smoke checklist

If the rhythm report calls are unavailable or still loading, verify the fallback wording remains understandable:

```text
- 週次リズムレポート: 読み込み未完了 can appear for the weekly card fallback.
- 月次リズムレポート: 読み込み未完了 can appear for the monthly card fallback.
- リズムレポートはまだ読み込めていません。 explains that the report card is unavailable.
- 履歴一覧と既存の週次まとめはそのまま確認できます。 keeps the rest of History usable.
- fallback cards still avoid raw Quality / Source / Scope labels.
```

### Non-goals for this smoke

The v1.7.0 Day6 manual Chrome smoke does not require:

```text
- real AI Character Framework checkout
- provider-backed LLM credentials
- Google Health real API access
- microphone or TTS runtime
- Live2D / VTS runtime
- App Store / Google Play packaging
- release zip creation or release zip rebuild
```

The smoke does not make medical, diagnostic, treatment, or health-improvement guarantee claims.



## v1.8.0 Day11 Flutter / Chrome app-side verification

v1.8.0 Day11 reuses the fixed release zip and verifies the app side without rebuilding release artifacts.

```powershell
$zip = "release\DailyRhythmCompanion_20260522_234744.zip"

python -m compileall -q backend scripts
python scripts\check_v180_report_advice_handoff_day11.py $zip
```

The automated check reruns Day10 final release readiness against the same fixed zip, runs `flutter test` from the app directory, runs `flutter devices`, and verifies that Chrome is detected as a Flutter web device.

The manual Chrome smoke path remains a separate operator action with the backend running. For v1.8.0, include the report-informed advice and saved reflection path in the manual smoke:

```text
- the app opens without a red error screen.
- Daily Rhythm Companion title renders.
- advice generation still works in mock-safe mode without provider credentials.
- report-informed advice context appears with user-facing wording when optional report_handoff metadata is present.
- the report context is described as historical context only, not today's sleep.
- raw source_label, data_scope, data_quality, and full rhythm_report+... basis strings are not used as the main UI copy.
- saved DailyRecord entries can show report-informed reflection in History.
- report-informed reflection remains conservative and non-medical.
- fallback or insufficient report context does not block normal advice or History review.
```

If Day11 reveals an app issue that requires code changes, rerun Day8 cleanup, build one new fixed release zip, and restart Day9 through Day11 with that new zip before writing release notes.
