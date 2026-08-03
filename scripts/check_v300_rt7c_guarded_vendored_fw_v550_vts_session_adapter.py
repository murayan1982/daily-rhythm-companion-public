"""RT-7c guarded vendored FW v5.5.0 VTS acceptance-sync gate.

The gate is credential-free and network-free. It verifies the historical exact
eleven-file implementation, exact four-file strict-boolean corrective, current
exact seven-file documentation/static-gate acceptance sync, fixed vendor and
root-public loading, strict literal-boolean safety, closed guards, and a safe
incomplete-config preflight without provider, network, or real motion execution.
"""

from __future__ import annotations

import argparse
import ast
import importlib
from pathlib import Path
from types import SimpleNamespace
import re
import subprocess
import sys
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
IMPLEMENTATION_BASELINE = "35582f06ca037401b2cef8d97cfc5fc26cd40654"
IMPLEMENTATION_COMMIT = "4a2374854801791caefdf0be8cd246e5a2e9278e"
CORRECTIVE_COMMIT = "484ba17245d24a98407907984b28995b247581fa"
EXPECTED_HEAD = CORRECTIVE_COMMIT
FRAMEWORK_RELEASE = "v5.5.0"
FRAMEWORK_RELEASE_COMMIT = "f56697b6de066b062794ac7bb01330d2d9e91759"
FRAMEWORK_VENDOR_RELATIVE = Path("vendor/ai-character-framework-5.5.0")
FRAMEWORK_VENDOR = ROOT / FRAMEWORK_VENDOR_RELATIVE
FRAMEWORK_RELEASE_ELIGIBLE_FILES = 328

IMPLEMENTATION_PATHS = {
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v300_goal_checklist_small_commit.md",
    "docs/v300_rt7c_guarded_vendored_fw_v550_vts_session_adapter.md",
    "scripts/check_v300_rt7c_guarded_vendored_fw_v550_vts_session_adapter.py",
    "backend/requirements.txt",
    "backend/app/models/framework_vts_motion.py",
    "backend/app/services/framework_vts_motion_session_adapter.py",
    "backend/tests/test_framework_vts_motion_session_adapter.py",
}

CORRECTIVE_PATHS = {
    "backend/app/services/framework_vts_motion_session_adapter.py",
    "backend/tests/test_framework_vts_motion_session_adapter.py",
    "docs/v300_rt7c_guarded_vendored_fw_v550_vts_session_adapter.md",
    "scripts/check_v300_rt7c_guarded_vendored_fw_v550_vts_session_adapter.py",
}

EXACT_PATHS = {
    "README.md",
    "docs/DRC_v300_goal_checklist_small_commit.md",
    "docs/v300_rt7c_guarded_vendored_fw_v550_vts_session_adapter.md",
    "roadmap.md",
    "scripts/README.md",
    "scripts/check_v300_rt7c_guarded_vendored_fw_v550_vts_session_adapter.py",
    "tasklist.md",
}

PROTECTED_PATHS = {
    "backend/requirements.txt",
    "backend/app/models/framework_vts_motion.py",
    "backend/app/services/framework_vts_motion_session_adapter.py",
    "backend/tests/test_framework_vts_motion_session_adapter.py",
    "backend/.env.example",
    "backend/app/config.py",
    "backend/app/main.py",
    "backend/app/api/character_motion_presentation.py",
    "backend/app/models/character_motion.py",
    "backend/app/models/character_motion_adapter.py",
    "backend/app/models/character_motion_presentation.py",
    "backend/app/services/character_motion_mapper.py",
    "backend/app/services/framework_mock_motion_session_adapter.py",
    "backend/app/services/character_motion_presentation_service.py",
    "backend/tests/test_character_motion_mapper.py",
    "backend/tests/test_framework_mock_motion_session_adapter.py",
    "backend/tests/test_character_motion_presentation_api.py",
}

DOC_PATHS = EXACT_PATHS

