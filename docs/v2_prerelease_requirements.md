# v2.0.0 pre-release requirements

Daily Rhythm Companion v1.9.0 is a smartphone Web public demo release for AI Character Framework v4.0.0 capability evidence. It is not the final consumer-ready Daily Rhythm Companion release.

Before v2.0.0 can be considered release-ready, the project must explicitly satisfy and verify all requirements in this document.

## Required before v2.0.0

```text
v200_prerelease_requirement_real_llm_web_answer: required
v200_prerelease_requirement_real_tts_web_audio_output: required
v200_prerelease_requirement_real_google_health_sleep_data: required
v200_prerelease_requirement_web_image_display: required
v200_prerelease_requirement_public_repo_ready_fw_demo_app: required
v200_prerelease_requirement_explicit_release_requirements: required
```

### 1. Real LLM API Web answer generation

The app must use a real LLM API through the configured backend / AI Character Framework path and confirm that an answer can be generated and displayed on Web.

Evidence must show:

```text
- real LLM provider call is explicitly gated and operator opt-in only
- Web UI can request an answer through the actual DRC backend API
- a non-empty answer is displayed on Web
- prompt and response bodies are not committed into public evidence
- API keys and provider payloads are not committed
```

### 2. Real TTS API Web voice output

The app must use a real TTS API and confirm that voice output can be produced and played or otherwise audibly confirmed from Web.

Evidence must show:

```text
- real TTS provider call is explicitly gated and operator opt-in only
- generated audio is available to the Web UI through a safe backend contract
- Web UI can output voice from the generated audio path
- audio artifacts are handled with a public-safe retention policy
- API keys, provider payloads, and raw private text bodies are not committed
```

### 3. Real Google Health sleep data retrieval

The app must use the real Google Health API and confirm that real sleep data can be retrieved through the backend boundary.

Evidence must show:

```text
- real Google Health access is explicitly gated and operator opt-in only
- OAuth/token handling remains backend-owned
- Flutter does not own client secrets, refresh tokens, or raw provider payloads
- at least one real sleep summary can be retrieved and mapped into the DRC sleep summary contract
- public evidence records only safe shapes, counts, dates, or redacted summaries as appropriate
```

### 4. Web image display

The app must use image assets and confirm that they display on Web.

Evidence must show:

```text
- image assets are included in the Flutter asset manifest
- Flutter Web release build can display the images
- smartphone Web can display the images
- fallback behavior exists when an image is missing or unavailable
- release package includes required public-safe image assets or placeholders
```

### 5. Public repository readiness as a FW demo app

The repository must be ready to publish as an AI Character Framework demo app.

Evidence must show:

```text
- README explains that this is a public demo app for AI Character Framework
- roadmap explains v2.0.0 release gates and non-goals
- docs explain setup, configured real-provider gates, and public safety policy
- release package excludes local handoff docs, private paths, secrets, local data, and raw provider payloads
- LICENSE is present if the repository will be published publicly
```

### 6. Explicit release requirements

The requirements above must be explicitly listed as release requirements and guarded by source-tree checks before v2.0.0 release finalization.

Evidence must show:

```text
- README links to this requirements document
- roadmap links to this requirements document
- scripts/README.md lists the v2.0.0 prerequisite checks
- release notes and release finalization docs state whether the requirements are satisfied or still pending
- checks fail if the requirements are removed or watered down
```


## Day52 real LLM Web answer evidence

Day52 prepares the public-safe evidence contract for requirement #1.

See:

```text
docs/v200_real_llm_web_answer_evidence.md
scripts/smoke_framework_v200_real_llm_web_answer_evidence.py
scripts/smoke_framework_v200_real_llm_web_answer_evidence.py
```

Current Day52 status:

```text
v200_real_llm_web_answer_evidence_status: operator-evidence-contract-ready
```

This status means the evidence format and safe checks are ready. It does not mean the v2.0.0 real LLM Web answer requirement is satisfied yet.

The requirement can be marked satisfied only after a configured operator run confirms:

```text
- explicit opt-in was enabled
- the actual DRC backend API returned source.engine=framework
- the generated answer was non-empty
- the smartphone Web UI visibly displayed the answer
- public evidence omitted API keys, prompt bodies, answer bodies, raw provider payloads, raw LAN IPs, private paths, and raw screenshots
```


## Day53 real TTS provider gate design

Day53 prepares the safe provider gate for requirement #2.

See:

```text
docs/v200_real_tts_provider_gate.md
scripts/smoke_framework_v200_real_tts_provider_gate.py
scripts/smoke_framework_v200_real_tts_provider_gate.py
```

Current Day53 status:

```text
v200_real_tts_provider_gate_status: provider-gate-contract-ready
```

This status means the provider gate contract and mock-safe checks are ready. It does not mean the v2.0.0 real TTS Web voice output requirement is satisfied yet.

The requirement can be marked satisfied only after a configured operator run confirms:

