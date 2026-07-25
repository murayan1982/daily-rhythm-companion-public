# Daily Rhythm Companion v2.1.0 R-1c final PC/smartphone Web evidence aggregate

Updated: 2026-07-25
Status: COMPLETED / ACCEPTED
Completed small commit: R-1c
Current small commit: none (R-1e accepted; v2.1.0 released)
Parent phase: R-1 — COMPLETED / ACCEPTED
Release state: RELEASED / ACCEPTED
Accepted prerequisite: R-1a — COMPLETED / ACCEPTED at implementation commit `dbc84db`
Accepted prerequisite: R-1b — COMPLETED / ACCEPTED at implementation commit `72dd42c`

## Purpose

R-1c defines the final integrated PC and smartphone Flutter Web checkpoint for the exact clean v2.1.0 candidate source. It combines the accepted Google Health, daily advice, post-advice chat, in-app TTS, and deterministic character display surfaces into one public-safe private-manifest validation boundary.

The accepted R-1c record confirms that the final checkpoint ran against exact candidate source `1e922e68685dadfc1008f1119d0ce492584e8f19`. The committed public-safe implementation and acceptance record provide:

```text
docs/v210_final_smartphone_web_evidence.md
scripts/check_v210_final_smartphone_web_evidence.py
docs/operator_evidence_templates/v210_final_smartphone_web_evidence_r1c.example.json
```

## Required execution source

The accepted private manifest must be validated while all of the following are true:

```text
branch: main
HEAD == origin/main
working tree: clean
Backend APP_VERSION: 2.1.0
Flutter package version: 2.1.0+3
candidate_source_head: exact 40-character current HEAD
final candidate source used: true
```

R-1c evidence taken from an earlier commit, dirty working tree, rebuilt source copy, mock-only screen, API-only result, or command output does not count.

## Required integrated evidence

The final candidate must be reviewed on both PC Web and smartphone Web with the actual DRC Backend.

### Google Health sleep

```text
- real Google Health request confirmed;
- normalized sleep summary visible;
- UI source labels visible as Google Health / 実データ / 取得済み;
- Fitbit-origin provenance confirmed without publishing a device identifier;
- no exact private sleep value stored in the public-safe manifest.
```

This checkpoint builds on accepted W-5b2 record commit `ed50d9e`, but must use the final R-1c candidate source.

### Daily advice

```text
- mood selection visible;
- advice result visible;
- real sleep context visibly contributes to the daily loop;
- normal UI contains no token, raw provider payload, private path, or technical secret.
```

### Post-advice chat

```text
- post-advice chat starts after advice;
- a user-visible chat result is shown;
- lifecycle state is visible;
- continue or restart control is visible;
- API-only, command-output-only, unavailable-only, skipped, and placeholder states do not count.
```

### In-app TTS

```text
- real Framework/TTS execution confirmed;
- play / stop / replay / completion / regenerate behavior reviewed;
- raw audio URL and private artifact path remain hidden from normal UI;
- generated audio and provider details remain outside Git and the release ZIP.
```

This checkpoint builds on accepted T-1c implementation commit `4d3d5d5` and its accepted audible PC/smartphone evidence, but must use the final R-1c candidate source.

### Character display

```text
- mood and advice content states visible;
- idle, loading, and speaking presentation reviewed;
- repository-safe character assets visible;
- no Live2D/VTube Studio execution claim is added.
```

### Final integrated review

```text
- daily loop completed coherently on PC and smartphone Web;
- all required results are visible in the Web UI;
- screenshots are captured and reviewed privately;
- no private value is visible in the normal UI;
- operator confirms the candidate is ready to enter R-1d.
```

## Private manifest handling

Create the ignored private candidate from the deliberately rejected public example:

```powershell
New-Item -ItemType Directory -Force .\operator_evidence | Out-Null
Copy-Item `
  .\docs\operator_evidence_templates\v210_final_smartphone_web_evidence_r1c.example.json `
  .\operator_evidence\v210_final_smartphone_web_evidence_r1c.json
```

Required ignored destination:

```text
operator_evidence/v210_final_smartphone_web_evidence_r1c.json
```

Populate it only after reviewing the actual final candidate. Replace `candidate_source_head` with `git rev-parse HEAD`, set markers from observed evidence, and keep screenshot references as opaque values beginning with:

```text
private-operator-evidence://v210/r1c/
```

Do not put real filesystem paths, URLs, LAN IPs, account identifiers, exact sleep values, raw audio filenames, or secret values into the manifest.

Validate the ignored manifest on clean synchronized `main`:

```powershell
python scripts\check_v210_final_smartphone_web_evidence.py `
  --manifest-json .\operator_evidence\v210_final_smartphone_web_evidence_r1c.json
```

An accepted run ends with:

```text
v210_final_smartphone_web_evidence_private_manifest_validated: true
v210_final_smartphone_web_evidence_candidate_source_matches_head: true
v210_final_smartphone_web_evidence_official_main_synced: true
v210_final_smartphone_web_evidence_required_items_accepted: true
v210_final_smartphone_web_evidence_pc_web_execution_confirmed: true
v210_final_smartphone_web_evidence_smartphone_web_execution_confirmed: true
v210_final_smartphone_web_evidence_screenshot_references_public_safe: true
v210_final_smartphone_web_evidence_final_aggregate_accepted: true
[v210-final-smartphone-web-evidence-check] OK
```

## Public-safe evidence policy

The following remain ignored and uncommitted:

```text
raw screenshots
raw audio
generated audio filenames and URLs
raw Google Health payloads
exact private sleep values
OAuth credentials and tokens
provider payloads and identifiers
device/account identifiers
private filesystem paths
LAN IPs
operator_evidence files
```

Only a later acceptance-sync commit may record boolean/classification outcomes and the accepted candidate source commit. It must not copy the ignored manifest or raw evidence into Git.

## Historical R-1c acceptance record

```text
accepted on: 2026-07-25
implementation commit: 1e922e6
accepted candidate source HEAD: 1e922e68685dadfc1008f1119d0ce492584e8f19
private final manifest validation: completed / accepted
required evidence items: 6 / 6 accepted
actual DRC Backend API used: true
final PC Web aggregate: completed / accepted
final smartphone Web aggregate: completed / accepted
Google Health real request and normalized display: accepted
Framework daily advice and live post-advice chat: accepted
real Framework/TTS play / stop / replay / completion / regenerate: accepted
deterministic character display and final integrated review: accepted
public-safe opaque screenshot references: recorded
raw screenshots/audio/health data/private values committed: false
fixed ZIP: not built
DRC_v2.1.0 tag at R-1c acceptance: not created
GitHub Release at R-1c acceptance: not created
```

R-1c and R-1d are `COMPLETED / ACCEPTED`. R-1e and parent R-1 are `COMPLETED / ACCEPTED`; v2.1.0 is released.


## Accepted R-1e publication transition

```text
explicit final operator approval: received
annotated tag: DRC_v2.1.0
annotated tag target: 6e7af31f85eb6ee7887df3e184ac6a58142d6fec
GitHub Release: published
published fixed ZIP: DailyRhythmCompanion_v2.1.0_20260725_160036.zip
published asset size bytes: 1747337
published asset SHA-256: 55bf584592b1824948ec847205132582a436f2c521feb593bac914a4904074e5
post-publication downloaded-asset SHA-256: 55bf584592b1824948ec847205132582a436f2c521feb593bac914a4904074e5
post-publication SHA-256 re-verification: passed
fixed ZIP rebuilt or replaced: false
R-1e: COMPLETED / ACCEPTED
parent R-1: COMPLETED / ACCEPTED
```
