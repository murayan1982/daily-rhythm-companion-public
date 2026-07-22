# FW4.0.0 Live2D / VTS motion smartphone Web boundary evidence

Day43 records the guarded Live2D / VTS motion smartphone Web boundary evidence for v1.9.0.

The goal is to verify that DRC exposes the motion demo boundary through the backend API and Flutter Web UI without performing configured Live2D/VTS runtime execution.

Expected source-tree evidence:

```text
motion_smartphone_web_boundary_evidence_status: verified
motion_smartphone_web_boundary_evidence_mode: source-tree-boundary
motion_smartphone_web_boundary_source_mode: motion_demo_boundary
motion_smartphone_web_boundary_status_route_present: True
motion_smartphone_web_boundary_request_route_present: True
motion_smartphone_web_boundary_api_client_route_present: True
motion_smartphone_web_boundary_flutter_section_visible: True
motion_smartphone_web_boundary_flutter_button_visible: True
motion_smartphone_web_boundary_request_contract_metadata_only: True
motion_smartphone_web_boundary_motion_send_blocked: True
motion_smartphone_web_boundary_vts_connection_not_used: True
motion_smartphone_web_boundary_live2d_runtime_not_loaded: True
motion_smartphone_web_boundary_motion_payload_hidden_or_absent: True
motion_smartphone_web_boundary_public_safe_evidence_only: True
motion_smartphone_web_boundary_next_step: record-manual-smartphone-web-motion-boundary-evidence
```

Source-tree checks cover:

```text
GET /demo/motion/status
POST /demo/motion
BackendApiClient.submitMotionDemoRequest
Motion Demo section
Motion demo button
metadata-only request fields such as motion_event, character_id, expression_id, and requested_adapter_mode
safe response fields where motion_sent and vts_connection_used remain false
```

Configured Live2D/VTS runtime execution remains a separate explicit opt-in decision. Day43 does not connect to VTube Studio, load Live2D runtime code, dispatch motion/expression commands, call configured providers, import AI Character Framework runtime modules, create sessions, call ask, call ask_stream, synthesize speech, process audio, or upload audio.

Public-safe evidence must not contain VTS WebSocket payloads, Live2D runtime state, motion payload bodies, provider payloads, API key values, authorization headers, private paths, raw LAN IPs, raw screenshots, raw provider error payloads, prompt bodies, response bodies, transcript bodies, raw audio, generated audio, or text bodies beyond placeholder/metadata labels.

Manual smartphone Web evidence can be recorded later with:

```powershell
python scripts\smoke_framework_motion_smartphone_web_boundary_evidence.py `
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
