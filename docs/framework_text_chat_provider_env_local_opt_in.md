# Framework text chat provider env local opt-in

Day27 records the local operator step after Day26 provider env readiness reported:

```text
status: blocked
required_env_names: GOOGLE_API_KEY
env: GOOGLE_API_KEY set= False
```

The active blocker is now local provider env readiness for the vendored AI Character Framework v4.0.0 text chat session preflight.

## Public-safe rule

Do not commit, paste, print, or document actual API key values.

The DRC checks only record:

```text
provider env name
set=True|False
readiness status: blocked|ready
```

## Local process env option

Use this only on the local operator machine. Replace the placeholder locally and do not paste the value into chat or docs.

```powershell
$env:FRAMEWORK_PROJECT_ROOT="<repo-root>\vendor\AI-Character-Framework_v4.0.0"
$env:DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_SESSION_PREFLIGHT="1"
$env:GOOGLE_API_KEY="<local-secret-value>"

python scripts\smoke_framework_text_chat_provider_env_operator_opt_in.py --check-local --required-env GOOGLE_API_KEY
python scripts\smoke_framework_text_chat_session_creation_diagnosis.py --require-real-framework
```

After the local check, remove process env values if needed:

```powershell
Remove-Item Env:GOOGLE_API_KEY -ErrorAction SilentlyContinue
Remove-Item Env:DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_SESSION_PREFLIGHT -ErrorAction SilentlyContinue
Remove-Item Env:FRAMEWORK_PROJECT_ROOT -ErrorAction SilentlyContinue
```

## backend/.env option

`backend/.env` is gitignored. Copy `backend/.env.example` to `backend/.env` and fill only local values there.

```text
GOOGLE_API_KEY=
GEMINI_API_KEY=
OPENAI_API_KEY=
XAI_API_KEY=
```

Keep `CONVERSATION_ENGINE=mock` unless intentionally testing the configured framework path.

## Day27 conclusion

Day27 does not require a real provider key in source-tree mode. It documents the local opt-in path and adds a smoke check that proves readiness can move from `blocked` to `ready` without exposing values.

Day27 does not call `ask`, `ask_stream`, OpenAI, Gemini, Grok, ElevenLabs, Google Health, or VTube Studio. The optional strict session diagnosis may create a framework session only after local env readiness is configured, but it still must not send a text chat message or call provider APIs.
