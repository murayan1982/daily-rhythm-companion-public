"""Render or validate v2.0.0 Day81 final release readiness with accepted Web evidence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.app.services.framework_v200_final_release_readiness_with_web_evidence import (  # noqa: E402
    build_v200_final_release_readiness_with_web_evidence_contract,
    render_v200_final_release_readiness_with_web_evidence_contract,
    render_v200_final_release_readiness_with_web_evidence_validation,
    validate_v200_final_release_readiness_with_web_evidence,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release-zip", help="Optional fixed release zip path to validate.")
    parser.add_argument("--manifest-json", help="Optional private Day80 manifest JSON to validate.")
    parser.add_argument("--final-evidence-json", help="Optional private Day81 final evidence JSON to validate.")
    args = parser.parse_args()

    contract = build_v200_final_release_readiness_with_web_evidence_contract()
    print(render_v200_final_release_readiness_with_web_evidence_contract(contract))

    if args.manifest_json or args.final_evidence_json or args.release_zip:
        if not (args.manifest_json and args.final_evidence_json and args.release_zip):
            print("[smoke-framework-v200-final-release-readiness-with-web-evidence] INCOMPLETE")
            print("release zip, Day80 manifest JSON, and Day81 final evidence JSON are required together")
            return 1
        day80_manifest = json.loads(Path(args.manifest_json).read_text(encoding="utf-8"))
        final_evidence = json.loads(Path(args.final_evidence_json).read_text(encoding="utf-8"))
        validation = validate_v200_final_release_readiness_with_web_evidence(
            final_evidence,
            day80_manifest,
            args.release_zip,
        )
        print(render_v200_final_release_readiness_with_web_evidence_validation(validation))
        if validation.status != "accepted":
            print("[smoke-framework-v200-final-release-readiness-with-web-evidence] INCOMPLETE")
            return 1

    print("[smoke-framework-v200-final-release-readiness-with-web-evidence] OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
