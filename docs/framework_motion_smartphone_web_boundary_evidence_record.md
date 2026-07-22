# Live2D / VTS motion smartphone Web boundary evidence record

Day44 records the manual smartphone Web evidence shape for the guarded Live2D / VTS motion demo boundary.

The expected record output is public-safe:

```text
v190_motion_smartphone_web_boundary_record_status: recorded
v190_motion_smartphone_web_boundary_record_from_evidence_status: verified
v190_motion_smartphone_web_boundary_record_source_mode: motion_demo_boundary
v190_motion_smartphone_web_boundary_record_motion_send_blocked: True
v190_motion_smartphone_web_boundary_record_vts_connection_not_used: True
v190_motion_smartphone_web_boundary_record_live2d_runtime_not_loaded: True
v190_motion_smartphone_web_boundary_record_motion_payload_hidden_or_absent: True
v190_motion_smartphone_web_boundary_record_next_step: update-fw40-capability-coverage-after-motion-boundary-evidence
```

Manual smartphone Web recording command:

```powershell
python scripts\smoke_framework_motion_smartphone_web_boundary_evidence_record.py `
  --record-manual-ui-evidence `
  --backend-status-ok `
  --api-base-url-visible `
  --motion-section-visible `
  --motion-button-visible `
  --motion-request-sent `
  --motion-response-visible `
  --capability-status-visible `
  --checks-visible `
  --motion-send-blocked `
  --vts-connection-not-used `
  --live2d-runtime-not-loaded `
  --motion-payload-hidden-or-absent
```

Configured Live2D/VTS runtime execution remains a separate explicit opt-in decision. Day44 does not connect to VTube Studio, load Live2D runtime code, dispatch motion, store motion payload bodies, store VTS WebSocket payloads, store Live2D runtime state, call providers, start Flutter, open a browser, or call the backend.
