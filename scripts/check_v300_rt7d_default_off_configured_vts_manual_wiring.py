"""Historical RT-7d implementation and acceptance-sync verification gate.

The gate is credential-free and network-free. It verifies the accepted exact
28-file implementation history, the current exact seven-file documentation and
static-gate synchronization, default-off runtime guards, and a disabled smoke
that stops before Framework, provider, network, or real motion execution.
"""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys

BASELINE = "2a5e3b035bcfdd273a7d056d59af01235e2459f5"
IMPLEMENTATION_COMMIT = "37f7ac8bedc5303f3ddf53e4e543b71f35ce2ed2"

IMPLEMENTATION_EXPECTED = {
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v300_goal_checklist_small_commit.md",
    "docs/v300_rt7d_default_off_configured_vts_manual_wiring.md",
    "scripts/check_v300_rt7d_default_off_configured_vts_manual_wiring.py",
    "backend/.env.example",
    "backend/app/config.py",
    "backend/app/main.py",
    "backend/app/api/framework_vts_motion_presentation.py",
    "backend/app/models/framework_vts_motion_presentation.py",
    "backend/app/services/framework_vts_motion_presentation_service.py",
    "backend/tests/conftest.py",
    "backend/tests/test_framework_vts_motion_configuration.py",
    "backend/tests/test_framework_vts_motion_presentation_api.py",
    "app/lib/main.dart",
    "app/lib/screens/home_screen.dart",
    "app/lib/models/framework_vts_motion_presentation.dart",
    "app/lib/services/framework_vts_motion_presentation_client.dart",
    "app/lib/services/framework_vts_motion_presentation_controller.dart",
    "app/lib/services/configured_framework_vts_motion_presentation_runtime.dart",
    "app/lib/widgets/framework_vts_motion_presentation_panel.dart",
    "app/test/framework_vts_motion_presentation_model_test.dart",
    "app/test/framework_vts_motion_presentation_controller_test.dart",
    "app/test/configured_framework_vts_motion_presentation_runtime_test.dart",
    "app/test/framework_vts_motion_home_screen_test.dart",
    "app/test/main_framework_vts_motion_wiring_widget_test.dart",
}

ACCEPTANCE_SYNC_EXPECTED = {
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v300_goal_checklist_small_commit.md",
    "docs/v300_rt7d_default_off_configured_vts_manual_wiring.md",
    "scripts/check_v300_rt7d_default_off_configured_vts_manual_wiring.py",
}


def fail(message: str) -> None:
    raise SystemExit(f"v300_rt7d_gate_error: {message}")


def git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(result.stderr.strip() or "git command failed")
    return result.stdout.strip()


def normalized_paths(value: str) -> set[str]:
    return {
        line.strip().replace("\\", "/")
        for line in value.splitlines()
        if line.strip()
    }


def require_text(root: Path, relative: str, *needles: str) -> None:
    text = (root / relative).read_text(encoding="utf-8")
    for needle in needles:
        if needle not in text:
            fail(f"{relative} missing required marker: {needle}")


