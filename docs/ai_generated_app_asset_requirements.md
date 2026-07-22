# AI-generated app asset requirements

Daily Rhythm Companion uses app visual assets to support its role as a public AI Character Framework demo app.

Image assets such as backgrounds and character images are planned to be created with image-generation AI when needed.

## Scope

Planned AI-generated asset categories:

```text
- screen backgrounds
- character standing images
- character bust images
- character expression variations
- advice / mood / report state illustrations
- voice input / voice output / Live2D-VTS demo state illustrations
- placeholder-safe visuals for unavailable, skipped, fallback, and configured-success states
```

## Development requirement

When a feature requires visual assets, the implementation plan should define:

```text
- asset purpose
- target screen or component
- character or state represented
- aspect ratio
- approximate pixel dimensions
- transparent background requirement
- naming convention
- number of variations
- safe public-repository usage notes
```

## Character asset direction

The built-in demo should remain lightweight.

Preferred direction:

```text
- flat-image or chibi-style character presentation
- small expression set per bundled character
- no dependency on a heavy bundled Live2D model for the default demo path
- Live2D/VTS remains a configured demo capability rather than a required built-in asset dependency
```

Possible expression/state set:

```text
- neutral
- happy
- tired / sleepy
- thinking
- listening
- speaking
- fallback / unavailable
- report-informed
```

## Background asset direction

Background images should support a calm daily rhythm companion feel.

Possible background groups:

```text
- morning home screen
- evening reflection screen
- sleep report screen
- history / records screen
- configured FW demo status screen
```

## Safety and repository policy

Generated assets must be safe for public repository use.

Avoid:

```text
- copyrighted characters
- trademarked designs
- direct imitation of a named living artist
- private user data in prompts or metadata
- secrets, tokens, or local paths in prompts or filenames
```

## Timing

Do not generate final image assets prematurely.

Use placeholder-friendly UI first where possible, then request or generate assets at the milestone where:

```text
- the screen layout is stable enough
- the required aspect ratio is known
- character/state variations are known
- the asset will be committed or packaged intentionally
```

## v2.0.0 initial image-generation handoff

This section is a concrete handoff for the v2.0.0 image asset generation/intake step. It is documentation only: it does **not** mean the images have already been generated, reviewed, committed, displayed on Web, or accepted as release evidence.

### Folder creation

Run these commands from the repository root before saving reviewed image files:

```powershell
mkdir app\assets\images\characters
mkdir app\assets\images\backgrounds
mkdir app\assets\images\placeholders
```

Optional local-only work folders may be used while generating candidates, but they must not be committed:

```text
_local/image_generation_work/v200/**
```

Only final reviewed PNG files under `app/assets/images/**` are commit candidates.

### Required v2.0.0 demo asset inventory

```text
app/assets/images/characters/gentle_mina_demo.png
- Usage: gentle_mina demo character image for the app UI
- Required size: 1024x1024 PNG
- Aspect ratio: 1:1
- Background: transparent preferred
- Commit target: yes, after review

app/assets/images/characters/cheerful_sora_demo.png
- Usage: cheerful_sora demo character image for the app UI
- Required size: 1024x1024 PNG
- Aspect ratio: 1:1
- Background: transparent preferred
- Commit target: yes, after review

app/assets/images/characters/cool_rei_demo.png
- Usage: cool_rei demo character image for the app UI
- Required size: 1024x1024 PNG
- Aspect ratio: 1:1
- Background: transparent preferred
- Commit target: yes, after review

app/assets/images/backgrounds/morning_room_soft.png
- Usage: soft morning room background for Web UI image display verification
- Required size: 1920x1080 PNG
- Aspect ratio: 16:9
- Background: full background image, not transparent
- Commit target: yes, after review

app/assets/images/backgrounds/night_room_calm.png
- Usage: calm night room background for Web UI image display verification
- Required size: 1920x1080 PNG
- Aspect ratio: 16:9
- Background: full background image, not transparent
- Commit target: yes, after review

app/assets/images/placeholders/character_fallback.png
- Usage: repository-safe fallback image when a character asset is missing
- Required size: 1024x1024 PNG
- Aspect ratio: 1:1
- Background: transparent preferred
- Commit target: yes, after review
```

### Public-safe prompt summaries

Use these as public-safe prompt summaries or as the public-safe basis for local prompts. Do not commit raw prompts if they contain private context, generator settings, seeds, source screenshots, or local paths.

```text
gentle_mina_demo.png
Original gentle chibi-style daily rhythm companion character, soft friendly expression, cozy home-advice feel, clean flat illustration, transparent background, no text, no logo, no copyrighted character, no living-person likeness.

cheerful_sora_demo.png
Original cheerful chibi-style daily rhythm companion character, energetic welcoming pose, bright morning-advice feel, clean flat illustration, transparent background, no text, no logo, no copyrighted character, no living-person likeness.

cool_rei_demo.png
Original calm practical chibi-style daily rhythm companion character, composed supportive pose, checklist/report-advice feel, clean flat illustration, transparent background, no text, no logo, no copyrighted character, no living-person likeness.

morning_room_soft.png
Original soft morning room background for a daily rhythm companion app, calm sunlight, tidy desk, plants or simple decor, warm and uncluttered 16:9 composition, no identifiable location, no text, no logo.

night_room_calm.png
Original calm night room background for sleep reflection, soft lamp or moonlight, tidy room, restful 16:9 composition, no identifiable location, no text, no logo.

character_fallback.png
Original simple fallback mascot or silhouette for missing character image, gentle neutral expression or crescent-moon motif, clean flat illustration, transparent background, no text, no logo, no copyrighted character.
```

### Safety review before commit

Before committing generated images, confirm:

```text
- each selected asset matches the required filename and size/aspect ratio
- character images and fallback image have transparent backgrounds where possible
- backgrounds are original, generic, and not identifiable private locations
- no copyrighted characters, trademarked designs, named artist imitations, private photos, or living-person likenesses are present
- no text, logos, secrets, tokens, local paths, LAN IPs, prompt metadata, seeds, or raw generation metadata are embedded in filenames or committed docs
- raw generation work folders and rejected candidates are excluded from git
- Web display evidence remains separate and is not accepted until the Web UI/smartphone Web UI screenshot evidence step is completed
```

