# Daily Rhythm Companion v3.0.0 RT-5f1 app-visible real-STT contract

Updated: 2026-07-31

## Status

```text
RT-5: CURRENT / NOT_COMPLETED
RT-5f0: COMPLETED / ACCEPTED / PUSHED
RT-5f1: COMPLETED / ACCEPTED / PUSHED
RT-5f1 implementation commit: daca3a68672eb3106e861278ebb65612380140ed
DRC implementation baseline: e4ecd46487b43e20b359ce350fc90b5e0ac36d95
FW v5.4.0: d313eb6acb643103fe25988720ebee5976a04f78
commit/push: completed
```

RT-5f1 created and accepted the first normal app-visible, provider-neutral transcript source at implementation commit `daca3a68672eb3106e861278ebb65612380140ed` without wiring it into normal startup or HomeScreen. The accepted implementation remains strictly default-off and uses only the FW v5.4.0 root public API.

## Functional boundary

```text
BackendVoiceInputStagedArtifact
→ POST /demo/voice-input/transcript
→ host-owned private credential builder
→ accepted FW root-public real executor assembly
→ single-use staged WAV consume
→ bounded final transcript response
→ BackendProviderNeutralTranscriptProvider
→ ProviderNeutralTranscriptResult
→ existing RealtimeTextStreamTranscriptHandoff compatibility
```

RT-5f1 does not add microphone capture wiring, automatic text-stream start,
automatic TTS, speech activity, barge-in, HomeScreen controls, or operator
acceptance.

## Backend endpoint

```http
POST /demo/voice-input/transcript
Content-Type: application/json
```

The staging ID is never placed in the URL path or query string.

### Request

```json
{
  "staging_id": "0123456789abcdef0123456789abcdef",
  "foreground_opt_in": true,
  "language": "ja",
  "duration_ms": 1000
}
```

Rules:

```text
staging_id: exactly 32 lowercase hexadecimal characters
foreground_opt_in: must be true
duration_ms: 1..15000 when present
language: null or at most 32 characters
provider/model/credential/path/payload fields: forbidden by contract
```

Malformed staging IDs are rejected by a fixed public-safe 400 problem rather
than the default framework validation body, preventing input echo in the error
response.

### Success response

```json
{
  "accepted": true,
  "request_state": "final_transcript_ready",
  "result_id": "abcdef0123456789abcdef0123456789",
  "text": "final transcript",
  "is_final": true
}
```

The response contains exactly five keys. It does not include provider, model,
confidence, provider request ID, staging ID, private path, audio URL, payload,
credential, or debug metadata.

Required response headers:

```text
Cache-Control: no-store
Pragma: no-cache
X-Content-Type-Options: nosniff
```

### Public-safe problems

The endpoint exposes only allow-listed public codes and fixed messages:

```text
voice_input_transcript_opt_in_required
voice_input_transcript_busy
voice_input_transcript_request_invalid
voice_input_transcript_artifact_unavailable
voice_input_transcript_unavailable
```

Provider exception text, response body, staging ID, transcript, credential,
private path, model, and provider name are not concatenated into public errors.

## Execution gates

Every gate below must pass before the staged artifact is consumed:

```text
CONVERSATION_ENGINE=framework
VOICE_INPUT_DEMO_ENABLED=1
VOICE_INPUT_ADAPTER_MODE=framework
VOICE_INPUT_REAL_STT_ENABLED=1
foreground_opt_in=true
private OPENAI_API_KEY value available to the host-only builder
configured FW root exists and exposes framework/__init__.py
process-wide real-STT execution slot acquired
```

A failed gate leaves the staged artifact available for an explicit later
attempt. The busy path returns immediately and does not consume the artifact.

## Credential boundary

`PrivateVoiceInputCredentialSource` reads the private environment value only
when the FW credential type is already available and assembly is about to
occur. It returns one instance of the released
`OpenAIVoiceInputPrivateCredential` type.

The raw value is not:

```text
stored in AppConfig
stored on the credential source
returned from a DRC public method
placed in a request or response
included in repr/str
logged or persisted
read by Flutter
```

DRC does not import the OpenAI SDK and does not create an OpenAI client.

## Framework boundary

The adapter reuses:

```text
FrameworkVoiceInputOpenAIRealExecutorAssembler
OpenAIVoiceInputPrivateCredential
OpenAIVoiceInputRealProviderPolicy
OpenAIVoiceInputRealClientFactory
OpenAIVoiceInputProviderAdapter
OpenAIVoiceInputRealProviderExecutor
VoiceInputAudioFormat
VoiceInputAudioSource
VoiceInputRequest
```

All Framework symbols are obtained through the root public package context. No
FW internal module is imported by the new DRC implementation.

The private path exists only inside `VoiceInputStagingStore.consume()`. The
single-use cleanup behavior remains owned by the existing staging store.

## Result validation

The adapter accepts only a completed result with non-empty text and no unsafe
public metadata flags.

