# Framework text chat live message evidence

Day31 records the public-safe evidence shape after the Day30 live text-chat message smoke reaches a real response.

Day30 strict smoke confirmed this shape locally:

```text
live_text_chat_message_smoke_status: responded
live_text_chat_message_smoke_gate_status: ready
live_text_chat_message_smoke_gate_enabled: True
live_text_chat_message_smoke_session_created: True
live_text_chat_message_smoke_has_session_info: True
live_text_chat_message_smoke_provider_call_attempted: True
live_text_chat_message_smoke_response_received: True
live_text_chat_message_smoke_response_type: str
live_text_chat_message_smoke_response_non_empty: True
live_text_chat_message_smoke_failure_kind: none
```

The evidence renderer converts that to a smaller public-safe record:

```text
live_text_chat_message_evidence_status: verified
live_text_chat_message_evidence_smoke_status: responded
live_text_chat_message_evidence_gate_status: ready
live_text_chat_message_evidence_gate_enabled: True
live_text_chat_message_evidence_session_created: True
live_text_chat_message_evidence_has_session_info: True
live_text_chat_message_evidence_provider_call_attempted: True
live_text_chat_message_evidence_response_received: True
live_text_chat_message_evidence_response_type: str
live_text_chat_message_evidence_response_text_length_present: True
live_text_chat_message_evidence_response_non_empty: True
live_text_chat_message_evidence_failure_kind: none
live_text_chat_message_evidence_next_step: wire-live-text-chat-response-through-drc-adapter
```

## Public-safe boundary

The evidence may record booleans, status names, response type, and whether a response text length was present. It must not record prompt bodies, response bodies, raw provider payloads, authorization headers, API key values, token counts, private absolute paths, or raw LAN IPs.

Day31 source-tree mode does not call `ask`, `ask_stream`, OpenAI, Gemini, Grok, ElevenLabs, Google Health, Fitbit, or VTube Studio. It uses fake Day30 smoke results only.

Day31 strict local mode may re-run the Day30 live-message smoke path once and then render evidence. It requires `DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_SESSION_PREFLIGHT=1`, `DRC_FW40_ENABLE_LIVE_TEXT_CHAT_MESSAGE=1`, and a configured framework root. Prompt and response bodies are hidden.

## Commands

Source-tree check:

```powershell
python scripts\smoke_framework_text_chat_live_message_evidence.py
```

Strict local evidence smoke:

```powershell
$env:FRAMEWORK_PROJECT_ROOT="<path-to-daily-rhythm-companion>\vendor\AI-Character-Framework_v4.0.0"
$env:DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_SESSION_PREFLIGHT="1"
$env:DRC_FW40_ENABLE_LIVE_TEXT_CHAT_MESSAGE="1"

python scripts\smoke_framework_text_chat_live_message_evidence.py --require-real-framework
```

## Day31 conclusion

FW4.0.0 text chat is verified through one bounded live `session.ask` response in the local operator environment. The next DRC-side step is to wire the verified response path through the post-advice chat adapter/API boundary without exposing provider internals.

