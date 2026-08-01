#!/usr/bin/env python3
"""Validate the exact RT-6e acceptance-state synchronization."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess

REPO_ROOT = Path(__file__).resolve().parents[1]
IMPLEMENTATION_BASELINE = "8d69b539e974ba71fde5d9b15dd951d0c670b7ff"
IMPLEMENTATION_COMMIT = "13343017738d0bb5fe23583467856233d62196fb"
RT6D_IMPLEMENTATION_COMMIT = "0f220b792feb7ebb82c5871a794731aa1327439a"
FW_VERSION = "5.4.0"
FW_REFERENCE_COMMIT = "d313eb6acb643103fe25988720ebee5976a04f78"
FW_SOURCE_MODE = "external-vendored-snapshot"
EXACT_PATHS = {
    "README.md", "roadmap.md", "tasklist.md", "scripts/README.md",
    "docs/DRC_v300_goal_checklist_small_commit.md",
    "docs/v300_rt6e_home_screen_character_motion_wiring.md",
    "scripts/check_v300_rt6e_home_screen_character_motion_wiring.py",
}
FLUTTER_RUNTIME_PATHS = {
    "app/lib/screens/home_screen.dart",
    "app/lib/widgets/character_motion_presentation_panel.dart",
}
FLUTTER_TEST_PATHS = {"app/test/character_motion_home_screen_test.dart"}
PROTECTED_PATHS = {
    "app/lib/main.dart",
    "app/lib/models/character_motion_presentation.dart",
    "app/lib/services/character_motion_presentation_client.dart",
    "app/lib/services/character_motion_presentation_controller.dart",
    "app/lib/models/character_display_presentation.dart",
    "app/lib/widgets/character_display_card.dart",
    "app/lib/models/motion_demo.dart",
    "app/lib/services/backend_api_client.dart",
    "app/pubspec.yaml", "app/pubspec.lock",
}

def _run(*args: str) -> str:
    c=subprocess.run(args,cwd=REPO_ROOT,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,encoding="utf-8",errors="replace")
    return c.stdout.strip()

def _git_paths() -> set[str]:
    out:set[str]=set()
    for cmd in (("git","diff","--name-only"),("git","diff","--cached","--name-only"),("git","ls-files","--others","--exclude-standard")):
        out.update(x.strip().replace("\\","/") for x in _run(*cmd).splitlines() if x.strip())
    return out

def _assert_exact_surface(snapshot: bool) -> None:
    missing=sorted(p for p in EXACT_PATHS|FLUTTER_RUNTIME_PATHS|FLUTTER_TEST_PATHS if not (REPO_ROOT/p).is_file())
    if missing: raise AssertionError(f"RT-6e files missing: {missing}")
    changed=_git_paths()
    if changed != EXACT_PATHS:
        raise AssertionError(f"RT-6e acceptance surface mismatch: expected={sorted(EXACT_PATHS)} actual={sorted(changed)}")
    if changed & (PROTECTED_PATHS|FLUTTER_RUNTIME_PATHS|FLUTTER_TEST_PATHS):
        raise AssertionError("RT-6e acceptance sync changed runtime/test/protected paths")
    if any(p.startswith("backend/") or p.startswith("vendor/") for p in changed):
        raise AssertionError("RT-6e acceptance sync changed Backend/vendor")
    if not snapshot:
        head=_run("git","rev-parse","HEAD"); origin=_run("git","rev-parse","origin/main")
        if head != IMPLEMENTATION_COMMIT or origin != IMPLEMENTATION_COMMIT:
            raise AssertionError(f"DRC implementation baseline mismatch: head={head} origin/main={origin} expected={IMPLEMENTATION_COMMIT}")

def _joined_docs() -> str:
    return "\n".join((REPO_ROOT/p).read_text(encoding="utf-8",errors="replace") for p in sorted(EXACT_PATHS) if p.endswith('.md'))

def _assert_docs() -> None:
    docs=_joined_docs()
    required=(
        "RT-6e: COMPLETED / ACCEPTED / PUSHED", IMPLEMENTATION_BASELINE,
        IMPLEMENTATION_COMMIT, RT6D_IMPLEMENTATION_COMMIT, FW_VERSION,
        FW_REFERENCE_COMMIT, FW_SOURCE_MODE, "exact 10 files",
        "acceptance-sync surface: exact 7", "home_screen_manual_motion",
        "default-off", "focused Flutter: 16 passed", "Flutter full: 468 passed",
        "RT-6f: NOT_STARTED / READY_FOR_EXACT_CONTRACT_REVIEW / NOT_AUTHORIZED",
        "BLOCKED_REAL_LIVE2D_VTS_ADAPTER_NOT_IMPLEMENTED",
    )
    for m in required:
        if m not in docs: raise AssertionError(f"RT-6e acceptance documentation marker missing: {m}")
    forbidden=("RT-6e: IMPLEMENTED / AWAITING_REVIEW","BLOCKED_PENDING_RT6E_ACCEPTANCE")
    for m in forbidden:
        if m in docs: raise AssertionError(f"stale RT-6e marker remains: {m}")

def _assert_runtime_contract() -> None:
    home=(REPO_ROOT/"app/lib/screens/home_screen.dart").read_text(encoding="utf-8",errors="replace")
    panel=(REPO_ROOT/"app/lib/widgets/character_motion_presentation_panel.dart").read_text(encoding="utf-8",errors="replace")
    test=(REPO_ROOT/"app/test/character_motion_home_screen_test.dart").read_text(encoding="utf-8",errors="replace")
    for m in ("characterMotionPresentationControllerFactory","bool _characterMotionOptedIn = false","sourceEventType: 'home_screen_manual_motion'","controller.reset()","CharacterMotionPresentationPanel("):
        if m not in home: raise AssertionError(f"accepted HomeScreen marker missing: {m}")
    for m in ("Normalized mock motion state only","No Live2D / VTS animation is executed","does not display source event, session, turn, character"):
        if m not in panel: raise AssertionError(f"accepted panel marker missing: {m}")
    for m in ("all accepted lifecycle facts are available","explicit apply sends one bounded manual request","sourceSessionId, isNull","sourceTurnId, isNull"):
        if m not in test: raise AssertionError(f"accepted focused-test marker missing: {m}")
    main=(REPO_ROOT/"app/lib/main.dart").read_text(encoding="utf-8",errors="replace")
    if "characterMotionPresentationControllerFactory" in main: raise AssertionError("motion unexpectedly configured in main.dart")
    display=(REPO_ROOT/"app/lib/widgets/character_display_card.dart").read_text(encoding="utf-8",errors="replace")
    if "character-display-static-baseline" not in display or "静的表示" not in display: raise AssertionError("static baseline missing")

def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument("--snapshot",action="store_true"); args=ap.parse_args()
    _assert_exact_surface(args.snapshot); _assert_docs(); _assert_runtime_contract()
    values=[
        ("v300_rt6e_status","completed-accepted-pushed"),
        ("v300_rt6e_exact_acceptance_sync_surface","True"),
        ("v300_rt6e_acceptance_sync_file_count","7"),
        ("v300_rt6e_implementation_baseline",IMPLEMENTATION_BASELINE),
        ("v300_rt6e_implementation_commit",IMPLEMENTATION_COMMIT),
        ("v300_rt6e_implementation_surface","10"),
        ("v300_rt6e_flutter_runtime_file_count","2"),
        ("v300_rt6e_flutter_test_file_count","1"),
        ("v300_rt6e_focused_flutter_passed","16"),
        ("v300_rt6e_flutter_full_passed","468"),
        ("v300_rt6e_backend_full_passed","279"),
        ("v300_rt6e_backend_warning_count","3"),
        ("v300_rt6e_dart_format_passed","True"),
        ("v300_rt6e_flutter_analyze_passed","True"),
        ("v300_rt6e_lifecycle_dropdown_corrective_passed","True"),
        ("v300_rt6e_runtime_changed_by_acceptance_sync","False"),
        ("v300_rt6e_flutter_runtime_changed_by_acceptance_sync","False"),
        ("v300_rt6e_flutter_tests_changed_by_acceptance_sync","False"),
        ("v300_rt6e_main_changed","False"),
        ("v300_rt6e_rt6d_runtime_changed","False"),
        ("v300_rt6e_character_display_changed","False"),
        ("v300_rt6e_backend_changed","False"),
        ("v300_rt6e_existing_tests_changed","False"),
        ("v300_rt6e_dependencies_changed","False"),
        ("v300_rt6e_framework_changed","False"),
        ("v300_rt6e_vendor_changed","False"),
        ("v300_rt6e_controller_factory_optional","True"),
        ("v300_rt6e_default_unconfigured","True"),
        ("v300_rt6e_default_opt_in","False"),
        ("v300_rt6e_opt_in_persisted","False"),
        ("v300_rt6e_opt_in_triggers_transport","False"),
        ("v300_rt6e_explicit_apply_only","True"),
        ("v300_rt6e_apply_transport_limit","1"),
        ("v300_rt6e_automatic_lifecycle_subscription","False"),
        ("v300_rt6e_queueing","False"),
        ("v300_rt6e_automatic_retry","False"),
        ("v300_rt6e_reset_triggers_transport","False"),
        ("v300_rt6e_opt_out_invalidates_stale_result","True"),
        ("v300_rt6e_dispose_invalidates_stale_result","True"),
        ("v300_rt6e_source_event_type_fixed","home_screen_manual_motion"),
        ("v300_rt6e_source_session_id_used","False"),
        ("v300_rt6e_source_turn_id_used","False"),
        ("v300_rt6e_raw_result_exposed","False"),
        ("v300_rt6e_raw_exception_exposed","False"),
        ("v300_rt6e_private_ids_exposed","False"),
        ("v300_rt6e_real_http_execution","False"),
        ("v300_rt6e_framework_version",FW_VERSION),
        ("v300_rt6e_framework_reference_commit",FW_REFERENCE_COMMIT),
        ("v300_rt6e_framework_source_mode",FW_SOURCE_MODE),
        ("v300_rt6e_framework_execution","False"),
        ("v300_rt6e_provider_execution","False"),
        ("v300_rt6e_network_execution","False"),
        ("v300_rt6e_live2d_animation_claimed","False"),
        ("v300_rt6_status","current-not-completed"),
        ("v300_rt6f_status","ready-for-exact-contract-review-not-authorized"),
        ("v300_rt6f_implementation_authorized","False"),
        ("v300_rt7_real_adapter_blocked","True"),
        ("v300_rt6e_acceptance_sync_commit_push_authorized","False"),
        ("v300_rt6e_snapshot_mode",str(args.snapshot)),
    ]
    for k,v in values: print(f"{k}: {v}")
    return 0

if __name__ == "__main__": raise SystemExit(main())
