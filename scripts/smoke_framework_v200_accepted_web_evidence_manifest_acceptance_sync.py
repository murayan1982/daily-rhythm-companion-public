"""Verify G-5 public-safe Day80 private manifest acceptance synchronization.

This source-tree check reads committed public-safe markers only. It does not
read operator evidence, inspect private screenshots/audio/health data, build
release artifacts, create tags, call providers, call Google Health, start
backend/Web services, open browsers, publish to GitHub, or access networks.
"""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

_CHECKLIST_PATH = ROOT / "docs/DRC_v200_goal_checklist_small_commit.md"
_DAY80_DOC_PATH = ROOT / "docs/v200_accepted_web_evidence_manifest_aggregate.md"
_ROADMAP_PATH = ROOT / "roadmap.md"
_SCRIPTS_README_PATH = ROOT / "scripts/README.md"

_ACCEPTANCE_SCOPE = "commit_scope: Commit G-5 only"
_ACCEPTANCE_REQUIRED_SNIPPETS = (
    "implementation_status: accepted-private-evidence-manifest-public-safe-synchronized",
    "accepted_requirement_key: accepted_private_evidence_manifest",
    "day80_private_manifest_validation_status: accepted",
    "day80_private_manifest_public_safe: True",
    "day80_screenshot_references_public_safe: True",
    "day80_required_items_accepted: True",
    "day80_forbidden_success_states_absent: True",
    "required_evidence_items: real_llm_web_answer,real_tts_web_audio_output,real_google_health_sleep_data,web_image_display,image_asset_intake_review,public_repo_final_sweep_review,final_aggregate_review",
    "actual_drc_backend_api_used_for_web_capabilities: True",
    "web_ui_execution_confirmed_for_web_capabilities: True",
    "web_execution_results_visible: True",
    "all_required_screenshots_captured: True",
    "all_screenshot_references_recorded: True",
    "screenshots_private_storage_confirmed: True",
    "operator_review_accepted: True",
    "api_only_source_tree_command_output_rejected: True",
    "mock_fallback_skipped_unavailable_placeholder_rejected: True",
    "private_manifest_committed: False",
    "raw_evidence_committed: False",
    "accepted_private_evidence_manifest: ACCEPTED",
    "final_fixed_release_zip: not-built",
    "DRC_v2.0.0_tag: not-created",
    "release_completion_status: NOT_RELEASED",
)
_PRIVATE_SAFETY_SNIPPET = (
    "private_evidence_policy: raw screenshots, audio, health data, prompts, provider payloads, "
    "secrets, tokens, LAN IPs, private paths, and operator evidence files remain ignored and uncommitted"
)
_REQUIRED_MANIFEST_CHECKLIST_ITEMS = (
    "Private evidence manifest exists outside public release material.",
    "It records accepted evidence for `real_llm_web_answer`.",
    "It records accepted evidence for `real_tts_web_audio_output`.",
    "It records accepted evidence for `real_google_health_sleep_data`.",
    "It records accepted evidence for `image_asset_intake_review`.",
    "It records accepted evidence for `web_image_display`.",
    "It records accepted evidence for `public_repo_final_sweep_review`.",
    "It records accepted evidence for `final_aggregate_review`.",
    "Every Web-executed item includes a screenshot reference.",
    "API-only evidence is rejected.",
    "Source-tree-only evidence is rejected.",
    "Command-output-only evidence is rejected.",
    "Skipped evidence is rejected.",
    "Unavailable evidence is rejected.",
    "Fallback evidence is rejected.",
    "Mock evidence is rejected.",
    "Placeholder evidence is rejected.",
    "screenshot_missing evidence is rejected.",
)
_FORBIDDEN_ACCEPTANCE_BLOCK_TOKENS = (
    "http://",
    "https://",
    "file://",
    "localhost",
    "127.0.0.1",
    "192.168.",
    "private-operator-evidence://",
    "\\operator_evidence\\",
    "/operator_evidence/",
    "access_token",
    "refresh_token",
    "client_secret",
    "authorization: bearer",
)


def main() -> int:
    print("[smoke-framework-v200-accepted-web-evidence-manifest-acceptance-sync] RESULT")

    if not _check_required_files():
        return 1
    if not _check_checklist_source_of_truth():
        return 1
    if not _check_current_state():
        return 1
    if not _check_definition_of_done():
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

    print("v200_accepted_web_evidence_manifest_acceptance_sync_status: accepted")
    print("v200_accepted_web_evidence_manifest_acceptance_sync_public_safe: True")
    print("v200_accepted_web_evidence_manifest_acceptance_sync_requirement_satisfied: True")
    print("v200_accepted_web_evidence_manifest_acceptance_sync_remaining_release_status: NOT_RELEASED")
    print("[smoke-framework-v200-accepted-web-evidence-manifest-acceptance-sync] OK")
    print(
        "No operator evidence read, private screenshot/audio/health inspection, release build or zip "
        "inspection, provider/Google Health call, backend/Web startup, browser action, GitHub "
        "publication, tag creation, or external network access was performed."
    )
    return 0


def _check_required_files() -> bool:
    paths = (_CHECKLIST_PATH, _DAY80_DOC_PATH, _ROADMAP_PATH, _SCRIPTS_README_PATH)
    missing = [str(path.relative_to(ROOT)) for path in paths if not path.exists()]
    if missing:
        return _error("missing required files: " + ",".join(missing))
    print("v200_accepted_web_evidence_manifest_acceptance_sync_required_files: present")
    return True


