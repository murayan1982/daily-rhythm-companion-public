# v2.0.0 Day67 image asset generation and repository-safe intake evidence

Day67 prepares the public-safe acceptance layer for the image side of the v2.0.0 real execution evidence phase.

It builds on Day56, which prepared the Web image display evidence gate. Day67 is intentionally earlier than Web display: it confirms that generated or sourced image assets are safe to place in the repository and package before the app proceeds to Flutter asset registration and smartphone Web display evidence.

## Status markers

```text
v200_image_asset_generation_intake_evidence_status: operator-execution-evidence-contract-ready
image_asset_intake_review: ACCEPTED
```

The `v200_image_asset_generation_intake_evidence_status` marker is the default mock-safe source-tree contract status emitted by the smoke renderer.

The `image_asset_intake_review: ACCEPTED` marker records the configured Commit B asset-intake result in this repository package. It means the selected image files were created, reviewed for repository-safe intake, and recorded with stable asset paths, sizes, intended usage, and public-safe source notes.

This does **not** mean that the images have been registered in Flutter, displayed on Web, confirmed on smartphone Web, included in a final fixed v2.0.0 release package, or accepted as final v2.0.0 real Web execution evidence.

## Required configured-run evidence

A configured Day67 asset-intake run can satisfy this gate only after all of the following are confirmed:

```text
- explicit_operator_opt_in_enabled
- image_asset_generation_review_completed
- public_safe_asset_sources_confirmed
- required_asset_inventory_selected
- repository_safe_asset_paths_reserved
- generated_asset_metadata_sanitized
- third_party_or_copyrighted_sources_absent
- private_or_living_person_references_absent
- raw_generation_workspace_excluded
- fallback_placeholder_strategy_confirmed
- public_safe_evidence_recorded
```

The configured run should prove:

```text
- the operator intentionally ran the image-generation or asset-sourcing step
- generated or sourced assets were reviewed for public repository use
- selected assets match the small v2.0.0 demo inventory
- repository asset paths are stable and safe
- prompts, metadata, seeds, source references, and filenames do not expose private context
- copyrighted characters, third-party character references, trademarked designs, private photos, and living-person likeness references are absent
- raw generation work folders and unreviewed intermediate outputs are excluded
- fallback placeholder strategy is defined before Web display verification
- shared evidence is marker-only and public-safe
```

## Required v2.0.0 asset inventory

Use a small set first. These are the only default v2.0.0 image-asset commit candidates until the Web layout proves it needs more images.

```text
app/assets/images/characters/gentle_mina_demo.png
- Usage: gentle_mina demo character image for the app UI
- Required size: 1024x1024 PNG
- Aspect ratio: 1:1
- Background: transparent preferred

app/assets/images/characters/cheerful_sora_demo.png
- Usage: cheerful_sora demo character image for the app UI
- Required size: 1024x1024 PNG
- Aspect ratio: 1:1
- Background: transparent preferred

app/assets/images/characters/cool_rei_demo.png
- Usage: cool_rei demo character image for the app UI
- Required size: 1024x1024 PNG
- Aspect ratio: 1:1
- Background: transparent preferred

app/assets/images/backgrounds/morning_room_soft.png
- Usage: soft morning room background for Web UI image display verification
- Required size: 1920x1080 PNG
- Aspect ratio: 16:9
- Background: full background image, not transparent

app/assets/images/backgrounds/night_room_calm.png
- Usage: calm night room background for Web UI image display verification
- Required size: 1920x1080 PNG
- Aspect ratio: 16:9
- Background: full background image, not transparent

app/assets/images/placeholders/character_fallback.png
- Usage: repository-safe fallback image when a character asset is missing
- Required size: 1024x1024 PNG
- Aspect ratio: 1:1
- Background: transparent preferred
```

This inventory mirrors the Day56 future demo image plan and should remain small until the Web layout proves it needs more images.

## Configured Commit B asset intake record

Commit B adds the following reviewed repository-safe PNG files:

```text
app/assets/images/characters/gentle_mina_demo.png
- Intake status: accepted
- Size: 1024x1024 PNG
- Aspect ratio: 1:1
- Background: transparent
- Source note: original repository-safe demo character asset

app/assets/images/characters/cheerful_sora_demo.png
- Intake status: accepted
- Size: 1024x1024 PNG
- Aspect ratio: 1:1
- Background: transparent
- Source note: original repository-safe demo character asset

app/assets/images/characters/cool_rei_demo.png
- Intake status: accepted
- Size: 1024x1024 PNG
- Aspect ratio: 1:1
- Background: transparent
- Source note: original repository-safe demo character asset

app/assets/images/backgrounds/morning_room_soft.png
- Intake status: accepted
- Size: 1920x1080 PNG
- Aspect ratio: 16:9
- Background: full background image
- Source note: original repository-safe demo background asset

app/assets/images/backgrounds/night_room_calm.png
- Intake status: accepted
- Size: 1920x1080 PNG
- Aspect ratio: 16:9
- Background: full background image
- Source note: original repository-safe demo background asset

app/assets/images/placeholders/character_fallback.png
- Intake status: accepted
- Size: 1024x1024 PNG
- Aspect ratio: 1:1
- Background: transparent
- Source note: original repository-safe fallback asset
```

