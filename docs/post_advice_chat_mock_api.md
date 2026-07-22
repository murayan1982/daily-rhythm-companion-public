# Post-advice chat mock API

This document defines the mock-safe backend API added for the post-advice chat continuation flow.

## Purpose

The app originally intended to let the user continue into a lightweight character chat after receiving daily advice.

Day9 implements the first backend boundary for that flow without calling external providers.

## Implemented endpoints

```text
POST /chat/sessions
GET  /chat/sessions/{session_id}
POST /chat/sessions/{session_id}/messages
```

## Implemented models

```text
PostAdviceChatContext
ChatSessionCreateRequest
ChatSessionResponse
ChatMessage
ChatMessageRequest
ChatMessageResponse
ChatSource
```

## Session creation

`POST /chat/sessions` accepts advice context and creates a mock-safe active chat session.

The context can include:

```text
- character
- mood
- advice_message
- advice_basis
- advice_source
- report_handoff
- daily_record_id
```

The first response includes an assistant opening message so the UI can show that the chat continuation started.

## Message continuation

`POST /chat/sessions/{session_id}/messages` accepts a user message and returns a deterministic mock-safe character reply.

The reply uses:

```text
- selected character display name
- the previous advice message as context
- the user message
```

It remains short, safe, non-medical, and provider-free.

## Source metadata

Chat responses use:

```text
engine: mock
mode: post_advice_chat
```

This is intentionally not framework-backed success.

## Non-goals

Day9 does not implement:

```text
- Flutter post-advice chat UI
- provider-backed chat
- AI Character Framework text chat execution
- full transcript persistence
- STT voice chat
- TTS playback
- Live2D/VTS motion integration
```

## Future work

Next likely implementation steps:

```text
- add Flutter post-advice prompt
- add chat panel or screen
- wire POST /chat/sessions from the advice result
- wire POST /chat/sessions/{session_id}/messages from message input
- add DailyRecord / History relation flag if needed
- later add configured AI Character Framework text chat verification
```
