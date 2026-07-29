# Daily Rhythm Companion v3.0.0 RT-3d3 private real-STT operator boundary

Updated: 2026-07-29

```text
RT-3d3: REAL_OPERATOR_EXECUTION_COMPLETED / ACCEPTANCE_CANDIDATE
RT-3d2: IMPLEMENTED / ACCEPTANCE_CANDIDATE
RT-3d: REAL_STT_ACCEPTANCE_CANDIDATE_PENDING_APPROVAL
DRC baseline HEAD: cc5a970ed22e372fd41f08470d9526f7ee589f73
FW release: v5.4.0
FW tag commit: d313eb6acb643103fe25988720ebee5976a04f78
Real provider execution performed by the private operator checkpoint: True
Private operator acceptance candidate: True
Transport response status: 200
Transcript nonempty: True
Expected phrase match: True
Staged artifact cleanup complete: True
Provider payload exposed: False
Private path exposed: False
Raw audio exposed: False
Transcript exposed: False
Private operator evidence committed: False
Explicit operator approval: PENDING
Implementation commit: PENDING
```

## Purpose

RT-3d3 adds the smallest private DRC execution boundary that can run the
released FW v5.4.0 OpenAI real-STT executor after an operator explicitly opts
in. It does not expose a public API route and does not change the Flutter app.

The accepted RT-3d2c assembly service remains the only place that constructs
the Framework execution configuration, private credential object, real policy,
real client factory, provider adapter, and real executor. RT-3d3 reuses that
service instead of creating a DRC provider client.

## Execution boundary

The private operator request requires every gate below to be true:

```text
operator_handoff_enabled
allow_provider_execution
credentials_available
allow_provider_sdk_import
allow_provider_client_creation
allow_real_provider_execution
```

If any gate is false, the Framework root is not resolved, the private
credential builder is not called, and the staged artifact is preserved.

After all gates pass, one private staged WAV is consumed through:

```text
VoiceInputStagingStore.consume()
-> FrameworkVoiceInputOpenAIRealExecutorAssembler
-> VoiceInputAudioFormat.wav()
-> VoiceInputAudioSource.from_file_path()
-> VoiceInputRequest
-> OpenAIVoiceInputRealProviderExecutor.execute()
```

The private staged path is available only inside the scoped consumer. Once
consume begins, success and failure both remove the artifact.

## Private transcript boundary

A completed transcript is returned only through the private in-memory operator
result. The transcript field is excluded from dataclass `repr`. It must not be
printed, logged, persisted, included in screenshots, copied into provider
evidence, or committed.

The public-safe result contains only status, outcome, language, duration,
public error information, retryability, and boolean execution metadata.

## Exposure rejection

RT-3d3 rejects a Framework result that reports public exposure of any of the
following:

```text
private path
audio path
raw audio
provider payload or response
provider error body
provider request identifier
credential
private credential
transcript
microphone access
```

Provider exceptions are converted to a fixed public-safe DRC error and do not
copy the provider body or private path into the public message.

## Non-goals

RT-3d3 adds no:

- FastAPI route;
- Flutter change;
- AppConfig credential or real-execution environment flag;
- OpenAI dependency in DRC;
- custom DRC provider client or HTTP request;
- microphone access;
- committed credential, audio, payload, transcript, screenshot, LAN address, or
  operator evidence;
- version, release, tag, or publication change.

## Current verification

Before this document and the dedicated gate were applied:

```text
static boundary audit: PASS
focused Backend synthetic tests: 5 passed
Backend full tests: 163 passed, one existing warning
Flutter full tests: 200 passed
credential value read: False
OpenAI SDK imported: False
provider client created: False
network request executed: False
real provider execution: False
```

These checks prove only the DRC-to-FW public execution wiring with synthetic
objects. They are not real-STT evidence.

## Remaining operator work

Actual execution requires a separate explicit operator opt-in. The credential
handoff and audio input must remain outside the repository. The operator run
must not display or commit credential values, private paths, raw audio,
provider payloads, transcripts, screenshots, LAN addresses, or raw operator
evidence.

A public-safe acceptance decision may record only booleans and aggregate
status, such as whether SDK import, client creation, network execution, audio
read, real provider execution, transcript completion, cleanup, and redaction
succeeded. The private run is now complete and produced a public-safe acceptance
candidate. RT-3d3 remains pending explicit operator approval and the
implementation commit; no private execution evidence is added to Git.
