# Daily Rhythm Companion v3.0.0 RT-7b vendored Framework v5.5.0 readiness

Updated: 2026-08-02

## Candidate state

```text
RT-6: COMPLETED / ACCEPTED / PUSHED
RT-7: CURRENT / NOT_COMPLETED
RT-7a: COMPLETED / ACCEPTED / PUSHED
RT-7b: IMPLEMENTED / AWAITING_REVIEW
DRC baseline: 8413c2f08879b34f83496441c6a7e20181486469
Framework release: v5.5.0
Framework release commit: f56697b6de066b062794ac7bb01330d2d9e91759
Framework local source: vendor/ai-character-framework-5.5.0
change surface: exact 8 documentation/static-gate/ignore files
runtime composition: NOT_AUTHORIZED
real VTube Studio execution: NOT_AUTHORIZED
commit / push: NOT_AUTHORIZED
```

## Purpose

RT-7b fixes the local Framework source boundary that DRC may use for the later
RT-7 real-motion integration. It does not add a Backend real-motion route,
private configuration loader, VTube Studio session, Flutter behavior, provider
execution, operator evidence, or real motion.

The only allowed local Framework source is the extracted fixed release under:

```text
vendor/ai-character-framework-5.5.0
```

A Framework development checkout, moving branch, checkout-relative import,
current-working-directory workaround, or ad-hoc `sys.path` fallback is outside
the DRC integration contract. DRC code and verification must resolve
`framework` from the fixed vendor directory and verify the imported module
origin.

## Accepted precondition audit

The read-only precondition and corrective audits established:

```text
DRC HEAD / origin/main: 8413c2f08879b34f83496441c6a7e20181486469
vendor exists: true
vendor reparse point: false
vendor Git metadata count: 0
required public/release files: 14 / 14
vendor total file count before exclusion: informational / may include generated local cache files
release-eligible vendor file count after exclusion: 328
private artifact hits: 0
framework origin is vendor: true
motion API version: 5.5.0
root-public exports complete: true
mock motion completed: true
closed execution guard status: provider_execution_not_allowed
closed guard real adapter supported: false
pyvts imported: false
network execution: false
real motion execution: false
DRC working tree clean: true
```

The first audit used an obsolete generic `MotionRequest(value=...)` assumption.
The corrective audit used the released intent-specific contract through
`MotionRequest.emotion_update(...)` and passed. The initial exception was an
audit-script issue, not a Framework release failure.

## Candidate key-file observation

The precondition audit recorded SHA-256 values for selected public-boundary
files from the pre-existing local vendor copy. Those values are diagnostic only
and are not the final provenance authority because text files may differ in
working-copy line endings. RT-7b acceptance does not freeze a local total file
count or accept those observed hashes as a substitute for the official release
artifact.

The authoritative provenance condition is the explicit official v5.5.0 release
ZIP and sidecar comparison below. In strict mode, every release-eligible vendor
member, including the selected key files, must match the corresponding ZIP bytes.

## Release-artifact provenance condition

The root-public API version, required files, privacy scan, and runtime-safe
audit establish a bounded candidate readiness check. Final RT-7b
acceptance additionally requires the original deterministic release ZIP and its
SHA-256 sidecar to be supplied explicitly to the gate.

Strict verification must confirm:

```text
sidecar digest equals ZIP digest
sidecar filename equals the supplied ZIP filename
ZIP integrity passes
ZIP duplicate entries are absent
ZIP member set equals the vendor release-eligible file set
all ZIP member bytes equal the corresponding vendor file bytes
selected vendor key files therefore match the official artifact
private token/configuration/evidence paths are absent
```

The ZIP and sidecar are local verification inputs only. They must not be copied
into the tracked DRC source tree or committed.

The total number of files physically present below the vendor directory is
informational because local Python imports may create excluded `__pycache__` or
`.pyc` files. The fixed membership contract is the 328 release-eligible files;
excluded generated files neither satisfy nor invalidate artifact membership.

Until strict ZIP/sidecar comparison passes:

```text
RT-7b implementation review may proceed
RT-7b acceptance remains pending provenance evidence
RT-7c runtime composition remains NOT_AUTHORIZED
```

## Root-public-only Framework boundary

DRC may import motion APIs only from the Framework root:

```python
from framework import (
    MotionAdapterStatus,
    MotionCapability,
    MotionErrorCode,
    MotionEventType,
    MotionIntent,
    MotionOutcome,
    MotionRequest,
    MotionResult,
    MotionSession,
    MotionSessionInfo,
    create_motion_session,
)
```

