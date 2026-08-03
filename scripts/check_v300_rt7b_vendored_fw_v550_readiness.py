"""RT-7b vendored Framework v5.5.0 acceptance-sync gate.

This gate is local, credential-free, provider-free, network-free, and
real-motion-free. The only Framework source it imports is the fixed DRC vendor.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import os
import pathlib
import stat
import subprocess
import sys
import zipfile
from collections.abc import Iterable

ROOT = pathlib.Path(__file__).resolve().parents[1]
EXPECTED_HEAD = "c766610ce66a539efaabf4e4026a7c12ad2887c9"
IMPLEMENTATION_BASELINE = "8413c2f08879b34f83496441c6a7e20181486469"
FRAMEWORK_RELEASE = "v5.5.0"
FRAMEWORK_RELEASE_COMMIT = "f56697b6de066b062794ac7bb01330d2d9e91759"
FRAMEWORK_VENDOR_RELATIVE = pathlib.Path("vendor/ai-character-framework-5.5.0")
FRAMEWORK_VENDOR = ROOT / FRAMEWORK_VENDOR_RELATIVE
OFFICIAL_ZIP_NAME = "ai-character-framework_v5.5.0.zip"
OFFICIAL_ZIP_SHA256 = "d6603003ea33abd5d543d85d4437f71e00571a86a9ed06a902506e6be3a9b5fe"
OFFICIAL_ZIP_SIZE = 681335
OFFICIAL_ZIP_FILE_COUNT = 328

EXPECTED_CHANGE_FILES = (
    "README.md",
    "docs/DRC_v300_goal_checklist_small_commit.md",
    "docs/v300_rt7b_vendored_fw_v550_readiness.md",
    "roadmap.md",
    "scripts/README.md",
    "scripts/check_v300_rt7b_vendored_fw_v550_readiness.py",
    "tasklist.md",
)

REQUIRED_VENDOR_FILES = (
    ".env.example",
    "README.md",
    "requirements.txt",
    "framework/__init__.py",
    "framework/motion.py",
    "framework/motion_adapter_execution.py",
    "framework/motion_session.py",
    "framework/vtube_studio_motion_composition.py",
    "framework/vtube_studio_pyvts_transport.py",
    "framework/vtube_studio_transport.py",
    "docs/release_notes_v5.5.0.md",
    "docs/v550_drc_real_motion_release_handoff.md",
    "docs/v550_final_release_tag_readiness.md",
    "scripts/build_v550_release_package.py",
)

REQUIRED_EXPORTS = (
    "MotionAdapterExecutionConfig",
    "MotionAdapterStatus",
    "MotionCapability",
    "MotionErrorCode",
    "MotionEventType",
    "MotionIntent",
    "MotionOutcome",
    "MotionRequest",
    "MotionResult",
    "MotionSession",
    "MotionSessionInfo",
    "create_motion_session",
    "get_motion_adapter_execution_capability",
    "resolve_motion_adapter_execution_config",
)

PRIVATE_BASENAMES = {
    ".env",
    "bootstrap_evidence.json",
    "real_motion_operator_evidence.json",
    "vts_private_config.json",
}

ACCEPTED_MARKERS = (
    "COMPLETED / ACCEPTED / PUSHED",
    EXPECTED_HEAD,
    "vendor/ai-character-framework-5.5.0",
)


class GateError(RuntimeError):
    """Raised when the RT-7b acceptance-sync contract is not satisfied."""


def _git(*args: str, check: bool = True) -> str:
    completed = subprocess.run(
        ["git", "-C", str(ROOT), *args],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if check and completed.returncode != 0:
        raise GateError(
            f"git {' '.join(args)} failed: "
            f"{completed.stderr.strip() or completed.stdout.strip()}"
        )
    return completed.stdout


def _status_paths() -> tuple[str, ...]:
    lines = _git("status", "--short", "--untracked-files=normal").splitlines()
    paths: list[str] = []
    for line in lines:
        if len(line) < 4:
            raise GateError(f"unexpected git status record: {line!r}")
        path = line[3:].strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        paths.append(path.replace("\\", "/"))
    return tuple(sorted(paths))


def _read(relative: str) -> str:
    path = ROOT / relative
    if not path.is_file():
        raise GateError(f"required file is missing: {relative}")
    return path.read_text(encoding="utf-8")


def _is_reparse_point(path: pathlib.Path) -> bool:
    information = path.stat()
    attributes = getattr(information, "st_file_attributes", 0)
    flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    return bool(attributes & flag)


def _release_eligible(relative: pathlib.PurePosixPath) -> bool:
    parts = relative.parts
    lowered_parts = tuple(part.lower() for part in parts)
    name = relative.name.lower()

    if not parts:
        return False
    if ".git" in lowered_parts:
        return False
    if "__pycache__" in lowered_parts:
        return False
    if any(part in {".pytest_cache", ".mypy_cache", ".ruff_cache"} for part in lowered_parts):
        return False
    if parts[0].lower() == "release":
        return False
    if name.endswith((".pyc", ".pyo", ".pyd")):
        return False
    if name == ".env":
        return False
    if name.startswith(".env.") and name != ".env.example":
        return False
    return True


def _vendor_files() -> dict[str, pathlib.Path]:
    result: dict[str, pathlib.Path] = {}
    for path in FRAMEWORK_VENDOR.rglob("*"):
        if not path.is_file():
            continue
        relative = pathlib.PurePosixPath(path.relative_to(FRAMEWORK_VENDOR).as_posix())
        if _release_eligible(relative):
            result[relative.as_posix()] = path
    return result


def _private_hits(paths: Iterable[pathlib.Path]) -> tuple[str, ...]:
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
            or (basename.startswith(".env.") and basename != ".env.example")
        ):
            hits.append(relative)
    return tuple(sorted(hits))


def _sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _parse_sidecar(path: pathlib.Path) -> tuple[str, str]:
    text = path.read_text(encoding="utf-8").strip()
    fields = text.split()
    if len(fields) < 2:
        raise GateError("release sidecar has an invalid format")
    return fields[0].lower(), fields[-1].lstrip("*")


def _strict_artifact_check(
    release_zip: pathlib.Path,
    release_sidecar: pathlib.Path,
    vendor_files: dict[str, pathlib.Path],
) -> None:
    if not release_zip.is_file():
        raise GateError(f"release ZIP is missing: {release_zip}")
    if not release_sidecar.is_file():
        raise GateError(f"release sidecar is missing: {release_sidecar}")

    digest = _sha256(release_zip)
    sidecar_digest, sidecar_name = _parse_sidecar(release_sidecar)

    if release_zip.name != OFFICIAL_ZIP_NAME:
        raise GateError(f"unexpected release ZIP filename: {release_zip.name}")
    if digest != OFFICIAL_ZIP_SHA256:
        raise GateError(
            "release ZIP SHA-256 mismatch: "
            f"expected={OFFICIAL_ZIP_SHA256}, actual={digest}"
        )
    if release_zip.stat().st_size != OFFICIAL_ZIP_SIZE:
        raise GateError(
            "release ZIP size mismatch: "
            f"expected={OFFICIAL_ZIP_SIZE}, actual={release_zip.stat().st_size}"
        )
    if sidecar_digest != digest or sidecar_name != release_zip.name:
        raise GateError("release ZIP sidecar does not match the supplied ZIP")

    with zipfile.ZipFile(release_zip, "r") as archive:
        if archive.testzip() is not None:
            raise GateError("release ZIP integrity check failed")
        names = [name for name in archive.namelist() if not name.endswith("/")]
        if len(names) != len(set(names)):
            raise GateError("release ZIP contains duplicate file members")
        if len(names) != OFFICIAL_ZIP_FILE_COUNT:
            raise GateError(
                "release ZIP file count mismatch: "
                f"expected={OFFICIAL_ZIP_FILE_COUNT}, actual={len(names)}"
            )
        if set(names) != set(vendor_files):
            missing = sorted(set(names) - set(vendor_files))
            extra = sorted(set(vendor_files) - set(names))
            raise GateError(
                "release ZIP/vendor membership mismatch: "
                f"missing={missing[:3]}, extra={extra[:3]}"
            )
        for name in names:
            if archive.read(name) != vendor_files[name].read_bytes():
                raise GateError(f"release ZIP/vendor byte mismatch: {name}")


def _check_docs() -> None:
    for relative in EXPECTED_CHANGE_FILES:
        text = _read(relative)
        for marker in ACCEPTED_MARKERS:
            if marker not in text:
                raise GateError(f"{relative} is missing accepted marker: {marker}")

    contract = _read("docs/v300_rt7b_vendored_fw_v550_readiness.md")
    required_contract_markers = (
        "acceptance-sync surface: exact 7 documentation/static-gate files",
        f"official ZIP SHA-256: {OFFICIAL_ZIP_SHA256}",
        "vendor / ZIP membership: exact",
        "vendor / ZIP file bytes: exact",
        "RT-7c exact contract review: READY",
        "RT-7c runtime implementation: NOT_AUTHORIZED",
    )
    for marker in required_contract_markers:
        if marker not in contract:
            raise GateError(f"accepted contract is missing marker: {marker}")

    ignore_text = _read(".gitignore")
    if "vendor/ai-character-framework-*/" not in ignore_text:
        raise GateError("repository-shared lower-case Framework vendor ignore rule is missing")

    # Build prohibited path fragments at runtime so the gate does not match its
    # own source while scanning the exact acceptance-sync surface.
    project_root_key = "framework_project_" + "root"
    development_backslash = "ai-character-framework" + "\\" + "development"
    development_slash = "ai-character-framework" + "/" + "development"
    prohibited = (
        project_root_key + "=..",
        development_backslash,
        development_slash,
        "../" + "ai-character-framework",
        "from framework" + ".",
    )
    combined = "\n".join(_read(relative).casefold() for relative in EXPECTED_CHANGE_FILES)
    for pattern in prohibited:
        if pattern.casefold() in combined:
            raise GateError(f"prohibited non-vendor Framework reference found: {pattern}")


def _check_framework(vendor_files: dict[str, pathlib.Path]) -> dict[str, object]:
    for relative in REQUIRED_VENDOR_FILES:
        if relative not in vendor_files:
            raise GateError(f"required vendored Framework file is missing: {relative}")

    if _is_reparse_point(FRAMEWORK_VENDOR):
        raise GateError("Framework vendor directory must not be a reparse point")
    if any(path.name == ".git" for path in FRAMEWORK_VENDOR.rglob(".git")):
        raise GateError("Framework vendor contains Git metadata")

    private_hits = _private_hits(FRAMEWORK_VENDOR.rglob("*"))
    if private_hits:
        raise GateError(
            "Framework vendor contains private artifact candidates: "
            f"{private_hits[:3]}"
        )

    sys.dont_write_bytecode = True
    vendor_resolved = FRAMEWORK_VENDOR.resolve()
    sys.path.insert(0, str(vendor_resolved))
    try:
        for name in tuple(sys.modules):
            if name == "framework" or name.startswith("framework."):
                del sys.modules[name]
        importlib.invalidate_caches()
        framework = importlib.import_module("framework")

        origin = pathlib.Path(framework.__file__).resolve()
        if vendor_resolved not in origin.parents:
            raise GateError(f"framework imported from unexpected origin: {origin}")

        missing_exports = tuple(
            name for name in REQUIRED_EXPORTS if not hasattr(framework, name)
        )
        if missing_exports:
            raise GateError(f"missing root-public Framework exports: {missing_exports}")

        if "pyvts" in sys.modules:
            raise GateError("pyvts imported during Framework root import")

        request = framework.MotionRequest.emotion_update("rt7b_acceptance_placeholder")
        mock_session = framework.create_motion_session()
        try:
            result = mock_session.apply_motion(request)
            if result.outcome.value != "completed":
                raise GateError(
                    f"mock motion returned unexpected outcome: {result.outcome.value}"
                )
            api_version = mock_session.info.api_version
        finally:
            mock_session.close()

        if api_version != "5.5.0":
            raise GateError(f"unexpected Framework motion API version: {api_version}")

        closed = framework.create_motion_session(
            adapter="vts",
            real_adapter_enabled=True,
            allow_provider_execution=False,
            runtime_available=True,
            model_selected=True,
            vts_endpoint_host="127.0.0.1",
            vts_endpoint_port=8001,
            vts_authentication_token="rt7b_acceptance_placeholder",
            vts_hotkey_bindings={
                "emotion:rt7b_acceptance_placeholder":
                    "rt7b_acceptance_placeholder",
            },
        )
        try:
            capability = closed.preflight()
            if (
                capability.adapter_status
                is not framework.MotionAdapterStatus.PROVIDER_EXECUTION_NOT_ALLOWED
            ):
                raise GateError(
                    "closed guard returned unexpected status: "
                    f"{capability.adapter_status.value}"
                )
            if capability.supports_real_adapter:
                raise GateError("closed guard unexpectedly reports real-adapter support")
        finally:
            closed.close()

        if "pyvts" in sys.modules:
            raise GateError("pyvts imported while provider execution guard was closed")

        intent_values = {member.value for member in framework.MotionIntent}
        required_intents = {
            "expression",
            "emotion",
            "gesture",
            "reset_expression",
        }
        if not required_intents.issubset(intent_values):
            raise GateError(
                "required motion intents are incomplete: "
                f"{sorted(required_intents - intent_values)}"
            )

        return {
            "origin_is_vendor": True,
            "api_version": api_version,
            "root_exports_complete": True,
            "mock_completed": True,
            "closed_guard_status": capability.adapter_status.value,
            "closed_guard_real_adapter_supported": capability.supports_real_adapter,
            "pyvts_imported": "pyvts" in sys.modules,
        }
    finally:
        try:
            sys.path.remove(str(vendor_resolved))
        except ValueError:
            pass


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-release-artifact", action="store_true")
    parser.add_argument("--release-zip", type=pathlib.Path)
    parser.add_argument("--release-sidecar", type=pathlib.Path)
    args = parser.parse_args()

    try:
        head = _git("rev-parse", "HEAD").strip()
        origin_main = _git("rev-parse", "origin/main").strip()
        if head != EXPECTED_HEAD:
            raise GateError(f"unexpected DRC HEAD: {head}")
        if origin_main != EXPECTED_HEAD:
            raise GateError(f"unexpected DRC origin/main: {origin_main}")

        changed = _status_paths()
        expected = tuple(sorted(EXPECTED_CHANGE_FILES))
        if changed != expected:
            raise GateError(
                "RT-7b acceptance-sync exact surface mismatch: "
                f"expected={expected}, actual={changed}"
            )

        _check_docs()

        if not FRAMEWORK_VENDOR.is_dir():
            raise GateError(
                "fixed Framework vendor directory is missing: "
                f"{FRAMEWORK_VENDOR_RELATIVE.as_posix()}"
            )

        vendor_files = _vendor_files()
        if len(vendor_files) != OFFICIAL_ZIP_FILE_COUNT:
            raise GateError(
                "Framework vendor release-eligible file count mismatch: "
                f"expected={OFFICIAL_ZIP_FILE_COUNT}, actual={len(vendor_files)}"
            )

        framework_result = _check_framework(vendor_files)

        if args.require_release_artifact and (
            args.release_zip is None or args.release_sidecar is None
        ):
            raise GateError(
                "--require-release-artifact requires --release-zip and "
                "--release-sidecar"
            )

        artifact_reverified = False
        if args.release_zip is not None or args.release_sidecar is not None:
            if args.release_zip is None or args.release_sidecar is None:
                raise GateError(
                    "--release-zip and --release-sidecar must be supplied together"
                )
            _strict_artifact_check(
                args.release_zip.resolve(),
                args.release_sidecar.resolve(),
                vendor_files,
            )
            artifact_reverified = True

        print("v300_rt7b_status: completed-accepted-pushed")
        print("v300_rt7_status: current-not-completed")
        print("v300_rt7b_acceptance_sync_status: implemented-awaiting-review")
        print("v300_rt7b_exact_change_surface: True")
        print(f"v300_rt7b_change_file_count: {len(changed)}")
        print(f"v300_rt7b_implementation_baseline: {IMPLEMENTATION_BASELINE}")
        print(f"v300_rt7b_implementation_commit: {EXPECTED_HEAD}")
        print(f"v300_rt7b_framework_release: {FRAMEWORK_RELEASE}")
        print(
            "v300_rt7b_framework_release_commit: "
            f"{FRAMEWORK_RELEASE_COMMIT}"
        )
        print(
            "v300_rt7b_framework_vendor_path: "
            f"{FRAMEWORK_VENDOR_RELATIVE.as_posix()}"
        )
        print("v300_rt7b_framework_development_checkout_referenced: False")
        print("v300_rt7b_framework_local_source_is_vendor_only: True")
        print(
            "v300_rt7b_vendor_total_file_count: "
            f"{sum(1 for path in FRAMEWORK_VENDOR.rglob('*') if path.is_file())}"
        )
        print("v300_rt7b_vendor_total_file_count_is_informational: True")
        print(
            "v300_rt7b_vendor_release_eligible_file_count: "
            f"{len(vendor_files)}"
        )
        print("v300_rt7b_vendor_required_files_complete: True")
        print("v300_rt7b_vendor_git_metadata_present: False")
        print("v300_rt7b_vendor_private_artifact_hits: 0")
        print(
            "v300_rt7b_framework_origin_is_vendor: "
            f"{framework_result['origin_is_vendor']}"
        )
        print(
            "v300_rt7b_framework_api_version: "
            f"{framework_result['api_version']}"
        )
        print(
            "v300_rt7b_root_public_exports_complete: "
            f"{framework_result['root_exports_complete']}"
        )
        print(
            "v300_rt7b_mock_motion_completed: "
            f"{framework_result['mock_completed']}"
        )
        print(
            "v300_rt7b_closed_guard_status: "
            f"{framework_result['closed_guard_status']}"
        )
        print(
            "v300_rt7b_closed_guard_real_adapter_supported: "
            f"{framework_result['closed_guard_real_adapter_supported']}"
        )
        print(
            "v300_rt7b_pyvts_imported: "
            f"{framework_result['pyvts_imported']}"
        )
        print("v300_rt7b_network_execution: False")
        print("v300_rt7b_real_motion_execution: False")
        print("v300_rt7b_required_expression: True")
        print("v300_rt7b_required_emotion: True")
        print("v300_rt7b_required_gesture: True")
        print("v300_rt7b_required_reset_expression: True")
        print("v300_rt7b_stop_motion_optional: True")
        print("v300_rt7b_speaking_state_support_assumed: False")
        print("v300_rt7b_idle_motion_support_assumed: False")
        print("v300_rt7b_look_at_support_assumed: False")
        print(
            "v300_rt7b_official_release_zip_sha256: "
            f"{OFFICIAL_ZIP_SHA256}"
        )
        print(
            "v300_rt7b_official_release_zip_file_count: "
            f"{OFFICIAL_ZIP_FILE_COUNT}"
        )
        print("v300_rt7b_release_artifact_byte_match_accepted: True")
        print(
            "v300_rt7b_release_artifact_reverified_this_run: "
            f"{artifact_reverified}"
        )
        print("v300_rt7b_acceptance_blocked_release_artifact_match_pending: False")
        print("v300_rt7b_backend_full_accepted: 289")
        print("v300_rt7b_flutter_analyze_accepted: True")
        print("v300_rt7b_flutter_full_accepted: 483")
        print("v300_rt7b_backend_runtime_changed: False")
        print("v300_rt7b_flutter_runtime_changed: False")
        print("v300_rt7b_existing_tests_changed: False")
        print("v300_rt7b_framework_vendor_changed: False")
        print("v300_rt7c_exact_contract_review_ready: True")
        print("v300_rt7c_runtime_composition_authorized: False")
        print("v300_rt7b_acceptance_sync_commit_push_authorized: False")
        return 0
    except (GateError, OSError, ValueError, zipfile.BadZipFile) as error:
        print(f"v300_rt7b_gate_error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
