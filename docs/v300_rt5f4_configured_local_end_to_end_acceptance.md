# Daily Rhythm Companion v3.0.0 RT-5f4 configured local end-to-end and audible soft-barge-in acceptance

Status: **COMPLETED / ACCEPTED / PUSHED**

```text
checkpoint baseline: ec6844c63b89803041e0b4e064d45c924e2d0438
checkpoint commit: c84617e7ce07ecb1ca1605956eda7435b797c2fe
corrective commit / accepted DRC HEAD: bf17538f8b33aa504671289edda8f55c511fe77d
RT-5f3 implementation: 75504424c37222234ea8a4314d01ce386ff92d23
FW v5.4.0: d313eb6acb643103fe25988720ebee5976a04f78
exact checkpoint surface: 7 files
exact corrective surface: 5 files
acceptance sync surface: exact seven files
private operator execution: COMPLETED / ACCEPTED
operator acceptance: ACCEPTED
acceptance-sync commit/push: NOT_AUTHORIZED
RT-5f: COMPLETED / ACCEPTED
RT-5: COMPLETED / ACCEPTED
RT-6: NOT_STARTED / READY_FOR_EXACT_CONTRACT_REVIEW / NOT_AUTHORIZED
```

## Purpose

RT-5f4 accepts the configured local Android voice-turn path and the bounded
DRC-local soft-barge-in claim built on the accepted RT-5f3 dependency graph.
It records only public-safe outcomes and commit hashes. It does not retain or
publish private operator evidence.

The accepted path is:

```text
real bounded microphone capture
→ private staging and cleanup
→ FW v5.4.0 root-public real STT
→ app-visible final provider-neutral transcript handoff
→ FW root-public incremental text streaming
→ completed terminal
→ app-owned TTS queue
→ FW root-public real TTS
→ dedicated audible local playback
→ real user-speech-triggered DRC-local soft interruption
→ old work remains inert
→ next explicit real voice turn completes
```

## Exact committed surfaces

