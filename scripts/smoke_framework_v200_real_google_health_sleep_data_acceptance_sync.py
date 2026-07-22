"""Verify E-9 public-safe real Google Health sleep-data acceptance sync.

This source-tree check reads committed documentation markers only. It does not
call Google Health, read credentials or OAuth tokens, start the DRC backend, open
Flutter Web, inspect screenshots, read operator evidence, or build release
artifacts.
"""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

_CHECKLIST_PATH = ROOT / "docs/DRC_v200_goal_checklist_small_commit.md"
_RUNBOOK_PATH = ROOT / "docs/v200_real_google_health_sleep_data_operator_runbook.md"
_ROADMAP_PATH = ROOT / "roadmap.md"
_SCRIPTS_README_PATH = ROOT / "scripts/README.md"

_ACCEPTANCE_SCOPE = "commit_scope: Commit E-9 only"
_ACCEPTANCE_REQUIRED_SNIPPETS = (
    "implementation_status: real-google-health-sleep-data-acceptance-public-safe-synchronized",
    "accepted_requirement_key: real_google_health_sleep_data",
    "actual_drc_backend_api_status: confirmed",
    "pc_web_ui_status: confirmed",
    "smartphone_web_ui_status: confirmed",
    "day55_evidence_status: accepted",
    "day55_public_safe: True",
    "day66_execution_evidence_status: accepted",
    "day66_public_safe: True",
    "day66_forbidden_success_states_absent: True",
    "day66_requirement_satisfied: True",
    "day78_screenshot_evidence_status: accepted",
    "day78_public_safe: True",
    "day78_screenshot_reference_public_safe: True",
    "day78_forbidden_success_states_absent: True",
    "combined_acceptance_status: accepted",
    "combined_requirement_satisfied: True",
    "operator_evidence_acceptance_status: ACCEPTED",
    "accepted_private_evidence_manifest: NOT_ACCEPTED",
    "final_fixed_release_zip: not-built",
    "DRC_v2.0.0_tag: not-created",
    "release_completion_status: NOT_RELEASED",
    "real_google_health_sleep_data: ACCEPTED",
)
_PRIVATE_SAFETY_SNIPPET = (
    "private_evidence_policy: raw screenshots, raw Google Health payloads, raw sleep values, "
    "precise timestamps, OAuth values, credentials, authorization headers, LAN IPs, private "
    "paths, and operator evidence files remain uncommitted"
)
_GOOGLE_HEALTH_CHECKLIST_ITEMS = (
    "Real Google Health / OAuth flow is configured with explicit opt-in only.",
    "The Web UI / smartphone Web UI calls the actual DRC backend API.",
    "Real sleep data is retrieved from Google Health.",
    "The data is normalized into the DRC sleep summary surface.",
    "The Web UI shows that the result is real Google Health-backed data.",
    "A screenshot of the Web UI result is captured.",
    "The screenshot reference is recorded in private operator evidence.",
    "Tokens, authorization headers, raw health payloads, raw personal health data, and private paths are not committed.",
    "Mock, fallback, skipped, unavailable, or placeholder data is not counted as success.",
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
    print("[smoke-framework-v200-real-google-health-sleep-data-acceptance-sync] RESULT")

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

    print("v200_real_google_health_sleep_data_acceptance_sync_status: accepted")
    print("v200_real_google_health_sleep_data_acceptance_sync_public_safe: True")
    print("v200_real_google_health_sleep_data_acceptance_sync_requirement_satisfied: True")
    print("v200_real_google_health_sleep_data_acceptance_sync_remaining_release_status: NOT_RELEASED")
    print("[smoke-framework-v200-real-google-health-sleep-data-acceptance-sync] OK")
    print(
        "No Google Health call, credential/token read, backend/Web startup, screenshot "
        "inspection, private evidence read, fixed zip build, or tag creation was performed."
    )
    return 0


def _check_required_files() -> bool:
    paths = (_CHECKLIST_PATH, _RUNBOOK_PATH, _ROADMAP_PATH, _SCRIPTS_README_PATH)
    missing = [str(path.relative_to(ROOT)) for path in paths if not path.exists()]
    if missing:
        return _error("missing required files: " + ",".join(missing))
    print("v200_real_google_health_sleep_data_acceptance_sync_required_files: present")
    return True


def _check_checklist_source_of_truth() -> bool:
    legacy_path = ROOT / "DRC_v200_goal_checklist_small_commit.md"
    if legacy_path.exists():
        return _error("legacy root checklist copy still exists")
    print("v200_real_google_health_sleep_data_acceptance_sync_checklist_source_of_truth: docs-only")
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
        "### 2.3 Real Google Health sleep data evidence",
        "### 2.4 Image asset generation and safe intake evidence",
    )
    if not section:
        return _error("Google Health Definition of Done section is missing")
    missing = [
        item for item in _GOOGLE_HEALTH_CHECKLIST_ITEMS if f"- [x] {item}" not in section
    ]
    if missing:
        return _error("Google Health Definition of Done remains incomplete: " + " | ".join(missing))
    if "real_google_health_sleep_data: ACCEPTED" not in section:
        return _error("Google Health source-of-truth status is not ACCEPTED")
    print("v200_real_google_health_sleep_data_acceptance_sync_definition_of_done: complete")
    return True


