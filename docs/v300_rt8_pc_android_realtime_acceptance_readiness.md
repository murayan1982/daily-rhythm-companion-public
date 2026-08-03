# Daily Rhythm Companion v3.0.0 RT-8a PC/Android realtime acceptance readiness

Updated: 2026-08-03

## Candidate state

```text
RT-7: COMPLETED / ACCEPTED
RT-7e: COMPLETED / ACCEPTED / PUSHED
RT-7e Control E commit: 0440aa28fa7d1f49a8e15fd056de8735c83ce2ae
RT-8: CURRENT / NOT_COMPLETED
RT-8a: IMPLEMENTED / AWAITING_REVIEW
RT-8a baseline: 0440aa28fa7d1f49a8e15fd056de8735c83ce2ae
RT-8a surface: exact 7 documentation/static-gate files
readiness: READY_FOR_PLATFORM_APPROPRIATE_PC_WINDOWS_AND_ANDROID_REALTIME_ACCEPTANCE
RT-8b exact contract review: BLOCKED_PENDING_RT8A_ACCEPTANCE
RT-8b implementation: NOT_AUTHORIZED
RT-9: BLOCKED_PENDING_RT8
private configuration read: false
provider execution attempted: false
microphone used: false
network execution attempted: false
real motion executed: false
commit / push: NOT_AUTHORIZED
```

## Purpose

RT-8a freezes the final realtime acceptance-evidence scope after RT-1 through
RT-7 have been accepted. It resolves the ambiguous roadmap phrase "PC and
smartphone realtime acceptance evidence" into a platform-appropriate Windows
PC and Android smartphone matrix.

RT-8a is inventory and planning only. It changes no runtime or existing test
and executes no configured capability.

## Readiness classification

```text
READY_FOR_PLATFORM_APPROPRIATE_PC_WINDOWS_AND_ANDROID_REALTIME_ACCEPTANCE
```

This classification means:

```text
- accepted default-off PC-capable manual stream, TTS, app-owned motion, and VTS
  presentation paths exist;
- accepted default-off Android integrated voice-turn and manual VTS paths exist;
- accepted historical operator results define controls and non-claims;
- a private bounded final-evidence run can be designed without runtime changes.
```

It does not mean:

```text
READY_FOR_IDENTICAL_CROSS_PLATFORM_VOICE_RUNTIME
READY_FOR_PC_REAL_MICROPHONE_OR_STT
READY_FOR_AUTOMATIC_VOICE_TO_VTS_SYNCHRONIZATION
READY_FOR_FRAMEWORK_UNIFIED_REALTIME_RUNTIME
READY_FOR_RELEASE
```

## Source-derived platform boundary

Normal `app/lib/main.dart` independently assembles five optional runtime
families:

```text
configured realtime text streaming
configured terminal voice output
configured integrated voice turn
configured app-owned character motion
configured Framework VTS motion
```

Every runtime remains default-off and separately guarded.

`ConfiguredIntegratedVoiceTurnRuntime` is supported only when all of the
following are true:

```text
Flutter is not Web
platform is Android or iOS
DRC_RT5F3_ENABLE_CONFIGURED_VOICE_TURN=true
DRC_RT4_ENABLE_CONFIGURED_TEXT_STREAM=true
DRC_RT5_ENABLE_CONFIGURED_VOICE_OUTPUT=true
Backend base URL is valid
session-local opt-in and explicit UI actions occur
```

Therefore:

```text
PC Windows integrated real microphone/STT/soft-barge-in support: false
Android integrated real voice-turn support: true
Web integrated real voice-turn support: false
iOS source support: present but RT-8 operator acceptance: not in scope
```

The configured text-stream and VTS presentation runtimes use bounded HTTP
clients and are not limited by a mobile microphone plugin. The configured TTS
runtime owns explicit queue/process/flush behavior and local playback. These
paths are eligible for PC Windows evidence.

## Historical evidence reuse boundary

Historical acceptance remains authoritative for the implementation contracts,
controls, and allowed claims, but it does not replace RT-8 evidence against the
final RT-8 candidate source.

Relevant accepted checkpoints:

```text
RT-4f4:
- manual real incremental text streaming accepted;
- cooperative cancel accepted;
- provider-level hard cancel not claimed.

RT-5e:
- explicit real TTS accepted;
- natural audible local playback accepted;
- explicit DRC-local playback stop accepted;
- Backend/provider synthesis hard cancel and FW real flush not claimed.

RT-5f4:
- configured local Android real voice turn accepted;
- bounded microphone capture, private staging cleanup, real STT, transcript
  handoff, incremental stream, real TTS, audible playback, DRC-local soft
  interruption, inert old work, and recovery turn accepted;
- PC, iOS, all Android devices, provider hard cancellation, and unified FW
  realtime runtime not claimed.

RT-6f:
- configured local mock/app-owned character-motion presentation accepted.

RT-7e:
- manual configured local VTS execution accepted;
- Backend/Flutter real_motion_executed remains false;
- operator-visible physical motion is separate operator evidence.
```

## RT-8 exact split

```text
RT-8a  PC/Android realtime acceptance readiness inventory and exact split
RT-8b  Private operator manifest, validator, and runbook
RT-8c  Configured PC Windows realtime acceptance
RT-8d  Configured Android smartphone realtime acceptance
RT-8e  Aggregate cleanup and RT-8 acceptance synchronization
```

Each step requires a separate exact contract review and explicit authorization.
No later step is authorized by RT-8a.

## RT-8b target boundary

RT-8b may add credential-free tooling only:

