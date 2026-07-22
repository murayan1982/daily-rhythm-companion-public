"""Smoke renderer for Day69 public repository final sweep evidence.

Default mode is source-tree only. It does not publish a repository, call GitHub,
build release artifacts, create release zips, call providers, call Google
Health, start backend services, run Flutter, open browsers, inspect screenshots,
inspect audio/image binaries, or use external network services.

Optional evidence JSON validation is local and marker-only. It validates a small
redacted summary created by an operator after the public repository final sweep.
It must not be used with raw screenshots, provider payloads, health payloads,
audio files, image work folders, token dumps, LAN URLs, or private paths.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.app.services.framework_v200_public_repo_final_sweep import (  # noqa: E402
    build_v200_public_repo_final_sweep_contract,
    render_v200_public_repo_final_sweep,
    validate_v200_public_repo_final_sweep_operator_evidence,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Render or validate v2.0.0 Day69 public repository final sweep markers."
    )
    parser.add_argument(
        "--operator-evidence-json",
        type=Path,
        help="Validate a small redacted marker-only operator evidence JSON file.",
    )
    args = parser.parse_args()

    result = build_v200_public_repo_final_sweep_contract()
    print("[smoke-framework-v200-public-repo-final-sweep] RESULT")
    print(render_v200_public_repo_final_sweep(result))

    if args.operator_evidence_json is None:
        print("[smoke-framework-v200-public-repo-final-sweep] OK")
        print(
            "No GitHub publishing, release build, release zip creation, provider call, "
            "Google Health call, backend request, Flutter run, browser automation, "
            "screenshot inspection, audio/image inspection, or external network access was made."
        )
        return 0

    try:
        payload = json.loads(args.operator_evidence_json.read_text(encoding="utf-8"))
    except OSError as exc:
        print(
            "[smoke-framework-v200-public-repo-final-sweep] ERROR: "
            f"could not read evidence JSON: {exc.__class__.__name__}."
        )
        return 1
    except json.JSONDecodeError:
        print(
            "[smoke-framework-v200-public-repo-final-sweep] ERROR: "
            "operator evidence JSON was not valid JSON."
        )
        return 1

    if not isinstance(payload, dict):
        print(
            "[smoke-framework-v200-public-repo-final-sweep] ERROR: "
            "operator evidence JSON must be an object."
        )
        return 1

    validation = validate_v200_public_repo_final_sweep_operator_evidence(payload)
    print(
        "v200_public_repo_final_sweep_operator_evidence_validation_status: "
        + validation.status
    )
    print(
        "v200_public_repo_final_sweep_operator_evidence_public_safe: "
        + str(validation.public_safe)
    )
    print(
        "v200_public_repo_final_sweep_operator_evidence_forbidden_success_states_absent: "
        + str(validation.forbidden_success_states_absent)
    )
    print(
        "v200_public_repo_final_sweep_operator_evidence_accepted_markers: "
        + ",".join(validation.accepted_markers)
    )
    print(
        "v200_public_repo_final_sweep_operator_evidence_missing_markers: "
        + ",".join(validation.missing_markers)
    )
    print(
        "v200_public_repo_final_sweep_requirement_satisfied: "
        + str(validation.status == "accepted")
    )

    if validation.status != "accepted":
        print("[smoke-framework-v200-public-repo-final-sweep] ERROR")
        return 1

    print("[smoke-framework-v200-public-repo-final-sweep] OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
