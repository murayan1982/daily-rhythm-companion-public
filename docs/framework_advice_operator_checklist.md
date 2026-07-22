# Framework-backed advice operator checklist

This checklist is for a local/demo operator who wants to verify the AI Character Framework-backed advice path in Daily Rhythm Companion.

It separates three levels of verification:

```text
1. mock-safe source-tree verification
2. configured framework verification without external LLM calls
3. optional provider-backed LLM verification with explicit opt-in
```

The checklist must remain safe for public repository use. Do not paste provider keys, tokens, raw provider payloads, authorization headers, private local paths, or local token files into issues, docs, commits, release notes, or screenshots.

---

## Day9 final release readiness

After Day8 passes, verify final release readiness against the same fixed zip:

```powershell
$zip = "release\DailyRhythmCompanion_YYYYMMDD_HHMMSS.zip"
python scripts\check_v130_framework_llm_configured_demo_day9.py $zip
```

The Day9 check must not rebuild the package. It verifies the v1.3.0 Day8 fixed zip gate and protected v1.0.0 release checks against the same artifact.

---

## Day8 fixed release zip verification

After Day7 passes, create the release zip once and verify that fixed zip:

```powershell
.\build_release.bat
$zip = "release\DailyRhythmCompanion_YYYYMMDD_HHMMSS.zip"
python scripts\check_v130_framework_llm_configured_demo_day8.py $zip
```

The Day8 check requires a zip path argument and inspects the provided zip as-is. It does not rebuild the package and does not replace optional provider-backed verification.

---

## Day7 final source-tree verification

Before release packaging, run the Day7 final source-tree check:

```powershell
python -m compileall -q backend scripts
python scripts\check_v130_framework_llm_configured_demo_day7.py
```

The Day7 check runs Day6 aggregate readiness and verifies v1.3.0 docs/check/smoke inventory. It does not replace optional provider-backed verification; provider-backed LLM verification remains explicit opt-in.

---

## Day6 aggregate readiness check

For normal v1.3.0 source-tree readiness, use the Day6 aggregate check:

```powershell
python -m compileall -q backend scripts
python scripts\check_v130_framework_llm_configured_demo_day6.py
python scripts\check_v130_framework_llm_configured_demo_day7.py
```

The aggregate runs the Day1-Day5 checks and verifies the configured smoke SKIP path in a mock-safe subprocess. It does not replace optional provider-backed verification; provider-backed LLM verification remains explicit opt-in.

---

## 1. Start from mock-safe verification

Before configuring AI Character Framework or provider credentials, verify the safe default path:

```powershell
python -m compileall -q backend scripts
python scripts\check_v130_framework_llm_configured_demo_day1.py
python scripts\check_v130_framework_llm_configured_demo_day2.py
python scripts\check_v130_framework_llm_configured_demo_day3.py
python scripts\check_v130_framework_llm_configured_demo_day4.py
python scripts\check_v130_framework_llm_configured_demo_day5.py
python scripts\check_v130_framework_llm_configured_demo_day6.py
```

Expected baseline:

```text
[v130-framework-llm-day1-check] OK
[v130-framework-llm-day2-check] OK
[v130-framework-llm-day3-check] OK
[v130-framework-llm-day4-check] OK
[v130-framework-llm-day5-check] OK
[v130-framework-llm-day6-check] OK
[v130-framework-llm-day7-check] OK
```

If the configured smoke is run without framework setup, this is a normal mock-safe result:

```powershell
python scripts\smoke_v130_framework_llm_configured_demo.py --ignore-dotenv
```

Expected baseline:

```text
[v130-framework-llm-configured-smoke] SKIP: FRAMEWORK_ROOT/FRAMEWORK_PROJECT_ROOT is not configured.
```

---

## 2. Configure framework mode privately

Configure framework mode only in a local private environment such as process environment variables or an uncommitted local `.env` file.

Minimum framework-mode settings:

```env
CONVERSATION_ENGINE=framework
SLEEP_PROVIDER=mock
FRAMEWORK_ROOT=<path-to-ai-character-framework>
FRAMEWORK_PROJECT_ROOT=<path-to-ai-character-framework>
FRAMEWORK_PRESET=text_chat
FRAMEWORK_CHARACTER=default
FRAMEWORK_ADAPTER_MODE=local_import
```

Recommended private PowerShell session shape:

```powershell
$env:CONVERSATION_ENGINE = "framework"
$env:SLEEP_PROVIDER = "mock"
$env:FRAMEWORK_ROOT = "<path-to-ai-character-framework>"
$env:FRAMEWORK_PROJECT_ROOT = "<path-to-ai-character-framework>"
$env:FRAMEWORK_PRESET = "text_chat"
$env:FRAMEWORK_CHARACTER = "default"
$env:FRAMEWORK_ADAPTER_MODE = "local_import"
```

Do not commit local `.env` files or local framework paths.

---

