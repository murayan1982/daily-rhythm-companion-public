# v2.0.0 Day56 Web image display evidence

Day56 prepares the public-safe evidence contract for the v2.0.0 pre-release requirement:

```text
画像を用いて、Web上で表示確認できること / Web image display evidence
```

Default checks are still mock-safe. They do not generate images, call image-generation services, start Flutter, open a browser, build Web release artifacts, call the backend, create image artifacts, or validate screenshots.

## Status marker

```text
v200_web_image_display_evidence_status: operator-evidence-contract-ready
```

This means the evidence contract is ready. It does **not** mean the Web image display requirement is satisfied yet.

## Required configured-run evidence

A configured Web image display run can satisfy this gate only after all of the following are confirmed:

```text
- public_safe_image_assets_selected
- flutter_asset_manifest_registration_confirmed
- flutter_web_release_build_display_confirmed
- smartphone_web_display_confirmed
- missing_image_fallback_confirmed
- release_package_asset_inclusion_confirmed
- public_safe_evidence_recorded
```

The configured run should prove:

```text
- image assets or placeholders are safe to include in a public repository
- assets are registered in the Flutter asset manifest
- Flutter Web displays the image surface
- smartphone Web displays the image surface through the actual app
- a missing-image or unavailable-image fallback is visible and non-crashing
- the release package includes the required public-safe image assets or placeholders
- shared evidence is marker-based and public-safe
```

## Public safety policy

Do not record or commit:

```text
- raw screenshots
- raw LAN IPs
- private absolute paths
- unreviewed image artifacts
- private generated prompts that contain private context
- copyrighted source-image references
- third-party character images without clear rights
- generated image seeds or metadata when they expose private context
- local image-generation work folders
```

Public evidence should use only coarse markers, redacted labels, safe asset paths, and reviewed public-safe image filenames.

## Future demo image asset plan

Day56 does not generate or add images yet. When the project is ready to add actual image assets, use a small public-safe set under `app/assets/images/` and register it in `app/pubspec.yaml`.

Suggested minimal asset set:

```text
app/assets/images/characters/gentle_mina_demo.png
app/assets/images/characters/cheerful_sora_demo.png
app/assets/images/characters/cool_rei_demo.png
app/assets/images/backgrounds/morning_room_soft.png
app/assets/images/backgrounds/night_room_calm.png
app/assets/images/placeholders/character_fallback.png
```

Suggested display targets:

```text
- home screen character card
- advice result character area
- fallback character image when a selected image is unavailable
- optional gentle background in the main Web layout
```

Suggested generation prompt outlines, to be reviewed before use:

```text
- gentle_mina_demo.png: original lightweight chibi flat-image character, gentle sleepy-morning companion, soft expression, simple clean shapes, transparent background, 1:1, public-demo-safe
- cheerful_sora_demo.png: original lightweight chibi flat-image character, cheerful energetic daily companion, bright friendly expression, simple clean shapes, transparent background, 1:1, public-demo-safe
- cool_rei_demo.png: original lightweight chibi flat-image character, calm practical daily companion, cool concise expression, simple clean shapes, transparent background, 1:1, public-demo-safe
- morning_room_soft.png: original simple soft morning room background, no identifiable location, calm daily rhythm companion mood, 16:9, public-demo-safe
- night_room_calm.png: original simple calm night room background, no identifiable location, sleep reflection mood, 16:9, public-demo-safe
- character_fallback.png: generic original fallback character silhouette or mascot placeholder, neutral expression, transparent background, 1:1, public-demo-safe
```

The images should be generated or sourced only after a licensing/public-safety review. Do not use copyrighted characters, real people, private photos, or unreviewed third-party image references.

## Mock-safe source-tree check

```powershell
python -m compileall -q backend scripts
python scripts\smoke_v200_web_image_display_evidence.py

cd app
flutter test
cd ..
```

Expected output includes:

```text
[v200-prerelease-requirements-check] OK
[v200-real-llm-web-answer-day52-check] OK
[v200-real-tts-provider-gate-day53-check] OK
[v200-real-tts-web-audio-output-day54-check] OK
[v200-real-google-health-sleep-data-day55-check] OK
[v200-web-image-display-day56-check] OK
```

## Default smoke renderer

```powershell
python scripts\smoke_v200_web_image_display_evidence.py
```

Expected marker:

```text
v200_web_image_display_evidence_status: operator-evidence-contract-ready
```

## Optional redacted operator evidence validation

After a configured manual run, an operator may create a small **local-only** redacted JSON summary. Do not commit the file unless it has been reviewed for public safety.

Example shape:

```json
{
  "public_safe_image_assets_selected": true,
  "flutter_asset_manifest_registration_confirmed": true,
  "flutter_web_release_build_display_confirmed": true,
  "smartphone_web_display_confirmed": true,
  "missing_image_fallback_confirmed": true,
  "release_package_asset_inclusion_confirmed": true,
  "public_safe_evidence_recorded": true,
  "raw_screenshots_included": false,
  "raw_lan_ips_included": false,
  "private_paths_included": false,
  "unreviewed_image_artifacts_included": false,
  "copyrighted_source_image_references_included": false,
  "private_generated_prompts_included": false
}
```

Validation command:

```powershell
python scripts\smoke_v200_web_image_display_evidence.py --operator-evidence-json .\operator_evidence.json
```

This validation does not start Flutter, open a browser, build Web release artifacts, read images, or validate screenshots. It only checks that a marker-only summary has all required booleans and does not claim unsafe publication.

## Requirement status

Day56 keeps the v2.0.0 Web image display requirement pending until a configured operator run confirms asset manifest registration, Flutter Web display, smartphone Web display, missing-image fallback behavior, and release-package inclusion for public-safe image assets or placeholders. The source-tree check only confirms that the evidence contract, safety policy, future asset plan, and previous Day52-Day55 gates remain intact.
