# Public and Private development policy

Updated: 2026-07-22
Applies after: DRC v2.0.0 Public release

## Public source ownership

`murayan1982/daily-rhythm-companion-public` is the source repository for post-v2.0.0 product changes and future releases.

Public source may contain:

```text
- Application and backend source.
- Credential-free tests and fake fixtures.
- Public-safe setup examples with placeholders.
- Runtime and API contracts.
- Public documentation and release records.
- Repository-safe character and UI assets.
```

Public source must not contain:

```text
- API keys, client secrets, access tokens, or refresh tokens.
- Raw provider or raw health payloads.
- Raw generated audio retained as operator evidence.
- Private screenshots or screenshot manifests with local paths.
- LAN IP addresses, private absolute paths, or credential-file locations.
- Ignored operator evidence or Private Git history.
```

## Private operator environment

The Private operator environment is for explicit real-integration execution and evidence review. It is not a second release source of truth.

Private-only material includes:

```text
- Local `.env` files and OAuth credentials.
- Provider credentials and token stores.
- Raw Google Health or Fitbit responses.
- Raw LLM/TTS provider payloads.
- Screenshots, audio, and operator evidence.
- Local URLs, LAN addresses, and absolute paths.
```

Public-safe acceptance markers may record that a requirement was accepted, but must not copy raw private values into the repository.

## Integration rules

```text
- Mock-safe behavior remains the credential-free default.
- Real external execution requires explicit opt-in.
- DRC uses stable AI Character Framework public APIs only.
- Provider-specific LLM, TTS, or STT implementations stay outside DRC.
- Fallback, unavailable, skipped, blocked, detected, configured, and successful states remain distinct.
```

## Release rules

```text
- Never move or rewrite a published release tag.
- Never replace a published fixed release asset.
- Build a future fixed ZIP from the final committed Public source.
- Build that ZIP once for a release attempt and verify the same artifact throughout.
- Record the source commit, tag target, artifact name, size, and SHA-256.
- Publish corrections under a new semantic version.
```

## Local Private source copies

A disposable or Private working copy may be used for configured execution, but it must remain traceable to a Public commit. It must not become an alternate source history for a future release. Source changes intended for release return to the Public repository through normal commits.
