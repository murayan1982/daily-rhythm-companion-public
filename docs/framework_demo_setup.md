# AI Character Framework demo setup

Daily Rhythm Companion can run in mock mode or framework mode.

Mock mode is the default. Framework mode is optional and should be enabled only in a configured local/demo environment.

This guide is the public first-read page for the AI Character Framework demo path. Use `docs/framework_local_setup.md` for the longer operator checklist.

---

## Mode summary

| Mode | Purpose | External requirements | Expected source label |
| --- | --- | --- | --- |
| mock mode | Normal local development and public smoke checks | none | `AdviceSource.engine=mock` |
| framework mode | Route text advice through AI Character Framework | local FW checkout | `AdviceSource.engine=framework` when successful |
| framework fallback | Keep `/advice` usable when framework mode is selected but unavailable | none beyond normal backend | `AdviceSource.engine=framework_fallback` |
| configured LLM mode | Prove provider-backed FW text generation in a prepared local/demo environment | local FW checkout plus provider setup | `AdviceSource.engine=framework` when successful |

Configured LLM mode is not the default and must not become mandatory for mock-safe development.

---

## Mock mode

```env
CONVERSATION_ENGINE=mock
SLEEP_PROVIDER=mock
```

Use mock mode for:

- normal local development
- public repository smoke checks
- Flutter widget tests
- release package checks
- smartphone Web demo checks that do not need real FW/LLM

Mock mode must not import AI Character Framework or call external LLM providers.

---

## Framework mode

```env
CONVERSATION_ENGINE=framework
SLEEP_PROVIDER=mock
FRAMEWORK_ROOT=<path-to-ai-character-framework>
FRAMEWORK_PRESET=text_chat
FRAMEWORK_CHARACTER=default
FRAMEWORK_ADAPTER_MODE=local_import
```

Use framework mode to demonstrate that Daily Rhythm Companion can pass app context into AI Character Framework and display FW-backed responses.

The backend currently supports the `local_import` adapter mode. It imports the public `framework` package from `FRAMEWORK_ROOT` and creates a text chat session through the public facade.

### Framework settings

| Setting | Meaning | Default / expected value |
| --- | --- | --- |
| `CONVERSATION_ENGINE` | Selects DRC's advice engine boundary | `framework` for FW mode |
| `SLEEP_PROVIDER` | Selects sleep summary source | keep `mock` for FW setup checks |
| `FRAMEWORK_ROOT` | Local AI Character Framework project/package root | `<path-to-ai-character-framework>` |
| `FRAMEWORK_PROJECT_ROOT` | Backward-compatible alias | accepted when `FRAMEWORK_ROOT` is absent |
| `FRAMEWORK_PRESET` | Framework preset name passed to `create_text_chat_session` | `text_chat` |
| `FRAMEWORK_CHARACTER` | Framework character override for local/demo checks | `default` |
| `FRAMEWORK_ADAPTER_MODE` | Adapter implementation | `local_import` |

Prefer `FRAMEWORK_ROOT` for new setup. Keep `FRAMEWORK_PROJECT_ROOT` only as a compatibility alias.

---

## Provider keys

Provider API keys are not required for mock-safe checks or source-tree checks.

Only configure provider keys when intentionally validating real FW/LLM generation in a prepared local/demo environment.

Use placeholders in docs and examples:

```env
GEMINI_API_KEY=<provider-api-key>
GOOGLE_API_KEY=<provider-api-key>
XAI_API_KEY=<provider-api-key>
```

Do not commit `.env`, provider keys, local credentials, raw provider responses, authorization headers, token values, or private local paths.

---

## Current local import behavior

The DRC framework adapter temporarily changes the current working directory to `FRAMEWORK_ROOT` while creating a text chat session and while calling `session.ask()`.

This is a compatibility workaround for current framework config/preset resolution behavior. The preferred framework-side direction is for AI Character Framework to load presets and characters relative to its package/project root, or from an explicit project root, without relying on the caller's current working directory.

---

## Expected v1.3 framework demo flow

```txt
Start backend in framework mode
→ confirm `/demo/status` and setup docs describe the configured state
→ open app
→ confirm sleep/context still comes from mock or another explicit provider
→ select mood
→ select character
→ generate advice
→ verify the advice source indicates framework path when configured
→ verify fallback label is visible if FW setup is unavailable
→ save DailyRecord
→ review History
```

The text advice flow should remain usable even when optional voice, TTS, motion, Google Health, or provider-backed LLM pieces are not configured.

---

## Configured-only smoke checks

Use the v1.3.0 configured smoke only when intentionally checking the framework path.

Safe default behavior:

```txt
unset framework configuration → SKIP
FRAMEWORK_ROOT configured → public facade import check
--create-session → session creation without ask()
--ask → provider-backed ask only with explicit opt-in
```

Basic configured smoke:

```powershell
python scripts\smoke_v130_framework_llm_configured_demo.py
```

Session creation smoke without calling `ask()`:

```powershell
python scripts\smoke_v130_framework_llm_configured_demo.py --create-session
```

Provider-backed FW/LLM ask smoke is explicit opt-in:

