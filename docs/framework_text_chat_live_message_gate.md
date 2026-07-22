# Framework text chat live message gate

Day29 defines the explicit gate that must be opened before DRC sends a real
text-chat message through AI Character Framework v4.0.0.

Day28 verified the path through session creation only:

```text
session_created_evidence_status: created
session_created_evidence_session_created: True
session_created_evidence_has_session_info: True
session_created_evidence_next_step: design-explicit-live-text-chat-message-gate
```

Day29 adds the next boundary without executing it:

```text
DRC_FW40_ENABLE_LIVE_TEXT_CHAT_MESSAGE=1
```

The default gate status remains blocked:

```text
live_text_chat_message_gate_status: blocked
live_text_chat_message_gate_env_name: DRC_FW40_ENABLE_LIVE_TEXT_CHAT_MESSAGE
live_text_chat_message_gate_enabled: False
live_text_chat_message_gate_session_created_evidence_status: created
live_text_chat_message_gate_session_created: True
live_text_chat_message_gate_has_session_info: True
live_text_chat_message_gate_next_step: enable-explicit-live-text-chat-message-gate-locally
```

When local operator env is explicitly enabled, the gate can become ready:

```text
live_text_chat_message_gate_status: ready
live_text_chat_message_gate_env_name: DRC_FW40_ENABLE_LIVE_TEXT_CHAT_MESSAGE
live_text_chat_message_gate_enabled: True
live_text_chat_message_gate_next_step: run-explicit-live-text-chat-message-smoke
```

## Important boundary

Day29 does not call `ask`, `ask_stream`, OpenAI, Gemini, Grok, ElevenLabs,
Google Health, VTube Studio, STT, TTS, or Live2D/VTS runtime paths.

Day29 only records the public-safe rule for the next step:

1. session-created evidence must be verified;
2. provider env values must stay local and hidden;
3. `DRC_FW40_ENABLE_LIVE_TEXT_CHAT_MESSAGE=1` must be explicit; and
4. the actual live-message smoke must be a separate command.

## Source-tree smoke

```powershell
python scripts\smoke_framework_text_chat_live_message_gate.py
```

This source-tree smoke uses fake evidence only. It verifies `blocked`, `ready`,
and `session-not-ready` gate states without importing the real framework.

## Optional strict gate check

After local provider env readiness and Day28 session-created evidence are ready:

```powershell
$env:FRAMEWORK_PROJECT_ROOT="<path-to-daily-rhythm-companion>\vendor\AI-Character-Framework_v4.0.0"
$env:DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_SESSION_PREFLIGHT="1"

python scripts\smoke_framework_text_chat_live_message_gate.py --require-real-framework
```

With the live-message gate still off, expected status is:

```text
live_text_chat_message_gate_status: blocked
```

To intentionally prepare the next local live-message smoke, the operator can set:

```powershell
$env:DRC_FW40_ENABLE_LIVE_TEXT_CHAT_MESSAGE="1"
```

Day29 still does not send a message. The first actual message send belongs to a
separate future check.

