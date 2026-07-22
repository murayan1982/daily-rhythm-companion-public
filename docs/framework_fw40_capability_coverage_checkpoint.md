# FW4.0.0 capability coverage checkpoint

Day36 records the v1.9.0 FW4.0.0 capability coverage checkpoint after the LLM/text-chat smartphone Web proof was completed.

## Capability scope

The v1.9.0 public demo app scope tracks these FW4.0.0-facing capability groups:

```text
LLM / text chat
STT / voice input boundary
TTS / voice output boundary
Live2D / VTS motion boundary
```

## Day36 checkpoint

```text
v190_fw40_capability_coverage_status: text-chat-complete-boundary-capabilities-pending
v190_fw40_capability_llm_text_chat_status: completed
v190_fw40_capability_stt_voice_input_status: boundary-ready
v190_fw40_capability_tts_voice_output_status: boundary-ready
v190_fw40_capability_live2d_vts_motion_status: boundary-ready
v190_fw40_capability_completed_count: 1
v190_fw40_capability_boundary_ready_count: 3
v190_fw40_capability_pending_configured_evidence_count: 3
v190_fw40_capability_public_safe_evidence_only: True
v190_fw40_capability_next_focus: stt_voice_input
```

## Meaning

Day35 completed the LLM/text-chat smartphone Web proof chain. The remaining STT, TTS, and Live2D/VTS areas already have guarded DRC backend/Web UI boundary surfaces, but they are not counted as configured runtime success yet.

For the remaining capabilities, `boundary-ready` means:

```text
- backend boundary/status surface exists
- smartphone Web UI surface exists
- evidence can stay public-safe
- configured runtime execution is not yet verified
- smartphone Web configured-success evidence is still pending
```

## Source-tree smoke

```powershell
python scripts\smoke_framework_fw40_capability_coverage_checkpoint.py
```

The Day36 source-tree smoke does not start Flutter, open a browser, import AI Character Framework, create sessions, call `ask`, call `ask_stream`, call provider APIs, touch microphones, upload audio, generate audio, connect to VTube Studio, or dispatch Live2D/VTS motion.

## Public-safe evidence policy

The checkpoint may store only capability IDs, status labels, booleans, counts, and next-step labels.

Do not store:

```text
- prompt bodies
- response bodies
- raw audio
- generated audio payloads
- screenshots with private data
- provider payloads
- API key values
- authorization headers
- private absolute paths
- raw LAN IPs
- raw provider error payloads
```

## Next focus

The next capability focus is `stt_voice_input`: start with smartphone Web voice-input boundary evidence, then decide whether configured STT runtime execution belongs in v1.9.0 or should remain documented as a guarded future proof point.
