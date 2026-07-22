"""Verify G-2 public-safe public repository final sweep acceptance synchronization.

This source-tree check reads committed documentation markers only. It does not
read operator evidence, publish to GitHub, build release artifacts, create
release zips, call providers, call Google Health, start backend/Web services,
open browsers, inspect screenshots, or access external networks.
"""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

_CHECKLIST_PATH = ROOT / "docs/DRC_v200_goal_checklist_small_commit.md"
_DAY69_DOC_PATH = ROOT / "docs/v200_public_repo_final_sweep.md"
_ROADMAP_PATH = ROOT / "roadmap.md"
_SCRIPTS_README_PATH = ROOT / "scripts/README.md"

_ACCEPTANCE_SCOPE = "commit_scope: Commit G-2 only"
_ACCEPTANCE_REQUIRED_SNIPPETS = (
    "implementation_status: public-repo-final-sweep-acceptance-public-safe-synchronized",
    "accepted_requirement_key: public_repo_final_sweep_review",
    "day69_evidence_status: accepted",
    "day69_public_safe: True",
    "day69_forbidden_success_states_absent: True",
    "day69_requirement_satisfied: True",
    "license_scope_confirmed: True",
    "public_positioning_claims_reviewed: True",
    "public_docs_secret_hygiene_final_scan_completed: True",
    "release_surface_local_artifacts_absent: True",
    "raw_evidence_material_excluded: True",
    "mock_safe_default_preserved: True",
    "public_safe_evidence_recorded: True",
    "tracked_private_or_build_files_absent: True",
    "tracked_private_evidence_media_absent: True",
    "secret_shape_matches_absent: True",
    "raw_private_lan_ip_matches_absent: True",
    "private_absolute_path_matches_absent: True",
    "public_repo_final_sweep_review: ACCEPTED",
    "accepted_private_evidence_manifest: NOT_ACCEPTED",
    "final_aggregate_review: NOT_ACCEPTED",
    "final_fixed_release_zip: not-built",
    "DRC_v2.0.0_tag: not-created",
    "release_completion_status: NOT_RELEASED",
)
_PRIVATE_SAFETY_SNIPPET = (
    "private_evidence_policy: raw evidence, operator evidence files, screenshots, audio, "
    "provider payloads, health data, secrets, tokens, LAN IPs, private paths, and local "
    "artifacts remain uncommitted"
)
_PUBLIC_REPO_CHECKLIST_ITEMS = (
    "LICENSE exists.",
    "README / roadmap / docs clearly position DRC as an AI Character Framework public demo app.",
    "No API keys are committed.",
    "No tokens are committed.",
    "No authorization headers are committed.",
    "No raw provider payloads are committed.",
    "No raw audio is committed.",
    "No raw health data is committed.",
    "No raw screenshots are committed.",
    "No private paths are committed.",
    "No private LAN IPs are committed.",
    "Public docs explain that real execution requires explicit opt-in.",
    "Public docs do not claim v2.0.0 completion without accepted real Web evidence.",
    "Final public repo sweep is recorded as accepted evidence.",
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
    print("[smoke-framework-v200-public-repo-final-sweep-acceptance-sync] RESULT")

    if not _check_required_files():
        return 1
    if not _check_checklist_source_of_truth():
        return 1
    if not _check_definition_of_done():
        return 1
    if not _check_public_safe_acceptance_blocks():
        return 1
    if not _check_remaining_release_gates():
        return 1
    if not _check_roadmap_sync():
        return 1
    if not _check_scripts_readme_sync():
        return 1
    if not _check_gitignore_boundary():
        return 1

    print("v200_public_repo_final_sweep_acceptance_sync_status: accepted")
    print("v200_public_repo_final_sweep_acceptance_sync_public_safe: True")
    print("v200_public_repo_final_sweep_acceptance_sync_requirement_satisfied: True")
    print("v200_public_repo_final_sweep_acceptance_sync_remaining_release_status: NOT_RELEASED")
    print("[smoke-framework-v200-public-repo-final-sweep-acceptance-sync] OK")
    print(
        "No operator evidence read, GitHub publication, release build, release zip creation, "
        "provider/Google Health call, backend/Web startup, browser action, screenshot inspection, "
        "or external network access was performed."
    )
    return 0


def _check_required_files() -> bool:
    paths = (_CHECKLIST_PATH, _DAY69_DOC_PATH, _ROADMAP_PATH, _SCRIPTS_README_PATH)
    missing = [str(path.relative_to(ROOT)) for path in paths if not path.exists()]
    if missing:
        return _error("missing required files: " + ",".join(missing))
    print("v200_public_repo_final_sweep_acceptance_sync_required_files: present")
    return True


def _check_checklist_source_of_truth() -> bool:
    legacy_path = ROOT / "DRC_v200_goal_checklist_small_commit.md"
    if legacy_path.exists():
        return _error("legacy root checklist copy still exists")
    print("v200_public_repo_final_sweep_acceptance_sync_checklist_source_of_truth: docs-only")
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


def _check_definition_of_done() -> bool:
    text = _CHECKLIST_PATH.read_text(encoding="utf-8")
    section = _extract_section(
        text,
        "### 2.6 Public repository readiness evidence",
        "### 2.7 Accepted private evidence manifest",
    )
    if not section:
        return _error("public repository Definition of Done section is missing")
    missing = [
        item for item in _PUBLIC_REPO_CHECKLIST_ITEMS if f"- [x] {item}" not in section
    ]
    if missing:
        return _error("public repository Definition of Done remains incomplete: " + " | ".join(missing))
    if "public_repo_final_sweep_review: ACCEPTED" not in section:
        return _error("public repository source-of-truth status is not ACCEPTED")
    print("v200_public_repo_final_sweep_acceptance_sync_definition_of_done: complete")
    return True


def _check_public_safe_acceptance_blocks() -> bool:
    for path in (_CHECKLIST_PATH, _DAY69_DOC_PATH,):
        text = path.read_text(encoding="utf-8")
        block = _extract_commit_block(text)
        if not block:
            return _error(f"{path.relative_to(ROOT)} is missing the G-2 acceptance block")
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
    print("v200_public_repo_final_sweep_acceptance_sync_public_blocks: safe")
    return True


def _check_remaining_release_gates() -> bool:
    text = _CHECKLIST_PATH.read_text(encoding="utf-8")
    required = (
        "public_repo_final_sweep_review: ACCEPTED",
        "final_aggregate_review: ACCEPTED",
        "accepted_private_evidence_manifest: NOT_ACCEPTED",
        "final_fixed_release_zip: not-built",
        "DRC_v2.0.0_tag: not-created",
        "Status: **NOT RELEASED**",
    )
    missing = [snippet for snippet in required if snippet not in text]
    if missing:
        return _error("a later release gate advanced early: " + " | ".join(missing))
    print("v200_public_repo_final_sweep_acceptance_sync_later_gates: unchanged")
    return True


def _check_roadmap_sync() -> bool:
    text = _ROADMAP_PATH.read_text(encoding="utf-8")
    checkpoint = _extract_section(text, "Current v2.0.0 checkpoint:", "## Current baseline")
    required = (
        "real_google_health_sleep_data: ACCEPTED",
        "public_repo_final_sweep_review: ACCEPTED",
        "final_aggregate_review: ACCEPTED",
        "accepted_private_evidence_manifest: ACCEPTED",
        "final_fixed_release_zip: not-built",
        "DRC_v2.0.0_tag: not-created",
        "release_status: NOT_RELEASED",
        "G-1 removed tracked private evidence",
        "G-2 synchronizes the accepted Day69 public repository final sweep",
        "G-3 synchronizes the accepted Day70 final prerelease aggregate review",
        "G-5 synchronizes public-safe acceptance",
    )
    missing = [snippet for snippet in required if snippet not in checkpoint]
    if missing:
        return _error("roadmap checkpoint is not synchronized: " + " | ".join(missing))
    print("v200_public_repo_final_sweep_acceptance_sync_roadmap: synchronized")
    return True


def _check_scripts_readme_sync() -> bool:
    text = _SCRIPTS_README_PATH.read_text(encoding="utf-8")
    required = (
        "## v2.0.0 Commit G-2 public-safe public repository final sweep acceptance synchronization",
        "## v2.0.0 Commit G-3 public-safe final prerelease aggregate acceptance synchronization",
        "smoke_framework_v200_public_repo_final_sweep_acceptance_sync.py",
        "public_repo_final_sweep_review: ACCEPTED",
        "final_aggregate_review: ACCEPTED",
        "accepted_private_evidence_manifest: NOT_ACCEPTED",
        "release_status: NOT_RELEASED",
    )
    missing = [snippet for snippet in required if snippet not in text]
    if missing:
        return _error("scripts README is not synchronized: " + " | ".join(missing))
    print("v200_public_repo_final_sweep_acceptance_sync_scripts_readme: synchronized")
    return True


def _check_gitignore_boundary() -> bool:
    text = (ROOT / ".gitignore").read_text(encoding="utf-8")
    required = ("operator_evidence/", "_local/", "*.local.env")
    missing = [snippet for snippet in required if snippet not in text]
    if missing:
        return _error("gitignore no longer protects local-only evidence: " + " | ".join(missing))
    print("v200_public_repo_final_sweep_acceptance_sync_gitignore_boundary: protected")
    return True


def _error(message: str) -> bool:
    print(
        "[smoke-framework-v200-public-repo-final-sweep-acceptance-sync] "
        f"ERROR: {message}."
    )
    return False


if __name__ == "__main__":
    raise SystemExit(main())
