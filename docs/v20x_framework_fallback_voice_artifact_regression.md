# v2.0.x Framework fallback and voice artifact safety regression

Updated: 2026-07-22
Small commit: M-4
Status: COMPLETED

## Purpose

M-4 extended the normal credential-free backend regression suite to two already-implemented runtime boundaries: configured AI Character Framework advice and DRC-managed voice output artifacts. It adds tests only; it does not change runtime behavior.

## Framework advice boundary

The success test creates a temporary fake package with the public import shape:

```text
<pytest tmp_path>/fake_fw/framework/__init__.py
- create_text_chat_session(*, preset, character_name)
- returned session.ask(text)
```

The test verifies:

```text
- FrameworkConversationEngine imports from the configured temporary root.
- create_text_chat_session receives preset=text_chat and character_name=default.
- the prompt contains the DRC character ID and stable mood ID.
- AdviceSource.engine=framework.
- framework_preset=text_chat.
- framework_character=default.
- framework_character_source=mapped_default.
- an empty framework response raises FrameworkEngineError.
```

This is a contract fake, not a real AI Character Framework checkout or provider execution.

## Visible fallback boundary

The fallback test injects an engine that raises FrameworkEngineError and verifies:

```text
- engine_basis=framework_fallback.
- AdviceSource.engine=framework_fallback.
- DRC character ID/name remain visible.
- framework preset/character fields are absent.
- the mock response does not claim Framework success.
```

Before importing `app.api.advice`, the test replaces the default persistence-store constructors. This prevents test collection or execution from creating or reading `backend/local_data`.

## Voice artifact safety boundary

Voice artifact tests create a temporary `VoiceOutputArtifactStore` root through pytest `tmp_path`.

Accepted case:

```text
- source is a regular .mp3 file inside the managed staging directory.
- source is moved into the managed public directory.
- caller receives only /demo/voice-output/audio/<opaque-id>.
- opaque ID is 32 lowercase hexadecimal characters.
- media type is audio/mpeg.
- the local temporary path is not exposed in the URL.
```

Rejected cases:

```text
- MP3 outside the managed staging directory.
- unsupported WAV format.
- mismatched declared format and file extension.
- traversal-like artifact ID.
- absolute-path-like artifact ID.
- non-hex or wrong-length artifact ID.
```

The dummy bytes used by the test are not provider-generated audio and are deleted with the temporary test directory.

## Commands

From the repository root:

```powershell
python -m pip install -r backend/requirements-dev.txt
python -m compileall -q backend scripts
python scripts\check_v20x_maintenance_baseline.py
python scripts\check_v20x_application_version_metadata.py
python scripts\check_v20x_backend_mock_safe_regression.py
python scripts\check_v20x_framework_fallback_voice_artifact_regression.py
python -m pytest -q backend/tests

cd app
flutter test
cd ..
```

## Explicit exclusions

```text
- real Framework checkout or import
- provider credentials
- network access
- real LLM or TTS execution
- audio playback or browser evidence
- chat session or TTS artifact TTL/cleanup changes (M-5)
- fixed ZIP, tag, GitHub Release, or v2.0.1 release creation
```

M-4 does not alter the published DRC_v2.0.0 asset or historical release records.

M-4 was accepted before M-5 runtime lifecycle work began. Its original safety assertions remain protected by the M-4 check.
