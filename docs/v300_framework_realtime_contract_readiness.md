# v3.0.0 RT-0b Framework public realtime contract readiness

Updated: 2026-07-26

```text
Parent phase: RT-0 CURRENT / NOT_COMPLETED
Small commit: RT-0b COMPLETED / ACCEPTED
Implementation state: COMPLETED / ACCEPTED
Acceptance date: 2026-07-26
Framework readiness decision: BLOCKED_FRAMEWORK_UPDATE_REQUIRED
RT-1 implementation authorization: BLOCKED_PENDING_RT-0c_AND_RELEASED_FW_UPDATE
DRC runtime changed: false
Framework runtime changed: false
Real provider execution: false
Network/provider call from the source-tree gate: false
```

## Purpose

RT-0b inspects the released, public AI Character Framework surface that DRC is
allowed to use for v3.0.0. It does not infer readiness from internal runtime
modules, presets, README feature claims, source-file discovery, or unreleased
candidate code.

The review answers three questions:

```text
1. Which released public Framework contracts already satisfy DRC needs?
2. Which contracts exist only partially and cannot safely support realtime DRC work?
3. Which public contracts are absent and must be implemented in Framework first?
```

RT-0b is docs/test-only. It does not modify DRC runtime, Framework runtime,
existing tests, version metadata, dependencies, permissions, or release records.

## Released Framework snapshot inspected

```text
Repository: murayan1982/ai-character-framework
Released line: v5.0.0
Inspected public-source commit: 6494da306015c4f714f869b43e773ba51a2478a2
Commit message: v5.0.0release
Release implementation commit: a2df57e2e8ed226b7c9e9c72ed68a79c8a48b6db
Release scope: Public Voice Output / TTS Boundary Foundation
```

Public files inspected at the released commit:

```text
README.md
framework/__init__.py
framework/facade.py
framework/audio/__init__.py
framework/audio/voice_output.py
```

Packaging files checked at the released commit:

```text
pyproject.toml: absent
setup.py: absent
setup.cfg: absent
```

The absence of packaging metadata is treated as evidence only for the inspected
release snapshot. RT-0b does not claim that a later unreleased branch or local
checkout has the same state.

## Public export inventory

The released `framework` package exports these session factories:

```text
create_text_chat_session
create_voice_output_session
```

It exports these app-facing session and result types:

```text
TextChatSession
TextChatSessionInfo
TextChatSessionEvent
TextChatStateChange
VoiceOutputSession
VoiceOutputSessionInfo
VoiceOutputRequest
VoiceOutputResult
```

The released root public export does not include:

```text
create_voice_input_session
create_stt_session
create_realtime_session
RealtimeSession
RealtimeEvent
RealtimeCapabilities
create_motion_session
create_vts_session
MotionEvent
```

Internal Framework voice, STT, runtime, plugin, or VTS modules do not count as
public host-app contracts and cannot unblock DRC.

## Readiness classifications

```text
READY_CURRENT_USE
  Released public contract is sufficient for the already accepted v2.1.0 use.

PARTIAL_BLOCKING
  A released public contract exists, but its semantics are insufficient for the
  coordinated v3 realtime runtime.

MISSING_BLOCKING
  No released public contract exists for the required capability.

DEFECT_BLOCKING
  Released public documentation and implementation disagree at the host-app
  boundary and must be stabilized before a new integration depends on it.
```

## Readiness matrix