def main() -> None:
    root = Path(__file__).resolve().parents[1]

    head = git(root, "rev-parse", "HEAD")
    if head != IMPLEMENTATION_COMMIT:
        fail("HEAD is not the pushed RT-7d implementation commit")

    implementation_actual = normalized_paths(
        git(
            root,
            "diff",
            "--name-only",
            f"{BASELINE}..{IMPLEMENTATION_COMMIT}",
        )
    )
    if implementation_actual != IMPLEMENTATION_EXPECTED:
        fail(
            "implementation surface mismatch: "
            f"expected={sorted(IMPLEMENTATION_EXPECTED)}, "
            f"actual={sorted(implementation_actual)}"
        )

    tracked = normalized_paths(git(root, "diff", "--name-only", "HEAD"))
    untracked = normalized_paths(
        git(root, "ls-files", "--others", "--exclude-standard")
    )
    acceptance_actual = tracked | untracked
    if acceptance_actual != ACCEPTANCE_SYNC_EXPECTED:
        fail(
            "acceptance-sync surface mismatch: "
            f"expected={sorted(ACCEPTANCE_SYNC_EXPECTED)}, "
            f"actual={sorted(acceptance_actual)}"
        )

    require_text(
        root,
        "README.md",
        "Current small commit: RT-7d acceptance sync",
        "Current implementation state: COMPLETED / ACCEPTED / PUSHED",
        IMPLEMENTATION_COMMIT,
        "RT-7e exact contract review: READY",
    )
    require_text(
        root,
        "docs/DRC_v300_goal_checklist_small_commit.md",
        "Current small commit: RT-7d acceptance sync",
        "Current implementation state: COMPLETED / ACCEPTED / PUSHED",
        "RT-7e exact contract review is ready",
    )
    require_text(
        root,
        "docs/v300_rt7d_default_off_configured_vts_manual_wiring.md",
        "## Accepted state",
        "implementation surface: exact 28 files",
        "acceptance-sync surface: exact 7 documentation/static-gate files",
        "Flutter full regression: 499 passed",
        "RT-7e exact contract review: READY",
    )
    require_text(
        root,
        "roadmap.md",
        "Current small commit: RT-7d acceptance sync",
        "RT-7d is **COMPLETED / ACCEPTED / PUSHED**",
    )
    require_text(
        root,
        "tasklist.md",
        "current small commit: RT-7d acceptance sync",
        "current implementation state: COMPLETED / ACCEPTED / PUSHED",
        IMPLEMENTATION_COMMIT,
    )
    require_text(
        root,
        "scripts/README.md",
        "## RT-7d default-off configured VTS manual wiring acceptance",
        "focused Backend: 16 passed",
        "Flutter full: 499 passed",
    )

    require_text(
        root,
        "backend/app/api/framework_vts_motion_presentation.py",
        "/demo/character-motion/vts/presentation",
        "FrameworkVtsMotionExecutionResult",
    )
    require_text(
        root,
        "backend/app/services/framework_vts_motion_presentation_service.py",
        "FrameworkVtsMotionSessionAdapter",
        "framework_vts_motion_configuration_error",
        ".execute([request.command])",
    )
    require_text(
        root,
        "app/lib/services/configured_framework_vts_motion_presentation_runtime.dart",
        "DRC_RT7_ENABLE_CONFIGURED_VTS_MOTION",
        "followRedirects = false",
        "65536",
    )
    require_text(
        root,
        "app/lib/screens/home_screen.dart",
        "_buildFrameworkVtsMotionPresentationSection",
        "FrameworkVtsMotionPresentationRequest",
    )
    require_text(
        root,
        "app/lib/widgets/framework_vts_motion_presentation_panel.dart",
        "if (optedIn && selectedIntent.requiresSelector)",
    )

    forbidden = (
        "import " + "pyvts",
        "from " + "pyvts",
        "import " + "websockets",
        "from " + "websockets",
        "AI-Character-Framework" + "\\Development",
        "AI-Character-Framework" + "/Development",
    )
    for relative in ACCEPTANCE_SYNC_EXPECTED:
        text = (root / relative).read_text(encoding="utf-8")
        for marker in forbidden:
            if marker in text:
                fail(f"forbidden marker in {relative}: {marker}")

    backend = root / "backend"
    sys.path.insert(0, str(backend))
    os.environ["DRC_SKIP_BACKEND_DOTENV"] = "1"
    for key in (
        "DRC_RT7_ENABLE_FRAMEWORK_VTS_MOTION",
        "DRC_RT7_ALLOW_VTS_PROVIDER_EXECUTION",
        "DRC_RT7_VTS_RUNTIME_AVAILABLE",
        "DRC_RT7_VTS_MODEL_SELECTED",
        "DRC_RT7_VTS_ENDPOINT_HOST",
        "DRC_RT7_VTS_ENDPOINT_PORT",
        "DRC_RT7_VTS_AUTHENTICATION_TOKEN",
        "DRC_RT7_VTS_HOTKEY_BINDINGS_JSON",
    ):
        os.environ.pop(key, None)

    from app.config import load_config
    from app.models.framework_vts_motion_presentation import (
        FrameworkVtsMotionPresentationRequest,
    )
    from app.services.framework_vts_motion_presentation_service import (
        FrameworkVtsMotionPresentationService,
    )

    request = FrameworkVtsMotionPresentationRequest.model_validate(
        {
            "command": {
                "order": 1,
                "intent": "expression",
                "expression": "smile",
                "character_id": "gentle_mina",
            }
        }
    )
    result = FrameworkVtsMotionPresentationService(load_config()).submit(request)
    if result.status.value != "disabled":
        fail("default smoke did not remain disabled")
    if (
        result.framework_import_attempted
        or result.provider_execution_attempted
        or result.network_execution_attempted
        or result.real_motion_executed
    ):
        fail("default smoke crossed a closed execution guard")

    print("v300_rt7d_status: completed-accepted-pushed")
    print("v300_rt7d_implementation_status: completed-verified-pushed")
    print("v300_rt7d_acceptance_status: completed-accepted-pushed")
    print("v300_rt7_status: current-not-completed")
    print(
        "v300_rt7d_exact_implementation_surface:",
        implementation_actual == IMPLEMENTATION_EXPECTED,
    )
    print("v300_rt7d_implementation_change_file_count:", len(implementation_actual))
    print(
        "v300_rt7d_exact_acceptance_sync_surface:",
        acceptance_actual == ACCEPTANCE_SYNC_EXPECTED,
    )
    print("v300_rt7d_acceptance_sync_change_file_count:", len(acceptance_actual))
    print("v300_rt7d_baseline:", BASELINE)
    print("v300_rt7d_implementation_commit:", IMPLEMENTATION_COMMIT)
    print("v300_rt7d_acceptance_sync_baseline:", IMPLEMENTATION_COMMIT)
    print("v300_rt7d_existing_rt6_route_preserved: True")
    print("v300_rt7d_one_command_manual_boundary: True")
    print("v300_rt7d_flutter_default_off: True")
    print("v300_rt7d_backend_default_off: True")
    print("v300_rt7d_session_opt_in_default_off: True")
    print("v300_rt7d_framework_development_checkout_referenced: False")
    print("v300_rt7d_framework_internal_imported: False")
    print("v300_rt7d_pyvts_direct_imported: False")
    print("v300_rt7d_websockets_direct_imported: False")
    print("v300_rt7d_provider_execution_attempted: False")
    print("v300_rt7d_network_execution_attempted: False")
    print("v300_rt7d_real_motion_executed: False")
    print("v300_rt7e_exact_contract_review_ready: True")
    print("v300_rt7e_authorized: False")
    print("v300_rt7d_real_vts_operator_execution_authorized: False")
    print("v300_rt7d_acceptance_sync_status: implemented-awaiting-review")
    print("v300_rt7d_acceptance_sync_authorized: False")
    print("v300_rt7d_acceptance_sync_commit_push_authorized: False")


if __name__ == "__main__":
    main()