Checkpoint commit `c84617e7ce07ecb1ca1605956eda7435b797c2fe` changed exactly:

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v300_goal_checklist_small_commit.md
docs/v300_rt5f4_configured_local_end_to_end_acceptance.md
scripts/check_v300_rt5f4_configured_local_end_to_end_acceptance.py
```

Corrective commit `bf17538f8b33aa504671289edda8f55c511fe77d` changed exactly:

```text
app/lib/services/integrated_voice_turn_home_screen_binding.dart
app/lib/services/record_speech_activity_source.dart
app/test/integrated_voice_turn_home_screen_binding_test.dart
app/test/integrated_voice_turn_home_screen_widget_test.dart
app/test/record_speech_activity_source_test.dart
```

This acceptance sync changes the same seven documentation/static-gate files as
the checkpoint and changes no Flutter runtime, Backend, Framework, dependency,
lockfile, platform manifest, version, or release metadata.

## Accepted controls

```text
Control A — natural full-turn control: PASS / ACCEPTED
Control B — silent-playback negative control: PASS / ACCEPTED
Control C — real user-speech interruption: PASS / ACCEPTED
Control D — recovery turn: PASS / ACCEPTED
repeated Stop Capture corrective: REAL-DEVICE PASS
playback-time speech detection corrective: REAL-DEVICE PASS
```

Control A accepted real capture, private staging and cleanup, real STT,
incremental streaming, completed terminal-to-TTS handoff, real TTS, dedicated
audible playback, and natural completion.

Control B accepted that playback remained active during the deliberate silent
window without an interruption.

Control C accepted one confirmed real user-speech event during active playback,
one interrupted outcome, successful dedicated local-player stop, zero pending
voice output, no retry-required state, bounded audible stop, no old-audio
resume, and inert late old-turn work.

Control D accepted a new explicit recovery turn through real capture, real STT,
incremental streaming, real TTS, audible playback, and natural completion.

## Accepted correctives

The repeated Stop Capture corrective makes capture-session changes observable
to the HomeScreen binding so a second already-authorized turn exposes its Stop
Capture action without relying on a permission rebuild.

The playback-time speech detection corrective sets the production record
stream to `AudioInterruptionMode.none`, preserving the speech-activity stream
while dedicated local playback is active. The accepted detector remains mono
16 kHz PCM16 with auto gain, echo cancellation, noise suppression, bounded
threshold/consecutive-sample confirmation, and one event per arming generation.
These are bounded implementation defaults, not universal acoustic quality
claims.

## Accepted verification

```text
Backend full: 204 passed, 1 existing warning
Flutter analyze: No issues found
Flutter full: 411 passed
checkpoint exact surface review: passed
corrective exact surface review: passed
private-data exclusion review: passed
DRC HEAD/origin-main: bf17538f8b33aa504671289edda8f55c511fe77d
DRC working tree after push: clean
FW HEAD: d313eb6acb643103fe25988720ebee5976a04f78
FW working tree: clean
```

The dedicated checkpoint gate was run before the checkpoint commit. The later
acceptance-sync gate is bound to accepted HEAD `bf17538f8b33aa504671289edda8f55c511fe77d` and the
exact seven-file uncommitted acceptance-sync surface. After the acceptance-sync
commit, that gate is historical and is not rerun against the new HEAD.

## Exact accepted claim

```text
configured local Android real voice turn accepted
real bounded microphone capture accepted
private staging and cleanup accepted
FW root-public real STT accepted
in-memory final transcript handoff accepted
FW root-public incremental stream accepted
completed terminal-to-TTS handoff accepted
FW root-public real TTS accepted
dedicated audible playback accepted
real user-speech-triggered DRC-local soft barge-in accepted
old app-owned work remained inert
next explicit real voice turn completed
```

DRC-local soft barge-in means only:

```text
operation epoch invalidated before the first await
old active turn detached
cooperative text-stream cancel requested
app-owned pending queue cleared
dedicated local player stop requested and succeeded
late old STT/stream/TTS/playback completions ignored
```

## Explicit non-claims

RT-5f4 does not add or accept:

```text
provider-level LLM hard cancel
Backend HTTP hard cancel
provider STT hard cancel
provider TTS synthesis hard cancel
FW real TTS queue flush
Framework unified realtime runtime
always-on microphone
automatic next-turn capture
universal VAD accuracy
universal echo-cancellation effectiveness
fixed provider cancellation latency
all Android devices
iOS acceptance
PC acceptance
noisy-room acceptance
provider identity/model/payload acceptance
configured Live2D / VTS adapter execution
v3.0.0 release readiness
```

## Public-safe record boundary

The tracked record contains only fixed booleans, typed outcomes, counts, and
commit hashes. It never retains or commits:

```text
spoken phrase
transcript
generated response
audio or raw PCM
audio URL or artifact ID
staging/result/event/session/turn identifiers
amplitude values or sample sequence
provider/model identity
provider payload
credential
private env value
private path
LAN IP or private host
screenshot or screen recording
raw Backend/FW/Flutter log
operator evidence file
```

## Parent completion and next gate

```text
RT-5f4: COMPLETED / ACCEPTED / PUSHED
RT-5f: COMPLETED / ACCEPTED
RT-5: COMPLETED / ACCEPTED
RT-6: NOT_STARTED / READY_FOR_EXACT_CONTRACT_REVIEW / NOT_AUTHORIZED
RT-7: BLOCKED
RT-8: BLOCKED
RT-9: BLOCKED
```

RT-6 may proceed only to a separate exact contract review using the released
FW root-public provider-neutral mock-safe motion contract. This acceptance sync
does not authorize RT-6 implementation, motion runtime wiring, Live2D/VTS
execution, commit, or push.

## Acceptance-sync verification

Run before the acceptance-sync commit while HEAD remains the pushed corrective
commit and only the exact seven files are modified:

```powershell
python -m compileall -q backend scripts
python scripts\check_v300_rt5f4_configured_local_end_to_end_acceptance.py
python -m pytest -q backend/tests --basetemp .pytest-tmp -p no:cacheprovider

cd app
flutter analyze
flutter test
cd ..

Remove-Item -Recurse -Force .pytest-tmp
git -c core.whitespace=cr-at-eol diff --check
git diff --name-only
git diff --stat
git status --short
```

## Acceptance state

```text
RT-5f4: COMPLETED / ACCEPTED / PUSHED
private operator execution: COMPLETED / ACCEPTED
operator acceptance: ACCEPTED
checkpoint and corrective pushes: COMPLETED
acceptance-sync commit/push: NOT_AUTHORIZED
RT-5f: COMPLETED / ACCEPTED
RT-5: COMPLETED / ACCEPTED
RT-6: NOT_STARTED / READY_FOR_EXACT_CONTRACT_REVIEW / NOT_AUTHORIZED
```