| Public contract | Released evidence | Classification | DRC consequence |
| --- | --- | --- | --- |
| Full-response text chat | `TextChatSession.ask()` returns one string | READY_CURRENT_USE | Existing v2.1.0 chat remains valid; this alone does not provide realtime orchestration. |
| Incremental text streaming | `ask_stream()` yields string chunks and emits small dictionary events | PARTIAL_BLOCKING | No typed chunk/final/cancel outcome, sequence ID, correlation ID, or provider-neutral terminal reason. |
| Text state/events | `responding`, `interrupted`, `error`, then return to `idle` | PARTIAL_BLOCKING | Not a unified listening/transcribing/thinking/responding/speaking lifecycle. |
| Provider-level cancellation | `interrupt()` sets a local flag; documentation says hard cancellation is not provided | MISSING_BLOCKING | DRC cannot guarantee active LLM cancellation or bounded barge-in. |
| Single voice-output artifact | `VoiceOutputRequest` / `VoiceOutputResult` and one `create_output()` call | READY_CURRENT_USE | Sufficient for accepted v2.1.0 one-shot TTS handoff only. |
| TTS queue / cancel / flush | No public queue, utterance ID, cancel, flush, or interruption operation | MISSING_BLOCKING | DRC cannot coordinate queued speech or stop provider work during barge-in. |
| Voice-input / STT session | No released root public factory or session type | MISSING_BLOCKING | RT-2/RT-3 cannot integrate real voice input through a supported Framework boundary. |
| Unified realtime session | No released public realtime session, event stream, or lifecycle contract | MISSING_BLOCKING | RT-1 cannot define an adapter against a released Framework runtime. |
| Motion-event / VTS adapter | No released root public motion or VTS factory/session/event type | MISSING_BLOCKING | RT-6/RT-7 cannot send real motion through a supported Framework boundary. |
| Capability reporting | Text and voice-output session info expose separate booleans/status | PARTIAL_BLOCKING | DRC lacks one provider-neutral capability snapshot for voice input, streaming, hard cancel, queue control, motion, and close. |
| Typed results and public errors | Voice output has a dataclass result; text chat returns strings/generator chunks and broad exceptions | PARTIAL_BLOCKING | DRC would still need exception-message classification and ad-hoc normalization. |
| Installable SDK import | Release setup is clone + requirements; standard packaging metadata is absent | MISSING_BLOCKING | DRC still requires checkout-root/import-context ownership rather than a stable installed package. |
| Stable project-root-independent factory | Voice output exposes `project_root` and `artifact_dir`; DRC text integration inspects signatures | PARTIAL_BLOCKING | Host integration remains coupled to source-tree layout and evolving keyword names. |
| Session close/dispose | Text info says `supports_close=False`; voice output `close()` is a no-op | PARTIAL_BLOCKING | A long-lived realtime adapter has no uniform resource lifecycle contract. |
| Opaque voice artifact handoff | `audio_url` or `audio_artifact_ref` is public and provider-neutral | READY_CURRENT_USE | Preserve and extend this boundary; do not regress to provider paths or raw audio internals. |
| Public docs/API conformance | Released README calls `session.speak(...)`; implementation exposes `create_output(...)` and no `speak()` method | DEFECT_BLOCKING | Public method naming and examples must be synchronized before factory/method contracts are treated as stable. |
| Provider configuration responsibility | Voice output keeps provider details in FW; text integration still exposes provider/model selection and DRC owns env diagnosis/workarounds | PARTIAL_BLOCKING | Provider-neutral configuration and safe public error codes need to be consistent across all session types. |

## Text-chat public boundary findings

`TextChatSessionInfo` advertises:

```text
supports_streaming=True
supports_reset=True
supports_interrupt=True
supports_events=True
supports_close=False
supports_voice_input=False
supports_voice_output=False
supports_live2d=False
```

The current streaming boundary is useful but not sufficient for DRC v3:

```text
- chunks are plain strings;
- events carry untyped dictionaries;
- there is no request/turn correlation ID;
- no typed final result distinguishes completed, cancelled, interrupted, failed,
  timed out, disconnected, or provider-unavailable;
- interrupt does not hard-cancel the provider request;
- error events include raw exception text and type names.
```

This is classified as a valid v4 text integration boundary and a partial v3
realtime prerequisite, not as a failed existing feature.

## Voice-output public boundary findings

The v5 voice-output boundary correctly keeps provider-specific voice IDs, keys,
model IDs, request parameters, and SDK calls outside the host request. It also
provides an opaque Web-oriented handoff through `audio_url` or
`audio_artifact_ref`.

The public session remains one-shot:

```text
create_output(request) -> VoiceOutputResult
close() -> None
```

The released contract does not expose:

```text
utterance ID
queue position
queued/started/completed event stream
cancel one utterance
cancel current utterance
flush queue
interrupt acknowledgement
provider synthesis cancellation status
barge-in transition
```

The v2.1.0 DRC playback stop operation therefore remains a local Flutter audio
stop. It must not be reported as Framework synthesis cancellation.

## Public documentation mismatch

At the inspected release commit:

```text
README example: session.speak(VoiceOutputRequest(...))
implementation: VoiceOutputSession.create_output(...)
```

The complete inspected `VoiceOutputSession` implementation has no public
`speak()` method. RT-0b records this as a public docs/API conformance defect. DRC
must not add method-probing compatibility for the new realtime path; Framework
should publish one stable method name and update examples/checks together.

## Existing DRC integration-cost evidence

The accepted DRC v2.1.0 adapters currently compensate for source-tree and public
contract instability with:

