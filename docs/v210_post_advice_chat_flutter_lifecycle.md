# DRC v2.1.0 C-1c — Flutter post-advice chat lifecycle and recovery UI

Updated: 2026-07-24
Status: IMPLEMENTED / NOT_ACCEPTED
Current small commit: C-1c
Parent phase: C-1 CURRENT / NOT_COMPLETED

## Purpose

C-1c consumes the accepted C-1b provider-neutral chat lifecycle contract in Flutter. It makes active, bounded, unavailable, fallback, and terminal states visible without exposing provider payloads or requiring configured Framework execution.

## Accepted boundaries preserved

```text
POST_ADVICE_CHAT_TTL_SECONDS=1800
POST_ADVICE_CHAT_MAX_SESSIONS=100
POST_ADVICE_CHAT_MAX_TURNS=8
capacity eviction: LRU
Backend runtime changed by C-1c: false
```

C-1c does not alter Backend routing, lifecycle storage, terminal-reason caching, Framework adapters, or C-1b tests.

## Flutter contract

```text
- ChatLifecycle parses state, turn_count, turn_limit, can_send_message, and can_restart.
- ChatOutcome parses kind, can_continue, can_restart, user_message, and technical_code.
- ChatSessionProblem parses session_expired, session_evicted, session_not_found,
  and turn_limit_reached details.
- PostAdviceChatApiException carries a typed structured problem when the Backend
  returns FastAPI detail JSON, while malformed/legacy errors retain a fallback message.
- ChatSession and ChatMessageResponse keep constructor defaults and legacy JSON fallback.
- turn progress is presented as current / limit when known.
- mock, configured, fallback, unavailable, blocked, skipped, and pending remain distinct.
- terminal lifecycle/outcome states hide the message field and offer a direct restart.
- structured terminal HTTP failures clear the stale local session before restart.
- generic transient failures keep the current session so the user can retry.
- normal user copy is shown before a separate developer-details section.
```

## User-facing recovery behavior

```text
active/configured/mock/fallback:
  show messages and allow sending when both lifecycle and outcome allow continuation.

turn_limit_reached:
  show the final conversation state, disable sending, and offer a new conversation.

session_expired/session_evicted/session_not_found:
  clear the stale local session, show the structured user message, and offer restart.

unavailable/blocked/skipped:
  show the provider-neutral user message, disable sending, and offer restart.
```

## Mock-safe tests

```text
app/test/post_advice_chat_lifecycle_test.dart
  - structured lifecycle/outcome parsing
  - legacy payload compatibility
  - structured problem parsing
  - typed exception copy

app/test/post_advice_chat_lifecycle_widget_test.dart
  - turn-limit send disabling and restart
  - expired-session stale-state clearing and direct restart
  - unavailable outcome copy and restart
```

All focused tests use fake BackendApiClient implementations. They do not open OAuth, read local tokens, call wearable/health providers, call a real Framework/LLM, generate audio, use microphone input, or access Live2D/VTS.

## Verification

```powershell
python -m compileall -q backend scripts
python scripts\check_v210_post_advice_chat_current_behavior_inventory.py
python scripts\check_v210_post_advice_chat_backend_lifecycle.py
python scripts\check_v210_post_advice_chat_flutter_lifecycle.py
python scripts\check_v20x_fitbit_current_state_contract.py
python scripts\check_v20x_maintenance_baseline.py
python -m pytest -q backend/tests

cd app
flutter test test/post_advice_chat_lifecycle_test.dart test/post_advice_chat_lifecycle_widget_test.dart
flutter test
cd ..
```

Expected implementation checkpoint:

```text
focused Flutter tests: 7 passed
full Backend pytest: 110 passed
full Flutter test: 64 passed
real Framework execution: false
release records changed: false
```

These counts must be confirmed on the operator machine. Source presence or focused-test success alone does not accept C-1c or parent C-1.

## Non-release boundary

C-1c does not build a fixed ZIP, create a tag, publish a GitHub Release, complete T-1/V-1/R-1, or alter v2.0.0/v2.0.1 publication records.
