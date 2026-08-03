# Daily Rhythm Companion v3.0.0 RT-8d configured Android realtime acceptance

Updated: 2026-08-03

## Stage 1 candidate state

```text
RT-8: CURRENT / NOT_COMPLETED
RT-8c: COMPLETED / ACCEPTED / PUSHED
RT-8c acceptance-sync commit: b889ce884a928809125c473dcd2e8cd7a4c020ef
RT-8d: CURRENT / NOT_COMPLETED
RT-8d Stage 1: IMPLEMENTED / AWAITING_REVIEW
RT-8d Stage 1 baseline: b889ce884a928809125c473dcd2e8cd7a4c020ef
RT-8d Stage 1 surface: exact 9 files
RT-8d Stage 2: BLOCKED_PENDING_STAGE1_ACCEPTANCE / NOT_AUTHORIZED
RT-8d Stage 3: BLOCKED_PENDING_ANDROID_CONTROLS_A_H / NOT_AUTHORIZED
RT-8e: BLOCKED_PENDING_RT8D / NOT_AUTHORIZED
schema: drc.v3.rt8-platform-acceptance.2
accepted PC candidate source: fa39065130a4a4689c2e54195f231a5e79c62a35
private manifest read: false
private manifest modified: false
Android execution: false
commit / push: NOT_AUTHORIZED
```

## Purpose

RT-8d re-runs the accepted configured Android voice-turn and manual VTS
boundaries against one final RT-8 Android candidate source. Stage 1 adds only
credential-free operator tooling, focused synthetic tests, documentation, and
a static gate. It does not execute Android Controls A-H.

