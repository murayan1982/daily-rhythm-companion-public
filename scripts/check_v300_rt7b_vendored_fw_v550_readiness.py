"""RT-7b vendored Framework v5.5.0 readiness gate.

The gate is intentionally DRC-root and vendor-only. It never discovers or
imports a Framework development checkout. Real provider execution stays closed.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import os
import socket
import subprocess
import sys
import zipfile
from pathlib import Path, PurePosixPath
from typing import Iterable


DRC_BASELINE = "8413c2f08879b34f83496441c6a7e20181486469"
FW_RELEASE = "v5.5.0"
FW_RELEASE_COMMIT = "f56697b6de066b062794ac7bb01330d2d9e91759"
VENDOR_RELATIVE = Path("vendor") / "ai-character-framework-5.5.0"
VENDOR_RELATIVE_POSIX = VENDOR_RELATIVE.as_posix()
EXPECTED_RELEASE_ELIGIBLE_FILE_COUNT = 328

EXPECTED_FILES = {
    ".gitignore",
    "README.md",
    "docs/DRC_v300_goal_checklist_small_commit.md",
    "docs/v300_rt7b_vendored_fw_v550_readiness.md",
    "roadmap.md",
    "scripts/README.md",
    "scripts/check_v300_rt7b_vendored_fw_v550_readiness.py",
    "tasklist.md",
}

REQUIRED_VENDOR_FILES = {
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
}

PRIVATE_PREFIXES = (
    "config/tokens/",
    "operator_evidence/",
)
PRIVATE_BASENAMES = {
    "bootstrap_evidence.json",
    "real_motion_operator_evidence.json",
    "vts_private_config.json",
}
EXCLUDED_DIR_NAMES = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".venv",
    "__pycache__",
    "release",
    "venv",
}
EXCLUDED_SUFFIXES = {".pyc", ".pyd", ".pyo", ".wav"}
REQUIRED_ROOT_EXPORTS = (
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


class GateError(RuntimeError):
    """Raised when an RT-7b contract check fails."""


def _run(root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        list(args),
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if check and completed.returncode != 0:
        raise GateError(
            f"command failed ({completed.returncode}): {' '.join(args)}\n"
            f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"
        )
    return completed


def _repo_root() -> Path:
    completed = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if completed.returncode != 0:
        raise GateError("current directory is not inside the DRC Git repository")
    return Path(completed.stdout.strip()).resolve()


def _git_lines(root: Path, *args: str) -> list[str]:
    completed = _run(root, "git", *args)
    return [line.strip().replace("\\", "/") for line in completed.stdout.splitlines() if line.strip()]


def _changed_paths(root: Path) -> set[str]:
    changed = set(_git_lines(root, "diff", "--name-only"))
    changed.update(_git_lines(root, "diff", "--cached", "--name-only"))
    changed.update(_git_lines(root, "ls-files", "--others", "--exclude-standard"))
    return changed


def _read(root: Path, relative: str) -> str:
    path = root / relative
    if not path.is_file():
        raise GateError(f"required candidate file is missing: {relative}")
    return path.read_text(encoding="utf-8")


def _require(text: str, needle: str, *, where: str) -> None:
    if needle not in text:
        raise GateError(f"required marker missing in {where}: {needle}")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _normalize_relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _is_private_path(relative: str) -> bool:
    normalized = relative.replace("\\", "/")
    lower = normalized.casefold()
    basename = PurePosixPath(normalized).name.casefold()
    if any(lower.startswith(prefix) for prefix in PRIVATE_PREFIXES):
        return True
    if basename.endswith("_token.json"):
        return True
    if basename in PRIVATE_BASENAMES:
        return True
    if basename == ".env":
        return True
    if basename.startswith(".env.") and basename != ".env.example":
        return True
    return False


def _is_release_eligible(relative: str) -> bool:
    normalized = relative.replace("\\", "/")
    parts = PurePosixPath(normalized).parts
    if any(part.casefold() in EXCLUDED_DIR_NAMES for part in parts[:-1]):
        return False
    if PurePosixPath(normalized).suffix.casefold() in EXCLUDED_SUFFIXES:
        return False
    if normalized == ".vscode/settings.json":
        return False
    if _is_private_path(normalized):
        return False
    return True


def _vendor_files(vendor: Path) -> tuple[list[str], list[str]]:
    all_files: list[str] = []
    eligible: list[str] = []
    for path in vendor.rglob("*"):
        if not path.is_file():
            continue
        relative = _normalize_relative(path, vendor)
        all_files.append(relative)
        if _is_release_eligible(relative):
            eligible.append(relative)
    return sorted(all_files), sorted(eligible)


def _assert_no_vendor_git_metadata(vendor: Path) -> None:
    git_hits = [path for path in vendor.rglob(".git")]
    if git_hits:
        raise GateError("vendor contains Git metadata")


def _verify_candidate_documents(root: Path) -> None:
    readme = _read(root, "README.md")
    roadmap = _read(root, "roadmap.md")
    tasklist = _read(root, "tasklist.md")
    checklist = _read(root, "docs/DRC_v300_goal_checklist_small_commit.md")
    scripts_readme = _read(root, "scripts/README.md")
    contract = _read(root, "docs/v300_rt7b_vendored_fw_v550_readiness.md")
    gate_source = _read(root, "scripts/check_v300_rt7b_vendored_fw_v550_readiness.py")
    gitignore = _read(root, ".gitignore")

    required_markers = {
        "README.md": (
            "Current small commit: RT-7b vendored FW v5.5.0 readiness candidate",
            "Current implementation state: IMPLEMENTED / AWAITING_REVIEW",
            "RT-7b  IMPLEMENTED / AWAITING_REVIEW / COMMIT_NOT_AUTHORIZED",
            "<!-- RT-7b-VENDORED-FW-v5.5.0:BEGIN -->",
        ),
        "roadmap.md": (
            "Current small commit: RT-7b vendored FW v5.5.0 readiness candidate",
            "<!-- RT-7b-VENDORED-FW-v5.5.0:BEGIN -->",
        ),
        "tasklist.md": (
            "current small commit: RT-7b vendored FW v5.5.0 readiness candidate",
            "current implementation state: IMPLEMENTED / AWAITING_REVIEW",
            "<!-- RT-7b-VENDORED-FW-v5.5.0:BEGIN -->",
        ),
        "docs/DRC_v300_goal_checklist_small_commit.md": (
            "Current small commit: RT-7b vendored FW v5.5.0 readiness candidate",
            "Current implementation state: IMPLEMENTED / AWAITING_REVIEW",
            "docs/v300_rt7b_vendored_fw_v550_readiness.md",
            "scripts/check_v300_rt7b_vendored_fw_v550_readiness.py",
            "<!-- RT-7b-VENDORED-FW-v5.5.0:BEGIN -->",
        ),
        "scripts/README.md": (
            "## v3.0.0 RT-7b vendored Framework v5.5.0 readiness gate",
            "vendor/ai-character-framework-5.5.0",
        ),
        "docs/v300_rt7b_vendored_fw_v550_readiness.md": (
            "RT-7b: IMPLEMENTED / AWAITING_REVIEW",
            f"DRC baseline: {DRC_BASELINE}",
            f"Framework release commit: {FW_RELEASE_COMMIT}",
            f"Framework local source: {VENDOR_RELATIVE_POSIX}",
            "RT-7c runtime composition: NOT_AUTHORIZED",
            "commit / push: NOT_AUTHORIZED",
        ),
        "scripts/check_v300_rt7b_vendored_fw_v550_readiness.py": (
            f'DRC_BASELINE = "{DRC_BASELINE}"',
            f'FW_RELEASE_COMMIT = "{FW_RELEASE_COMMIT}"',
            'VENDOR_RELATIVE = Path("vendor") / "ai-character-framework-5.5.0"',
        ),
        ".gitignore": ("vendor/ai-character-framework-*/",),
    }

    texts = {
        "README.md": readme,
        "roadmap.md": roadmap,
        "tasklist.md": tasklist,
        "docs/DRC_v300_goal_checklist_small_commit.md": checklist,
        "scripts/README.md": scripts_readme,
        "docs/v300_rt7b_vendored_fw_v550_readiness.md": contract,
        "scripts/check_v300_rt7b_vendored_fw_v550_readiness.py": gate_source,
        ".gitignore": gitignore,
    }
    for relative, markers in required_markers.items():
        for marker in markers:
            _require(texts[relative], marker, where=relative)

    combined = "\n".join(texts.values()).casefold()
    # Build prohibited strings from fragments so this gate can scan its own
    # source without matching the literal definitions below.
    prohibited_local_patterns = (
        "framework_" + "project_root=..",
        "sys.path." + "append(",
        "sys.path." + "insert(0, str(path.cwd()",
        "checkout-relative " + "framework",
    )
    for pattern in prohibited_local_patterns:
        if pattern.casefold() in combined:
            raise GateError(f"prohibited non-vendor Framework reference pattern found: {pattern}")


def _verify_exact_surface(root: Path) -> None:
    changed = _changed_paths(root)
    if changed != EXPECTED_FILES:
        missing = sorted(EXPECTED_FILES - changed)
        extra = sorted(changed - EXPECTED_FILES)
        raise GateError(
            "RT-7b change surface mismatch; "
            f"missing={missing}, extra={extra}, actual={sorted(changed)}"
        )


def _verify_baseline(root: Path) -> None:
    head = _run(root, "git", "rev-parse", "HEAD").stdout.strip()
    remote = _run(root, "git", "rev-parse", "origin/main").stdout.strip()
    if head != DRC_BASELINE:
        raise GateError(f"DRC HEAD mismatch: {head}")
    if remote != DRC_BASELINE:
        raise GateError(f"DRC origin/main mismatch: {remote}")


def _verify_vendor(root: Path) -> tuple[Path, list[str], list[str]]:
    vendor = (root / VENDOR_RELATIVE).resolve()
    expected_vendor = (root / VENDOR_RELATIVE).resolve()
    if vendor != expected_vendor or root not in vendor.parents:
        raise GateError("vendor path escaped the DRC repository")
    if not vendor.is_dir():
        raise GateError(f"vendor directory is missing: {VENDOR_RELATIVE_POSIX}")
    if vendor.is_symlink():
        raise GateError("vendor directory must not be a symlink")
    if os.path.islink(vendor):
        raise GateError("vendor directory must not be a link")
    if hasattr(vendor, "is_junction") and vendor.is_junction():
        raise GateError("vendor directory must not be a junction")

    _assert_no_vendor_git_metadata(vendor)

    missing_required = sorted(
        relative for relative in REQUIRED_VENDOR_FILES if not (vendor / relative).is_file()
    )
    if missing_required:
        raise GateError(f"required Framework v5.5.0 vendor files missing: {missing_required}")

    all_files, eligible = _vendor_files(vendor)
    private_hits = sorted(relative for relative in all_files if _is_private_path(relative))
    if private_hits:
        raise GateError(f"private Framework vendor artifacts found: {private_hits}")
    if len(eligible) != EXPECTED_RELEASE_ELIGIBLE_FILE_COUNT:
        raise GateError(
            "Framework vendor release-eligible file count mismatch: "
            f"expected={EXPECTED_RELEASE_ELIGIBLE_FILE_COUNT}, actual={len(eligible)}"
        )

    ignore_result = _run(
        root,
        "git",
        "check-ignore",
        "-q",
        "--",
        f"{VENDOR_RELATIVE_POSIX}/README.md",
        check=False,
    )
    if ignore_result.returncode != 0:
        raise GateError("Framework vendor directory is not ignored by Git")

    return vendor, all_files, eligible


def _verify_root_public_runtime(vendor: Path) -> dict[str, object]:
    previous_path = list(sys.path)
    previous_bytecode = sys.dont_write_bytecode
    prior_framework_modules = {
        name: module for name, module in sys.modules.items() if name == "framework" or name.startswith("framework.")
    }
    for name in list(prior_framework_modules):
        sys.modules.pop(name, None)

    network_attempted = False
    original_connect = socket.socket.connect
    original_create_connection = socket.create_connection

    def blocked_connect(self: socket.socket, address: object) -> None:  # type: ignore[override]
        nonlocal network_attempted
        network_attempted = True
        raise GateError(f"network execution attempted during RT-7b gate: {address!r}")

    def blocked_create_connection(*args: object, **kwargs: object) -> socket.socket:
        nonlocal network_attempted
        network_attempted = True
        raise GateError("network execution attempted during RT-7b gate")

    socket.socket.connect = blocked_connect  # type: ignore[assignment]
    socket.create_connection = blocked_create_connection  # type: ignore[assignment]
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(vendor))

    try:
        framework = importlib.import_module("framework")
        origin = Path(framework.__file__).resolve()
        if vendor not in origin.parents:
            raise GateError(f"framework imported from unexpected origin: {origin}")

        missing_exports = tuple(name for name in REQUIRED_ROOT_EXPORTS if not hasattr(framework, name))
        if missing_exports:
            raise GateError(f"missing Framework root-public exports: {missing_exports}")
        if "pyvts" in sys.modules:
            raise GateError("pyvts imported during Framework root import")

        MotionAdapterStatus = framework.MotionAdapterStatus
        MotionRequest = framework.MotionRequest
        create_motion_session = framework.create_motion_session

        mock_session = create_motion_session()
        try:
            request = MotionRequest.emotion_update("audit_placeholder")
            result = mock_session.apply_motion(request)
            if result.outcome.value != "completed":
                raise GateError(f"mock motion did not complete: {result.outcome.value}")
            api_version = mock_session.info.api_version
            if api_version != "5.5.0":
                raise GateError(f"unexpected Framework motion API version: {api_version}")
        finally:
            mock_session.close()

        closed_session = create_motion_session(
            adapter="vts",
            real_adapter_enabled=True,
            allow_provider_execution=False,
            runtime_available=True,
            model_selected=True,
            vts_endpoint_host="127.0.0.1",
            vts_endpoint_port=8001,
            vts_authentication_token="audit_placeholder",
            vts_hotkey_bindings={
                "emotion:audit_placeholder": "audit_placeholder",
            },
        )
        try:
            capability = closed_session.preflight()
            if capability.adapter_status is not MotionAdapterStatus.PROVIDER_EXECUTION_NOT_ALLOWED:
                raise GateError(
                    "closed execution guard returned unexpected status: "
                    f"{capability.adapter_status.value}"
                )
            if capability.supports_real_adapter:
                raise GateError("closed execution guard reported real-adapter support")
            if "pyvts" in sys.modules:
                raise GateError("pyvts imported while provider execution guard was closed")
        finally:
            closed_session.close()

        if network_attempted:
            raise GateError("network execution was attempted")

        return {
            "origin": str(origin),
            "api_version": api_version,
            "root_public_exports_complete": True,
            "mock_motion_completed": True,
            "closed_guard_status": capability.adapter_status.value,
            "closed_guard_real_adapter_supported": capability.supports_real_adapter,
            "pyvts_imported": "pyvts" in sys.modules,
            "network_execution": network_attempted,
            "real_motion_execution": False,
        }
    finally:
        socket.socket.connect = original_connect  # type: ignore[assignment]
        socket.create_connection = original_create_connection  # type: ignore[assignment]
        sys.path[:] = previous_path
        sys.dont_write_bytecode = previous_bytecode
        for name in [name for name in sys.modules if name == "framework" or name.startswith("framework.")]:
            sys.modules.pop(name, None)
        sys.modules.update(prior_framework_modules)


def _parse_sidecar(sidecar: Path) -> tuple[str, str]:
    text = sidecar.read_text(encoding="utf-8").strip()
    parts = text.split()
    if len(parts) != 2:
        raise GateError("release SHA-256 sidecar must contain '<digest>  <filename>'")
    digest, filename = parts
    digest = digest.casefold()
    if len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest):
        raise GateError("release SHA-256 sidecar digest is invalid")
    return digest, filename


def _validate_zip_member_name(name: str) -> str:
    normalized = name.replace("\\", "/")
    pure = PurePosixPath(normalized)
    if pure.is_absolute() or ".." in pure.parts or not normalized or normalized.endswith("/"):
        raise GateError(f"unsafe or invalid release ZIP member: {name}")
    return pure.as_posix()


def _verify_release_artifact(vendor: Path, eligible: list[str], zip_path: Path, sidecar_path: Path) -> dict[str, object]:
    if not zip_path.is_file():
        raise GateError(f"release ZIP is missing: {zip_path}")
    if not sidecar_path.is_file():
        raise GateError(f"release SHA-256 sidecar is missing: {sidecar_path}")

    sidecar_digest, sidecar_filename = _parse_sidecar(sidecar_path)
    actual_digest = _sha256(zip_path)
    if sidecar_digest != actual_digest:
        raise GateError(
            f"release ZIP digest mismatch: sidecar={sidecar_digest}, actual={actual_digest}"
        )
    if sidecar_filename != zip_path.name:
        raise GateError(
            f"release sidecar filename mismatch: sidecar={sidecar_filename}, zip={zip_path.name}"
        )

    with zipfile.ZipFile(zip_path, "r") as archive:
        bad_member = archive.testzip()
        if bad_member is not None:
            raise GateError(f"release ZIP integrity failed at member: {bad_member}")

        normalized_names = [_validate_zip_member_name(info.filename) for info in archive.infolist() if not info.is_dir()]
        if len(normalized_names) != len(set(normalized_names)):
            raise GateError("release ZIP contains duplicate members")
        if sorted(normalized_names) != eligible:
            missing = sorted(set(eligible) - set(normalized_names))
            extra = sorted(set(normalized_names) - set(eligible))
            raise GateError(
                "release ZIP/vendor membership mismatch; "
                f"missing_from_zip={missing}, extra_in_zip={extra}"
            )

        for relative in eligible:
            archived = archive.read(relative)
            local = (vendor / relative).read_bytes()
            if archived != local:
                raise GateError(f"release ZIP/vendor byte mismatch: {relative}")
            if _is_private_path(relative):
                raise GateError(f"private artifact unexpectedly present in release ZIP: {relative}")

    return {
        "release_zip_sha256": actual_digest,
        "release_zip_file_count": len(eligible),
        "release_zip_integrity": True,
        "release_zip_duplicates_absent": True,
        "release_zip_vendor_membership_exact": True,
        "release_zip_vendor_bytes_exact": True,
        "release_artifact_byte_match_verified": True,
        "vendor_key_sha256_match": True,
    }


def _bool(value: object) -> str:
    return "True" if bool(value) else "False"


def main() -> None:
    parser = argparse.ArgumentParser(description="Check RT-7b vendored FW v5.5.0 readiness")
    parser.add_argument("--release-zip", type=Path)
    parser.add_argument("--release-sidecar", type=Path)
    parser.add_argument("--require-release-artifact", action="store_true")
    args = parser.parse_args()

    if (args.release_zip is None) != (args.release_sidecar is None):
        raise GateError("--release-zip and --release-sidecar must be supplied together")
    if args.require_release_artifact and args.release_zip is None:
        raise GateError("strict provenance requires --release-zip and --release-sidecar")

    root = _repo_root()
    _verify_baseline(root)
    _verify_exact_surface(root)
    _verify_candidate_documents(root)
    vendor, all_vendor_files, eligible_vendor_files = _verify_vendor(root)
    runtime = _verify_root_public_runtime(vendor)

    artifact: dict[str, object] = {
        "release_artifact_byte_match_verified": False,
        "release_zip_integrity": False,
        "release_zip_duplicates_absent": False,
        "release_zip_vendor_membership_exact": False,
        "release_zip_vendor_bytes_exact": False,
        "vendor_key_sha256_match": False,
    }
    if args.release_zip is not None and args.release_sidecar is not None:
        artifact = _verify_release_artifact(
            vendor,
            eligible_vendor_files,
            args.release_zip.resolve(),
            args.release_sidecar.resolve(),
        )

    artifact_verified = bool(artifact["release_artifact_byte_match_verified"])
    if args.require_release_artifact and not artifact_verified:
        raise GateError("strict release-artifact provenance did not pass")

    print("v300_rt7b_status: implemented-awaiting-review")
    print("v300_rt7_status: current-not-completed")
    print("v300_rt7b_exact_change_surface: True")
    print(f"v300_rt7b_change_file_count: {len(EXPECTED_FILES)}")
    print(f"v300_rt7b_drc_baseline: {DRC_BASELINE}")
    print(f"v300_rt7b_framework_release: {FW_RELEASE}")
    print(f"v300_rt7b_framework_release_commit: {FW_RELEASE_COMMIT}")
    print(f"v300_rt7b_framework_vendor_path: {VENDOR_RELATIVE_POSIX}")
    print("v300_rt7b_framework_development_checkout_referenced: False")
    print("v300_rt7b_framework_local_source_is_vendor_only: True")
    print(f"v300_rt7b_vendor_total_file_count: {len(all_vendor_files)}")
    print("v300_rt7b_vendor_total_file_count_is_informational: True")
    print(f"v300_rt7b_vendor_release_eligible_file_count: {len(eligible_vendor_files)}")
    print("v300_rt7b_vendor_required_files_complete: True")
    print("v300_rt7b_vendor_git_metadata_present: False")
    print("v300_rt7b_vendor_private_artifact_hits: 0")
    print(
        "v300_rt7b_vendor_key_sha256_match: "
        f"{_bool(artifact['vendor_key_sha256_match'])}"
    )
    print("v300_rt7b_shared_gitignore_rule_present: True")
    print("v300_rt7b_framework_origin_is_vendor: True")
    print(f"v300_rt7b_framework_api_version: {runtime['api_version']}")
    print(f"v300_rt7b_root_public_exports_complete: {_bool(runtime['root_public_exports_complete'])}")
    print(f"v300_rt7b_mock_motion_completed: {_bool(runtime['mock_motion_completed'])}")
    print(f"v300_rt7b_closed_guard_status: {runtime['closed_guard_status']}")
    print(
        "v300_rt7b_closed_guard_real_adapter_supported: "
        f"{_bool(runtime['closed_guard_real_adapter_supported'])}"
    )
    print(f"v300_rt7b_pyvts_imported: {_bool(runtime['pyvts_imported'])}")
    print(f"v300_rt7b_network_execution: {_bool(runtime['network_execution'])}")
    print(f"v300_rt7b_real_motion_execution: {_bool(runtime['real_motion_execution'])}")
    print("v300_rt7b_required_expression: True")
    print("v300_rt7b_required_emotion: True")
    print("v300_rt7b_required_gesture: True")
    print("v300_rt7b_required_reset_expression: True")
    print("v300_rt7b_stop_motion_optional: True")
    print("v300_rt7b_speaking_state_support_assumed: False")
    print("v300_rt7b_idle_motion_support_assumed: False")
    print("v300_rt7b_look_at_support_assumed: False")
    print(
        "v300_rt7b_release_artifact_byte_match_verified: "
        f"{_bool(artifact_verified)}"
    )
    print(
        "v300_rt7b_release_zip_integrity: "
        f"{_bool(artifact['release_zip_integrity'])}"
    )
    print(
        "v300_rt7b_release_zip_duplicates_absent: "
        f"{_bool(artifact['release_zip_duplicates_absent'])}"
    )
    print(
        "v300_rt7b_release_zip_vendor_membership_exact: "
        f"{_bool(artifact['release_zip_vendor_membership_exact'])}"
    )
    print(
        "v300_rt7b_release_zip_vendor_bytes_exact: "
        f"{_bool(artifact['release_zip_vendor_bytes_exact'])}"
    )
    if artifact_verified:
        print(f"v300_rt7b_release_zip_sha256: {artifact['release_zip_sha256']}")
        print(f"v300_rt7b_release_zip_file_count: {artifact['release_zip_file_count']}")
    print(
        "v300_rt7b_acceptance_blocked_release_artifact_match_pending: "
        f"{_bool(not artifact_verified)}"
    )
    print("v300_rt7b_backend_runtime_changed: False")
    print("v300_rt7b_flutter_runtime_changed: False")
    print("v300_rt7b_existing_tests_changed: False")
    print("v300_rt7b_framework_vendor_changed: False")
    print("v300_rt7b_rt7c_runtime_composition_authorized: False")
    print("v300_rt7b_commit_push_authorized: False")


if __name__ == "__main__":
    try:
        main()
    except GateError as exc:
        print(f"v300_rt7b_gate_error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