```text
- ignored private operator manifest shape;
- deliberately non-secret example profile;
- network-free validator and source preflight;
- fixed runbook and public-safe marker schema;
- process, artifact, and private-value cleanup checklist;
- no Backend, Flutter, provider, microphone, network, TTS, playback, or VTS
  execution.
```

## RT-8c target PC Windows controls

PC evidence must use the normal Windows Flutter app and current default-off
runtime assembly. It must not claim the mobile-only integrated voice path.

```text
Control PC-A — inert/default-off startup
Control PC-B — manual real incremental stream completes
Control PC-C — manual cooperative cancel reaches cancelled terminal
Control PC-D — explicit real TTS completes audible local playback
Control PC-E — explicit local flush stops active dedicated playback
Control PC-F — explicit app-owned motion presentation completes
Control PC-G — exactly one manual VTS Apply completes and physical motion is
               operator-visible
Control PC-H — reset/opt-out/disposal and cleanup cause no additional execution
```

PC exact claims are limited to:

```text
manual text input
incremental stream and cooperative cancel
explicit TTS and DRC-local playback control
explicit app-owned motion presentation
explicit manual VTS execution with separate visual confirmation
```

## RT-8d target Android smartphone controls

Android evidence must use the normal smartphone app with all required flags,
private Backend/FW configuration, session-local opt-in, foreground execution,
and explicit operator actions.

```text
Control Android-A — inert/default-off startup
Control Android-B — natural full voice turn completes
Control Android-C — silent playback negative control does not interrupt
Control Android-D — real user speech triggers one DRC-local soft interruption
Control Android-E — old work remains inert after interruption
Control Android-F — explicit recovery voice turn completes
Control Android-G — exactly one manual VTS Apply completes and physical motion
                    is operator-visible
Control Android-H — reset/opt-out/disposal and cleanup cause no additional
                    execution
```

The Android claim remains DRC-local soft barge-in only:

```text
operation epoch invalidation
old active turn detachment
cooperative text-stream cancel request
app-owned pending queue clear
local player stop request and success
late old completion rejection
```

## Cross-platform evidence rules

```text
- PC and Android runs are separate bounded operator controls.
- A success on one platform does not imply success on the other.
- No spoken text, transcript, response text, raw audio, waveform, provider
  payload, private URL, token, path, LAN address, screenshot, raw log, or
  operator evidence file enters Git.
- Only public-safe booleans, counts, typed outcomes, fixed reason codes, commit
  hashes, and explicit operator confirmations may be recorded.
- Backend/Flutter real_motion_executed remains false even when physical VTS
  motion is visibly confirmed.
- Manual VTS Apply is not automatic conversation-state synchronization.
```

## Explicit non-claims

RT-8 must not claim:

```text
PC real microphone acceptance
PC real STT acceptance
PC speech-triggered soft barge-in
Web microphone acceptance
iOS operator acceptance
all Android devices
always-on or background microphone
automatic next-turn capture
provider-level LLM hard cancel
provider STT or TTS hard cancel
Backend HTTP hard cancel
FW real TTS queue flush
Framework unified realtime runtime
automatic voice/stream/TTS-to-VTS synchronization
automatic emotion/expression inference
physical VTS motion proven by Backend or Flutter response
universal VAD or echo-cancellation quality
production hosting or multi-user security readiness
v3.0.0 release readiness
```

## Exact RT-8a implementation surface

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v300_goal_checklist_small_commit.md
docs/v300_rt8_pc_android_realtime_acceptance_readiness.md
scripts/check_v300_rt8_pc_android_realtime_acceptance_readiness.py
```

## Protected and unchanged

```text
backend/**
app/lib/**
app/test/**
vendor/**
backend/.env.example
backend/requirements*.txt
app/pubspec.yaml
app/pubspec.lock
Android/iOS/Windows/Web platform declarations and generated registration
assets
version metadata
release/**
release_notes/**
fixed ZIPs
tags
GitHub Releases
Framework development checkout
private environment/token/endpoint/hotkey/model/evidence files
```

Historical RT-4 through RT-7 contracts and gates remain unchanged. Their
checkpoint-specific status markers are not mass-rewritten.

## RT-8a non-actions

```text
Backend startup: false
Flutter runtime startup: false
private configuration read: false
microphone permission requested: false
microphone capture: false
audio staged: false
real STT: false
LLM/provider execution: false
real TTS: false
local playback: false
HTTP/network request: false
VTS WebSocket opened: false
real physical motion executed: false
screenshot or recording captured: false
private operator manifest created: false
```

## Verification

Run before the RT-8a commit while HEAD and origin/main remain
`0440aa28fa7d1f49a8e15fd056de8735c83ce2ae`:

```powershell
python -m compileall -q backend scripts
python scripts\check_v300_rt8_pc_android_realtime_acceptance_readiness.py
python -m pytest -q backend\tests

cd app
flutter analyze
flutter test
cd ..

python scripts\check_v300_rt8_pc_android_realtime_acceptance_readiness.py
git -c core.whitespace=cr-at-eol diff --check
git status --short
git diff --name-only
```

Expected current regression baseline:

```text
Backend full: 345 passed, 1 existing warning
Flutter analyze: No issues found
Flutter full: 500 passed
exact RT-8a surface: 7 files
```

## Stop rule

After implementation and automated verification:

```text
- stop for exact diff and privacy review;
- do not create a private RT-8 manifest;
- do not start Backend or Flutter;
- do not enable any real-execution flag;
- do not perform PC or Android operator controls;
- do not commit or push without explicit approval;
- do not start RT-8b until RT-8a is accepted, pushed, and both working-tree and
  origin/main synchronization are verified.
```