Commit B public-safe evidence summary:

```text
explicit_operator_opt_in_enabled: true
image_asset_generation_review_completed: true
public_safe_asset_sources_confirmed: true
required_asset_inventory_selected: true
repository_safe_asset_paths_reserved: true
generated_asset_metadata_sanitized: true
third_party_or_copyrighted_sources_absent: true
private_or_living_person_references_absent: true
raw_generation_workspace_excluded: true
fallback_placeholder_strategy_confirmed: true
public_safe_evidence_recorded: true
```

Commit B public-safe omission summary:

```text
raw_prompts_with_private_context: omitted
raw_generation_metadata: omitted
raw_seed_metadata: omitted
source_screenshots: omitted
rejected_candidates: omitted
local_generation_work_folders: omitted
private_photos: omitted
living_person_references: omitted
third_party_character_references: omitted
copyrighted_character_references: omitted
trademarked_designs: omitted
private_paths: omitted
raw_lan_ips: omitted
api_keys_or_tokens: omitted
```

This configured intake record is limited to asset creation and repository-safe intake. Flutter asset registration and Web display evidence remain separate follow-up work.


## Local folder setup

Run these commands from the repository root before saving reviewed image files:

```powershell
mkdir app\assets\images\characters
mkdir app\assets\images\backgrounds
mkdir app\assets\images\placeholders
```

Optional local-only work folders may be used during generation, but they must not be committed:

```text
_local/image_generation_work/v200/**
```

Only final reviewed PNG files under `app/assets/images/**` are commit candidates. Raw prompts with private context, raw generator exports, raw generation metadata, seed files, source screenshots, and rejected candidates are non-commit local work files.

## Public-safe generation prompt boundaries

Prompts should describe only original, generic, public-demo-safe assets.

Allowed prompt concepts:

```text
- original lightweight chibi flat-image character
- gentle daily rhythm companion
- cheerful daily rhythm companion
- calm practical daily rhythm companion
- soft morning room background
- calm night room background
- generic fallback mascot or silhouette
- simple clean shapes
- transparent background for character assets
- no identifiable location
```

Avoid prompt concepts:

```text
- copyrighted characters
- named manga/anime/game characters
- direct imitation of a named living artist
- living-person likeness
- private photos or private user context
- trademarked designs
- private local paths
- LAN IPs
- API keys or provider identifiers
- raw seed or generation metadata
```

## Public-safe v2.0.0 prompt summaries

Use these public-safe summaries for the configured local image-generation/intake run. If the operator expands them into longer raw prompts, keep private context, generator parameters, seeds, source screenshots, and local paths out of committed files.

```text
app/assets/images/characters/gentle_mina_demo.png
- Public-safe prompt summary: original gentle chibi-style daily rhythm companion character, soft friendly expression, cozy home-advice feel, clean flat illustration, transparent background, no text, no logo, no copyrighted character, no living-person likeness.
- Negative/safety guidance: avoid copyrighted characters, named manga/anime/game characters, named living artists, private photos, living-person likeness, trademarked designs, text, logos, raw local paths, and raw metadata.

app/assets/images/characters/cheerful_sora_demo.png
- Public-safe prompt summary: original cheerful chibi-style daily rhythm companion character, energetic welcoming pose, bright morning-advice feel, clean flat illustration, transparent background, no text, no logo, no copyrighted character, no living-person likeness.
- Negative/safety guidance: avoid copyrighted characters, named manga/anime/game characters, named living artists, private photos, living-person likeness, trademarked designs, text, logos, raw local paths, and raw metadata.

app/assets/images/characters/cool_rei_demo.png
- Public-safe prompt summary: original calm practical chibi-style daily rhythm companion character, composed supportive pose, checklist/report-advice feel, clean flat illustration, transparent background, no text, no logo, no copyrighted character, no living-person likeness.
- Negative/safety guidance: avoid copyrighted characters, named manga/anime/game characters, named living artists, private photos, living-person likeness, trademarked designs, text, logos, raw local paths, and raw metadata.

app/assets/images/backgrounds/morning_room_soft.png
- Public-safe prompt summary: original soft morning room background for a daily rhythm companion app, calm sunlight, tidy desk, plants or simple decor, warm and uncluttered 16:9 composition, no identifiable location, no text, no logo.
- Negative/safety guidance: avoid copyrighted rooms or sets, identifiable private locations, trademarked products, text, logos, raw local paths, and raw metadata.

app/assets/images/backgrounds/night_room_calm.png
- Public-safe prompt summary: original calm night room background for sleep reflection, soft lamp or moonlight, tidy room, restful 16:9 composition, no identifiable location, no text, no logo.
- Negative/safety guidance: avoid copyrighted rooms or sets, identifiable private locations, trademarked products, text, logos, raw local paths, and raw metadata.

app/assets/images/placeholders/character_fallback.png
- Public-safe prompt summary: original simple fallback mascot or silhouette for missing character image, gentle neutral expression or crescent-moon motif, clean flat illustration, transparent background, no text, no logo, no copyrighted character.
- Negative/safety guidance: avoid copyrighted mascots, named characters, trademarked designs, living-person likeness, text, logos, raw local paths, and raw metadata.
```