```text
- explicit opt-in was enabled
- DRC used a neutral AI Character Framework voice output boundary
- provider-specific implementation details stayed out of DRC
- the configured real TTS provider generated audio
- generated audio was exposed through a safe backend contract
- Web output was audibly confirmed
- public evidence omitted API keys, private text bodies, raw provider payloads, audio artifacts, raw LAN IPs, private paths, and raw screenshots
```


## Day54 real TTS Web audio output evidence

Day54 prepares the configured-run evidence contract for requirement #2 after the Day53 provider gate.

See:

```text
docs/v200_real_tts_web_audio_output_evidence.md
scripts/smoke_framework_v200_real_tts_web_audio_output_evidence.py
scripts/smoke_framework_v200_real_tts_web_audio_output_evidence.py
```

Current Day54 status:

```text
v200_real_tts_web_audio_evidence_status: operator-evidence-contract-ready
```

This status means the evidence format and marker-only validation are ready. It does not mean the v2.0.0 real TTS Web voice output requirement is satisfied yet.

The requirement can be marked satisfied only after a configured operator run confirms:

```text
- explicit opt-in was enabled
- DRC used the neutral AI Character Framework voice output boundary
- the configured real TTS provider synthesized audio
- generated audio was exposed through a safe backend audio contract
- Web audio output was audibly confirmed
- public evidence omitted API keys, private text bodies, raw provider payloads, audio artifacts, raw LAN IPs, private paths, raw screenshots, and raw audio URLs
```


## Day55 real Google Health sleep data evidence

Day55 prepares the configured-run evidence contract for requirement #3.

See:

```text
docs/v200_real_google_health_sleep_data_evidence.md
scripts/smoke_v200_real_google_health_sleep_data_evidence.py
scripts/smoke_v200_real_google_health_sleep_data_evidence.py
```

Current Day55 status:

```text
v200_real_google_health_sleep_evidence_status: operator-evidence-contract-ready
```

This status means the evidence format and marker-only validation are ready. It does not mean the v2.0.0 real Google Health sleep-data requirement is satisfied yet.

The requirement can be marked satisfied only after a configured operator run confirms:

```text
- explicit opt-in was enabled
- real Google Health API gates were enabled
- an OAuth connection was available without exposing tokens or authorization headers
- real sleep data was fetched from Google Health
- fetched data was normalized into the public SleepSummary contract
- the backend sleep summary path confirmed a real-data result through safe fields
- public evidence omitted client secrets, access tokens, refresh tokens, authorization headers, raw Google Health payloads, raw sleep events, precise personal sleep timestamps, raw LAN IPs, private paths, raw screenshots, browser storage, and local token files
```


## Day56 Web image display evidence

Day56 prepares the configured-run evidence contract for requirement #4.

See:

```text
docs/v200_web_image_display_evidence.md
scripts/smoke_v200_web_image_display_evidence.py
scripts/smoke_v200_web_image_display_evidence.py
```

Current Day56 status:

```text
v200_web_image_display_evidence_status: operator-evidence-contract-ready
```

This status means the evidence format and marker-only validation are ready. It does not mean the v2.0.0 Web image display requirement is satisfied yet.

The requirement can be marked satisfied only after a configured operator run confirms:

```text
- image assets were selected from public-safe generated or placeholder assets
- Flutter asset manifest registration was confirmed
- Flutter Web release build displayed the image surface
- smartphone Web displayed the image surface
- missing-image fallback behavior was confirmed
- release package inclusion was confirmed for required public-safe assets or placeholders
- public evidence omitted raw screenshots, private generated prompts, copyrighted source-image references, raw LAN IPs, private paths, and unreviewed image artifacts
```


## Historical Public-readiness gate retirement

The former Day57 public-repository readiness and Day58 aggregate-gate implementation files were preparation-stage contracts. Cleanup-6 removes those dedicated files after Public-P2 becomes the current direct validator.

Current Public requirement validation:

```text
LICENSE exists.
README and release metadata identify Daily Rhythm Companion v2.0.0 correctly.
Public-P2 validates required files, version/Web metadata, forbidden private/local artifacts, sensitive-content patterns, and fixed-ZIP hygiene.
Day80 records accepted real Web evidence.
Day82 and Day83 verify the same final fixed ZIP without rebuilding.
```

This consolidation does not mark the GitHub Release as published. The release remains incomplete until the clean Public repository, Public source commit, final fixed ZIP, Public annotated tag, and GitHub Release exist.

## v1.9.0 release scope correction

v1.9.0 may be finalized as an AI Character Framework v4.0.0 smartphone Web public demo evidence release only if the release notes clearly state that the v2.0.0 pre-release requirements are still pending.

```text
v190_release_scope: fw40-smartphone-web-public-demo-evidence
v190_not_consumer_release: true
v190_v200_prerelease_requirements_status: documented-pending
```
