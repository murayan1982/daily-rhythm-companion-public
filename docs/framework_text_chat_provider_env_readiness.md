# Framework text chat provider env readiness

v1.9.0 Day26 adds a public-safe readiness check for the configured AI Character Framework text chat provider environment.

Day25 identified the next strict configured session-creation blocker:

```text
framework-root-cwd -> OSError
safe_message: GOOGLE_API_KEY is not defined.
failure_kind: provider-env-missing
```

Day26 does not add a provider call. It only checks whether the required provider env var names are set locally.

## Public-safe rule

The readiness helper may report:

```text
GOOGLE_API_KEY set=True|False
GEMINI_API_KEY set=True|False
OPENAI_API_KEY set=True|False
XAI_API_KEY set=True|False
```

It must not print, persist, or return actual API key values. Do not commit secrets.

## Added files

```text
backend/app/services/framework_text_chat_provider_env_readiness.py
scripts/smoke_framework_text_chat_provider_env_readiness.py
scripts/check_v190_smartphone_web_fw_demo_day26.py
docs/framework_text_chat_provider_env_readiness.md
docs/internal/v190_smartphone_web_fw_demo_day26.md
```

## Source-tree smoke

```powershell
python scripts\smoke_framework_text_chat_provider_env_readiness.py
```

This mode uses fake env mappings and verifies that secret-like values are never rendered.

## Local readiness check

After setting provider env values locally only, an operator can run:

```powershell
python scripts\smoke_framework_text_chat_provider_env_readiness.py --required-env GOOGLE_API_KEY
```

Expected behavior:

```text
status: ready    # when the required env var is set locally
status: blocked  # when the required env var is unset
```

The output lists env names and boolean set/unset states only.

## Strict session diagnosis integration

Day26 also makes the strict session diagnosis output more actionable. When a session creation attempt fails with `provider-env-missing`, the script prints:

```text
provider_env_readiness_status: blocked|ready
provider_env_required_names: GOOGLE_API_KEY
provider_env: GOOGLE_API_KEY set= False|True
```

The script still does not call `ask`, `ask_stream`, or provider APIs.

## Day26 conclusion

The active blocker after Day25 is not registry import layout. It is provider env readiness for configured FW session creation. Day26 gives a safe local readiness gate so the next run can either create a session or reveal the next public-safe failure site.


Reminder: do not commit secrets.