## Forbidden success states

The following must not be counted as Day67 success:

```text
- unreviewed_image_artifacts
- copyrighted_source_image
- third_party_character_reference
- private_photo
- living_person_reference
- trademarked_character
- private_prompt_context
- raw_generation_metadata
- raw_seed_metadata
- local_generation_work_folder
- committed_external_work_folder
- missing_rights_review
- unsafe_filename
- private_path
- raw_lan_ip
- raw_screenshot
- skipped
- unavailable
- fallback_only
- error
```

## What Day67 does not do

Day67 does not modify `app/pubspec.yaml` during default checks.

Day67 does not:

```text
- generate images during normal checks
- call image-generation services
- commit unreviewed artifacts
- register Flutter assets
- modify `app/pubspec.yaml`
- start the backend
- run Flutter Web
- open a browser
- validate screenshots
- verify smartphone Web display
- build or verify a release zip
```

The asset-generation/intake part has been completed by the configured Commit B record above. Flutter registration, backend/browser execution, screenshot validation, smartphone Web display, and release artifact work remain for the following Web image display execution evidence step.

## Mock-safe source-tree check

```powershell
python -m compileall -q backend scripts
python scripts\smoke_framework_v200_image_asset_generation_intake_evidence.py

cd app
flutter test
cd ..
```

Expected output includes:

```text
[smoke-framework-v200-image-asset-generation-intake-evidence] RESULT
v200_image_asset_generation_intake_evidence_status: operator-execution-evidence-contract-ready
[smoke-framework-v200-image-asset-generation-intake-evidence] OK
```

The previously documented `scripts\check_v200_image_asset_generation_intake_day67.py` command is not used here because this repository package contains `scripts\smoke_framework_v200_image_asset_generation_intake_evidence.py` as the actual Day67 image-intake evidence renderer.

## Default smoke renderer

```powershell
python scripts\smoke_framework_v200_image_asset_generation_intake_evidence.py
```

Expected marker:

```text
v200_image_asset_generation_intake_evidence_status: operator-execution-evidence-contract-ready
```

## Optional redacted operator evidence validation

After a configured local asset-generation/intake review, an operator may create a small **local-only** redacted JSON summary. Do not commit the file unless it has been reviewed for public safety.

Example shape:

```json
{
  "explicit_operator_opt_in_enabled": true,
  "image_asset_generation_review_completed": true,
  "public_safe_asset_sources_confirmed": true,
  "required_asset_inventory_selected": true,
  "repository_safe_asset_paths_reserved": true,
  "generated_asset_metadata_sanitized": true,
  "third_party_or_copyrighted_sources_absent": true,
  "private_or_living_person_references_absent": true,
  "raw_generation_workspace_excluded": true,
  "fallback_placeholder_strategy_confirmed": true,
  "public_safe_evidence_recorded": true,
  "unreviewed_image_artifacts_included": false,
  "copyrighted_source_image_included": false,
  "third_party_character_reference_included": false,
  "private_photo_included": false,
  "living_person_reference_included": false,
  "trademarked_character_included": false,
  "private_prompt_context_included": false,
  "raw_generation_metadata_included": false,
  "raw_seed_metadata_included": false,
  "local_generation_work_folder_included": false,
  "committed_external_work_folder_included": false,
  "private_paths_included": false,
  "raw_lan_ips_included": false,
  "raw_screenshots_included": false
}
```

Validation command:

```powershell
python scripts\smoke_framework_v200_image_asset_generation_intake_evidence.py --operator-evidence-json .\operator_evidence.json
```

This validation does not call image-generation services, read image files, inspect prompts, inspect screenshots, register Flutter assets, or build Web artifacts. It only checks that a marker-only summary has all required booleans and does not claim unsafe publication.

## Requirement status

Day67 image asset generation and repository-safe intake is accepted for Commit B.

Day67 by itself kept the v2.0.0 Web image display requirement pending. Commit F-1 later added Flutter asset registration and display surfaces, and Commit F-2 accepted the marker-only Web image display execution and screenshot evidence.

```text
image_asset_intake_review: ACCEPTED
web_image_display: ACCEPTED
web_image_display_acceptance_commit: Commit F-2
v2.0.0_release_status: NOT_RELEASED
```