## Exact Stage 1 surface

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v300_goal_checklist_small_commit.md
docs/v300_rt8d_configured_android_realtime_acceptance.md
scripts/check_v300_rt8d_configured_android_realtime_acceptance.py
scripts/run_v300_rt8d_private_android_operator.py
backend/tests/test_v300_rt8d_private_android_operator.py
```

The last four files are new. Stage 1 changes no Backend runtime, Flutter
runtime, existing test, Android manifest, dependency, lockfile, vendor source,
version, release artifact, tag, or GitHub Release.

## Runner modes

```text
--check-inert
--preflight
--check-pc-transition
--record-android
```

`--check-inert` performs no Git inspection, private manifest access, private
configuration access, process startup, ADB operation, microphone operation,
HTTP/provider/network call, STT, streaming, TTS, playback, VTS, physical motion,
or manifest write.

`--preflight --expected-source-head <RT8D_STAGE1_COMMIT>` checks main,
HEAD/origin-main synchronization, clean tree, RT-8c/PC ancestry, and the fixed
target's exists/ignored/untracked/non-symlink metadata without reading content.

`--check-pc-transition` is a later separately authorized read-only mode. It
requires exact accepted schema-v2 stage `pc_windows`, PC candidate
`fa39065130a4a4689c2e54195f231a5e79c62a35`, Android placeholder, aggregate
`not_run`, and transition-aware ancestry. It writes nothing.

`--record-android` accepts only:

```text
PASS-ANDROID-A
PASS-ANDROID-B
PASS-ANDROID-C
PASS-ANDROID-D
PASS-ANDROID-E
PASS-ANDROID-F
PASS-ANDROID-G
PASS-ANDROID-H
ACCEPT-ANDROID
```

It then produces exact stage `android`, preserves the accepted PC section,
sets the current Android source, retains aggregate `not_run`, and keeps all
privacy/non-claim markers false. The update uses exclusive same-directory temp
creation, strict UTF-8 and 65536-byte limits, exact pre-write validation,
original-content recheck, atomic `os.replace`, no backup, and temp cleanup.
No manifest path/content/private value/operator input is printed.

## Fixed later chronology

```text
A -> B -> C -> D -> E -> F -> G -> H
```

- Android-A: default-off and configured-idle startup, no explicit execution.
- Android-B: one natural voice turn with bounded capture, cleaned private
  staging, real STT, transcript handoff, stream, real TTS, audible completion.
- Android-C: active-playback silent negative control, zero interruption.
- Android-D: one confirmed user-speech event and one DRC-local interruption.
- Android-E: old work remains inert, old audio does not resume, pending zero.
- Android-F: one recovery turn completes STT/stream/TTS/playback.
- Android-G: exactly one Android UI VTS Apply, 1/1/1, separate visible-motion
  confirmation, runtime `real_motion_executed: false`.
- Android-H: opt-out/reset/disposal/process/ADB/private-artifact cleanup with no
  additional request/provider/network/visible motion.

## Exact accepted Android counts

```text
natural_voice_turn_count: 1
silent_control_interruption_count: 0
confirmed_user_speech_event_count: 1
drc_local_interruption_count: 1
pending_voice_output_after_interruption: 0
recovery_voice_turn_count: 1
manual_vts_apply_count: 1
vts_commands_requested: 1
vts_commands_applied: 1
vts_commands_completed: 1
```

## Focused tests

The new focused file contains exactly eighteen credential-free tests covering
inert behavior, metadata preflight, target boundaries, transition-aware schema
and ancestry, fixed confirmations, exact Android generation, accepted-PC
preservation, atomic replacement failure, temp cleanup, and public-safe output.
They use synthetic manifests and temporary directories only.

## Stage 2 split

```text
Stage 2a: credential-free source/target metadata preflight
Stage 2b: private PC-manifest transition check, read-only
Stage 2c: configured Android Controls A-H
Stage 2d: fixed-token Android manifest transition
Stage 2e: strict Android manifest validation
```

Every substage requires separate authorization.

## Android transport boundary

The later run uses one selected physical Android device and explicit USB/reverse:

```text
adb reverse tcp:8000 tcp:8000
DRC_BACKEND_API_BASE_URL=http://127.0.0.1:8000
DRC_RT4_ENABLE_CONFIGURED_TEXT_STREAM=true
DRC_RT5_ENABLE_CONFIGURED_VOICE_OUTPUT=true
DRC_RT5F3_ENABLE_CONFIGURED_VOICE_TURN=true
DRC_RT7_ENABLE_CONFIGURED_VTS_MOTION=true
```

No ADB command is executed by Stage 1 tooling or its gate.

## Explicit non-claims and privacy

No all-device/iOS/Web/background-mic/provider-hard-cancel/Backend-hard-cancel/FW
real-flush/unified-runtime/automatic-motion/runtime-physical-proof/security or
release claim is added. No spoken text, transcript, generated response, raw
audio, identifier, provider data, credential, private endpoint/path/LAN value,
VTS private identity, screenshot, recording, raw log, exception, private
manifest content, or operator evidence enters tracked source or public output.

## Protected and unchanged

```text
backend/app/**
all existing backend/tests/**
app/**
vendor/**
scripts/validate_v300_rt8_private_operator_manifest.py
scripts/run_v300_rt8c_private_pc_windows_operator.py
docs/v300_rt8c_configured_pc_windows_realtime_acceptance.md
docs/operator_evidence_templates/**
.gitignore
backend/.env*
backend/env_profiles/**
dependency and lock files
platform declarations
assets and version metadata
release/**
release_notes/**
tags and GitHub Releases
Framework repository
operator_evidence/**
```

## Stage 1 verification

```powershell
python -m compileall -q backend scripts
python scripts\check_v300_rt8d_configured_android_realtime_acceptance.py
python -m pytest -q backend/tests/test_v300_rt8d_private_android_operator.py
python -m pytest -q backend/tests
cd app
flutter analyze
flutter test
cd ..
python scripts\check_v300_rt8d_configured_android_realtime_acceptance.py
git -c core.whitespace=cr-at-eol diff --check
git status --short
git diff --name-only
```

Expected: focused Backend 18 passed, Backend full 399 passed with one existing
warning, Flutter analyze PASS, Flutter full 500 passed, exact 9 files, private
manifest read/modified false, Android execution false.

## Stop rule

After verification, stop for exact diff/privacy review. Do not read or modify
the private manifest, start any runtime/device operation, commit, or push
without separate explicit approval.