def _check_checklist_source_of_truth() -> bool:
    legacy_path = ROOT / "DRC_v200_goal_checklist_small_commit.md"
    if legacy_path.exists():
        return _error("legacy root checklist copy still exists")
    print("v200_accepted_web_evidence_manifest_acceptance_sync_checklist_source_of_truth: docs-only")
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
        "- [x] Commit G-5 synchronizes the accepted Day80 private evidence manifest using public-safe markers only.",
        "- [x] Accepted private evidence manifest has been populated with real evidence.",
        "accepted_private_evidence_manifest: ACCEPTED",
        "final_fixed_release_zip: not-built",
        "DRC_v2.0.0_tag: not-created",
        "Status: **NOT RELEASED**",
    )
    missing = [snippet for snippet in required if snippet not in text]
    if missing:
        return _error("current source-of-truth state is not synchronized: " + " | ".join(missing))
    print("v200_accepted_web_evidence_manifest_acceptance_sync_current_state: synchronized")
    return True


def _check_definition_of_done() -> bool:
    text = _CHECKLIST_PATH.read_text(encoding="utf-8")
    section = _extract_section(
        text,
        "### 2.7 Accepted private evidence manifest",
        "### 2.8 Final fixed release zip",
    )
    missing = [
        item for item in _REQUIRED_MANIFEST_CHECKLIST_ITEMS if f"- [x] {item}" not in section
    ]
    if "accepted_private_evidence_manifest: ACCEPTED" not in section:
        missing.append("accepted_private_evidence_manifest: ACCEPTED")
    if missing:
        return _error("accepted private manifest definition of done is incomplete: " + " | ".join(missing))
    print("v200_accepted_web_evidence_manifest_acceptance_sync_definition_of_done: complete")
    return True


def _check_public_safe_acceptance_blocks() -> bool:
    for path in (_CHECKLIST_PATH, _DAY80_DOC_PATH,):
        text = path.read_text(encoding="utf-8")
        block = _extract_commit_block(text)
        if not block:
            return _error(f"{path.relative_to(ROOT)} is missing the G-5 acceptance block")
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
    print("v200_accepted_web_evidence_manifest_acceptance_sync_public_blocks: safe")
    return True


def _check_downstream_release_gates() -> bool:
    text = _CHECKLIST_PATH.read_text(encoding="utf-8")
    zip_section = _extract_section(
        text,
        "### 2.8 Final fixed release zip",
        "### 2.9 Final tag/release",
    )
    required_checked = (
        "All accepted Web evidence requirements are complete before building the final release zip.",
    )
    required_unchecked = (
        "Build the final release zip once.",
        "Record the exact zip path.",
        "Run final checks against that same fixed zip without rebuilding.",
    )
    missing = [item for item in required_checked if f"- [x] {item}" not in zip_section]
    missing.extend(
        item for item in required_unchecked if f"- [ ] {item}" not in zip_section
    )
    global_required = (
        "final_fixed_release_zip: not-built",
        "DRC_v2.0.0_tag: not-created",
        "Status: **NOT RELEASED**",
    )
    missing.extend(snippet for snippet in global_required if snippet not in text)
    if missing:
        return _error("a downstream release gate advanced early: " + " | ".join(missing))
    print("v200_accepted_web_evidence_manifest_acceptance_sync_downstream_gates: unchanged")
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
        "G-5 synchronizes public-safe acceptance",
        "The next unresolved gates are the final fixed release zip",
    )
    missing = [snippet for snippet in required if snippet not in checkpoint]
    if missing:
        return _error("roadmap checkpoint is not synchronized: " + " | ".join(missing))
    print("v200_accepted_web_evidence_manifest_acceptance_sync_roadmap: synchronized")
    return True


def _check_scripts_readme_sync() -> bool:
    text = _SCRIPTS_README_PATH.read_text(encoding="utf-8")
    required = (
        "## v2.0.0 Commit G-5 public-safe accepted private evidence manifest synchronization",
        "smoke_framework_v200_accepted_web_evidence_manifest_acceptance_sync.py",
        "accepted_private_evidence_manifest: ACCEPTED",
        "final_fixed_release_zip: not-built",
        "DRC_v2.0.0_tag: not-created",
        "release_status: NOT_RELEASED",
    )
    missing = [snippet for snippet in required if snippet not in text]
    if missing:
        return _error("scripts README is not synchronized: " + " | ".join(missing))
    print("v200_accepted_web_evidence_manifest_acceptance_sync_scripts_readme: synchronized")
    return True


def _check_gitignore_boundary() -> bool:
    text = (ROOT / ".gitignore").read_text(encoding="utf-8")
    required = ("operator_evidence/", "_local/", "*.local.env")
    missing = [snippet for snippet in required if snippet not in text]
    if missing:
        return _error("gitignore no longer protects local-only evidence: " + " | ".join(missing))
    print("v200_accepted_web_evidence_manifest_acceptance_sync_gitignore_boundary: protected")
    return True


def _error(message: str) -> bool:
    print(
        "[smoke-framework-v200-accepted-web-evidence-manifest-acceptance-sync] "
        f"ERROR: {message}."
    )
    return False


if __name__ == "__main__":
    raise SystemExit(main())