```powershell
$env:DRC_V130_ENABLE_CONFIGURED_LLM_SMOKE = "1"
# Equivalent gate marker: DRC_V130_ENABLE_CONFIGURED_LLM_SMOKE=1
python scripts\smoke_v130_framework_llm_configured_demo.py --ask
```

Do not run the `--ask` path unless the local FW checkout and provider route are intentionally configured. The smoke should not log provider keys, raw prompts, raw provider payloads, token values, or private local paths.

---

## Optional capabilities

Voice input, voice output / TTS, and Live2D / VTS motion are demo capabilities. They are not mandatory for the normal text advice flow.

Expected behavior:

```txt
configured and available → demo capability can run
not configured → status explains unavailable/skipped/fallback
failure/unavailable → text advice and History remain usable
```

The app should not silently make optional capabilities mandatory.

---

## Public repository rule

Public docs should use placeholders such as:

```txt
<path-to-ai-character-framework>
<provider-api-key>
```

Do not document a local machine path, personal account path, token value, client secret, raw provider payload, Authorization header, local token file, or private absolute path.


---

## Source labels and fallback wording

Framework / LLM demo hardening uses small app-facing source labels so the operator can tell whether advice came from mock mode, framework mode, or framework fallback.

Current `/advice` source labels:

```text
AdviceSource.engine=mock
AdviceSource.engine=framework
AdviceSource.engine=framework_fallback
```

Current saved DailyRecord suffixes:

```text
+mock
+framework
+framework_fallback
```

Configured LLM skip is an operator-check state, not an `AdviceSource.engine` value. A configured-only smoke SKIP means the check did not run the provider-backed ask path and should not be described as generated advice.

For the full contract, see [Framework source labels](framework_source_labels.md).

Mock-safe source-label check:

```powershell
python scripts\check_v130_framework_llm_configured_demo_day4.py
```


---

## FW-backed advice operator checklist

For a full local/demo operator flow, use [Framework-backed advice operator checklist](framework_advice_operator_checklist.md).

The checklist separates:

```text
- mock-safe source-tree checks
- configured framework smoke without external LLM calls
- optional provider-backed LLM ask smoke with DRC_V130_ENABLE_CONFIGURED_LLM_SMOKE=1
- backend /health, /demo/status, /characters, and /advice verification
- AdviceSource.engine and DailyRecord.advice_basis source-label review
- History review after saving a DailyRecord
```

Provider API keys are never required for the default Day1-Day5 checks. When used for the optional configured ask smoke, keys must stay in a private local environment and must not be committed, logged, or copied into shared notes.

Mock-safe operator check:

```powershell
python scripts\check_v130_framework_llm_configured_demo_day5.py
```


---

## v1.3.0 aggregate readiness check

Day6 adds one mock-safe aggregate command:

```powershell
python scripts\check_v130_framework_llm_configured_demo_day6.py
```

The aggregate runs the Day1-Day5 checks and verifies configured smoke SKIP-first behavior in an isolated subprocess where `FRAMEWORK_ROOT`, `FRAMEWORK_PROJECT_ROOT`, and provider-key variables are cleared.

This aggregate does not replace optional provider-backed LLM verification. It does not create or rebuild release artifacts.


---

## v1.3.0 final source-tree verification

Day7 adds the final source-tree verification command before release packaging:

```powershell
python scripts\check_v130_framework_llm_configured_demo_day7.py
```

This command runs the Day6 aggregate check, verifies the v1.3.0 docs/check/smoke inventory, and confirms public Framework / LLM demo docs avoid sensitive-looking values.

It does not create or rebuild release artifacts, and it does not replace optional provider-backed LLM verification.


---

## v1.3.0 fixed release zip verification

Day8 verifies a release zip that has already been created:

```powershell
.\build_release.bat
$zip = "release\DailyRhythmCompanion_YYYYMMDD_HHMMSS.zip"
python scripts\check_v130_framework_llm_configured_demo_day8.py $zip
```

The Day8 check inspects the provided zip as-is. It confirms that v1.3.0 Framework / LLM docs, internal guardrail docs, checks, and the configured smoke script are included, while obvious private/dev/generated artifacts are absent.

Do not rerun `build_release.bat` between recording the fixed zip path and running the Day8 check.


---

## v1.3.0 final release readiness

Day9 reuses the fixed release zip that already passed Day8:

```powershell
$zip = "release\DailyRhythmCompanion_YYYYMMDD_HHMMSS.zip"
python scripts\check_v130_framework_llm_configured_demo_day9.py $zip
```

The Day9 check runs the Day8-passed fixed zip inventory and protected v1.0.0 release gates against the same artifact. It does not rebuild the zip and does not require provider API keys or live LLM calls.


---

## v1.3.0 release notes verification

Day10 adds release notes after the fixed zip has already passed Day8 and Day9:

```powershell
$zip = "release\DailyRhythmCompanion_20260521_155200.zip"
python scripts\check_v130_framework_llm_configured_demo_day10.py $zip
```

The Day10 check verifies `release_notes_v1.3.0.md` and re-runs Day9 final release readiness against the same fixed zip. It does not rebuild the zip and does not require provider API keys or live LLM calls.
