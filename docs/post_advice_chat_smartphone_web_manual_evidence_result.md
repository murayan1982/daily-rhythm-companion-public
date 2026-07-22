# Post-advice chat smartphone Web manual evidence result

This document records the Day13 smartphone Web post-advice chat manual verification result in a public-safe form.

## Result summary

```text
Result: mock-safe smartphone Web post-advice chat UI verified
```

## Runtime shape

```text
Runtime: release build static hosting
Backend URL shape: http://<PC_LAN_IP>:8000
Web URL shape: http://<PC_LAN_IP>:18080
```

The actual private LAN IP value is intentionally not recorded in this public-safe evidence file.

## Confirmed manual flow

The operator confirmed the following smartphone Web flow:

```text
1. DRC Home was visible in the smartphone browser.
2. Backend status: ok was visible.
3. API base URL was visible.
4. API base URL shape was http://<PC_LAN_IP>:8000.
5. Character selection was visible.
6. Mood selection was visible.
7. Advice action was usable.
8. Advice result was visible.
9. Post-advice Chat was visible.
10. 少し話す was visible and selected.
11. Chat session was visible.
12. Message input was usable.
13. User message was visible after sending.
14. Character response was visible.
15. Chat source was visible.
```

## Public-safe evidence summary

```text
Manual smartphone Web post-advice chat evidence:
- Runtime: release build static hosting
- Backend URL shape: http://<PC_LAN_IP>:8000
- Web URL shape: http://<PC_LAN_IP>:18080
- Smartphone browser opened DRC Home: yes
- Backend status shown in UI: ok
- API base URL shown in UI: http://<PC_LAN_IP>:8000
- Advice result visible: yes
- Post-advice Chat visible: yes
- 少し話す flow started: yes
- User message visible: yes
- Character response visible: yes
- Chat source visible: yes
- Result: mock-safe smartphone Web post-advice chat UI verified
```

## What this verifies

This verifies:

```text
- smartphone Web UI can load the release-built DRC app
- smartphone Web UI can reach the actual DRC backend API
- smartphone Web UI can show Backend status: ok
- smartphone Web UI can show the configured API base URL
- smartphone Web UI can create advice
- smartphone Web UI can start the post-advice chat flow
- smartphone Web UI can send a message
- smartphone Web UI can show user and character messages
- smartphone Web UI can show Chat source
```

## What this does not claim

This does not claim:

```text
- configured real LLM chat succeeded
- AI Character Framework text chat succeeded
- STT voice chat succeeded
- TTS playback succeeded
- Live2D/VTS motion succeeded
- Google Health real API access succeeded
```

Those remain later explicit opt-in verification targets.

## Non-exposure confirmation

This public-safe evidence file does not include:

```text
- real API keys
- OAuth client secrets
- access tokens
- refresh tokens
- authorization headers
- private credential paths
- raw provider payloads
- full provider debug traces
- private absolute paths
- private LAN IP values
```
