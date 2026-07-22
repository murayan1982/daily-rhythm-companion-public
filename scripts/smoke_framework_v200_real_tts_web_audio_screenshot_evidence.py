"""Render or validate v2.0.0 Day77 real TTS Web audio screenshot evidence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.app.services.framework_v200_real_tts_web_audio_screenshot_evidence import (  # noqa: E402
    build_v200_real_tts_web_audio_screenshot_evidence_contract,
    render_v200_real_tts_web_audio_screenshot_evidence_contract,
    render_v200_real_tts_web_audio_screenshot_evidence_validation,
    validate_v200_real_tts_web_audio_screenshot_evidence,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence-json", help="Optional private real TTS Web audio evidence JSON to validate.")
    args = parser.parse_args()

    contract = build_v200_real_tts_web_audio_screenshot_evidence_contract()
    print(render_v200_real_tts_web_audio_screenshot_evidence_contract(contract))

    if args.evidence_json:
        evidence_path = Path(args.evidence_json)
        evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
        validation = validate_v200_real_tts_web_audio_screenshot_evidence(evidence)
        print(render_v200_real_tts_web_audio_screenshot_evidence_validation(validation))
        if validation.status != "accepted":
            print("[smoke-framework-v200-real-tts-web-audio-screenshot-evidence] INCOMPLETE")
            return 1

    print("[smoke-framework-v200-real-tts-web-audio-screenshot-evidence] OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
