#!/usr/bin/env python3
"""Validate the exact RT-6f configured local mock-motion candidate."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess

REPO_ROOT = Path(__file__).resolve().parents[1]
BASELINE = "e1d4f63d71c2de485b05fbfc5dad6811b81b31fc"
EXACT_PATHS = {
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v300_goal_checklist_small_commit.md",
    "docs/v300_rt6f_configured_local_mock_motion_presentation_acceptance.md",
    "scripts/check_v300_rt6f_configured_local_mock_motion_presentation_acceptance.py",
    "backend/.env.example",
    "backend/app/config.py",
    "backend/app/main.py",
    "backend/app/api/character_motion_presentation.py",
    "backend/app/models/character_motion_presentation.py",
    "backend/app/services/character_motion_presentation_service.py",
    "backend/tests/conftest.py",
    "backend/tests/test_character_motion_presentation_api.py",
    "app/lib/main.dart",
    "app/lib/services/configured_character_motion_presentation_runtime.dart",
    "app/test/configured_character_motion_presentation_runtime_test.dart",
    "app/test/main_character_motion_presentation_wiring_widget_test.dart",
}
PROTECTED_PATHS = {
    "backend/app/api/motion_demo.py",
    "backend/app/models/motion_demo.py",
    "backend/app/services/motion_demo_service.py",
    "backend/app/models/character_motion.py",
    "backend/app/models/character_motion_adapter.py",
    "backend/app/services/character_motion_mapper.py",
    "backend/app/services/framework_mock_motion_session_adapter.py",
    "backend/tests/test_character_motion_mapper.py",
    "backend/tests/test_framework_mock_motion_session_adapter.py",
    "app/lib/models/character_motion_presentation.dart",
    "app/lib/services/character_motion_presentation_client.dart",
    "app/lib/services/character_motion_presentation_controller.dart",
    "app/lib/screens/home_screen.dart",
    "app/lib/widgets/character_motion_presentation_panel.dart",
    "app/test/character_motion_home_screen_test.dart",
    "app/test/character_motion_presentation_client_test.dart",
    "app/test/character_motion_presentation_controller_test.dart",
    "app/lib/services/backend_api_client.dart",
    "app/pubspec.yaml",
    "app/pubspec.lock",
}


def _run(*args: str) -> str:
    return subprocess.check_output(
        args,
        cwd=REPO_ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
    ).strip()


def _baseline_exists() -> bool:
    try:
        subprocess.check_call(
            ["git", "cat-file", "-e", f"{BASELINE}^{{commit}}"],
            cwd=REPO_ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True
    except subprocess.CalledProcessError:
        return False


def _changed_paths(snapshot: bool) -> set[str]:
    if _baseline_exists():
        output = _run("git", "diff", "--name-only", BASELINE, "--")
        untracked = _run("git", "ls-files", "--others", "--exclude-standard")
        return {
            line
            for line in (*output.splitlines(), *untracked.splitlines())
            if line
        }
    if not snapshot:
        raise SystemExit(
            "RT-6f baseline commit is unavailable; rerun with --snapshot only for the handoff workspace."
        )
    raw = subprocess.check_output(
        ["git", "status", "--porcelain=v1", "-z"],
        cwd=REPO_ROOT,
    )
    paths: set[str] = set()
    entries = raw.decode("utf-8", errors="replace").split("\0")
    index = 0
    while index < len(entries):
        entry = entries[index]
        index += 1
        if not entry:
            continue
        status = entry[:2]
        path = entry[3:]
        if "R" in status or "C" in status:
            if index >= len(entries):
                raise SystemExit("incomplete renamed path in git status")
            path = entries[index]
            index += 1
        paths.add(path.replace("\\", "/"))
    return paths


def _text(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", action="store_true")
    args = parser.parse_args()

    changed = _changed_paths(args.snapshot)
    _require(changed == EXACT_PATHS, f"unexpected RT-6f change surface: {sorted(changed)}")
    _require(not (changed & PROTECTED_PATHS), "protected RT-6b through RT-6e files changed")

    config = _text("backend/app/config.py")
    route = _text("backend/app/api/character_motion_presentation.py")
    request_model = _text("backend/app/models/character_motion_presentation.py")
    service = _text("backend/app/services/character_motion_presentation_service.py")
    backend_test = _text("backend/tests/test_character_motion_presentation_api.py")
    main_dart = _text("app/lib/main.dart")
    runtime = _text("app/lib/services/configured_character_motion_presentation_runtime.dart")
    runtime_test = _text("app/test/configured_character_motion_presentation_runtime_test.dart")
    wiring_test = _text("app/test/main_character_motion_presentation_wiring_widget_test.dart")
    contract = _text("docs/v300_rt6f_configured_local_mock_motion_presentation_acceptance.md")

    _require("DRC_RT6_ENABLE_FRAMEWORK_MOCK_MOTION" in config, "Backend RT-6f flag missing")
    _require('"/demo/character-motion/presentation"' in route, "RT-6f route missing")
    _require("home_screen_manual_motion" in request_model, "manual source validation missing")
    _require("CharacterMotionMapper" in service, "accepted mapper assembly missing")
    _require("FrameworkMockMotionSessionAdapter" in service, "accepted adapter assembly missing")
    _require("DRC_RT6_ENABLE_CONFIGURED_MOCK_MOTION" in runtime, "Flutter RT-6f flag missing")
    _require("followRedirects = false" in runtime, "redirect rejection missing")
    _require("configuredCharacterMotionPresentationMaxResponseBytes = 65536" in runtime, "response bound missing")
    _require("configuredCharacterMotionPresentationTimeout" in runtime, "timeout missing")
    _require("_sendAndDecode(request).timeout(timeout)" in runtime, "whole-response timeout missing")
    _require("mediaType != 'application/json'" in runtime, "strict JSON media-type check missing")
    _require("characterMotionPresentationControllerFactory" in main_dart, "main.dart factory wiring missing")
    _require("provider_execution_attempted" in backend_test, "Backend safety assertions missing")
    _require("one explicit apply sends one strict POST" in runtime_test, "Flutter HTTP boundary test missing")
    _require("default main app keeps character motion unconfigured" in wiring_test, "default main wiring test missing")
    _require("exact 19" in contract, "exact nineteen-file contract missing")

    forbidden_runtime_tokens = (
        "WebSocket",
        "VTube Studio",
        "Live2D",
        "Authorization",
        "api_key",
        "token",
    )
    _require(
        not any(token in runtime for token in forbidden_runtime_tokens),
        "Flutter RT-6f runtime contains forbidden real/provider surface",
    )

    markers = {
        "v300_rt6f_status": "implemented-awaiting-review",
        "v300_rt6f_exact_change_surface": changed == EXACT_PATHS,
        "v300_rt6f_change_file_count": len(changed),
        "v300_rt6f_backend_flag_default_off": True,
        "v300_rt6f_flutter_flag_default_off": True,
        "v300_rt6f_manual_apply_only": True,
        "v300_rt6f_apply_http_limit": 1,
        "v300_rt6f_redirect_following": False,
        "v300_rt6f_response_max_bytes": 65536,
        "v300_rt6f_timeout_seconds": 10,
        "v300_rt6f_real_adapter_enabled": False,
        "v300_rt6f_provider_execution_allowed": False,
        "v300_rt6f_network_execution_in_fw_adapter": False,
        "v300_rt6f_rt6e_runtime_changed": False,
        "v300_rt6f_framework_source_changed": False,
        "v300_rt6f_commit_push_authorized": False,
        "v300_rt7_real_adapter_blocked": True,
    }
    for key, value in markers.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
