"""Render or validate v2.0.0 Day80 accepted Web evidence manifest aggregate."""

from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.app.services.framework_v200_accepted_web_evidence_manifest_aggregate import (  # noqa: E402
    build_v200_accepted_web_evidence_manifest_aggregate_contract,
    render_v200_accepted_web_evidence_manifest_aggregate_contract,
    render_v200_accepted_web_evidence_manifest_aggregate_validation,
    validate_v200_accepted_web_evidence_manifest_aggregate,
)


_EXAMPLE_MANIFEST_PATH = (
    ROOT
    / "docs"
    / "operator_evidence_templates"
    / "v200_accepted_web_evidence_manifest_day80.example.json"
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest-json", help="Optional private Day80 Web evidence manifest JSON to validate.")
    args = parser.parse_args()

    contract = build_v200_accepted_web_evidence_manifest_aggregate_contract()
    print(render_v200_accepted_web_evidence_manifest_aggregate_contract(contract))

    if not _run_source_tree_contract_checks():
        return 1

    if args.manifest_json:
        try:
            manifest_path = Path(args.manifest_json)
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            print("[smoke-framework-v200-accepted-web-evidence-manifest-aggregate] INCOMPLETE")
            print(f"private Day80 manifest could not be read as JSON: {exc.__class__.__name__}")
            return 1

        validation = validate_v200_accepted_web_evidence_manifest_aggregate(manifest)
        print(render_v200_accepted_web_evidence_manifest_aggregate_validation(validation))
        if validation.status != "accepted":
            print("[smoke-framework-v200-accepted-web-evidence-manifest-aggregate] INCOMPLETE")
            return 1

    print("[smoke-framework-v200-accepted-web-evidence-manifest-aggregate] OK")
    return 0


def _run_source_tree_contract_checks() -> bool:
    """Exercise the committed Day80 template and validator without private evidence."""

    if not _EXAMPLE_MANIFEST_PATH.exists():
        return _source_tree_error("public Day80 example manifest is missing")

    try:
        example = json.loads(_EXAMPLE_MANIFEST_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return _source_tree_error(
            f"public Day80 example manifest could not be read as JSON: {exc.__class__.__name__}"
        )

    example_validation = validate_v200_accepted_web_evidence_manifest_aggregate(example)
    if example_validation.status == "accepted":
        return _source_tree_error("public Day80 example manifest must remain non-accepted")
    print("v200_accepted_web_evidence_manifest_aggregate_example_status: rejected-as-template")

    synthetic = _build_synthetic_accepted_manifest(example)
    synthetic_validation = validate_v200_accepted_web_evidence_manifest_aggregate(synthetic)
    if synthetic_validation.status != "accepted":
        return _source_tree_error(
            "synthetic accepted manifest failed: " + ",".join(synthetic_validation.missing_markers)
        )
    print("v200_accepted_web_evidence_manifest_aggregate_synthetic_accepted_status: accepted")

    rejection_cases: tuple[tuple[str, dict[str, Any]], ...] = (
        ("missing_required_item", _without_required_item(synthetic, "real_llm_web_answer")),
        ("screenshot_missing", _with_value(synthetic, ("screenshot_missing",), True)),
        (
            "unsafe_screenshot_reference",
            _with_value(
                synthetic,
                ("web_evidence", "real_llm_web_answer", "screenshot_reference"),
                _unsafe_private_path_reference(),
            ),
        ),
        ("placeholder_success", _with_value(synthetic, ("placeholder_success",), True)),
        ("private_paths_included", _with_value(synthetic, ("private_paths_included",), True)),
    )
    for label, candidate in rejection_cases:
        validation = validate_v200_accepted_web_evidence_manifest_aggregate(candidate)
        if validation.status == "accepted":
            return _source_tree_error(f"negative case unexpectedly accepted: {label}")
    print(
        "v200_accepted_web_evidence_manifest_aggregate_negative_cases: "
        + ",".join(label for label, _ in rejection_cases)
    )
    return True


def _build_synthetic_accepted_manifest(example: dict[str, Any]) -> dict[str, Any]:
    contract = build_v200_accepted_web_evidence_manifest_aggregate_contract()
    manifest = deepcopy(example)
    manifest["status"] = "accepted"
    manifest["release_target"] = "v2.0.0"
    manifest["manifest_kind"] = "private_web_execution_evidence"

    for marker in contract.required_top_level_true_markers:
        manifest[marker] = True
    for marker in contract.required_top_level_false_markers:
        manifest[marker] = False
    for marker in contract.forbidden_success_states:
        manifest[marker] = False

    web_evidence = manifest.setdefault("web_evidence", {})
    for item_name in contract.required_evidence_items:
        item = web_evidence.setdefault(item_name, {})
        item["status"] = "accepted"
        item["capability"] = item_name
        item["operator_review_accepted"] = True
        if item_name in contract.web_capability_items:
            for marker in contract.required_web_item_true_markers:
                item[marker] = True
            item["screenshot_reference"] = (
                f"private-operator-evidence://v200/day80/{item_name}-screenshot-redacted"
            )

    # Keep the synthetic positive case aligned with the capability-specific fields
    # already present in the public example, even though Day80 aggregates prior acceptance.
    web_evidence["real_tts_web_audio_output"]["web_audio_playback_confirmed"] = True
    web_evidence["real_google_health_sleep_data"]["google_health_source_confirmed"] = True
    web_evidence["real_google_health_sleep_data"]["sleep_summary_normalized"] = True
    web_evidence["web_image_display"]["web_image_display_visible"] = True
    web_evidence["image_asset_intake_review"]["repository_safe_image_asset_used"] = True
    return manifest


def _unsafe_private_path_reference() -> str:
    # Build the negative fixture without committing a private-path-shaped literal.
    separator = "\\"
    return "private-operator-evidence://" + "C:" + separator + "Users" + separator + "operator"


def _without_required_item(manifest: dict[str, Any], item_name: str) -> dict[str, Any]:
    candidate = deepcopy(manifest)
    web_evidence = candidate.get("web_evidence")
    if isinstance(web_evidence, dict):
        web_evidence.pop(item_name, None)
    return candidate


def _with_value(
    manifest: dict[str, Any],
    path: tuple[str, ...],
    value: Any,
) -> dict[str, Any]:
    candidate = deepcopy(manifest)
    current: dict[str, Any] = candidate
    for key in path[:-1]:
        child = current.get(key)
        if not isinstance(child, dict):
            child = {}
            current[key] = child
        current = child
    current[path[-1]] = value
    return candidate


def _source_tree_error(message: str) -> bool:
    print(f"[smoke-framework-v200-accepted-web-evidence-manifest-aggregate] ERROR: {message}.")
    return False


if __name__ == "__main__":
    raise SystemExit(main())
