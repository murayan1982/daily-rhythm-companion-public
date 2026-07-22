# Post-advice chat Flutter UI

Day10 adds the Flutter Web UI path for the mock-safe post-advice chat API.

## Implemented flow

```text
advice result
→ Post-advice Chat section
→ 少し話す / 今日はここまで
→ mock-safe chat session
→ message input
→ character reply
```

## Flutter files

```text
app/lib/models/chat.dart
app/lib/services/backend_api_client.dart
app/lib/screens/home_screen.dart
app/test/widget_test.dart
```

## Backend API calls

```text
POST /chat/sessions
POST /chat/sessions/{session_id}/messages
```

## UI evidence

The Web UI now exposes:

```text
Post-advice Chat
少し話す
今日はここまで
Chat session
Chat source
メッセージ
送信
あなた
キャラクター
```

## Mock-safe behavior

Day10 remains provider-free.

```text
engine: mock
mode: post_advice_chat
```

The UI can prove that the post-advice chat continuation flow exists in the app, but it does not prove configured AI Character Framework text chat success.

## Non-goals

Day10 does not implement:

```text
- provider-backed chat
- AI Character Framework text chat execution
- STT voice chat
- TTS playback
- Live2D/VTS motion tied to chat
- persistent full transcript storage
```

## Smartphone Web evidence

On smartphone Web, Day10 evidence should show:

```text
- advice result is visible
- Post-advice Chat section is visible
- 少し話す starts a chat session
- a character opening message is visible
- user can send one message
- a mock-safe character reply is visible
- 今日はここまで leaves the DailyRecord / History flow usable
```
