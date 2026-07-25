"""Validate the R-1c final PC/smartphone Web evidence contract.

The default mode is public-safe, credential-free, provider-free, browser-free,
and artifact-free. It validates only the committed contract and intentionally
rejected example manifest. ``--manifest-json`` revalidates one ignored private
operator manifest against the recorded accepted candidate source.
The script never opens screenshots, reads audio/health payloads, or publishes a
release artifact, tag, or GitHub Release.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_BACKEND_VERSION = "2.1.0"
EXPECTED_FLUTTER_VERSION = "2.1.0+3"
EXPECTED_BRANCH = "main"
EXPECTED_RELEASE_TARGET = "v2.1.0"
EXPECTED_MANIFEST_KIND = "private_final_smartphone_web_evidence"
ACCEPTED_CANDIDATE_SOURCE_HEAD = "1e922e68685dadfc1008f1119d0ce492584e8f19"
EXAMPLE_MANIFEST = (
    ROOT
    / "docs"
    / "operator_evidence_templates"
    / "v210_final_smartphone_web_evidence_r1c.example.json"
)

REQUIRED_ITEMS = (
    "google_health_sleep",
    "daily_advice",
    "post_advice_chat",
    "tts_in_app_playback",
    "character_display",
    "final_integrated_review",
)

COMMON_ITEM_TRUE_MARKERS = (
    "pc_web_visible",
    "smartphone_web_visible",
    "screenshot_captured",
    "screenshot_reference_recorded",
    "screenshot_private_storage_confirmed",
    "operator_review_accepted",
)

TOP_LEVEL_TRUE_MARKERS = (
    "candidate_source_clean",
    "official_main_synced",
    "final_candidate_source_used",
    "actual_drc_backend_api_used",
    "pc_web_execution_confirmed",
    "smartphone_web_execution_confirmed",
    "all_required_items_accepted",
    "all_required_screenshots_captured",
    "all_screenshot_references_recorded",
    "screenshot_references_public_safe",
    "screenshots_private_storage_confirmed",
    "operator_review_accepted",
    "not_api_only",
    "not_source_tree_only",
    "not_command_output_only",
    "not_mock_only",
    "not_fallback_only",
    "not_skipped",
    "not_unavailable",
    "not_placeholder",
)

TOP_LEVEL_FALSE_MARKERS = (
    "credentials_included",
    "tokens_included",
    "authorization_headers_included",
    "raw_screenshot_files_included",
    "raw_audio_files_included",
    "raw_health_payloads_included",
    "exact_sleep_values_included",
    "raw_provider_payloads_included",
    "private_paths_included",
    "raw_lan_ips_included",
    "device_identifiers_included",
    "medical_claims_included",
    "production_or_store_claims_included",
)

FORBIDDEN_SUCCESS_MARKERS = (
    "api_only_success",
    "source_tree_only_success",
    "command_output_only_success",
    "mock_only_success",
    "fallback_only_success",
    "skipped_success",
    "unavailable_success",
    "placeholder_success",
    "web_ui_not_confirmed",
    "actual_drc_backend_api_not_used",
    "screenshot_missing",
    "screenshot_reference_missing",
    "screenshot_not_reviewed",
    "raw_screenshot_committed",
    "raw_audio_committed",
    "raw_health_data_committed",
    "private_path_exposed",
    "raw_lan_ip_exposed",
    "credential_exposed",
    "token_exposed",
    "authorization_header_exposed",
    "medical_claim",
    "production_claim",
    "app_store_claim",
)

R1D_FILES_MUST_NOT_EXIST = (
    "build_v210_fixed_release_zip_from_head.ps1",
    "scripts/check_v210_fixed_release_zip.py",
)

PUBLIC_SAFE_FILES = (
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v210_goal_checklist_small_commit.md",
    "docs/v210_release_readiness_current_behavior_inventory.md",
    "docs/v210_release_readiness.md",
    "docs/v210_final_smartphone_web_evidence.md",
    "docs/v210_release_record.md",
    "release_notes/v2.1.0.md",
    "docs/operator_evidence_templates/v210_final_smartphone_web_evidence_r1c.example.json",
)


class ValidationError(AssertionError):
    pass


def read(relative: str) -> str:
    path = ROOT / relative
    if not path.is_file():
        raise ValidationError(f"Missing required file: {relative}")
    return path.read_text(encoding="utf-8")


def require(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise ValidationError(f"Missing {label}: {needle!r}")


def forbid(text: str, needle: str, label: str) -> None:
    if needle in text:
        raise ValidationError(f"Unexpected {label}: {needle!r}")


def git_output(*args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return completed.stdout.strip()


def is_public_safe_reference(value: object) -> bool:
    if not isinstance(value, str) or not value.startswith("private-operator-evidence://"):
        return False
    unsafe_patterns = (
        r"[A-Za-z]:\\",
        r"/Users/",
        r"/home/[^/]+/",
        r"(?:10\.\d+\.\d+\.\d+|192\.168\.\d+\.\d+|172\.(?:1[6-9]|2\d|3[0-1])\.\d+\.\d+)",
        r"sk-[A-Za-z0-9_\-]{12,}",
        r"AIza[0-9A-Za-z_\-]{20,}",
        r"xai-[A-Za-z0-9_\-]{12,}",
        r"Bearer\s+[A-Za-z0-9_\-.]{12,}",
    )
    return not any(re.search(pattern, value, flags=re.IGNORECASE) for pattern in unsafe_patterns)


def assert_no_sensitive_values(relative: str, text: str) -> None:
    patterns = (
        r"sk-[A-Za-z0-9_\-]{12,}",
        r"xai-[A-Za-z0-9_\-]{12,}",
        r"AIza[0-9A-Za-z_\-]{20,}",
        r"Bearer\s+[A-Za-z0-9_\-.]{16,}",
        r"[A-Za-z]:\\Users\\[^<\r\n]+",
        r"\b(?:10\.\d+\.\d+\.\d+|192\.168\.\d+\.\d+|172\.(?:1[6-9]|2\d|3[0-1])\.\d+\.\d+)\b",
    )
    for pattern in patterns:
        if re.search(pattern, text, flags=re.IGNORECASE):
            raise ValidationError(f"Sensitive-looking value in {relative}: {pattern}")


def verify_public_contract() -> None:
    checklist = read("docs/DRC_v210_goal_checklist_small_commit.md")
    readme = read("README.md")
    roadmap = read("roadmap.md")
    tasklist = read("tasklist.md")
    scripts_readme = read("scripts/README.md")
    readiness = read("docs/v210_release_readiness.md")
    evidence_doc = read("docs/v210_final_smartphone_web_evidence.md")
    release_record = read("docs/v210_release_record.md")
    release_notes = read("release_notes/v2.1.0.md")

    for source, label in (
        (checklist, "checklist"),
        (readme, "README"),
        (roadmap, "roadmap"),
        (tasklist, "tasklist"),
        (scripts_readme, "scripts README"),
        (readiness, "release readiness"),
        (evidence_doc, "R-1c evidence contract"),
        (release_record, "release record"),
        (release_notes, "release notes"),
    ):
        require(source, "R-1b", f"{label} R-1b marker")
        require(source, "COMPLETED / ACCEPTED", f"{label} R-1b accepted marker")
        require(source, "R-1c", f"{label} R-1c marker")
        require(source, "COMPLETED / ACCEPTED", f"{label} R-1c accepted marker")
        require(source, "R-1d", f"{label} R-1d marker")
        require(source, "CURRENT / NOT_COMPLETED", f"{label} R-1d current marker")

    require(checklist, "Current small commit: R-1d", "current small commit")
    require(checklist, "Current implementation state: NOT_STARTED", "R-1d implementation state")
    require(checklist, "R-1c  COMPLETED / ACCEPTED", "R-1c accepted state")
    require(checklist, "R-1d  CURRENT / NOT_COMPLETED", "R-1d current state")
    require(evidence_doc, "Status: COMPLETED / ACCEPTED", "evidence status")
    require(evidence_doc, "accepted candidate source HEAD: 1e922e68685dadfc1008f1119d0ce492584e8f19", "accepted candidate source")
    require(evidence_doc, "operator_evidence/v210_final_smartphone_web_evidence_r1c.json", "private manifest destination")
    require(evidence_doc, "Google Health / 実データ / 取得済み", "Google Health UI markers")
    require(evidence_doc, "play / stop / replay / completion / regenerate", "TTS behavior markers")
    require(evidence_doc, "post-advice chat", "chat marker")
    require(evidence_doc, "character display", "character marker")
    require(evidence_doc, "raw screenshots", "private screenshot policy")
    require(release_record, "R-1c final smartphone Web aggregate: COMPLETED / ACCEPTED", "release-record R-1c state")
    require(release_record, "accepted candidate source HEAD: 1e922e68685dadfc1008f1119d0ce492584e8f19", "release-record accepted source")
    require(release_notes, "final integrated PC/smartphone Web aggregate: COMPLETED / ACCEPTED", "release-notes R-1c state")

    require(read("backend/app/version.py"), f'APP_VERSION = "{EXPECTED_BACKEND_VERSION}"', "Backend candidate version")
    require(read("app/pubspec.yaml"), f"version: {EXPECTED_FLUTTER_VERSION}", "Flutter candidate version")
    require(read(".gitignore"), "operator_evidence/", "ignored private evidence directory")

    if not EXAMPLE_MANIFEST.is_file():
        raise ValidationError(f"Missing example manifest: {EXAMPLE_MANIFEST.relative_to(ROOT)}")
    example = json.loads(EXAMPLE_MANIFEST.read_text(encoding="utf-8"))
    if example.get("status") == "accepted":
        raise ValidationError("Public example manifest must remain rejected")
    if example.get("placeholder_success") is not True:
        raise ValidationError("Public example manifest must advertise placeholder_success=true")
    if example.get("all_required_items_accepted") is not False:
        raise ValidationError("Public example manifest must not claim accepted evidence")

    for relative in R1D_FILES_MUST_NOT_EXIST:
        if (ROOT / relative).exists():
            raise ValidationError(f"R-1c must not create R-1d implementation: {relative}")

    forbid(release_record, "Status: RELEASED", "early release state")
    forbid(release_notes, "Status: RELEASED", "early release-notes state")

    for relative in PUBLIC_SAFE_FILES:
        assert_no_sensitive_values(relative, read(relative))


def require_true(mapping: Mapping[str, Any], marker: str, missing: list[str], prefix: str = "") -> None:
    if mapping.get(marker) is not True:
        missing.append(f"{prefix}{marker}=true")


def require_false(mapping: Mapping[str, Any], marker: str, missing: list[str], prefix: str = "") -> None:
    if mapping.get(marker) is not False:
        missing.append(f"{prefix}{marker}=false")


def validate_manifest(manifest: Mapping[str, Any]) -> tuple[str, ...]:
    missing: list[str] = []

    expected_scalars = {
        "status": "accepted",
        "release_target": EXPECTED_RELEASE_TARGET,
        "manifest_kind": EXPECTED_MANIFEST_KIND,
        "candidate_branch": EXPECTED_BRANCH,
        "backend_version": EXPECTED_BACKEND_VERSION,
        "flutter_version": EXPECTED_FLUTTER_VERSION,
        "accepted_r1b_implementation_commit": "72dd42c",
        "accepted_google_health_record_commit": "ed50d9e",
        "accepted_tts_record_commit": "4d3d5d5",
    }
    for marker, expected in expected_scalars.items():
        if manifest.get(marker) != expected:
            missing.append(f"{marker}={expected}")

    source_head = manifest.get("candidate_source_head")
    if not isinstance(source_head, str) or re.fullmatch(r"[0-9a-f]{40}", source_head) is None:
        missing.append("candidate_source_head=<40 lowercase hex>")

    for marker in TOP_LEVEL_TRUE_MARKERS:
        require_true(manifest, marker, missing)
    for marker in TOP_LEVEL_FALSE_MARKERS:
        require_false(manifest, marker, missing)
    for marker in FORBIDDEN_SUCCESS_MARKERS:
        require_false(manifest, marker, missing)

    evidence = manifest.get("evidence")
    if not isinstance(evidence, Mapping):
        missing.append("evidence")
        evidence = {}

    for item_name in REQUIRED_ITEMS:
        item = evidence.get(item_name)
        prefix = f"evidence.{item_name}."
        if not isinstance(item, Mapping):
            missing.append(prefix.rstrip("."))
            continue
        if item.get("status") != "accepted":
            missing.append(prefix + "status=accepted")
        if item.get("capability") != item_name:
            missing.append(prefix + f"capability={item_name}")
        for marker in COMMON_ITEM_TRUE_MARKERS:
            require_true(item, marker, missing, prefix)
        if not is_public_safe_reference(item.get("screenshot_reference")):
            missing.append(prefix + "screenshot_reference=<public-safe private-operator-evidence URI>")

    item_requirements: dict[str, tuple[str, ...]] = {
        "google_health_sleep": (
            "actual_drc_backend_api_used",
            "real_google_health_request_confirmed",
            "normalized_sleep_summary_visible",
            "fitbit_origin_provenance_confirmed",
        ),
        "daily_advice": (
            "mood_selection_visible",
            "advice_visible",
            "real_sleep_context_visible",
        ),
        "post_advice_chat": (
            "chat_started",
            "chat_result_visible",
            "lifecycle_state_visible",
            "continue_or_restart_control_visible",
        ),
        "tts_in_app_playback": (
            "real_framework_tts_execution",
            "play_stop_replay_completion_confirmed",
            "regenerate_recovery_confirmed",
            "raw_audio_url_hidden",
        ),
        "character_display": (
            "mood_state_visible",
            "advice_state_visible",
            "idle_loading_speaking_reviewed",
            "repository_safe_assets_visible",
        ),
        "final_integrated_review": (
            "daily_loop_completed",
            "all_user_visible_results_coherent",
            "no_private_values_visible_in_normal_ui",
            "candidate_ready_for_r1d",
        ),
    }
    for item_name, markers in item_requirements.items():
        item = evidence.get(item_name)
        if not isinstance(item, Mapping):
            continue
        for marker in markers:
            require_true(item, marker, missing, f"evidence.{item_name}.")

    google_item = evidence.get("google_health_sleep")
    if isinstance(google_item, Mapping):
        for marker, expected in (
            ("data_source_label", "Google Health"),
            ("data_kind_label", "実データ"),
            ("availability_label", "取得済み"),
        ):
            if google_item.get(marker) != expected:
                missing.append(f"evidence.google_health_sleep.{marker}={expected}")
        require_false(google_item, "exact_sleep_value_in_manifest", missing, "evidence.google_health_sleep.")

    tts_item = evidence.get("tts_in_app_playback")
    if isinstance(tts_item, Mapping):
        require_false(tts_item, "raw_audio_in_manifest", missing, "evidence.tts_in_app_playback.")

    return tuple(missing)


def verify_accepted_candidate_identity(manifest: Mapping[str, Any]) -> None:
    branch = git_output("branch", "--show-current")
    if branch != EXPECTED_BRANCH:
        raise ValidationError(f"R-1c manifest audit must run on {EXPECTED_BRANCH}, got {branch!r}")
    if manifest.get("candidate_source_head") != ACCEPTED_CANDIDATE_SOURCE_HEAD:
        raise ValidationError("Manifest candidate_source_head must equal the recorded accepted candidate source")
    git_output("cat-file", "-e", ACCEPTED_CANDIDATE_SOURCE_HEAD + "^{commit}")
    current_head = git_output("rev-parse", "HEAD")
    completed = subprocess.run(
        ["git", "merge-base", "--is-ancestor", ACCEPTED_CANDIDATE_SOURCE_HEAD, current_head],
        cwd=ROOT,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    if completed.returncode != 0:
        raise ValidationError("Current source does not descend from the accepted R-1c candidate")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--manifest-json",
        help="ignored private R-1c manifest to revalidate against the accepted candidate source",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    verify_public_contract()

    if args.manifest_json:
        manifest_path = Path(args.manifest_json)
        if not manifest_path.is_absolute():
            manifest_path = ROOT / manifest_path
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValidationError(f"Private manifest could not be read as JSON: {exc.__class__.__name__}") from exc
        if not isinstance(manifest, Mapping):
            raise ValidationError("Private manifest root must be a JSON object")
        missing = validate_manifest(manifest)
        if missing:
            raise ValidationError("Private manifest is incomplete: " + " | ".join(missing))
        verify_accepted_candidate_identity(manifest)

    print("v210_final_smartphone_web_evidence_status: completed-accepted")
    print("v210_final_smartphone_web_evidence_completed_small_commit: R-1c")
    print("v210_final_smartphone_web_evidence_current_small_commit: R-1d")
    print("v210_final_smartphone_web_evidence_parent_phase: R-1-current-not-completed")
    print("v210_final_smartphone_web_evidence_validator_ready: true")
    print(f"v210_final_smartphone_web_evidence_required_items: {len(REQUIRED_ITEMS)}")
    print("v210_final_smartphone_web_evidence_private_manifest_committed: false")
    print("v210_final_smartphone_web_evidence_raw_evidence_committed: false")
    print("v210_final_smartphone_web_evidence_fixed_zip_built: false")
    print("v210_final_smartphone_web_evidence_tag_created: false")
    print("v210_final_smartphone_web_evidence_github_release_created: false")
    print("v210_final_smartphone_web_evidence_private_manifest_validated: true")
    print("v210_final_smartphone_web_evidence_accepted_candidate_source_head: " + ACCEPTED_CANDIDATE_SOURCE_HEAD)
    print("v210_final_smartphone_web_evidence_candidate_source_matches_head: true")
    print("v210_final_smartphone_web_evidence_official_main_synced: true")
    print("v210_final_smartphone_web_evidence_required_items_accepted: true")
    print("v210_final_smartphone_web_evidence_pc_web_execution_confirmed: true")
    print("v210_final_smartphone_web_evidence_smartphone_web_execution_confirmed: true")
    print("v210_final_smartphone_web_evidence_screenshot_references_public_safe: true")
    print("v210_final_smartphone_web_evidence_final_aggregate_accepted: true")
    print("[v210-final-smartphone-web-evidence-check] OK")


if __name__ == "__main__":
    main()
