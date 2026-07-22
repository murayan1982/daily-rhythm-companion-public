"""Verify G-3 public-safe final prerelease aggregate acceptance synchronization.

This source-tree check reads committed documentation markers only. It does not
read private operator evidence, build or inspect release zips, call providers or
Google Health, start backend/Web services, open browsers, inspect screenshots,
publish to GitHub, create tags, or access external networks.
"""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

_CHECKLIST_PATH = ROOT / "docs/DRC_v200_goal_checklist_small_commit.md"
_DAY70_DOC_PATH = ROOT / "docs/v200_final_prerelease_aggregate_gate.md"
_ROADMAP_PATH = ROOT / "roadmap.md"
_SCRIPTS_README_PATH = ROOT / "scripts/README.md"

_ACCEPTANCE_SCOPE = "commit_scope: Commit G-3 only"
_ACCEPTANCE_REQUIRED_SNIPPETS = (
    "implementation_status: final-prerelease-aggregate-acceptance-public-safe-synchronized",
    "accepted_requirement_key: final_aggregate_review",
    "day70_evidence_status: accepted",
    "day70_public_safe: True",
    "day70_forbidden_success_states_absent: True",
    "day70_requirement_satisfied: True",
    "day52_to_day58_foundation_gates_passed: True",
    "day64_real_llm_web_answer_execution_accepted: True",
    "day65_real_tts_web_audio_execution_accepted: True",
    "day66_real_google_health_sleep_data_execution_accepted: True",
    "day67_image_asset_intake_accepted: True",
    "day68_web_image_display_execution_accepted: True",
    "day69_public_repo_final_sweep_accepted: True",
    "smartphone_web_evidence_reviewed: True",
    "api_level_evidence_reviewed: True",
    "fallback_skipped_unavailable_not_counted: True",
    "mock_safe_default_preserved: True",
    "credential_free_default_checks_preserved: True",
    "public_safe_marker_only_evidence_preserved: True",
    "release_zip_not_created_by_aggregate_check: True",
    "ready_to_build_one_fixed_v200_release_candidate: True",
    "public_repo_final_sweep_review: ACCEPTED",
    "final_aggregate_review: ACCEPTED",
    "accepted_private_evidence_manifest: NOT_ACCEPTED",
    "final_fixed_release_zip: not-built",
    "DRC_v2.0.0_tag: not-created",
    "release_completion_status: NOT_RELEASED",
)
_PRIVATE_SAFETY_SNIPPET = (
    "private_evidence_policy: raw evidence, operator evidence files, screenshots, audio, "
    "provider payloads, health data, secrets, tokens, LAN IPs, private paths, release zips, "
    "and local artifacts remain uncommitted"
)
_FORBIDDEN_ACCEPTANCE_BLOCK_TOKENS = (
    "http://",
    "https://",
    "file://",
    "localhost",
    "127.0.0.1",
    "192.168.",
    "\\operator_evidence\\",
    "/operator_evidence/",
    "access_token",
    "refresh_token",
    "client_secret",
    "authorization: bearer",
)


def main() -> int:
    print("[smoke-framework-v200-final-prerelease-aggregate-acceptance-sync] RESULT")

    if not _check_required_files():
        return 1
    if not _check_checklist_source_of_truth():
        return 1
    if not _check_current_state():
        return 1
    if not _check_public_safe_acceptance_blocks():
        return 1
    if not _check_downstream_release_gates():
        return 1
    if not _check_roadmap_sync():
        return 1
    if not _check_scripts_readme_sync():
        return 1
    if not _check_gitignore_boundary():
        return 1

    print("v200_final_prerelease_aggregate_acceptance_sync_status: accepted")
    print("v200_final_prerelease_aggregate_acceptance_sync_public_safe: True")
    print("v200_final_prerelease_aggregate_acceptance_sync_requirement_satisfied: True")
    print("v200_final_prerelease_aggregate_acceptance_sync_remaining_release_status: NOT_RELEASED")
    print("[smoke-framework-v200-final-prerelease-aggregate-acceptance-sync] OK")
    print(
        "No operator evidence read, release build or zip inspection, provider/Google Health "
        "call, backend/Web startup, browser action, screenshot/audio/image inspection, "
        "GitHub publication, tag creation, or external network access was performed."
    )
    return 0


def _check_required_files() -> bool:
    paths = (_CHECKLIST_PATH, _DAY70_DOC_PATH, _ROADMAP_PATH, _SCRIPTS_README_PATH)
    missing = [str(path.relative_to(ROOT)) for path in paths if not path.exists()]
    if missing:
        return _error("missing required files: " + ",".join(missing))
    print("v200_final_prerelease_aggregate_acceptance_sync_required_files: present")
    return True


def _check_checklist_source_of_truth() -> bool:
    legacy_path = ROOT / "DRC_v200_goal_checklist_small_commit.md"
    if legacy_path.exists():
        return _error("legacy root checklist copy still exists")
    print("v200_final_prerelease_aggregate_acceptance_sync_checklist_source_of_truth: docs-only")
    return True


def _extract_section(text: str, start_marker: str, end_marker: str) -> str:
    start = text.find(start_marker)
    if start < 0:
        return ""
    end = text.find(end_marker, start)
    if end < 0:
        return ""
    return text[start:end]


def _extract_commit_block(text: str) -> str:
    start = text.find(_ACCEPTANCE_SCOPE)
    if start < 0:
        return ""
    end = text.find("```", start)
    if end < 0:
        return ""
    return text[start:end]