def _check_public_safe_acceptance_blocks() -> bool:
    for path in (_CHECKLIST_PATH, _RUNBOOK_PATH,):
        text = path.read_text(encoding="utf-8")
        block = _extract_commit_block(text)
        if not block:
            return _error(f"{path.relative_to(ROOT)} is missing the E-9 acceptance block")
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
    print("v200_real_google_health_sleep_data_acceptance_sync_public_blocks: safe")
    return True


def _check_remaining_release_gates() -> bool:
    text = _CHECKLIST_PATH.read_text(encoding="utf-8")
    required = (
        "- [x] Real Web UI execution evidence has been collected.",
        "- [x] Web UI result screenshots have been collected.",
        "real_google_health_sleep_data: ACCEPTED",
        "accepted_private_evidence_manifest: NOT_ACCEPTED",
        "final_fixed_release_zip: not-built",
        "DRC_v2.0.0_tag: not-created",
        "Status: **NOT RELEASED**",
    )
    missing = [snippet for snippet in required if snippet not in text]
    if missing:
        return _error("a later release gate is not preserved: " + " | ".join(missing))
    print("v200_real_google_health_sleep_data_acceptance_sync_later_gates: unchanged")
    return True


def _check_roadmap_sync() -> bool:
    text = _ROADMAP_PATH.read_text(encoding="utf-8")
    checkpoint = _extract_section(text, "Current v2.0.0 checkpoint:", "## Current baseline")
    required = (
        "real_tts_web_audio_output: ACCEPTED",
        "real_google_health_sleep_data: ACCEPTED",
        "accepted_private_evidence_manifest: ACCEPTED",
        "final_fixed_release_zip: not-built",
        "DRC_v2.0.0_tag: not-created",
        "release_status: NOT_RELEASED",
        "E-9 synchronizes public-safe acceptance",
        "G-5 synchronizes public-safe acceptance",
    )
    missing = [snippet for snippet in required if snippet not in checkpoint]
    if missing:
        return _error("roadmap checkpoint is not synchronized: " + " | ".join(missing))
    print("v200_real_google_health_sleep_data_acceptance_sync_roadmap: synchronized")
    return True


def _check_scripts_readme_sync() -> bool:
    text = _SCRIPTS_README_PATH.read_text(encoding="utf-8")
    required = (
        "## v2.0.0 Commit E-9 public-safe real Google Health sleep-data acceptance synchronization",
        "smoke_framework_v200_real_google_health_sleep_data_acceptance_sync.py",
        "real_google_health_sleep_data: ACCEPTED",
        "accepted_private_evidence_manifest: NOT_ACCEPTED",
        "release_status: NOT_RELEASED",
    )
    missing = [snippet for snippet in required if snippet not in text]
    if missing:
        return _error("scripts README is not synchronized: " + " | ".join(missing))
    print("v200_real_google_health_sleep_data_acceptance_sync_scripts_readme: synchronized")
    return True


def _check_gitignore_boundary() -> bool:
    text = (ROOT / ".gitignore").read_text(encoding="utf-8")
    required = ("operator_evidence/", "_local/", "*.local.env")
    missing = [snippet for snippet in required if snippet not in text]
    if missing:
        return _error("gitignore no longer protects local-only evidence: " + " | ".join(missing))
    print("v200_real_google_health_sleep_data_acceptance_sync_gitignore_boundary: protected")
    return True


def _error(message: str) -> bool:
    print(
        "[smoke-framework-v200-real-google-health-sleep-data-acceptance-sync] "
        f"ERROR: {message}."
    )
    return False


if __name__ == "__main__":
    raise SystemExit(main())
