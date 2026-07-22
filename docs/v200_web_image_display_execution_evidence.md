# v2.0.0 Day68 Web image display execution evidence

Day68 continues the v2.0.0 real execution evidence phase for the fourth completion requirement:

```text
画像を用いて、Web上で表示確認できること / Web image display execution evidence
```

Day56 prepared the Web image display evidence gate. Day67 prepared the repository-safe image asset generation/intake gate. Day68 adds marker-only acceptance for a configured operator run that confirms the reviewed app image assets or placeholders are registered and visible in the actual Flutter Web UI, including smartphone Web confirmation.

## Status marker

```text
v200_web_image_display_execution_evidence_status: operator-execution-evidence-contract-ready
```

This marker means the Day68 execution evidence acceptance contract is ready. It does **not** mean the requirement is satisfied by the default source-tree check.

## Required operator evidence markers

A configured Day68 Web image display run can be accepted only when all of these markers are true:

```text
explicit_operator_opt_in_enabled
day67_asset_intake_evidence_accepted
public_safe_assets_available_in_app_tree
flutter_asset_manifest_registration_confirmed
flutter_web_runtime_display_confirmed
smartphone_web_display_confirmed
actual_app_route_used
missing_image_fallback_confirmed
release_package_asset_inclusion_ready
public_safe_evidence_recorded
```

The evidence should prove:

```text
- Day67 repository-safe asset intake was accepted first.
- reviewed public-safe image assets or placeholders are available in the app tree.
- Flutter asset manifest registration is confirmed.
- Flutter Web displays the intended image surface.
- smartphone Web displays the intended image surface through the actual DRC app UI.
- the confirmation uses a real app route or screen, not an isolated static image preview.
- missing-image or unavailable-image fallback behavior is visible and non-crashing.
- selected asset paths are ready for later fixed release package inclusion verification.
- shared evidence remains public-safe and marker-only.
```

## Forbidden success states

The following states must not be counted as Web image display execution success:

```text
day67_not_accepted
unreviewed_asset
missing_asset_manifest_registration
flutter_web_not_confirmed
smartphone_web_not_confirmed
static_file_preview_only
screenshot_only_without_ui_confirmation
missing_image_fallback_not_confirmed
release_asset_inclusion_unknown
raw_screenshot
raw_lan_ip
private_path
private_prompt_context
raw_generation_metadata
copyrighted_source_image
third_party_character_reference
private_photo
living_person_reference
skipped
unavailable
fallback_only
error
```

## Public safety policy

Do not commit or share:

```text
- raw screenshots
- raw LAN IPs
- private absolute paths
- browser storage dumps
- raw image-generation prompts with private context
- raw generation metadata or raw seed metadata
- unreviewed intermediate image outputs
- local image-generation work folders
- copyrighted source-image references
- third-party character references
- private photos or living-person likeness references
```

Public evidence should use coarse markers, reviewed asset paths, and redacted labels only. Do not include device screenshots in public docs or release material.

## Canonical paths

```text
docs/v200_web_image_display_execution_evidence.md
docs/operator_evidence_templates/v200_web_image_display_execution_day68.example.json
backend/app/services/framework_v200_web_image_display_execution_evidence.py
scripts/smoke_framework_v200_web_image_display_execution_evidence.py
scripts/smoke_framework_v200_web_image_display_execution_evidence.py
```

## Mock-safe source-tree check

```powershell
python -m compileall -q backend scripts
python scripts\smoke_framework_v200_web_image_display_execution_evidence.py

cd app
flutter test
cd ..
```

Expected output includes:

```text
[v200-web-image-display-execution-day68-check] OK
```

## Default smoke renderer

```powershell
python scripts\smoke_framework_v200_web_image_display_execution_evidence.py
```

Expected marker:

```text
v200_web_image_display_execution_evidence_status: operator-execution-evidence-contract-ready
```

## Optional redacted operator evidence validation

After a configured Web image display run, a local operator may validate a small redacted JSON summary:

```powershell
python scripts\smoke_framework_v200_web_image_display_execution_evidence.py --operator-evidence-json docs\operator_evidence_templates\v200_web_image_display_execution_day68.example.json
```

This validation does not generate images, inspect image files, run Flutter Web builds, start backend services, open browsers, inspect screenshots, record LAN URLs, or create release artifacts. It only checks that a marker-only summary contains all required booleans and excludes unsafe publication states.

## Requirement status

Day68 can accept marker-only configured evidence for the Web image display requirement, but the default source-tree check does not satisfy the requirement by itself. The next work remains public repo readiness final sweep, final aggregate verification, and fixed v2.0.0 release zip verification.