def _check_current_state() -> bool:
    text = _CHECKLIST_PATH.read_text(encoding="utf-8")
    required = (
        "- [x] Commit G-3 synchronizes the accepted Day70 final prerelease aggregate review using public-safe markers only.",
        "public_repo_final_sweep_review: ACCEPTED",
        "final_aggregate_review: ACCEPTED",
        "accepted_private_evidence_manifest: NOT_ACCEPTED",
        "final_fixed_release_zip: not-built",
        "DRC_v2.0.0_tag: not-created",
        "Status: **NOT RELEASED**",
    )
    missing = [snippet for snippet in required if snippet not in text]
    if missing:
        return _error("current source-of-truth state is not synchronized: " + " | ".join(missing))
    print("v200_final_prerelease_aggregate_acceptance_sync_current_state: synchronized")
    return True


def _check_public_safe_acceptance_blocks() -> bool:
    for path in (_CHECKLIST_PATH, _DAY70_DOC_PATH,):
        text = path.read_text(encoding="utf-8")
        block = _extract_commit_block(text)
        if not block:
            return _error(f"{path.relative_to(ROOT)} is missing the G-3 acceptance block")
        missing = [snippet for snippet in _ACCEPTANCE_REQUIRED_SNIPPETS if snippet not in block]
        if _PRIVATE_SAFETY_SNIPPET not in block:
            missing.append(_PRIVATE_SAFETY_SNIPPET)
        if missing:
            return _error(
                f"{path.relative_to(ROOT)} is missing acceptance markers: " + " | ".join(missing)
            )
        lowered = block.lower()
        forbidden = [token for token in _FORBIDDEN_ACCEPTANCE_BLOCK_TOKENS if token.lower() in lowered]
        if forbidden:
            return _error(
                f"{path.relative_to(ROOT)} exposes private or endpoint-shaped data: "
                + " | ".join(forbidden)
            )
    print("v200_final_prerelease_aggregate_acceptance_sync_public_blocks: safe")
    return True


def _check_downstream_release_gates() -> bool:
    text = _CHECKLIST_PATH.read_text(encoding="utf-8")
    manifest_section = _extract_section(
        text,
        "### 2.7 Accepted private evidence manifest",
        "### 2.8 Final fixed release zip",
    )
    required = (
        "accepted_private_evidence_manifest: ACCEPTED",
        "- [x] Private evidence manifest exists outside public release material.",
        "- [x] It records accepted evidence for `final_aggregate_review`.",
        "commit_scope: Commit G-5 only",
    )
    missing = [snippet for snippet in required if snippet not in manifest_section]
    if missing:
        return _error("private evidence manifest acceptance is not synchronized: " + " | ".join(missing))
    global_required = (
        "final_fixed_release_zip: not-built",
        "DRC_v2.0.0_tag: not-created",
        "Status: **NOT RELEASED**",
    )
    missing = [snippet for snippet in global_required if snippet not in text]
    if missing:
        return _error("a downstream release gate advanced early: " + " | ".join(missing))
    print("v200_final_prerelease_aggregate_acceptance_sync_downstream_gates: manifest-accepted-fixed-zip-unchanged")
    return True


def _check_roadmap_sync() -> bool:
    text = _ROADMAP_PATH.read_text(encoding="utf-8")
    checkpoint = _extract_section(text, "Current v2.0.0 checkpoint:", "## Current baseline")
    required = (
        "public_repo_final_sweep_review: ACCEPTED",
        "final_aggregate_review: ACCEPTED",
        "accepted_private_evidence_manifest: ACCEPTED",
        "final_fixed_release_zip: not-built",
        "DRC_v2.0.0_tag: not-created",
        "release_status: NOT_RELEASED",
        "G-3 synchronizes the accepted Day70 final prerelease aggregate review",
        "The next unresolved gates are the final fixed release zip",
        "G-5 synchronizes public-safe acceptance",
    )
    missing = [snippet for snippet in required if snippet not in checkpoint]
    if missing:
        return _error("roadmap checkpoint is not synchronized: " + " | ".join(missing))
    print("v200_final_prerelease_aggregate_acceptance_sync_roadmap: synchronized")
    return True


def _check_scripts_readme_sync() -> bool:
    text = _SCRIPTS_README_PATH.read_text(encoding="utf-8")
    required = (
        "## v2.0.0 Commit G-3 public-safe final prerelease aggregate acceptance synchronization",
        "smoke_framework_v200_final_prerelease_aggregate_acceptance_sync.py",
        "public_repo_final_sweep_review: ACCEPTED",
        "final_aggregate_review: ACCEPTED",
        "accepted_private_evidence_manifest: NOT_ACCEPTED",
        "release_status: NOT_RELEASED",
    )
    missing = [snippet for snippet in required if snippet not in text]
    if missing:
        return _error("scripts README is not synchronized: " + " | ".join(missing))
    print("v200_final_prerelease_aggregate_acceptance_sync_scripts_readme: synchronized")
    return True


def _check_gitignore_boundary() -> bool:
    text = (ROOT / ".gitignore").read_text(encoding="utf-8")
    required = ("operator_evidence/", "_local/", "*.local.env")
    missing = [snippet for snippet in required if snippet not in text]
    if missing:
        return _error("gitignore no longer protects local-only evidence: " + " | ".join(missing))
    print("v200_final_prerelease_aggregate_acceptance_sync_gitignore_boundary: protected")
    return True


def _error(message: str) -> bool:
    print(
        "[smoke-framework-v200-final-prerelease-aggregate-acceptance-sync] "
        f"ERROR: {message}."
    )
    return False


if __name__ == "__main__":
    raise SystemExit(main())
