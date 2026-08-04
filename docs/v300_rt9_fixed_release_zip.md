# Daily Rhythm Companion v3.0.0 RT-9c fixed release ZIP tooling

Updated: 2026-08-04
Status: STAGE1_IMPLEMENTED / AWAITING_REVIEW

## Identity

```text
RT-9b accepted commit: 15908a548c229726287867ad89c7ce8b4b916298
RT-9c Stage 1 baseline: 15908a548c229726287867ad89c7ce8b4b916298
Backend candidate version: 3.0.0
Flutter candidate version: 3.0.0+4
planned tag: DRC_v3.0.0
fixed ZIP: NOT_BUILT
builder invocation count: 0
GitHub Release: NOT_CREATED
v3.0.0: NOT_RELEASED
```

## Three-stage RT-9c split

```text
Stage 1  credential-free builder/verifier tooling
Stage 2  clean committed-main private-manifest-aware no-build preflight
Stage 3  public-safe RT-9c acceptance synchronization
```

Stage 1 cannot complete the official preflight because the builder correctly
requires a clean committed and synchronized official Public `main`. Stage 2 runs
that preflight only after Stage 1 is accepted, committed, and pushed.

## One-time builder

`build_v300_fixed_release_zip_from_head.ps1` requires:

```text
official Public repository and main branch
clean working tree
HEAD == origin/main
exactly one root commit
annotated DRC_v2.0.0 / DRC_v2.0.1 / DRC_v2.1.0 tags preserved
DRC_v3.0.0 absent
DailyRhythmCompanion_v3.0.0_*.zip absent
explicit ignored RT-8 aggregate manifest path
full v3 source/test/build readiness gate
```

`-PreflightOnly` stops after the full gate with builder invocation count `0`. It
creates no worktree, generic ZIP, fixed ZIP, tag, or GitHub Release.

The later separately authorized non-preflight path creates a detached worktree
from the exact committed HEAD, invokes `build_release.bat release` exactly once,
requires exactly one generic ZIP, renames it to
`DailyRhythmCompanion_v3.0.0_<timestamp>.zip`, records source HEAD/basename/size/
SHA-256, and stops before verification or publication.

## Verifier

`scripts/check_v300_fixed_release_zip.py` supports:

```text
default        Stage 1 static/tooling contract; no private manifest or artifact
--source-tree  clean official main plus full readiness and manifest validation
--release-zip  one explicitly supplied same ZIP; never invokes a builder
```

The future `--release-zip` mode requires explicit expected source HEAD and SHA-
256, verifies hash before/after, ZIP CRC, one package root, safe normalized member
names, no duplicate/case-collision/path traversal/symlink, required Public files,
package denylist hygiene, v3 candidate metadata, historical release hashes, and
Backend/Flutter tests plus Web/Windows/Android debug builds from a safe temporary
extraction. It remains blocked until RT-9d authorization.

## Artifact/privacy boundary

The fixed ZIP must exclude `.git`, `release`, `vendor`, `operator_evidence`,
`backend/local_data`, local env files, keys/tokens/OAuth state, raw audio/logs,
databases, caches, build outputs, nested ZIPs, and private paths or LAN values.
AI Character Framework v5.5.0 is not bundled.

## Exact Stage 1 surface

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v300_goal_checklist_small_commit.md
docs/v300_rt9_release_readiness_current_behavior_inventory.md
docs/v300_rt9_release_readiness.md
docs/v300_release_record.md
release_notes/v3.0.0.md
scripts/check_v300_rt9_release_readiness.py
docs/v300_rt9_fixed_release_zip.md
build_v300_fixed_release_zip_from_head.ps1
scripts/check_v300_fixed_release_zip.py
```

## Stage 1 stop rule

After source/tooling verification, stop for review. Do not run `-PreflightOnly`
from the dirty candidate, do not build a fixed ZIP, do not record an artifact
tuple, and do not create a tag or GitHub Release.
