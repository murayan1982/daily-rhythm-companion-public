"""Smoke renderer for Day66 real Google Health sleep-data execution evidence.

Default mode is source-tree only. It does not call Google Health APIs, read
OAuth tokens, call the backend, open a browser, start Flutter, normalize real
health payloads, inspect health data, or create health-data artifacts.

Optional evidence JSON validation is local and marker-only. It validates a small
redacted summary created by an operator after a configured run. It must not be
used with raw Google Health payloads, token files, screenshots, logs, browser
storage, or local health-data artifacts.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.app.services.framework_v200_real_google_health_sleep_data_execution_evidence import (  # noqa: E402
    build_v200_real_google_health_sleep_data_execution_evidence_contract,
    render_v200_real_google_health_sleep_data_execution_evidence,
    validate_v200_real_google_health_sleep_data_execution_operator_evidence,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Render or validate v2.0.0 Day66 real Google Health sleep-data execution evidence markers."
    )
    parser.add_argument(
        "--operator-evidence-json",
        type=Path,
        help="Validate a small redacted marker-only operator evidence JSON file.",
    )
    args = parser.parse_args()

    result = build_v200_real_google_health_sleep_data_execution_evidence_contract()
    print("[smoke-framework-v200-real-google-health-sleep-data-execution-evidence] RESULT")
    print(render_v200_real_google_health_sleep_data_execution_evidence(result))

    if args.operator_evidence_json is None:
        print("[smoke-framework-v200-real-google-health-sleep-data-execution-evidence] OK")
        print(
            "No Google API call, OAuth/token read, backend request, browser, raw "
            "health payload parse, or health-data artifact was made."
        )
        return 0

    try:
        payload = json.loads(args.operator_evidence_json.read_text(encoding="utf-8"))
    except OSError as exc:
        print(
            "[smoke-framework-v200-real-google-health-sleep-data-execution-evidence] ERROR: "
            f"could not read evidence JSON: {exc.__class__.__name__}."
        )
        return 1
    except json.JSONDecodeError:
        print(
            "[smoke-framework-v200-real-google-health-sleep-data-execution-evidence] ERROR: "
            "operator evidence JSON was not valid JSON."
        )
        return 1

    if not isinstance(payload, dict):
        print(
            "[smoke-framework-v200-real-google-health-sleep-data-execution-evidence] ERROR: "
            "operator evidence JSON must be an object."
        )
        return 1

    validation = validate_v200_real_google_health_sleep_data_execution_operator_evidence(payload)
    print(
        "v200_real_google_health_sleep_data_execution_operator_evidence_validation_status: "
        + validation.status
    )
    print(
        "v200_real_google_health_sleep_data_execution_operator_evidence_public_safe: "
        + str(validation.public_safe)
    )
    print(
        "v200_real_google_health_sleep_data_execution_operator_evidence_forbidden_success_states_absent: "
        + str(validation.forbidden_success_states_absent)
    )
    print(
        "v200_real_google_health_sleep_data_execution_operator_evidence_accepted_markers: "
        + ",".join(validation.accepted_markers)
    )
    print(
        "v200_real_google_health_sleep_data_execution_operator_evidence_missing_markers: "
        + ",".join(validation.missing_markers)
    )
    print(
        "v200_real_google_health_sleep_data_execution_requirement_satisfied: "
        + str(validation.status == "accepted")
    )

    if validation.status != "accepted":
        print("[smoke-framework-v200-real-google-health-sleep-data-execution-evidence] ERROR")
        return 1

    print("[smoke-framework-v200-real-google-health-sleep-data-execution-evidence] OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
