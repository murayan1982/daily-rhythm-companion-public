# AI Character Framework Local Setup

This guide explains the optional local AI Character Framework integration path for Daily Rhythm Companion.

Normal local development remains mock-safe. Use framework mode only when intentionally testing the local AI Character Framework adapter or a configured FW-backed advice demo.

---

## 1. Start from mock-safe mode

Keep the normal backend `.env` in mock mode unless intentionally testing framework integration:

```env
CONVERSATION_ENGINE=mock
SLEEP_PROVIDER=mock
GEMINI_API_KEY=
GOOGLE_API_KEY=
XAI_API_KEY=
```

This keeps local development independent from AI Character Framework, LLM provider keys, audio dependencies, Live2D/VTS dependencies, and real health-data providers.

Recommended baseline check:

```powershell
python -m compileall -q backend scripts
python scripts\check_v130_framework_llm_configured_demo_day1.py
python scripts\check_v130_framework_llm_configured_demo_day2.py
python scripts\check_v130_framework_llm_configured_demo_day3.py
```

The v1.3.0 Day1-Day3 checks are source-tree checks. They do not require a real AI Character Framework checkout, provider credentials, or external LLM calls. Day3 verifies configured-only smoke behavior with an isolated fake FW fixture.

---

## 2. Prepare a local framework profile

Copy the example profile only when intentionally testing framework mode:

```powershell
Copy-Item backend\env_profiles\framework_local.env.example backend\.env -Force
```

Then edit `backend/.env` locally.

```env
CONVERSATION_ENGINE=framework
SLEEP_PROVIDER=mock

FRAMEWORK_ROOT=<path-to-ai-character-framework>
FRAMEWORK_PROJECT_ROOT=
FRAMEWORK_PRESET=text_chat
FRAMEWORK_CHARACTER=default
FRAMEWORK_ADAPTER_MODE=local_import

GEMINI_API_KEY=
GOOGLE_API_KEY=
XAI_API_KEY=
```

Do not commit `backend/.env`.

---

## 3. Framework settings

| Setting | Required for framework mode | Notes |
| --- | --- | --- |
| `CONVERSATION_ENGINE=framework` | yes | Routes `/advice` through `FrameworkConversationEngine`. |
| `SLEEP_PROVIDER=mock` | recommended for FW checks | Keeps FW setup independent from health provider setup. |
| `FRAMEWORK_ROOT` | yes for local import | Preferred setting. Points at the local AI Character Framework root containing the `framework` package. |
| `FRAMEWORK_PROJECT_ROOT` | compatibility alias | Used only when `FRAMEWORK_ROOT` is absent. Prefer `FRAMEWORK_ROOT` for new setup. |
| `FRAMEWORK_PRESET` | yes | Usually `text_chat`. Passed to `create_text_chat_session`. |
| `FRAMEWORK_CHARACTER` | yes | Usually `default` for local setup. Character mapping may override app-facing DRC character IDs later. |
| `FRAMEWORK_ADAPTER_MODE` | yes | Currently expected to be `local_import`. |
| `GEMINI_API_KEY`, `GOOGLE_API_KEY`, `XAI_API_KEY` | optional | Keep empty unless intentionally validating provider-backed FW/LLM generation. |

`FRAMEWORK_ROOT` should be a private local path in your own uncommitted `.env`, but public docs and committed examples must use `<path-to-ai-character-framework>`.

---

## 4. Current implementation behavior

The DRC framework adapter imports the public `framework` package from `FRAMEWORK_ROOT`.

Current implemented path:

```txt
/advice request
→ FrameworkConversationEngine
→ resolve DRC character to FW character
→ import framework.create_text_chat_session
→ create text chat session
→ build DRC advice prompt
→ call session.ask(prompt)
→ normalize returned text into AdviceResponse
```

Current source labels:

```txt
mock mode success         → AdviceSource.engine=mock
framework mode success    → AdviceSource.engine=framework
framework unavailable     → AdviceSource.engine=framework_fallback
```

When framework mode is selected but framework setup is unavailable, `/advice` falls back to the mock engine. The fallback should stay visible through API response metadata and saved `DailyRecord.advice_basis` values.

---

## 5. Current CWD workaround

The framework adapter temporarily changes the current working directory to `FRAMEWORK_ROOT` while creating a text chat session and while calling `session.ask()`.

This is a compatibility workaround for framework preset/character loading that may still depend on the process current working directory.

The preferred long-term fix is on the AI Character Framework side:

```txt
Framework facade/config loading should resolve presets and characters relative to the FW package root or an explicit project_root, not the caller's current working directory.
```

Until that is fixed, the DRC adapter must restore the previous current working directory after framework calls.

---

## 6. Optional local checks

Config and facade import check:

```powershell
python scripts\check_framework_local_config.py --require-config
```

Session creation check:

```powershell
python scripts\check_framework_local_config.py --create-session --require-config
```

The session creation check does not call `session.ask()`.

If `FRAMEWORK_ROOT` is unset and `--require-config` is not passed, the check exits as a safe SKIP:

```txt
[framework-local-config-check-v0.30.0] SKIP FRAMEWORK_ROOT/FRAMEWORK_PROJECT_ROOT is not configured.
```

The v1.3.0 configured-only smoke command uses the same SKIP-first style:

```powershell
python scripts\smoke_v130_framework_llm_configured_demo.py
```

With no framework root configured, expected output starts with:

```txt
[v130-framework-llm-configured-smoke] SKIP
```

After `FRAMEWORK_ROOT` is configured, the basic smoke imports the public FW facade but does not create a session. To create a text chat session without calling `ask()` (this does not call `ask()`):

```powershell
python scripts\smoke_v130_framework_llm_configured_demo.py --create-session
```

Use `--require-framework` only in an environment where missing FW configuration should fail CI/operator verification instead of SKIP.

---

## 7. Provider-backed LLM checks

Provider-backed LLM validation is intentionally separate from framework import/session checks.

Do not add provider API keys to committed docs or examples. In local `.env`, configure keys only when you intentionally want a real FW/LLM response:

```env
GEMINI_API_KEY=<provider-api-key>
GOOGLE_API_KEY=<provider-api-key>
XAI_API_KEY=<provider-api-key>
```

A provider-backed check should be opt-in, should clearly print SKIP when provider setup is missing, and should avoid logging raw prompts, raw provider payloads, token values, or private local paths.

The v1.3.0 configured ask smoke requires both an explicit gate and a provider key:

```powershell
$env:DRC_V130_ENABLE_CONFIGURED_LLM_SMOKE = "1"
# Equivalent gate marker: DRC_V130_ENABLE_CONFIGURED_LLM_SMOKE=1
$env:GEMINI_API_KEY = "<provider-api-key>"
python scripts\smoke_v130_framework_llm_configured_demo.py --ask
```

If the gate or provider key is missing, the smoke prints SKIP. Use `--require-llm` only when a prepared configured environment should fail instead of SKIP.

---


---

## Source label verification

After Day4, configured demo verification should check source labels as well as response text.

Mock-safe check:

```powershell
python scripts\check_v130_framework_llm_configured_demo_day4.py
```

Expected source-label contract:

```text
mock response              -> AdviceSource.engine=mock, DailyRecord suffix +mock
framework response         -> AdviceSource.engine=framework, DailyRecord suffix +framework
framework fallback response -> AdviceSource.engine=framework_fallback, DailyRecord suffix +framework_fallback
configured LLM skip         -> operator smoke SKIP, not AdviceSource.engine
```

When framework mode falls back, local fallback advice is acceptable, but operator wording must not claim configured LLM success or provider-backed generation success.

See [Framework source labels](framework_source_labels.md).

## 8. FW-backed advice operator checklist

Use [Framework-backed advice operator checklist](framework_advice_operator_checklist.md) when verifying a configured local/demo run end to end.

The operator checklist covers:

```text
- mock-safe Day1-Day5 checks
- configured FW import smoke
- configured session creation without ask
- optional provider-backed ask smoke
- backend status endpoints
- /advice source-label inspection
- DailyRecord save and History review
- safe result summaries without secrets, raw payloads, or private local paths
```

The checklist is intentionally split so provider API keys are only needed for optional provider-backed LLM verification.

---

## 9. Troubleshooting

### `FRAMEWORK_ROOT` is missing

Expected behavior:

```txt
configured-only checks without --require-config → SKIP
/advice in framework mode → framework_fallback metadata remains visible
```

Fix:

```txt
Set FRAMEWORK_ROOT in backend/.env or return to CONVERSATION_ENGINE=mock.
```

### `framework/facade.py` was not found

Expected cause:

```txt
FRAMEWORK_ROOT does not point at the AI Character Framework root.
```

Fix:

```txt
Use the directory that contains the framework package.
```

### Preset file not found

Expected cause:

```txt
Framework preset/character resolution depends on the wrong project root or current working directory.
```

Fix direction:

```txt
Keep using the DRC temporary CWD workaround for now; fix FW facade/config loading to use FW package root or explicit project_root later.
```

### Real LLM response is not generated

Expected causes:

```txt
provider key is missing
provider package is not installed
framework route falls back internally
configured LLM mode was not intentionally enabled
```

Fix:

```txt
Verify FW provider setup separately, then rerun configured-only checks.
```

---

## 9. Public safety checklist

Do not expose:

```txt
.env
provider API keys
access tokens
refresh tokens
client secrets
Authorization headers
raw provider payloads
raw prompts containing private data
local token files
local_data/
private absolute paths
```

Use placeholders such as:

```txt
<path-to-ai-character-framework>
<provider-api-key>
```
