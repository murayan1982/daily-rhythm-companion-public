#!/usr/bin/env python3
"""DRC-V4-1 FW v6.0.0 readiness acceptance sync gate.

This gate is local, credential-free, provider-free, network-free,
microphone-free, real STT/LLM/TTS-free, playback-free, VTube Studio-free, and
real-motion-free. It checks the public docs/static-gate contract only.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_BASELINE = "6311864237d8f5d86db49c14d17ca083e1af5c03"
FRAMEWORK_RELEASE = "v6.0.0"
FRAMEWORK_ANNOTATED_TAG_TARGET = "61e15f62d1ecc5faee016abae82200f8de56c5dd"
FRAMEWORK_OFFICIAL_ZIP = "ai-character-framework_v6.0.0.zip"
FRAMEWORK_OFFICIAL_ZIP_SHA256 = "6b303dba53830dc9bd65ec881bac6f498dbf80f0d0adf1385cea728a86e066f2"
FRAMEWORK_ROOT_PUBLIC_INVENTORY = "127 names / frozen"
EXPECTED_CHANGED_FILES = (
    "README.md",
    "docs/DRC_v400_goal_checklist_small_commit.md",
    "docs/v400_framework_v600_readiness_acceptance.md",
    "roadmap.md",
    "scripts/README.md",
    "scripts/check_v400_framework_v600_readiness_acceptance.py",
    "tasklist.md",
)
READINESS = (
    ("Unified RealtimeSession", "PARTIAL_READY"),
    ("Typed lifecycle events", "READY"),
    ("Interrupt/cancellation", "READY"),
    ("TTS queue/flush/invalidation", "READY"),
    ("Stale/late result rejection", "READY"),
    ("Capability snapshot", "READY"),
    ("Voice-input streaming", "PARTIAL_READY"),
    ("Backpressure", "READY"),
    ("Motion lifecycle", "PARTIAL_READY"),
    ("Recovery/reset", "PARTIAL_READY"),
    ("Safe diagnostics", "READY"),
    ("Aggregate", "PARTIAL_READY"),
)
CONTRACT_FILES = (
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v400_goal_checklist_small_commit.md",
    "docs/v400_framework_v600_readiness_acceptance.md",
)
PROVENANCE_MARKERS = (
    f"Framework release: {FRAMEWORK_RELEASE}",
    f"Framework annotated tag target: {FRAMEWORK_ANNOTATED_TAG_TARGET}",
    f"Framework official ZIP: {FRAMEWORK_OFFICIAL_ZIP}",
    f"Framework official ZIP SHA-256: {FRAMEWORK_OFFICIAL_ZIP_SHA256}",
    f"Framework root-public inventory: {FRAMEWORK_ROOT_PUBLIC_INVENTORY}",
)
V4_2_SCOPE_MARKERS = (
    "provider-free FW v6 RealtimeSession adapter first",
    "session identity",
    "turn identity",
    "generation identity",
    "canonical event ordering",
    "exactly-once terminal",
    "cooperative interrupt results",
    "stale-result rejection",
    "truthful capability snapshot",
    "safe diagnostics",
    "initial FW imports from root framework only",
    "explicit FW submodule adoption requires a separate exact review",
    "existing accepted v3 real adapters remain retained",
    "removal of v3 real adapters is NOT_AUTHORIZED",
    "real unified RealtimeSession remains NOT_CLAIMED / NOT_AVAILABLE",
)
DRC_OWNED_MARKERS = (
    "Flutter microphone permission / foreground lifecycle",
    "product UX and explicit opt-in policy",
    "DailyRecord / sleep / mood / character context",
    "host-local playback final control",
    "presentation state",
    "persistence",
)
PROHIBITED_CHANGED_PREFIXES = (
    "backend/",
    "app/",
    "vendor/",
    "release_notes/v3.0.0.md",
    "docs/v300_",
    "docs/DRC_v300_goal_checklist_small_commit.md",
)
SENSITIVE_PATTERNS = (
    re.compile(r"(?i)sk-[a-z0-9_-]{12,}"),
    re.compile(r"(?i)xai-[a-z0-9_-]{12,}"),
    re.compile(r"(?i)bearer\s+[a-z0-9._~+/-]{12,}"),
    re.compile(r"(?i)(?:api[_-]?key|access[_-]?token|refresh[_-]?token|client[_-]?secret)\s*[:=]"),
    re.compile(r"(?i)\b[a-z]:\\(?:users|home)\\"),
    re.compile(r"/(?:home|users)/[^/\s]+/"),
    re.compile(r"\b(?:10|169\.254|172\.(?:1[6-9]|2\d|3[01])|192\.168)\.\d{1,3}\.\d{1,3}\b"),
)


class GateError(RuntimeError):
    """Raised when the DRC-V4-1 acceptance sync contract is not satisfied."""


def _git(*args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(ROOT), *args],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if completed.returncode:
        raise GateError(
            f"git {' '.join(args)} failed: "
            f"{completed.stderr.strip() or completed.stdout.strip()}"
        )
    return completed.stdout


def _git_ok(*args: str) -> bool:
    return subprocess.run(
        ["git", "-C", str(ROOT), *args],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    ).returncode == 0


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
        raise GateError(f"missing required file: {relative}")
    return path.read_text(encoding="utf-8")


def _require_marker(relative: str, marker: str) -> None:
    if marker not in _read(relative):
        raise GateError(f"{relative} missing marker: {marker}")


def _check_exact_surface() -> tuple[str, ...]:
    head = _git("rev-parse", "HEAD").strip()
    if head != EXPECTED_BASELINE:
        raise GateError(f"unexpected HEAD: expected {EXPECTED_BASELINE}, actual {head}")

    changed = _status_paths()
    expected = tuple(sorted(EXPECTED_CHANGED_FILES))
    if changed != expected:
        raise GateError(
            "DRC-V4-1 exact surface mismatch: "
            f"expected={expected}, actual={changed}"
        )
    for relative in changed:
        if relative == ".gitignore":
            raise GateError(".gitignore must not be modified")
        if relative.startswith(PROHIBITED_CHANGED_PREFIXES):
            raise GateError(f"prohibited changed file for DRC-V4-1: {relative}")
    return changed


def _check_markers() -> None:
    common = (
        "DRC-V4-1",
        "FW v6.0.0",
        "PARTIAL_READY",
        "DRC-V4-2",
        "NOT_STARTED / NOT_AUTHORIZED",
        "v3.0.0",
        "RELEASED / ACCEPTED",
    )
    for relative in CONTRACT_FILES:
        for marker in common:
            _require_marker(relative, marker)
        for marker in PROVENANCE_MARKERS:
            _require_marker(relative, marker)

    matrix_doc = _read("docs/v400_framework_v600_readiness_acceptance.md")
    for label, decision in READINESS:
        pattern = re.compile(re.escape(label) + r"\s+" + re.escape(decision))
        if not pattern.search(matrix_doc):
            raise GateError(f"readiness matrix mismatch: {label} {decision}")

    non_claim = (
        "FW v6.0.0 does NOT provide a production real unified\n"
        "RealtimeSession.run_turn() pipeline coordinating\n"
        "real STT -> streaming LLM -> TTS -> motion."
    )
    for relative in (
        "roadmap.md",
        "docs/v400_framework_v600_readiness_acceptance.md",
    ):
        _require_marker(relative, non_claim)

    for marker in (
        "existing accepted v3 real runtime paths",
        "existing fixed FW v5.5.0 integration",
        "root-public-only Framework policy for initial v4 adoption",
        "provider/network",
        "microphone",
        "real STT/LLM/TTS",
        "playback",
        "VTube Studio",
        "real motion",
    ):
        _require_marker("docs/v400_framework_v600_readiness_acceptance.md", marker)

    for marker in V4_2_SCOPE_MARKERS:
        _require_marker("docs/v400_framework_v600_readiness_acceptance.md", marker)
    for marker in DRC_OWNED_MARKERS:
        _require_marker("docs/v400_framework_v600_readiness_acceptance.md", marker)
    _require_marker(
        "README.md",
        "Current release action: none; v3.0.0 publication is complete",
    )


def _check_privacy(changed: tuple[str, ...]) -> None:
    for relative in changed:
        if _git_ok("ls-files", "--error-unmatch", "--", relative):
            diff = _git("diff", "--unified=0", "HEAD", "--", relative)
            text = "\n".join(
                line[1:]
                for line in diff.splitlines()
                if line.startswith("+") and not line.startswith("+++")
            )
        else:
            text = _read(relative)
        for pattern in SENSITIVE_PATTERNS:
            if pattern.search(text):
                raise GateError(f"private-looking value found in {relative}")


def main() -> int:
    try:
        changed = _check_exact_surface()
        _check_markers()
        _check_privacy(changed)
        print("v400_drc_v4_1_status: implemented-awaiting-review")
        print("v400_drc_v4_1_baseline:", EXPECTED_BASELINE)
        print("v400_drc_v4_1_exact_change_surface: True")
        print("v400_drc_v4_1_change_file_count:", len(changed))
        print("v400_framework_release:", FRAMEWORK_RELEASE)
        print("v400_framework_annotated_tag_target:", FRAMEWORK_ANNOTATED_TAG_TARGET)
        print("v400_framework_official_zip:", FRAMEWORK_OFFICIAL_ZIP)
        print("v400_framework_official_zip_sha256:", FRAMEWORK_OFFICIAL_ZIP_SHA256)
        print("v400_framework_root_public_inventory:", FRAMEWORK_ROOT_PUBLIC_INVENTORY)
        for label, decision in READINESS:
            key = label.lower().replace("/", "_").replace(" ", "_").replace("-", "_")
            print(f"v400_readiness_{key}: {decision}")
        print("v400_aggregate_decision: PARTIAL_READY")
        print("v400_critical_unified_run_turn_pipeline_claimed: False")
        print("v400_backend_runtime_tests_changed: False")
        print("v400_flutter_runtime_tests_changed: False")
        print("v400_dependencies_lockfiles_changed: False")
        print("v400_version_metadata_changed: False")
        print("v400_framework_vendor_changed: False")
        print("v400_gitignore_changed: False")
        print("v400_v3_release_records_changed: False")
        print("v400_private_config_evidence_changed: False")
        print("v400_provider_network_execution: False")
        print("v400_microphone_execution: False")
        print("v400_real_stt_llm_tts_execution: False")
        print("v400_playback_execution: False")
        print("v400_vtube_studio_real_motion_execution: False")
        print("v400_root_public_only_initial_adoption_policy_preserved: True")
        print("v400_v4_2_provider_free_adapter_first: True")
        print("v400_v4_2_root_framework_imports_only_initial: True")
        print("v400_v4_2_fw_submodule_adoption_authorized: False")
        print("v400_v3_real_adapters_retained: True")
        print("v400_v3_real_adapters_removal_authorized: False")
        print("v400_real_unified_realtime_session_available: False")
        print("v400_drc_v4_2_status: not-started-not-authorized")
        print("v400_commit_push_authorized: False")
        return 0
    except (GateError, OSError) as error:
        print(f"v400_readiness_acceptance_gate_error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