```text
FRAMEWORK_ROOT / FRAMEWORK_PROJECT_ROOT configuration
sys.path insertion and restoration
sys.modules removal and restoration
importlib cache invalidation
temporary CWD changes
factory signature inspection
multiple candidate public module/factory/method names
DRC-owned provider-env placeholder diagnosis
raw exception sanitization and classification
```

These workarounds allowed v4/v5 integration to function, but they are not an
acceptable foundation for the v3 realtime runtime. RT-0b prohibits extending
this compatibility style into voice input, realtime sessions, cancellation, or
motion.

## Framework feedback inventory

The existing real-app integration feedback remains active:

```text
FW-F1  Eliminate host temporary CWD, sys.path, sys.modules, and import-cache manipulation.
FW-F2  Provide an installable SDK and project-root-independent public boundary.
FW-F3  Stabilize public factory and method signatures; keep docs/examples/checks conformant.
FW-F4  Add typed public results, provider-neutral error codes, and safe terminal outcomes.
FW-F5  Add one provider-neutral runtime capability snapshot.
FW-F6  Keep provider config/env aliases, validation, and ownership inside Framework.
FW-F7  Define uniform session close/dispose and resource cleanup semantics.
FW-F8  Preserve and strengthen the opaque voice artifact contract.
```

RT-0b adds realtime-specific feedback:

```text
FW-F9   Add a public voice-input/STT session with typed request, transcript, and terminal outcomes.
FW-F10  Add a unified realtime lifecycle/event contract and typed streaming chunks/results.
FW-F11  Add provider-level cancellation plus TTS queue/cancel/flush and barge-in acknowledgement.
FW-F12  Add a public motion-event / Live2D / VTS adapter contract with capability and acknowledgement states.
```

RT-0c will organize these findings into the DRC-to-FW handoff order. RT-0b does
not modify the Framework repository or choose a Framework version number.

## RT-0b decision

```text
Framework v5.0.0 public readiness for DRC v3.0.0: BLOCKED_FRAMEWORK_UPDATE_REQUIRED
RT-1 authorization: BLOCKED_PENDING_RT-0c_AND_RELEASED_FW_UPDATE
```

The block is caused by missing released public contracts, not by failure of the
accepted v4 text-chat or v5 one-shot voice-output boundaries.

DRC may proceed only with RT-0c documentation and handoff planning. It may not
start microphone capture, realtime transport, STT integration, streaming
orchestration, hard cancellation, TTS queueing, barge-in, or motion execution.

## RT-0b change surface

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v300_goal_checklist_small_commit.md
docs/v300_framework_realtime_contract_readiness.md
scripts/check_v300_framework_realtime_contract_readiness.py
```

## Explicit non-change surface

```text
backend/app/**
backend/tests/**
app/lib/**
app/test/**
app/pubspec.yaml
app/android/**
app/ios/**
backend/.env.example
backend/app/version.py
docs/v300_realtime_current_behavior_inventory.md
scripts/check_v300_realtime_current_behavior_inventory.py
release_notes/**
historical v2.x checklists and release records
AI Character Framework repository/runtime
release ZIPs, tags, GitHub Releases, and private operator evidence
```

## Verification

Run from the DRC repository root:

```powershell
python -m compileall -q backend scripts
python scripts\check_v300_realtime_current_behavior_inventory.py
python scripts\check_v300_framework_realtime_contract_readiness.py
python -m pytest -q backend/tests

cd app
flutter test
cd ..

git diff --check
git status --short
```

Accepted RT-0b check summary:

```text
v300_framework_realtime_contract_readiness_status: completed-accepted
v300_framework_release_snapshot: v5.0.0@6494da306015c4f714f869b43e773ba51a2478a2
v300_framework_public_readiness: blocked-framework-update-required
v300_framework_required_contracts_ready: False
v300_rt0b_drc_runtime_changed: False
v300_rt0b_existing_tests_changed: False
v300_rt0b_framework_runtime_changed: False
v300_rt0b_real_provider_execution: False
v300_rt1_authorization: blocked-pending-rt0c-and-released-fw-update
```

## Acceptance boundary

RT-0b acceptance requirements and results:

```text
- released Framework snapshot/public exports diff review: passed;
- readiness classifications and documentation mismatch acceptance: passed;
- compileall: passed;
- RT-0a and RT-0b source-tree gates: passed;
- Backend pytest: 110 passed;
- Flutter test: 103 passed;
- git diff --check: passed;
- runtime/non-change claims: confirmed;
- explicit operator approval: received.
```

Acceptance of RT-0b does not unblock RT-1. RT-0c must first accept the handoff
boundary, and a later released Framework version must provide the required
public contracts before DRC implementation can be authorized.