PRIVATE_BASENAMES = {
    ".env",
    "bootstrap_evidence.json",
    "real_motion_operator_evidence.json",
    "vts_private_config.json",
}

REQUIRED_INTENTS = {
    "expression",
    "emotion",
    "gesture",
    "reset_expression",
}
ALLOWED_INTENTS = REQUIRED_INTENTS | {"stop_motion"}
UNSUPPORTED_ASSUMPTIONS = {
    "speaking_state",
    "idle_motion",
    "look_at",
}


class GateError(RuntimeError):
    """Raised when the exact RT-7c acceptance-sync contract is not satisfied."""


def _run(*args: str, check: bool = True) -> str:
    completed = subprocess.run(
        list(args),
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if check and completed.returncode != 0:
        raise GateError(
            f"{' '.join(args)} failed: "
            f"{completed.stderr.strip() or completed.stdout.strip()}"
        )
    return completed.stdout


def _git(*args: str) -> str:
    return _run("git", *args)


def _text(relative: str) -> str:
    path = ROOT / relative
    if not path.is_file():
        raise GateError(f"required file is missing: {relative}")
    return path.read_text(encoding="utf-8")


def _status_paths() -> set[str]:
    paths: set[str] = set()
    for line in _git("status", "--short", "--untracked-files=normal").splitlines():
        if len(line) < 4:
            raise GateError(f"unexpected git status record: {line!r}")
        path = line[3:].strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        paths.add(path.replace("\\", "/"))
    return paths


def _release_eligible(relative: Path) -> bool:
    parts = tuple(part.lower() for part in relative.parts)
    name = relative.name.lower()
    if ".git" in parts or "__pycache__" in parts:
        return False
    if any(
        part in {".pytest_cache", ".mypy_cache", ".ruff_cache"}
        for part in parts
    ):
        return False
    if parts and parts[0] == "release":
        return False
    if name.endswith((".pyc", ".pyo", ".pyd")):
        return False
    if name == ".env":
        return False
    if name.startswith(".env.") and name != ".env.example":
        return False
    return True


def _vendor_release_files() -> tuple[Path, ...]:
    return tuple(
        sorted(
            (
                path
                for path in FRAMEWORK_VENDOR.rglob("*")
                if path.is_file()
                and _release_eligible(path.relative_to(FRAMEWORK_VENDOR))
            ),
            key=lambda path: path.relative_to(FRAMEWORK_VENDOR).as_posix(),
        )
    )


def _private_vendor_hits(paths: Iterable[Path]) -> tuple[str, ...]:
    hits: list[str] = []
    for path in paths:
        relative = path.relative_to(FRAMEWORK_VENDOR).as_posix()
        lower = relative.lower()
        basename = path.name.lower()
        if (
            lower.startswith("config/tokens/")
            or lower.startswith("operator_evidence/")
            or basename.endswith("_token.json")
            or basename in PRIVATE_BASENAMES
            or (
                basename.startswith(".env.")
                and basename != ".env.example"
            )
        ):
            hits.append(relative)
    return tuple(sorted(hits))


def _assert_git_surface(snapshot: bool) -> set[str]:
    if not snapshot:
        implementation = {
            line.strip().replace("\\", "/")
            for line in _git(
                "diff",
                "--name-only",
                IMPLEMENTATION_BASELINE,
                IMPLEMENTATION_COMMIT,
            ).splitlines()
            if line.strip()
        }
        if implementation != IMPLEMENTATION_PATHS:
            raise GateError(
                "RT-7c pushed implementation surface mismatch: "
                f"expected={sorted(IMPLEMENTATION_PATHS)}, "
                f"actual={sorted(implementation)}"
            )

        corrective = {
            line.strip().replace("\\", "/")
            for line in _git(
                "diff",
                "--name-only",
                IMPLEMENTATION_COMMIT,
                CORRECTIVE_COMMIT,
            ).splitlines()
            if line.strip()
        }
        if corrective != CORRECTIVE_PATHS:
            raise GateError(
                "RT-7c pushed corrective surface mismatch: "
                f"expected={sorted(CORRECTIVE_PATHS)}, "
                f"actual={sorted(corrective)}"
            )

    changed = _status_paths()
    if changed != EXACT_PATHS:
        raise GateError(
            "RT-7c acceptance-sync exact change surface mismatch: "
            f"expected={sorted(EXACT_PATHS)}, actual={sorted(changed)}"
        )
    if changed & PROTECTED_PATHS:
        raise GateError("RT-7c acceptance sync changed a protected path")
    if any(path.startswith("app/") for path in changed):
        raise GateError("RT-7c acceptance sync changed Flutter files")
    if any(path.startswith("vendor/") for path in changed):
        raise GateError("RT-7c acceptance sync changed tracked vendor files")

    if not snapshot:
        head = _git("rev-parse", "HEAD").strip()
        origin = _git("rev-parse", "origin/main").strip()
        if head != CORRECTIVE_COMMIT or origin != CORRECTIVE_COMMIT:
            raise GateError(
                "DRC acceptance-sync baseline mismatch: "
                f"head={head}, origin/main={origin}, "
                f"expected={CORRECTIVE_COMMIT}"
            )
    return changed

def _assert_docs() -> None:
    markers = (
        "RT-7c",
        "COMPLETED / ACCEPTED / PUSHED",
        IMPLEMENTATION_BASELINE,
        IMPLEMENTATION_COMMIT,
        CORRECTIVE_COMMIT,
        "implementation surface: exact 11 files",
        "corrective surface: exact 4 files",
        "acceptance-sync surface: exact 7 documentation/static-gate files",
        "vendor/ai-character-framework-5.5.0",
        "RT-7d exact contract review: READY",
        "RT-7d implementation: NOT_AUTHORIZED",
        "RT-7e: NOT_AUTHORIZED",
        "real VTube Studio execution: NOT_AUTHORIZED",
        "acceptance-sync commit / push: NOT_AUTHORIZED",
    )
    for relative in DOC_PATHS:
        contract = _text(relative)
        for marker in markers:
            if marker not in contract:
                raise GateError(f"{relative} is missing accepted marker: {marker}")

    required_contract = (
        "Framework development checkout: PROHIBITED",
        "Framework internal import: PROHIBITED",
        "pyvts direct import: PROHIBITED",
        "strict-boolean corrective",
        "literal `True`",
        "non-boolean private execution flags rejected: true",
        "non-boolean readiness capability fails closed: true",
        "non-boolean intent capability fails closed: true",
        "retryable requires literal true: true",
        "backend/app/services/framework_vts_motion_session_adapter.py",
        "backend/tests/test_framework_vts_motion_session_adapter.py",
        "pyvts==0.3.3",
        "websockets==16.0",
        "focused Backend: 31 passed",
        "Backend full: 320 passed",
        "Flutter full: 483 passed",
    )
    contract = _text(
        "docs/v300_rt7c_guarded_vendored_fw_v550_vts_session_adapter.md"
    )
    for marker in required_contract:
        if marker not in contract:
            raise GateError(f"RT-7c accepted contract is missing marker: {marker}")

def _assert_requirements() -> None:
    lines = [
        line.strip()
        for line in _text("backend/requirements.txt").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    for pin in ("pyvts==0.3.3", "websockets==16.0"):
        if lines.count(pin) != 1:
            raise GateError(f"required exact dependency pin is missing/duplicated: {pin}")
    if any(
        line.startswith("pyvts") and line != "pyvts==0.3.3"
        for line in lines
    ):
        raise GateError("conflicting pyvts dependency is present")
    if any(
        line.startswith("websockets") and line != "websockets==16.0"
        for line in lines
    ):
        raise GateError("conflicting websockets dependency is present")


def _attribute_chain(node: ast.AST) -> str:
    parts: list[str] = []
    current: ast.AST | None = node
    while isinstance(current, ast.Attribute):
        parts.append(current.attr)
        current = current.value
    if isinstance(current, ast.Name):
        parts.append(current.id)
    return ".".join(reversed(parts))


def _assert_service_static_contract() -> None:
    relative = "backend/app/services/framework_vts_motion_session_adapter.py"
    source = _text(relative)
    tree = ast.parse(source, filename=relative)

    imported_modules: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported_modules.append(node.module or "")
        elif isinstance(node, ast.Call):
            chain = _attribute_chain(node.func)
            if chain == "os.chdir":
                raise GateError("RT-7c service changes current working directory")
            if chain in {
                "sys.path.append",
                "sys.path.extend",
                "sys.path.insert",
                "sys.path.remove",
            }:
                raise GateError("RT-7c service mutates sys.path")

    prohibited_imports = tuple(
        name
        for name in imported_modules
        if (
            name == "framework"
            or name.startswith("framework.")
            or name == "pyvts"
            or name.startswith("pyvts.")
            or name == "websockets"
            or name.startswith("websockets.")
        )
    )
    if prohibited_imports:
        raise GateError(
            "RT-7c service contains prohibited direct imports: "
            f"{prohibited_imports}"
        )

    required_source_markers = (
        'Path("vendor/ai-character-framework-5.5.0")',
        "importlib.util.spec_from_file_location",
        "PathFinder.find_spec",
        "sys.meta_path.insert",
        "_assert_vendor_module_origins",
        'adapter="vts"',
        "real_adapter_enabled=True",
        "allow_provider_execution=True",
        "vts_endpoint_host=",
        "vts_authentication_token=",
        "vts_hotkey_bindings=",
        "MotionSessionInfo",
        "supports_intent",
        "COMPLETED_WITH_OPTIONAL_SKIP",
        "repr=False",
        "type(value) is not bool",
        "supports_intent(public_intent) is True",
        'getattr(raw_result, "retryable", False) is True',
    )
    for marker in required_source_markers:
        if marker not in source:
            raise GateError(f"RT-7c service is missing marker: {marker}")

    prohibited_source = (
        "FRAMEWORK_PROJECT_ROOT",
        "FRAMEWORK_ROOT",
        "framework_project_root",
        "project_root=str(",
        "from framework.",
        "import pyvts",
        "import websockets",
        "sys.path.insert",
        "sys.path.append",
        "sys.path.remove",
        "os.chdir",
    )
    for marker in prohibited_source:
        if marker in source:
            raise GateError(f"RT-7c service contains prohibited marker: {marker}")
    if "bool(" in source:
        raise GateError("RT-7c service contains implicit bool conversion")


def _assert_model_contract() -> None:
    relative = "backend/app/models/framework_vts_motion.py"
    source = _text(relative)
    tree = ast.parse(source, filename=relative)

    intent_values: set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == "FrameworkVtsMotionIntent":
            for statement in node.body:
                if (
                    isinstance(statement, ast.Assign)
                    and len(statement.targets) == 1
                    and isinstance(statement.value, ast.Constant)
                    and isinstance(statement.value.value, str)
                ):
                    intent_values.add(statement.value.value)

    if intent_values != ALLOWED_INTENTS:
        raise GateError(
            "RT-7c model intent vocabulary mismatch: "
            f"expected={sorted(ALLOWED_INTENTS)}, actual={sorted(intent_values)}"
        )
    if intent_values & UNSUPPORTED_ASSUMPTIONS:
        raise GateError("RT-7c model assumes unsupported released intents")

    for marker in (
        "extra=\"forbid\"",
        "FRAMEWORK_VTS_MOTION_MAX_COMMANDS = 5",
        "FrameworkVtsMotionExecutionResult",
        "network_execution_attempted",
        "real_motion_executed",
    ):
        if marker not in source:
            raise GateError(f"RT-7c model is missing marker: {marker}")


def _assert_test_contract() -> None:
    source = _text("backend/tests/test_framework_vts_motion_session_adapter.py")
    required = (
        "test_disabled_guard_precedes_vendor_and_framework_import",
        "test_provider_execution_guard_precedes_vendor_and_framework_import",
        "test_missing_fixed_vendor_returns_typed_unavailable_without_path",
        "test_unexpected_framework_origin_fails_closed",
        "test_required_four_intents_convert_and_complete_in_order",
        "test_unsupported_required_intent_is_typed_and_not_applied",
        "test_unsupported_stop_motion_is_optional_safe_degradation",
        "test_unreleased_assumptions_are_rejected_by_model",
        "test_preflight_unavailable_stops_before_apply_and_closes",
        "test_apply_exception_is_normalized_and_session_closes",
        "test_close_exception_returns_fixed_cleanup_failure",
        "test_private_config_repr_and_result_do_not_expose_values",
        "test_private_config_rejects_non_boolean_execution_flags",
        "test_non_boolean_readiness_capability_fails_closed_before_apply",
        "test_non_boolean_intent_capability_is_not_supported",
        "test_retryable_requires_literal_true",
    )
    for marker in required:
        if marker not in source:
            raise GateError(f"RT-7c focused tests are missing: {marker}")


def _candidate_added_text(relative: str) -> str:
    """Return only candidate-added text for privacy review.

    Historical documentation may contain old local operator command examples.
    Existing files are reviewed only for lines added relative to the fixed
    baseline. Newly introduced files are reviewed in full.
    """

    tracked_at_baseline = relative in {
        line.strip().replace("\\", "/")
        for line in _git(
            "ls-tree",
            "-r",
            "--name-only",
            EXPECTED_HEAD,
            "--",
            relative,
        ).splitlines()
        if line.strip()
    }
    if not tracked_at_baseline:
        return _text(relative)

    diff = _git(
        "diff",
        "--no-ext-diff",
        "--unified=0",
        EXPECTED_HEAD,
        "--",
        relative,
    )
    added: list[str] = []
    for line in diff.splitlines():
        if line.startswith("+++"):
            continue
        if line.startswith("+"):
            added.append(line[1:])
    return "\n".join(added)


def _assert_changed_content_privacy() -> None:
    drive_path = re.compile(r"(?i)\b[a-z]:[\\/]")
    secret_assignment = re.compile(
        r"(?i)(authentication_token|password|secret)\s*[:=]\s*[\"']"
        r"(?!test-|must-not-escape|<redacted>|)[^\"']{12,}[\"']"
    )
    for relative in EXACT_PATHS:
        text = _candidate_added_text(relative)
        if drive_path.search(text):
            raise GateError(
                f"private/local drive path added by RT-7c in {relative}"
            )
        if secret_assignment.search(text):
            raise GateError(
                f"credential-like literal added by RT-7c in {relative}"
            )


def _assert_vendor() -> int:
    if not FRAMEWORK_VENDOR.is_dir():
        raise GateError("fixed Framework v5.5.0 vendor directory is missing")
    if (FRAMEWORK_VENDOR / ".git").exists():
        raise GateError("fixed Framework vendor contains Git metadata")

    release_files = _vendor_release_files()
    if len(release_files) != FRAMEWORK_RELEASE_ELIGIBLE_FILES:
        raise GateError(
            "fixed Framework vendor release-eligible file count mismatch: "
            f"expected={FRAMEWORK_RELEASE_ELIGIBLE_FILES}, "
            f"actual={len(release_files)}"
        )
    private_hits = _private_vendor_hits(FRAMEWORK_VENDOR.rglob("*"))
    if private_hits:
        raise GateError(
            "fixed Framework vendor contains private artifacts: "
            f"{private_hits[:3]}"
        )
    return len(release_files)


def _strict_boolean_smoke() -> dict[str, bool]:
    sys.path.insert(0, str(ROOT / "backend"))
    try:
        model = importlib.import_module("app.models.framework_vts_motion")
        service = importlib.import_module(
            "app.services.framework_vts_motion_session_adapter"
        )

        invalid_values = ("false", "true", 1, 0, None, object())
        for field_name in (
            "enabled",
            "allow_provider_execution",
            "runtime_available",
            "model_selected",
        ):
            for invalid in invalid_values:
                try:
                    service.FrameworkVtsMotionPrivateConfig(
                        **{field_name: invalid}
                    )
                except TypeError as error:
                    expected = f"{field_name} must be a literal bool"
                    if str(error) != expected:
                        raise GateError(
                            "RT-7c strict config returned unexpected error: "
                            f"{error}"
                        ) from error
                else:
                    raise GateError(
                        "RT-7c accepted a non-boolean execution flag: "
                        f"field={field_name}, value_type={type(invalid).__name__}"
                    )

        readiness_cases = (
            SimpleNamespace(
                adapter_status="configured",
                supports_motion_session="false",
                supports_real_adapter=True,
            ),
            SimpleNamespace(
                adapter_status="configured",
                supports_motion_session=True,
                supports_real_adapter="false",
            ),
        )
        if any(
            service._is_ready_real_vts_capability(capability)
            for capability in readiness_cases
        ):
            raise GateError("RT-7c non-boolean readiness capability did not fail closed")

        public_intent = SimpleNamespace(
            EXPRESSION=object(),
            EMOTION=object(),
            GESTURE=object(),
            RESET_EXPRESSION=object(),
            STOP_MOTION=object(),
        )
        public_api = SimpleNamespace(motion_intent=public_intent)
        callable_capability = SimpleNamespace(
            supports_intent=lambda intent: "false"
        )
        attribute_capability = SimpleNamespace(
            supports_intent=None,
            supports_expression="false",
        )
        for capability in (callable_capability, attribute_capability):
            if service._supports_command(
                public_api,
                capability,
                model.FrameworkVtsMotionIntent.EXPRESSION,
            ):
                raise GateError(
                    "RT-7c non-boolean intent capability did not fail closed"
                )

        command = model.FrameworkVtsMotionCommand(
            order=1,
            intent=model.FrameworkVtsMotionIntent.RESET_EXPRESSION,
        )
        normalized = service._normalize_command_result(
            command,
            SimpleNamespace(
                outcome="failed",
                state="error",
                adapter_status="configured",
                public_error_code="provider_error",
                retryable="false",
            ),
        )
        if normalized.retryable:
            raise GateError("RT-7c non-boolean retryable value was accepted")
        literal_true = service._normalize_command_result(
            command,
            SimpleNamespace(
                outcome="failed",
                state="error",
                adapter_status="configured",
                public_error_code="provider_error",
                retryable=True,
            ),
        )
        if literal_true.retryable is not True:
            raise GateError("RT-7c literal True retryable value was not retained")

        return {
            "config_flags_rejected": True,
            "readiness_failed_closed": True,
            "intent_failed_closed": True,
            "retryable_literal_true_only": True,
        }
    finally:
        try:
            sys.path.remove(str(ROOT / "backend"))
        except ValueError:
            pass


def _safe_runtime_smoke() -> dict[str, object]:
    sys.path.insert(0, str(ROOT / "backend"))
    try:
        model = importlib.import_module("app.models.framework_vts_motion")
        service = importlib.import_module(
            "app.services.framework_vts_motion_session_adapter"
        )

        command = model.FrameworkVtsMotionCommand(
            order=1,
            intent=model.FrameworkVtsMotionIntent.RESET_EXPRESSION,
        )

        disabled = service.FrameworkVtsMotionSessionAdapter(
            service.FrameworkVtsMotionPrivateConfig()
        ).execute([command])
        if disabled.status.value != "disabled":
            raise GateError("RT-7c disabled smoke did not remain disabled")
        if disabled.framework_import_attempted:
            raise GateError("RT-7c disabled smoke imported Framework")

        closed = service.FrameworkVtsMotionSessionAdapter(
            service.FrameworkVtsMotionPrivateConfig(
                enabled=True,
                allow_provider_execution=False,
            )
        ).execute([command])
        if closed.status.value != "provider_execution_not_allowed":
            raise GateError("RT-7c closed provider guard returned wrong status")
        if closed.framework_import_attempted:
            raise GateError("RT-7c closed provider guard imported Framework")

        incomplete = service.FrameworkVtsMotionSessionAdapter(
            service.FrameworkVtsMotionPrivateConfig(
                enabled=True,
                allow_provider_execution=True,
                runtime_available=False,
                model_selected=False,
            )
        ).execute([command])
        if incomplete.status.value != "unavailable":
            raise GateError(
                "RT-7c incomplete-config smoke did not fail typed unavailable: "
                f"status={incomplete.status.value}, "
                f"reason={incomplete.reason_code}, "
                f"framework_import_attempted="
                f"{incomplete.framework_import_attempted}, "
                f"session_created={incomplete.session_created}, "
                f"session_closed={incomplete.session_closed}"
            )
        if not incomplete.framework_import_attempted:
            raise GateError("RT-7c incomplete-config smoke did not inspect vendor")
        if not incomplete.session_created or not incomplete.session_closed:
            raise GateError(
                "RT-7c incomplete-config smoke did not close the public session"
            )
        if (
            incomplete.provider_execution_attempted
            or incomplete.network_execution_attempted
            or incomplete.real_motion_executed
        ):
            raise GateError(
                "RT-7c incomplete-config smoke crossed the closed execution guard"
            )
        if "pyvts" in sys.modules:
            raise GateError("RT-7c safe smoke imported pyvts")

        return {
            "disabled": disabled.status.value,
            "closed_guard": closed.status.value,
            "incomplete": incomplete.status.value,
            "framework_imported_from_vendor": True,
            "session_closed": incomplete.session_closed,
            "pyvts_imported": "pyvts" in sys.modules,
            "provider_execution_attempted": (
                incomplete.provider_execution_attempted
            ),
            "network_execution_attempted": (
                incomplete.network_execution_attempted
            ),
            "real_motion_executed": incomplete.real_motion_executed,
        }
    finally:
        try:
            sys.path.remove(str(ROOT / "backend"))
        except ValueError:
            pass


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--snapshot",
        action="store_true",
        help="Skip HEAD/origin equality for artifact-generation snapshots.",
    )
    args = parser.parse_args()

    try:
        changed = _assert_git_surface(args.snapshot)
        _assert_docs()
        _assert_requirements()
        _assert_service_static_contract()
        _assert_model_contract()
        _assert_test_contract()
        _assert_changed_content_privacy()
        vendor_files = _assert_vendor()
        strict = _strict_boolean_smoke()
        smoke = _safe_runtime_smoke()

        print("v300_rt7c_status: completed-accepted-pushed")
        print("v300_rt7c_implementation_status: completed-verified-pushed")
        print("v300_rt7c_acceptance_status: completed-accepted-pushed")
        print("v300_rt7_status: current-not-completed")
        print("v300_rt7c_exact_implementation_surface: True")
        print("v300_rt7c_implementation_change_file_count: 11")
        print("v300_rt7c_exact_corrective_surface: True")
        print("v300_rt7c_corrective_change_file_count: 4")
        print("v300_rt7c_exact_acceptance_sync_surface: True")
        print(f"v300_rt7c_acceptance_sync_change_file_count: {len(changed)}")
        print(
            "v300_rt7c_implementation_baseline: "
            f"{IMPLEMENTATION_BASELINE}"
        )
        print(f"v300_rt7c_implementation_commit: {IMPLEMENTATION_COMMIT}")
        print(f"v300_rt7c_corrective_baseline: {IMPLEMENTATION_COMMIT}")
        print(f"v300_rt7c_corrective_commit: {CORRECTIVE_COMMIT}")
        print(f"v300_rt7c_acceptance_sync_baseline: {CORRECTIVE_COMMIT}")
        print(f"v300_rt7c_framework_release: {FRAMEWORK_RELEASE}")
        print(
            "v300_rt7c_framework_release_commit: "
            f"{FRAMEWORK_RELEASE_COMMIT}"
        )
        print(
            "v300_rt7c_framework_vendor_path: "
            f"{FRAMEWORK_VENDOR_RELATIVE.as_posix()}"
        )
        print("v300_rt7c_framework_development_checkout_referenced: False")
        print("v300_rt7c_framework_internal_imported: False")
        print("v300_rt7c_cwd_changed: False")
        print("v300_rt7c_sys_path_workaround_used: False")
        print(f"v300_rt7c_vendor_release_eligible_file_count: {vendor_files}")
        print("v300_rt7c_dependency_pyvts_pin_exact: True")
        print("v300_rt7c_dependency_websockets_pin_exact: True")
        print("v300_rt7c_allowed_intents_exact: True")
        print("v300_rt7c_required_expression: True")
        print("v300_rt7c_required_emotion: True")
        print("v300_rt7c_required_gesture: True")
        print("v300_rt7c_required_reset_expression: True")
        print("v300_rt7c_stop_motion_optional: True")
        print("v300_rt7c_speaking_state_assumed: False")
        print("v300_rt7c_idle_motion_assumed: False")
        print("v300_rt7c_look_at_assumed: False")
        print(
            "v300_rt7c_non_boolean_config_flags_rejected: "
            f"{strict['config_flags_rejected']}"
        )
        print(
            "v300_rt7c_non_boolean_readiness_fails_closed: "
            f"{strict['readiness_failed_closed']}"
        )
        print(
            "v300_rt7c_non_boolean_intent_fails_closed: "
            f"{strict['intent_failed_closed']}"
        )
        print(
            "v300_rt7c_retryable_requires_literal_true: "
            f"{strict['retryable_literal_true_only']}"
        )
        print(f"v300_rt7c_disabled_smoke_status: {smoke['disabled']}")
        print(
            "v300_rt7c_closed_guard_status: "
            f"{smoke['closed_guard']}"
        )
        print(
            "v300_rt7c_incomplete_config_status: "
            f"{smoke['incomplete']}"
        )
        print(
            "v300_rt7c_framework_origin_is_vendor: "
            f"{smoke['framework_imported_from_vendor']}"
        )
        print(
            "v300_rt7c_incomplete_session_closed: "
            f"{smoke['session_closed']}"
        )
        print(
            "v300_rt7c_pyvts_imported: "
            f"{smoke['pyvts_imported']}"
        )
        print(
            "v300_rt7c_provider_execution_attempted: "
            f"{smoke['provider_execution_attempted']}"
        )
        print(
            "v300_rt7c_network_execution_attempted: "
            f"{smoke['network_execution_attempted']}"
        )
        print(
            "v300_rt7c_real_motion_executed: "
            f"{smoke['real_motion_executed']}"
        )
        print("v300_rt7c_backend_api_changed: False")
        print("v300_rt7c_backend_config_changed: False")
        print("v300_rt7c_existing_rt6_runtime_changed: False")
        print("v300_rt7c_existing_tests_changed: False")
        print("v300_rt7c_flutter_changed: False")
        print("v300_rt7c_vendor_changed: False")
        print("v300_rt7d_exact_contract_review_ready: True")
        print("v300_rt7d_authorized: False")
        print("v300_rt7e_authorized: False")
        print("v300_rt7c_real_vts_operator_execution_authorized: False")
        print("v300_rt7c_acceptance_sync_status: implemented-awaiting-review")
        print("v300_rt7c_acceptance_sync_authorized: False")
        print("v300_rt7c_acceptance_sync_commit_push_authorized: False")
        return 0
    except (GateError, OSError, ValueError, SyntaxError) as error:
        print(f"v300_rt7c_gate_error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
