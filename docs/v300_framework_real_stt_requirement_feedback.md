# Daily Rhythm Companion v3.0.0 RT-3d0 Framework real STT requirement feedback

Updated: 2026-07-28

Status:

```text
RT-3d0: COMPLETED / ACCEPTED
RT-3d: BLOCKED_FRAMEWORK_REAL_PROVIDER_EXECUTION_NOT_IMPLEMENTED
latest released Framework: v5.3.0
next Framework version: UNDECIDED
first real STT provider: UNDECIDED
```

## Purpose

RT-3d0 records the additional AI Character Framework development requirement
identified while integrating Daily Rhythm Companion v3.0.0 voice input.

This is a DRC-side requirements feedback checkpoint only. It does not begin
Framework development, select a Framework version, select a provider, execute
real STT, or unblock RT-3d.

The requirement must be handled in the dedicated Framework development thread
through requirements definition, design, implementation, acceptance, and
release.

## Exact baselines

```text
DRC repository:
murayan1982/daily-rhythm-companion-public

DRC source HEAD before RT-3d0:
7cf980e00fd73ab6b3b465f91aff4c05fa9abc48

latest released DRC:
v2.1.0

strategic DRC target:
v3.0.0

latest released Framework:
v5.3.0

Framework v5.3.0 tag commit:
693f9b8d30cdaec72fefb1de6f63d1883e071457

post-release documentation-only Framework HEAD reviewed by DRC:
e2e1c16dc7702e9fe6f7fa0589f7bf94b084cabe
```

The post-release Framework HEAD adds the DRC demo application link. It is not a
new Framework feature release.

## Framework v5.3.0 capabilities already accepted by DRC

The released Framework provides:

- public `VoiceInputRequest` and `VoiceInputResult`;
- public `VoiceInputSession` and `create_voice_input_session(...)`;
- public host-owned `VoiceInputAudioSource`;
- public file-path and opaque-ID audio-source contracts;
- public lazy `VoiceInputProviderAdapter`;
- `FakeVoiceInputProviderAdapter`;
- `GuardedRealVoiceInputProviderAdapter`;
- public `transcribe_audio_result(...)`;
- provider-safe `import framework`;
- explicit provider-execution guard metadata;
- provider-neutral typed result and error boundaries;
- no Framework-owned microphone requirement.

DRC RT-3c4 proves the private staging to Framework public-session shape with the
fake adapter. That accepted path does not read audio or execute STT.

## Confirmed missing Framework capability

The released Framework does not provide accepted concrete real-provider
execution. After execution opt-in and credential-presence checks, the guarded
adapter still reports:

```text
available: false
guard: real_stt_not_implemented
provider_execution_executed: false
```

The missing GAP-5 capability is:

```text
DRC private staged audio
-> released Framework public API
-> concrete real STT provider execution
-> provider-neutral typed transcript/result
```

## Why DRC cannot fill GAP-5 internally

DRC v3.0.0 requires configured real voice-input evidence, not only a fake
public-contract transcript.

DRC explicitly excludes:

- provider-specific STT clients inside DRC;
- Framework internal-module imports;
- DRC-owned copies of Framework provider runtime;
- treating a mobile-local path as a Backend-local provider path.

Therefore an additional Framework development requirement exists.

## Required future Framework outcome

A future released Framework must support one explicitly authorized real STT
request through released public APIs, including:

1. a concrete real-provider adapter behind the public adapter contract;
2. explicit real-STT and provider-execution opt-in;
3. lazy provider SDK/client resolution;
4. credential checks without public secret exposure;
5. bounded host-owned audio-source validation;
6. real provider invocation;
7. provider-neutral transcript normalization;
8. provider-neutral public error normalization;
9. honest capability and execution status;
10. safe lifecycle and interruption/close behavior;
11. injected mock-client tests without network execution;
12. private real-provider operator acceptance;
13. a formally accepted and released Framework package.

## Safety boundaries to preserve

- `import framework` remains provider-safe.
- Guard failures do not read audio or create provider clients.
- Framework does not open the DRC microphone.
- Raw audio and local private paths do not enter public results.
- Credentials and authorization values are not logged or returned.
- Full provider payloads are not exposed through public metadata.
- Fake adapter and text-fallback paths remain available.
- Existing v5.2.0/v5.3.0 public behavior remains compatible or has an accepted
  migration contract.

## DRC responsibilities that remain in DRC

- microphone permission;
- recording start/stop and bounded capture;
- mobile private artifact ownership;
- private mobile-to-Backend transfer;
- bounded private Backend staging;
- staged-artifact cleanup;
- DRC UI state and retry presentation;
- operator evidence privacy;
- handing normalized text into DRC conversation orchestration.

## Decisions reserved for the Framework development thread

RT-3d0 does not decide:

- the next Framework version number;
- the first concrete STT provider;
- the provider model;
- credential configuration details;
- public class names;
- provider SDK choice;
- retry, timeout, or streaming policy;
- support for URL or opaque-ID resolution;
- Framework release schedule.

Required handoff statement:

```text
Additional Framework development requirement identified for DRC v3.0.0:
accepted concrete real STT provider execution through released public Framework
APIs, while preserving the v5.3.0 provider-neutral host-audio/session boundary.
```

## DRC block and restart gate

RT-3d remains blocked until:

```text
Framework requirements definition: ACCEPTED
Framework implementation: ACCEPTED
Framework private real-provider execution: ACCEPTED
Framework release readiness: ACCEPTED
Framework release package/tag/release: COMPLETED
DRC released-Framework adoption gate: ACCEPTED
```

DRC must not unblock RT-3d using an uncommitted Framework worktree, Framework
internal modules, or an unreleased provider adapter.

## RT-3d0 change surface

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v300_goal_checklist_small_commit.md
docs/v300_framework_real_stt_requirement_feedback.md
scripts/check_v300_framework_real_stt_requirement_feedback.py
```

## Acceptance sequencing

The six accepted RT-3 historical gates were rerun successfully on the clean
`7cf980e` tree before this checkpoint was applied. Those gates intentionally
validate their own historical changed-file surfaces.

After RT-3d0 is applied, its dedicated gate validates the exact new seven-file
surface. Backend/Flutter full tests and `git diff --check` are then run.

## Non-actions

RT-3d0 does not change Backend/Flutter runtime, dependencies, platform files,
versions, Framework source, private environment values, audio, microphone,
provider clients, provider execution, release artifacts, tags, or publications.


## Acceptance record

RT-3d0 is **COMPLETED / ACCEPTED** after:

```text
six accepted RT-3 historical gates on clean 7cf980e: PASS
RT-3d0 dedicated source-only gate: PASS
Backend tests: 145 passed, one existing warning
Flutter analyze: No issues found
Flutter tests: 200 passed
exact seven-file change surface: PASS
git diff --check: PASS
explicit operator approval: RECEIVED
```

The accepted outcome remains a requirements feedback handoff only. RT-3d stays
`BLOCKED_FRAMEWORK_REAL_PROVIDER_EXECUTION_NOT_IMPLEMENTED`.