The readiness audit verifies the additional v5.5.0 root-public execution
configuration symbols:

```text
MotionAdapterExecutionConfig
get_motion_adapter_execution_capability
resolve_motion_adapter_execution_config
```

DRC must not import Framework submodules, internal VTube Studio composition,
transport modules, `live2d`, provider plugins, `pyvts`, or WebSocket classes.

## Released request shape

`MotionRequest` uses intent-specific fields rather than a generic value field.
DRC must prefer the released factories where available:

```python
MotionRequest.emotion_update("happy")
MotionRequest.expression_change("smile")
MotionRequest.stop_motion()
```

Gesture and reset-expression requests must use the released public constructor
shape and remain provider-neutral. DRC must not expose configured hotkey names or
identifiers as public app data.

## Capability handoff

The accepted required v5.5.0 real-motion scope is:

```text
expression
emotion
gesture
reset_expression
```

Capability reporting is authoritative. DRC must branch from
`capability.supports_intent(...)` and typed result fields.

The following are not required capabilities:

```text
stop_motion: optional; accepted Framework model reported false
speaking_state: do not assume support
idle_motion: do not assume support
look_at: do not assume support
```

Unsupported or unavailable intents must degrade through typed Framework
capabilities/results. They must not trigger a DRC-owned provider workaround.

## Ownership boundary

DRC may own:

```text
lifecycle-to-motion intent selection
app-level character presentation policy
provider-neutral MotionRequest construction
bounded public status presentation
session creation/close orchestration
safe fallback for unsupported or unavailable intent
```

Framework owns:

```text
real-adapter guard evaluation
pyvts dependency and client construction
loopback WebSocket lifecycle
authentication and token use
model and hotkey inventory
configured selector-to-hotkey resolution
timeout and single-flight behavior
provider exception normalization
public capability/result/event normalization
idempotent transport cleanup
```

## Private local configuration boundary

RT-7b does not define or read private VTube Studio values. A later separately
reviewed stage must provide any required endpoint, authentication material, and
configured binding values without placing them in:

```text
tracked source
documentation output
test output
API response
Flutter response
log output
operator evidence committed to Git
release artifacts
```

The vendor directory itself must not contain private token, configuration, or
operator evidence artifacts.

## Portable ignore rule

The repository-shared `.gitignore` must include:

```gitignore
vendor/ai-character-framework-*/
```

A local Git exclude rule is not sufficient as the project contract. The vendor
release stays outside Git history while remaining available to explicit local
verification and runtime composition.

## Exact implementation surface

```text
README.md
.gitignore
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v300_goal_checklist_small_commit.md
docs/v300_rt7b_vendored_fw_v550_readiness.md
scripts/check_v300_rt7b_vendored_fw_v550_readiness.py
```

Total:

```text
exact 8 files
```

## Explicit non-change surface

RT-7b must not change:

```text
backend runtime
backend tests
Flutter runtime
Flutter tests
application dependencies
Framework vendor files
Framework release ZIP or sidecar
private configuration
operator evidence
release metadata
```

RT-7b must not:

```text
import pyvts during root import or closed-guard verification
open a WebSocket
connect to VTube Studio
read a real token
read private endpoint or binding values
load a private model
trigger a hotkey
execute real motion
create a DRC-owned VTS client
```

## Verification

Candidate source verification:

```powershell
python -m compileall -q backend scripts
python scripts\check_v300_rt7b_vendored_fw_v550_readiness.py
python -m pytest -q backend/tests

cd app
flutter analyze
flutter test
cd ..

python scripts\check_v300_rt7b_vendored_fw_v550_readiness.py
git diff --check
```

Strict release-artifact comparison:

```powershell
python scripts\check_v300_rt7b_vendored_fw_v550_readiness.py `
  --require-release-artifact `
  --release-zip <local-fixed-v5.5.0-zip> `
  --release-sidecar <local-fixed-v5.5.0-sha256-sidecar>
```

The strict paths are operator-local inputs and must not be written into tracked
files or command-output evidence committed to the repository.

## Stage decision

```text
RT-7b: IMPLEMENTED / AWAITING_REVIEW
RT-7b acceptance: PENDING_STRICT_RELEASE_ARTIFACT_PROVENANCE
RT-7c runtime composition: NOT_AUTHORIZED
real VTube Studio execution: NOT_AUTHORIZED
commit / push: NOT_AUTHORIZED
```