Unsafe true flags include:

```text
private_path_exposed
audio_path_exposed
raw_audio_exposed
provider_payload_exposed
provider_response_exposed
provider_error_body_exposed
request_id_exposed
credential_exposed
private_credential_exposed
microphone_accessed
```

Transcript text is trimmed and bounded to 4096 Unicode code points. A 32-character
lowercase hexadecimal result ID is generated by DRC rather than copied from a
provider response.

## Flutter provider

`BackendProviderNeutralTranscriptProvider` accepts:

```text
baseUrl
BackendStagedArtifactTaker
ForegroundVoiceInputOptIn
optional injected http.Client
optional language
bounded maximumResponseBytes
```

Processing order:

```text
disposed/closed check
→ in-flight check
→ foreground opt-in check
→ response-bound configuration check
→ take staged artifact exactly once
→ POST one JSON request
→ reject redirect
→ read bounded response
→ require HTTP 200 and Cache-Control no-store
→ require exact five-key response shape
→ validate final state, result ID, and transcript bound
→ return ProviderNeutralTranscriptResult
```

No automatic retry occurs. A duplicate invocation while a request is active
does not take another artifact and does not send another request.

The provider object retains no transcript, result ID, staging ID, response body,
provider payload, or raw exception after completion.

## Exact seventeen-file implementation surface

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v300_goal_checklist_small_commit.md
docs/v300_rt5f1_app_visible_real_stt_contract.md
scripts/check_v300_rt5f1_app_visible_real_stt_contract.py
backend/.env.example
backend/app/config.py
backend/app/models/voice_input_demo.py
backend/app/api/voice_input_demo.py
backend/app/services/private_voice_input_credential_source.py
backend/app/services/framework_voice_input_app_transcript.py
backend/tests/test_framework_voice_input_app_transcript.py
backend/tests/test_voice_input_real_transcript_api.py
app/lib/services/backend_provider_neutral_transcript_provider.dart
app/test/backend_provider_neutral_transcript_provider_test.dart
```

## Explicit non-change surface

```text
FW repository
backend private .env files
backend/app/main.py
voice_input_staging_store.py
private real-STT operator adapter
real-executor assembly implementation
app/lib/main.dart
app/lib/screens/home_screen.dart
provider-neutral transcript model
existing transcript handoff implementation
TTS queue/output files
speech activity or barge-in files
pubspec.yaml and pubspec.lock
platform wrappers
version and release metadata
```

## Verification

Credential-free and provider-free checks:

```powershell
python -m compileall -q backend scripts
python scripts\check_v300_rt5f1_app_visible_real_stt_contract.py
python -m pytest -q backend/tests/test_framework_voice_input_app_transcript.py
python -m pytest -q backend/tests/test_voice_input_real_transcript_api.py
python -m pytest -q backend/tests

cd app
flutter analyze
flutter test test/backend_provider_neutral_transcript_provider_test.dart
flutter test
cd ..

git diff --check
```

The synthetic tests do not read private credentials, import the OpenAI SDK,
create a provider client, execute network requests, access a microphone, play
audio, or create a real transcript.

## Acceptance evidence

```text
compileall: passed
dedicated RT-5f1 pre-commit gate: passed
focused Backend tests: 12 passed
Backend full tests: 204 passed, 1 existing warning
Flutter analyze: passed
focused Flutter tests: 12 passed
Flutter full tests: 355 passed
exact implementation surface: 17 files
changed-content privacy review: passed
git diff --check: passed
explicit operator approval: accepted
implementation commit: daca3a68672eb3106e861278ebb65612380140ed
implementation push: completed
post-push DRC/FW working trees: clean
```

The accepted synthetic verification did not read private credentials, import the
OpenAI SDK, create a provider client, execute network requests, access a
microphone, play audio, or create a real transcript.

```text
RT-5f2: NOT_STARTED / READY_FOR_EXACT_CONTRACT_REVIEW / NOT_AUTHORIZED
```

## Stop rule

Stop RT-5f1 if any of the following becomes necessary:

```text
FW internal import
DRC provider client or OpenAI SDK import
credential in Flutter/request/response/log
staging ID in URL path or success response
provider/model/payload in Flutter result contract
transcript persistence or logging
HomeScreen or main.dart change
TTS automation
speech activity or barge-in change
unbounded request/response/audio/text/concurrency
private env file modification
real provider execution for candidate validation
change outside the exact seventeen files
```

## Completion boundary

RT-5f1 implementation acceptance can claim only:

```text
provider-neutral Backend transcript endpoint implemented
single-use staged WAV preserved
FW root-public real-STT assembly reused
Flutter transcript provider implemented
existing transcript handoff compatibility verified with fake transport
normal main.dart wiring: false
HomeScreen integration: false
real provider execution: false
real-STT-to-stream operator acceptance: false
automatic TTS: false
speech activity: false
barge-in: false
```
