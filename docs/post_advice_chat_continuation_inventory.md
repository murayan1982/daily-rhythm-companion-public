# Post-advice chat continuation flow inventory

This document restores the originally intended post-advice chat continuation flow to the DRC roadmap.

## Purpose

DRC is a public demo app for AI Character Framework.

The app should not only produce a one-shot daily advice result. The intended experience also includes an optional character chat continuation after advice.

## Current implemented flow

Current implemented flow:

```text
sleep / mood / character
→ advice
→ optional DailyRecord save
→ History review
```

Current implemented surfaces:

```text
- Home sleep context
- Home mood choice
- Home character choice
- Home advice action
- Home advice result
- AdviceSource / fallback/source display
- DailyRecord save result
- History review
- report-informed advice/reflection when report_handoff is used
```

## Missing intended flow

Missing intended flow:

```text
advice result
→ post-advice prompt
→ "少し話す？" / "今日はここまで"
→ optional character chat continuation
→ optional save / History relation
```

This is not implemented yet.

Current app does not yet include:

```text
- post-advice chat prompt UI
- chat session ID
- chat message model
- chat message history
- /chat API
- character free-chat UI
- advice-context handoff into chat
- DailyRecord relation for chat continuation
```

## Intended UX

After an advice result is visible, the app should offer a lightweight choice:

```text
少し話す？
- 少し話す
- 今日はここまで
```

If the user chooses "少し話す":

```text
- open an inline chat panel or chat screen
- keep the selected character
- keep the selected mood
- keep the advice result as initial context
- keep report_handoff context if it was used
- allow one or more character replies
```

If the user chooses "今日はここまで":

```text
- keep the current advice result
- allow DailyRecord save
- do not start a chat session
```

## Future backend boundaries

Future backend model candidates:

```text
ChatSession
ChatMessage
PostAdviceChatContext
```

Future API candidates:

```text
POST /chat/sessions
POST /chat/sessions/{session_id}/messages
GET  /chat/sessions/{session_id}
```

Future request context should be able to include:

```text
- character_id
- mood
- advice_message
- advice_basis
- AdviceSource metadata
- report_handoff metadata when present
- DailyRecord ID when the advice has already been saved
```

## Mock-safe chat behavior

This section defines the future `mock-safe chat` path.

Mock-safe default must remain available.

Mock chat should be:

```text
- deterministic
- character-aware enough for demo use
- short and safe
- non-medical
- independent of external provider credentials
- clear when it is mock/fallback
```

## Framework-backed chat behavior

Configured framework chat should remain explicit opt-in.

Future framework-backed chat should use AI Character Framework text chat capability when configured.

Required distinction:

```text
mock chat != configured framework chat success
framework fallback != configured framework chat success
```

Configured success should require:

```text
- explicit opt-in
- framework configured
- backend API call
- Web UI visible chat response
- safe logs with no secrets or raw provider payloads
```

## DailyRecord and History relation

The first minimal version does not need to store a full chat transcript in DailyRecord.

Possible policy:

```text
- DailyRecord stores the advice result as before.
- DailyRecord may store a small chat_continued flag.
- DailyRecord may store a short safe summary in the future.
- Full transcript persistence is deferred until there is a clear product need.
```

History should avoid implying that free chat is medical advice or clinical analysis.

## Smartphone Web UI evidence requirements

Future post-advice chat verification should show:

```text
- advice result is visible
- post-advice prompt is visible
- "少し話す" option is visible
- "今日はここまで" option is visible
- choosing "少し話す" opens chat UI
- message input is visible
- character response is visible
- source/fallback state is understandable
- choosing not to chat leaves DailyRecord save/review flow usable
```

Configured framework chat success requires visible UI response from the configured path.

Fallback, unavailable, skipped, or mock states are useful visible states, but must not be counted as configured framework chat success.

## Non-goals for inventory

This inventory does not implement:

```text
- chat APIs
- chat UI
- persistence for full chat transcripts
- provider-backed chat calls
- STT/TTS voice chat
- Live2D/VTS chat motion
```

## Day8 conclusion

Post-advice chat continuation is part of the intended DRC experience and should be restored as an explicit v1.9.0+ feature path.

The next implementation step should be a mock-safe minimal post-advice chat API and UI boundary before provider-backed verification.
