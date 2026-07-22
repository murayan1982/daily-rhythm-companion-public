# Framework text chat smartphone Web UI evidence record

Day34 records the v1.9.0 public-safe evidence that the DRC smartphone Web UI displayed a live FW4.0.0 text-chat reply through the actual DRC backend API.

Day33 manual smartphone Web UI evidence reported:

```text
smartphone_web_ui_live_reply_evidence_status: verified
smartphone_web_ui_live_reply_evidence_mode: manual-smartphone-web-ui
smartphone_web_ui_live_reply_source_mode: framework_text_chat_live_message
smartphone_web_ui_live_reply_source_mode_matches: True
smartphone_web_ui_backend_status_ok: True
smartphone_web_ui_api_base_url_visible: True
smartphone_web_ui_advice_result_visible: True
smartphone_web_ui_post_advice_chat_visible: True
smartphone_web_ui_chat_source_visible: True
smartphone_web_ui_live_reply_visible: True
smartphone_web_ui_response_non_empty: True
smartphone_web_ui_body_hidden_in_evidence: True
```

Day34 converts that verified shape into the v1.9.0 record:

```text
v190_smartphone_web_ui_live_reply_record_status: recorded
v190_smartphone_web_ui_live_reply_record_from_evidence_status: verified
v190_smartphone_web_ui_live_reply_record_source_mode: framework_text_chat_live_message
v190_smartphone_web_ui_live_reply_record_source_mode_matches: True
v190_smartphone_web_ui_backend_status_ok: True
v190_smartphone_web_ui_api_base_url_visible: True
v190_smartphone_web_ui_advice_result_visible: True
v190_smartphone_web_ui_post_advice_chat_visible: True
v190_smartphone_web_ui_chat_source_visible: True
v190_smartphone_web_ui_live_reply_visible: True
v190_smartphone_web_ui_response_non_empty: True
v190_smartphone_web_ui_body_hidden_in_evidence: True
v190_smartphone_web_ui_live_reply_record_next_step: prepare-v190-fw40-demo-evidence-summary
```

## Source-tree record smoke

```powershell
python scripts\smoke_framework_text_chat_smartphone_web_ui_evidence_record.py
```

## Optional manual record rendering

After a local smartphone Web UI check, an operator may render the public-safe record again:

```powershell
python scripts\smoke_framework_text_chat_smartphone_web_ui_evidence_record.py `
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

Do not record prompt bodies, response bodies, provider payloads, API key values, authorization headers, private absolute paths, raw LAN IPs, or raw provider error payloads.

## Day34 conclusion

Day34 records the v1.9.0 smartphone Web UI live FW reply evidence using only public-safe booleans and labels. It does not start Flutter, open a browser, import AI Character Framework, call `ask`, call `ask_stream`, or call provider APIs in normal source-tree mode.