## 3. Verify framework import and session creation without ask

Framework import and session creation should be testable before any provider-backed LLM call.

Import/config boundary:

```powershell
python scripts\smoke_v130_framework_llm_configured_demo.py
```

Session creation without `ask()`:

```powershell
python scripts\smoke_v130_framework_llm_configured_demo.py --create-session
```

Expected result categories:

```text
- OK: framework import/session boundary is available.
- SKIP: framework root is not configured or optional setup is absent.
- NG: configured framework path is present but invalid.
```

The `--create-session` path must not call `session.ask()` and must not require provider API keys.

---

## 4. Verify backend advice response in framework mode

Start the backend from the private configured environment:

```powershell
cd backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

In another terminal, verify basic status endpoints:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-RestMethod http://127.0.0.1:8000/demo/status
Invoke-RestMethod http://127.0.0.1:8000/characters
```

Then trigger `/advice` from the Flutter UI or an operator script. The operator should inspect the app-facing source label, not only the generated message text.

Expected source-label categories:

```text
mock response               -> AdviceSource.engine=mock
framework response          -> AdviceSource.engine=framework
framework fallback response -> AdviceSource.engine=framework_fallback
configured LLM skip         -> operator-check SKIP, not AdviceSource.engine
```

If framework mode falls back, that is acceptable for fallback-path verification, but the UI/operator note must not claim configured LLM success.

---

## 5. Verify DailyRecord save and History labels

After generating advice in the UI, save the DailyRecord and open History.

Expected saved basis categories:

```text
mock response               -> DailyRecord.advice_basis suffix +mock
framework response          -> DailyRecord.advice_basis suffix +framework
framework fallback response -> DailyRecord.advice_basis suffix +framework_fallback
configured LLM skip         -> no DailyRecord generated by the skip itself
```

History wording should remain conservative. It should not claim medical diagnosis, guaranteed health improvement, raw provider output, or hidden credential status.

---

## 6. Optional provider-backed LLM verification

Provider-backed LLM verification is optional and must be explicit.

Use provider keys only in a private local environment. Examples of accepted provider-key variable names:

```env
OPENAI_API_KEY=<provider-api-key>
GEMINI_API_KEY=<provider-api-key>
GOOGLE_API_KEY=<provider-api-key>
XAI_API_KEY=<provider-api-key>
```

The configured ask smoke requires both an explicit v1.3 gate and a provider key:

```powershell
$env:DRC_V130_ENABLE_CONFIGURED_LLM_SMOKE = "1"
$env:GEMINI_API_KEY = "<provider-api-key>"
python scripts\smoke_v130_framework_llm_configured_demo.py --ask
```

Without the gate or provider key, the smoke must print SKIP. Use `--require-llm` only when a prepared local/demo operator wants missing configured LLM setup to fail instead of skip.

Never include the provider key, full raw prompt, raw provider response, or private local path in shared logs.

---

## 7. Operator result table

Record only safe summaries:

```text
mock-safe checks: OK / NG
configured framework smoke: OK / SKIP / NG
configured session smoke: OK / SKIP / NG
optional configured ask smoke: OK / SKIP / NG
/advice source label: mock / framework / framework_fallback
DailyRecord basis suffix: +mock / +framework / +framework_fallback
History review: OK / NG
```

A safe operator note looks like:

```text
Framework import smoke OK. Session creation OK. Optional ask smoke skipped because provider key was not configured. /advice returned framework_fallback and History saved +framework_fallback as expected.
```

A note should not include:

```text
- provider API keys
- access tokens or refresh tokens
- authorization headers
- raw provider payloads
- local token files
- private absolute paths
- full raw LLM prompts or provider debug traces
```

---

## 8. Troubleshooting checkpoints

### Configured smoke prints SKIP

This is expected when `FRAMEWORK_ROOT` / `FRAMEWORK_PROJECT_ROOT` is absent. Configure the framework path privately or keep using mock-safe mode.

### Framework root is configured but smoke is NG

Check that the path points to the AI Character Framework root and that the public facade expected by DRC is importable.

### Provider-backed ask is SKIP

Check that `DRC_V130_ENABLE_CONFIGURED_LLM_SMOKE=1` and a provider key are present in the current process environment. Do not add provider keys to committed files.

### `/advice` returns framework_fallback

This means the framework path was requested but the framework-backed advice path could not complete. Confirm the fallback label remains visible and do not claim configured LLM success.


---

## 9. Release notes verification

For v1.3.0 release preparation, keep the operator record tied to the fixed zip that passed Day8 and Day9:

```powershell
$zip = "release\DailyRhythmCompanion_20260521_155200.zip"
python scripts\check_v130_framework_llm_configured_demo_day10.py $zip
```

The release notes should mention only safe summaries: fixed zip path, check names, OK/SKIP results, and non-claims. Do not paste provider API keys, raw prompts, raw provider payloads, local token files, or private absolute paths into release notes.
