# Daily Rhythm Companion v3.0.0 RT-7b vendored Framework v5.5.0 readiness

Updated: 2026-08-03

## Accepted state

```text
RT-6: COMPLETED / ACCEPTED / PUSHED
RT-7: CURRENT / NOT_COMPLETED
RT-7a: COMPLETED / ACCEPTED / PUSHED
RT-7b: COMPLETED / ACCEPTED / PUSHED
implementation baseline: 8413c2f08879b34f83496441c6a7e20181486469
implementation commit: c766610ce66a539efaabf4e4026a7c12ad2887c9
implementation surface: exact 8 documentation/static-gate/ignore files
acceptance-sync surface: exact 7 documentation/static-gate files
Framework release: v5.5.0
Framework release commit: f56697b6de066b062794ac7bb01330d2d9e91759
Framework local source: vendor/ai-character-framework-5.5.0
RT-7c exact contract review: READY
RT-7c runtime composition: NOT_AUTHORIZED
real VTube Studio execution: NOT_AUTHORIZED
acceptance-sync commit / push: NOT_AUTHORIZED
```

## Accepted result

RT-7b fixes and accepts the only local Framework source boundary that DRC may
use for the later RT-7 real-motion integration:

```text
vendor/ai-character-framework-5.5.0
```

The fixed vendor was rehydrated from the official Framework v5.5.0 GitHub
Release asset. The official ZIP and sidecar were verification inputs only and
remain outside tracked DRC source.

The accepted implementation does not add a Backend real-motion route, private
configuration loader, VTube Studio session, Flutter behavior, provider
execution, operator evidence, or real motion.

## Accepted verification

```text
Python compileall: PASS
dedicated RT-7b gate before regression: PASS
Backend full: 289 passed
Backend dependency warnings: 1 existing Starlette/httpx deprecation warning
Flutter analyze: No issues found
Flutter full: 483 passed
dedicated RT-7b gate after regression: PASS
exact implementation surface: 8 files
CRLF-aware git diff --check: PASS
explicit implementation commit approval: ACCEPTED
implementation commit: c766610ce66a539efaabf4e4026a7c12ad2887c9
implementation push: COMPLETED
post-push HEAD / origin/main: c766610ce66a539efaabf4e4026a7c12ad2887c9
post-push DRC working tree: clean
```

The dependency warning did not fail the Backend regression suite.

## Official release provenance accepted

```text
Framework release: v5.5.0
Framework release commit: f56697b6de066b062794ac7bb01330d2d9e91759
official ZIP: ai-character-framework_v5.5.0.zip
official ZIP SHA-256: d6603003ea33abd5d543d85d4437f71e00571a86a9ed06a902506e6be3a9b5fe
official ZIP size: 681335 bytes
official ZIP file count: 328
official sidecar digest: matched
ZIP integrity: PASS
duplicate ZIP members: absent
vendor / ZIP membership: exact
vendor / ZIP file bytes: exact
private artifact hits: 0
vendor Git metadata: absent
```

The physical vendor file count is informational because excluded local Python
cache files may appear after later imports. The release-eligible membership
contract remains 328 files.

## Root-public-only Framework boundary

DRC may import motion APIs only from the Framework root:

```python
from framework import (
    MotionAdapterExecutionConfig,
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
    get_motion_adapter_execution_capability,
    resolve_motion_adapter_execution_config,
)
```

DRC must not import Framework submodules, provider transports, `pyvts`,
WebSocket classes, or private implementation modules. Checkout-relative,
current-working-directory, moving-branch, and ad-hoc fallback imports remain
outside the accepted contract.

## Accepted request and capability boundary

`MotionRequest` uses intent-specific public fields and factories. The accepted
required real-motion intent vocabulary is:

```text
expression
emotion
gesture
reset_expression
```

The following remain outside the required capability set:

```text
stop_motion: optional
speaking_state: support must not be assumed
idle_motion: support must not be assumed
look_at: support must not be assumed
```

Capability reporting and typed results are authoritative. Unsupported or
unavailable intents must remain provider-neutral and must not trigger a
DRC-owned provider workaround.

## Closed-guard acceptance

The accepted source-safe audit confirmed:

```text
Framework origin is below vendor/ai-character-framework-5.5.0
Motion API version is 5.5.0
root-public exports are complete
mock emotion motion completes
closed provider-execution guard reports provider_execution_not_allowed
closed guard reports real adapter unsupported
pyvts is not imported
network execution is false
real motion execution is false
```

## Ownership boundary

DRC may own:

```text
lifecycle-to-motion intent selection
app-level character presentation policy
provider-neutral MotionRequest construction
bounded public status presentation
session creation and close orchestration
safe fallback for unsupported or unavailable intents
```

Framework owns:

```text
real-adapter guard evaluation
provider dependency and client construction
loopback WebSocket lifecycle
authentication and token use
model and hotkey inventory
configured selector-to-hotkey resolution
timeout and single-flight behavior
provider exception normalization
public capability/result/event normalization
transport cleanup
```

## Private local configuration boundary

RT-7b reads no private VTube Studio values. Any later configuration stage must
keep endpoint values, authentication material, private model identifiers, raw
provider payloads, screenshots, and operator evidence outside tracked source,
API responses, Flutter responses, logs, and release artifacts.

The vendor directory must not contain private token, configuration, or evidence
artifacts.

## Portable vendor boundary

The repository-shared ignore rule remains:

```gitignore
vendor/ai-character-framework-*/
```

The vendor release stays outside Git history while remaining available to
explicit local verification and later separately authorized runtime
composition.

## Exact implementation surface

```text
.gitignore
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v300_goal_checklist_small_commit.md
docs/v300_rt7b_vendored_fw_v550_readiness.md
scripts/check_v300_rt7b_vendored_fw_v550_readiness.py
```

No Backend runtime, Flutter runtime, existing test, dependency, or tracked
Framework vendor file changed.

## Exact acceptance-sync surface

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v300_goal_checklist_small_commit.md
docs/v300_rt7b_vendored_fw_v550_readiness.md
scripts/check_v300_rt7b_vendored_fw_v550_readiness.py
```

`.gitignore` is not changed by the acceptance sync because the portable vendor
rule was already accepted in the RT-7b implementation commit.

## Explicit non-actions

This acceptance sync does not:

- access or infer a Framework development checkout;
- download or rebuild the official release artifact;
- read a private token, configuration, model, or evidence file;
- import `pyvts` or open a WebSocket;
- execute network or real motion;
- add Backend or Flutter runtime behavior;
- authorize RT-7c implementation;
- commit or push itself.

## Next boundary

```text
RT-7: CURRENT / NOT_COMPLETED
RT-7b: COMPLETED / ACCEPTED / PUSHED
RT-7c exact contract review: READY
RT-7c runtime implementation: NOT_AUTHORIZED
real VTube Studio execution: NOT_AUTHORIZED
```

Detailed historical implementation and accepted evidence remain represented by
this file and the dedicated gate:

```text
docs/v300_rt7b_vendored_fw_v550_readiness.md
scripts/check_v300_rt7b_vendored_fw_v550_readiness.py
```
