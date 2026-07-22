"""Smoke renderer for Day70 v2.0.0 final prerelease aggregate gate.

Default mode is source-tree only. It does not build release artifacts, create or
inspect release zips, call providers, call Google Health, start backend
services, run Flutter, open browsers, inspect screenshots, inspect audio/image
binaries, publish to GitHub, or access external network services.

Optional evidence JSON validation is local and marker-only.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.app.services.framework_v200_final_prerelease_aggregate_gate import (  # noqa: E402
    build_v200_final_prerelease_aggregate_contract,
    render_v200_final_prerelease_aggregate,
    validate_v200_final_prerelease_aggregate_operator_evidence,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render or validate Day70 v2.0.0 final prerelease aggregate evidence."
    )
    parser.add_argument(
        "--operator-evidence-json",
        type=Path,
        default=None,
        help="Optional redacted marker-only evidence JSON to validate.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = build_v200_final_prerelease_aggregate_contract()
    print("[smoke-framework-v200-final-prerelease-aggregate-gate] RESULT")
    print(render_v200_final_prerelease_aggregate(result))

    if args.operator_evidence_json is None:
        print("[smoke-framework-v200-final-prerelease-aggregate-gate] OK")
        print(
            "No release build, release zip creation, release zip inspection, provider call, "
            "Google Health call, backend request, Flutter run, browser automation, "
            "screenshot inspection, audio/image inspection, GitHub publication, or "
            "external network access was made."
        )
        return 0

    try:
        payload = json.loads(args.operator_evidence_json.read_text(encoding="utf-8"))
    except OSError as exc:
        print(
            "[smoke-framework-v200-final-prerelease-aggregate-gate] ERROR: "
            f"could not read evidence JSON: {exc.__class__.__name__}."
        )
        return 1
    except json.JSONDecodeError:
        print(
            "[smoke-framework-v200-final-prerelease-aggregate-gate] ERROR: "
            "operator evidence JSON was not valid JSON."
        )
        return 1

    if not isinstance(payload, dict):
        print(
            "[smoke-framework-v200-final-prerelease-aggregate-gate] ERROR: "
            "operator evidence JSON must be an object."
        )
        return 1

    validation = validate_v200_final_prerelease_aggregate_operator_evidence(payload)
    print(
        "v200_final_prerelease_aggregate_gate_operator_evidence_validation_status: "
        + validation.status
    )
    print(
        "v200_final_prerelease_aggregate_gate_operator_evidence_public_safe: "
        + str(validation.public_safe)
    )
    print(
        "v200_final_prerelease_aggregate_gate_operator_evidence_forbidden_success_states_absent: "
        + str(validation.forbidden_success_states_absent)
    )
    print(
        "v200_final_prerelease_aggregate_gate_operator_evidence_accepted_markers: "
        + ",".join(validation.accepted_markers)
    )
    print(
        "v200_final_prerelease_aggregate_gate_operator_evidence_missing_markers: "
        + ",".join(validation.missing_markers)
    )
    print(
        "v200_final_prerelease_aggregate_gate_requirement_satisfied: "
        + str(validation.status == "accepted")
    )

    if validation.status != "accepted":
        print("[smoke-framework-v200-final-prerelease-aggregate-gate] ERROR")
        return 1

    print("[smoke-framework-v200-final-prerelease-aggregate-gate] OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
