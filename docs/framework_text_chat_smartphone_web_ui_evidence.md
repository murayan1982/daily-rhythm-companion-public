# Framework text chat smartphone Web UI evidence

Day33 defines the public-safe evidence shape for verifying that a live FW4.0.0 text-chat reply can be seen from the DRC smartphone Web UI through the actual DRC backend API.

Day32 confirmed the backend adapter/API path:

```text
drc_adapter_live_reply_status: responded
drc_adapter_live_reply_source_mode: framework_text_chat_live_message
drc_chat_api_live_reply_body_hidden: True
drc_adapter_live_reply_next_step: verify-live-fw-response-through-smartphone-web-ui
```

Day33 does not add a new provider call to the normal source-tree check. It adds a manual smartphone Web UI evidence checklist and a renderer that records booleans and source labels only.

## Strict local UI setup

Use the same explicit gates as the Day32 live adapter smoke:

```text
DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_SMOKE=1
DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_SESSION_PREFLIGHT=1
DRC_FW40_ENABLE_LIVE_TEXT_CHAT_MESSAGE=1
FRAMEWORK_PROJECT_ROOT=<configured-framework-root>
```

Do not paste or commit provider API key values. Configure them only in the local operator environment or `backend/.env`.

Backend:

```powershell
cd <path-to-daily-rhythm-companion>\backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Flutter Web release build and static server:

```powershell
cd <path-to-daily-rhythm-companion>\app
flutter build web --release --dart-define=DRC_BACKEND_API_BASE_URL=http://<PC_LAN_IP>:8000
python -m http.server 18080 --bind 0.0.0.0 --directory build\web
```

Smartphone URL shape:

```text
http://<PC_LAN_IP>:18080
```

## Manual UI checklist

Verify the smartphone Web screen shows all of the following:

```text
- Backend status is ok.
- API base URL is visible and uses the local placeholder form in public notes.
- Advice result is visible.
- Post-advice chat UI is visible.
- Chat source is visible.
- Chat source mode is framework_text_chat_live_message.
- One live FW reply is visible in the chat UI.
- The reply is non-empty.
```

Do not record prompt bodies, response bodies, provider payloads, API key values, authorization headers, private absolute paths, or raw LAN IPs in public docs.

## Evidence renderer

Source-tree smoke:

```powershell
python scripts\smoke_framework_text_chat_smartphone_web_ui_evidence.py
```

Manual evidence rendering after the smartphone check:

```powershell
python scripts\smoke_framework_text_chat_smartphone_web_ui_evidence.py `
  --record-manual-ui-evidence `
  --backend-status-ok `
  --api-base-url-visible `
  --advice-result-visible `
  --post-advice-chat-visible `
  --chat-source-visible `
  --live-reply-visible `
  --response-non-empty `
  --body-hidden
```

Expected public-safe evidence shape:

```text
smartphone_web_ui_live_reply_evidence_status: verified
smartphone_web_ui_live_reply_source_mode: framework_text_chat_live_message
smartphone_web_ui_backend_status_ok: True
smartphone_web_ui_api_base_url_visible: True
smartphone_web_ui_advice_result_visible: True
smartphone_web_ui_post_advice_chat_visible: True
smartphone_web_ui_chat_source_visible: True
smartphone_web_ui_live_reply_visible: True
smartphone_web_ui_response_non_empty: True
smartphone_web_ui_body_hidden_in_evidence: True
smartphone_web_ui_next_step: record-v190-live-text-chat-smartphone-web-ui-evidence
```

## Day33 conclusion

Day33 prepares the final smartphone Web UI evidence path without adding a new provider call to normal checks. The live FW reply remains gated behind local operator opt-in, while public evidence records only safe booleans and labels.

