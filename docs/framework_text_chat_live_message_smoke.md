# Framework text chat live message smoke

Day30 adds the first explicitly gated local smoke that may send one bounded text message through AI Character Framework v4.0.0.

The smoke is deliberately separated from Day29's gate evaluator:

```text
Day28: session-created evidence
Day29: live text-chat message gate only
Day30: live text-chat message smoke, behind the Day29 gate
```

## Files

```text
backend/app/services/framework_text_chat_live_message_smoke.py
scripts/smoke_framework_text_chat_live_message.py
docs/framework_text_chat_live_message_smoke.md
docs/internal/v190_smartphone_web_fw_demo_day30.md
scripts/check_v190_smartphone_web_fw_demo_day30.py
```

## Default source-tree behavior

The default smoke does not import AI Character Framework and does not call `ask`, `ask_stream`, or any provider API.

```powershell
python scripts\smoke_framework_text_chat_live_message.py
```

Expected default line:

```text
[smoke-framework-text-chat-live-message] OK
```

## Local live-message opt-in

A local operator may run the strict smoke only after setting the existing session preflight gate and the Day29 live message gate:

The strict local gates are:

```text
DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_SESSION_PREFLIGHT=1
DRC_FW40_ENABLE_LIVE_TEXT_CHAT_MESSAGE=1
FRAMEWORK_PROJECT_ROOT=<configured-framework-root>
```

```powershell
$env:FRAMEWORK_PROJECT_ROOT="<path-to-daily-rhythm-companion>\vendor\AI-Character-Framework_v4.0.0"
$env:DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_SESSION_PREFLIGHT="1"
$env:DRC_FW40_ENABLE_LIVE_TEXT_CHAT_MESSAGE="1"

python scripts\smoke_framework_text_chat_live_message.py --require-real-framework
```

Day30 may call one bounded `session.ask` only in this strict local mode.

## Public-safe output shape

The script prints statuses and shapes only:

```text
live_text_chat_message_smoke_status: blocked
live_text_chat_message_smoke_status: responded
live_text_chat_message_smoke_gate_status: ready
live_text_chat_message_smoke_provider_call_attempted: True
live_text_chat_message_smoke_response_received: True
live_text_chat_message_smoke_response_type: str
live_text_chat_message_smoke_response_text_length: <number>
live_text_chat_message_smoke_response_non_empty: True
live_text_chat_message_smoke_next_step: record-live-text-chat-message-evidence
```

Prompt and response bodies are hidden.

The smoke does not print API key values, provider payloads, authorization headers, private absolute paths, raw LAN IPs, token counts, or raw response text.

## Placeholder guard

If a provider env var looks like a placeholder, the live call is blocked before any provider call:

```text
live_text_chat_message_smoke_status: blocked-provider-env-placeholder
live_text_chat_message_smoke_failure_kind: provider-env-placeholder
live_text_chat_message_smoke_next_step: replace-placeholder-provider-env-locally
```

This is useful when a local shell accidentally contains a literal placeholder such as `<local-secret-value>`.

## Day30 conclusion

Day30 creates the public-safe live-message smoke boundary. It keeps normal checks source-tree only while allowing a clearly gated local operator run to verify the first FW4.0.0 text-chat response path.

