# Daily Rhythm Companion v3.0.0 RT-5f4 configured local end-to-end and audible soft-barge-in acceptance

Status: **IMPLEMENTED / PRIVATE_OPERATOR_EXECUTION_PENDING**

```text
baseline DRC HEAD: ec6844c63b89803041e0b4e064d45c924e2d0438
RT-5f3 implementation: 75504424c37222234ea8a4314d01ce386ff92d23
FW v5.4.0: d313eb6acb643103fe25988720ebee5976a04f78
exact implementation surface: 7 files
private operator execution: NOT_AUTHORIZED
commit/push: NOT_AUTHORIZED
RT-5: CURRENT / NOT_COMPLETED
```

## Purpose

RT-5f4 freezes the private operator acceptance checkpoint for the already
accepted RT-5f3 configured integrated voice-turn graph. It adds no runtime,
route, dependency, permission, platform, version, or release behavior.

The later private run must establish, on one physical Android device and one
private local Backend/FW configuration:

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

The static candidate and gate do not execute or accept that flow.

## Exact seven-file surface

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v300_goal_checklist_small_commit.md
docs/v300_rt5f4_configured_local_end_to_end_acceptance.md
scripts/check_v300_rt5f4_configured_local_end_to_end_acceptance.py
```

Any changed or untracked path outside this set is a stop condition.

## Protected accepted runtime

The checkpoint relies on the committed RT-5f3 graph without modification:

```text
DRC_RT5F3_ENABLE_CONFIGURED_VOICE_TURN default false
DRC_RT4_ENABLE_CONFIGURED_TEXT_STREAM default false
DRC_RT5_ENABLE_CONFIGURED_VOICE_OUTPUT default false
Android/iOS-only configured binding factory
explicit session-local opt-in default off
explicit Start voice turn action
explicit Stop capture action
capture-phase speech activity disarmed
explicit-turn generation required for later speech arming
dedicated per-turn stream controller
dedicated queue/orchestrator/local player
metadata-only HomeScreen state
```

The production detector remains:

```text
record 6.2.1 PCM16 stream drained and dropped
mono 16 kHz
auto gain enabled
echo cancellation enabled
noise suppression enabled
100 ms amplitude interval
-24.0 dBFS threshold
3 consecutive samples
one event per arming generation
90 second maximum armed lifetime
```

These values are bounded implementation defaults, not universal acoustic
quality claims.

## Exact accepted claim if the later run passes

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
v3.0.0 release readiness
```

## Private operator prerequisites

Before any later execution:

```text
DRC HEAD/origin-main == ec6844c63b89803041e0b4e064d45c924e2d0438
DRC working tree clean
FW HEAD == d313eb6acb643103fe25988720ebee5976a04f78
FW working tree clean
physical Android device connected
microphone permission available
private ignored Backend/FW environments ready
Backend reachable from the device
configured integrated HomeScreen section visible
session opt-in default off
no microphone/network/provider work before explicit Start
```

The private Backend process may enable the already accepted framework
conversation, real-STT, stream, and real-TTS gates. The Flutter process may set
the three accepted compile-time switches and one private Backend URL. No actual
private value is written into this contract or any committed artifact.

## Operator sequence

### A. Natural full-turn control

```text
opt in
→ explicit Start voice turn
→ real capture
→ private spoken input
→ explicit Stop capture
→ private staging
→ real STT
→ incremental stream
→ completed terminal
→ real TTS
→ audible playback
→ natural completion
```

Required public-safe results:

```text
phase order includes capturing/staging/acquiringTranscript/streaming/voiceOutput/completed
turn generation increments once
real STT completes
transcript is nonempty but not recorded
exactly one stream starts
stream chunk count is positive
exactly one stream completes
real TTS completes
audible playback starts and completes naturally
last turn outcome is completed
interruption count does not change
pending voice output ends at zero
local stop retry required is false
```

This is the primary echo-only control: playback output alone must not trigger an
interruption.

### B. Silent-playback negative control

Start a second real turn and wait until dedicated playback is active. Do not
speak for at least 1500 ms.

Required result:

```text
playback remains active
interruption count unchanged
last speech outcome not interrupted
```

An interruption before deliberate operator speech is a stop condition.

### C. Real user-speech interruption

After the silent window, speak deliberately while dedicated playback remains
active.

Required result:

```text
speech source was armed
coordinator was in voiceOutput
one confirmed event forwarded
interruption count increments exactly once
last speech outcome is interrupted
local playback stop requested true
local playback stop succeeded true
final coordinator phase ready
pending voice output zero
local stop retry required false
audible playback stops within 3 seconds of speech
old audio does not resume during the following 5 seconds
late old turn work does not mutate final state
```

The 3-second bound is an operator acceptance bound for the local audible stop;
it is not a provider hard-cancel guarantee.

### D. Recovery turn

After the interrupted state is ready, start one new explicit voice turn and
complete it naturally.

Required result:

```text
turn generation increments
new capture starts
new real STT completes privately
new incremental stream completes
new real TTS/audible playback completes
last turn outcome completed
local stop retry required false
```

## Public-safe record schema

Only fixed booleans, typed outcomes, counts, and commit hashes may be retained:

```text
physical Android device used
configured integrated UI visible
opt-in default off
real microphone capture accepted
real STT completed
transcript nonempty
transcript exposed false
real incremental streaming accepted
stream chunk count positive
real TTS completed
natural audible playback accepted
echo-only natural control passed
silent playback control passed
user speech event confirmed
audible stop within 3 seconds
interruption count incremented once
last speech outcome interrupted
old audio resumed false
old turn state mutated false
recovery turn completed
private cleanup completed
DRC/FW trees clean after execution
```

Never retain or commit:

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

## Cleanup

The private run must stop Flutter and Backend processes, restore default-off
private gates, remove temporary capture/staging/generated-audio/operator files,
and end with clean DRC and FW working trees at the expected commits.

## Candidate verification

Run before commit while HEAD remains the baseline and this exact seven-file
candidate is uncommitted:

```powershell
python -m compileall -q backend scripts
python scripts\check_v300_rt5f4_configured_local_end_to_end_acceptance.py
python -m pytest -q backend/tests

cd app
flutter analyze
flutter test
cd ..

git diff --check
git status --short
```

The gate and synthetic regression commands read no private env or credential
and execute no real microphone, network, provider, STT, stream, synthesis,
playback, or speech activity.

## Stop rule

Stop if the surface differs; any app/Backend/FW/dependency/manifest/runtime
change appears; a default-off switch changes; Android physical execution is
replaced with a simulator; real STT/stream/TTS/playback is incomplete; echo or
silence triggers interruption; deliberate speech fails to stop playback; retry
is required; old audio resumes; old state mutates; the recovery turn fails;
cleanup fails; a tree remains dirty; or private data enters a tracked file.

## Candidate state

```text
RT-5f4: IMPLEMENTED / PRIVATE_OPERATOR_EXECUTION_PENDING
private operator execution: NOT_AUTHORIZED
operator acceptance: NOT_EXECUTED / NOT_CLAIMED
commit/push: NOT_AUTHORIZED
RT-5f: CURRENT / NOT_COMPLETED
RT-5: CURRENT / NOT_COMPLETED
```
