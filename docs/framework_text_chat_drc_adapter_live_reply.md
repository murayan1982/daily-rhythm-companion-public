# Framework text chat DRC adapter live reply

Day32 wires the verified FW4.0.0 live text-chat message path into the DRC post-advice chat adapter boundary.

## Day32 goal

Day31 verified the public-safe evidence shape after a strict local smoke reached a non-empty FW text-chat response:

```text
live_text_chat_message_evidence_status: verified
live_text_chat_message_evidence_smoke_status: responded
live_text_chat_message_evidence_next_step: wire-live-text-chat-response-through-drc-adapter
```

Day32 keeps that evidence and adds the app-facing adapter path:

```text
backend/app/services/framework_text_chat_drc_live_reply.py
backend/app/services/framework_text_chat_adapter.py
backend/app/services/post_advice_chat_service.py
scripts/smoke_framework_text_chat_drc_adapter_live_reply.py
```

## Gate policy

The DRC adapter may route one post-advice chat message through FW text chat only when all relevant local gates are explicitly enabled:

```text
DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_SMOKE=1
DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_SESSION_PREFLIGHT=1
DRC_FW40_ENABLE_LIVE_TEXT_CHAT_MESSAGE=1
FRAMEWORK_PROJECT_ROOT=<configured-framework-root>
```

If `DRC_FW40_ENABLE_LIVE_TEXT_CHAT_MESSAGE=1` is not set, the adapter returns `blocked-live-message-gate` and does not call the live reply service.

## Source-tree smoke

Default source-tree smoke injects a fake live reply service. It verifies DRC adapter/API wiring without importing AI Character Framework and without calling OpenAI, Gemini, Grok, ElevenLabs, Google Health, Fitbit, STT, TTS, Live2D/VTS, or provider APIs.

```powershell
python scripts\smoke_framework_text_chat_drc_adapter_live_reply.py
```

Expected public-safe lines include:

```text
drc_adapter_live_reply_status: responded
drc_adapter_live_reply_source_mode: framework_text_chat_live_message
drc_adapter_live_reply_configured_success: True
drc_chat_api_live_reply_source_mode: framework_text_chat_live_message
drc_chat_api_live_reply_body_hidden: True
```

The source-tree smoke does not print prompt bodies or response bodies.

## Strict local adapter smoke

Strict local mode routes one DRC post-advice chat message through the real adapter path. It may make one bounded `session.ask` call through FW4.0.0. The smoke hides the prompt body and response body in terminal output.

```powershell
$env:FRAMEWORK_PROJECT_ROOT="<path-to-daily-rhythm-companion>\vendor\AI-Character-Framework_v4.0.0"
$env:DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_SMOKE="1"
$env:DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_SESSION_PREFLIGHT="1"
$env:DRC_FW40_ENABLE_LIVE_TEXT_CHAT_MESSAGE="1"

python scripts\smoke_framework_text_chat_drc_adapter_live_reply.py --require-real-framework
```

Expected strict public-safe lines include:

```text
drc_adapter_live_reply_source_mode: framework_text_chat_live_message
drc_adapter_live_reply_response_received: True
drc_adapter_live_reply_response_text_length_present: True
drc_adapter_live_reply_response_non_empty: True
drc_chat_api_live_reply_body_hidden: True
```

## Day32 conclusion

Day32 connects the verified live text-chat response path to the DRC post-advice chat adapter/API boundary while preserving explicit opt-in gates. The app UI may receive the actual FW reply text in strict local mode, but smoke output and docs hide prompt bodies, response bodies, provider payloads, API key values, authorization headers, private paths, and raw LAN IPs.

The next step is `verify-live-fw-response-through-smartphone-web-ui`.

