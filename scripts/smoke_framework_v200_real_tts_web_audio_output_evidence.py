"""Smoke renderer for Day54 real TTS Web audio output evidence.

Default mode is source-tree only. It does not call ElevenLabs, OpenAI TTS,
AI Character Framework voice output, backend APIs, browser automation, Flutter,
audio generation, audio playback, or audio artifact creation.

Optional evidence JSON validation is local and marker-only. It validates a small
redacted summary created by an operator after a configured run. It must not be
used with raw provider responses, prompt/text bodies, screenshots, or audio
files.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.app.services.framework_v200_real_tts_web_audio_output_evidence import (  # noqa: E402
    build_v200_real_tts_web_audio_evidence_contract,
    render_v200_real_tts_web_audio_evidence,
    validate_v200_real_tts_web_audio_operator_evidence,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Render or validate v2.0.0 Day54 real TTS Web audio evidence markers."
    )
    parser.add_argument(
        "--operator-evidence-json",
        type=Path,
        help="Validate a small redacted marker-only operator evidence JSON file.",
    )
    args = parser.parse_args()

    result = build_v200_real_tts_web_audio_evidence_contract()
    print("[smoke-framework-v200-real-tts-web-audio-output-evidence] RESULT")
    print(render_v200_real_tts_web_audio_evidence(result))

    if args.operator_evidence_json is None:
        print("[smoke-framework-v200-real-tts-web-audio-output-evidence] OK")
        print(
            "No provider call, framework voice output call, backend request, browser, "
            "audio generation, audio playback, audio artifact, or Web UI action was made."
        )
        return 0

    try:
        payload = json.loads(args.operator_evidence_json.read_text(encoding="utf-8"))
    except OSError as exc:
        print(
            "[smoke-framework-v200-real-tts-web-audio-output-evidence] ERROR: "
            f"could not read evidence JSON: {exc.__class__.__name__}."
        )
        return 1
    except json.JSONDecodeError:
        print(
            "[smoke-framework-v200-real-tts-web-audio-output-evidence] ERROR: "
            "operator evidence JSON was not valid JSON."
        )
        return 1

    if not isinstance(payload, dict):
        print(
            "[smoke-framework-v200-real-tts-web-audio-output-evidence] ERROR: "
            "operator evidence JSON must be an object."
        )
        return 1

    validation = validate_v200_real_tts_web_audio_operator_evidence(payload)
    print("v200_real_tts_web_audio_operator_evidence_validation_status: " + validation.status)
    print("v200_real_tts_web_audio_operator_evidence_public_safe: " + str(validation.public_safe))
    print(
        "v200_real_tts_web_audio_operator_evidence_accepted_markers: "
        + ",".join(validation.accepted_markers)
    )
    print(
        "v200_real_tts_web_audio_operator_evidence_missing_markers: "
        + ",".join(validation.missing_markers)
    )

    if validation.status != "accepted":
        print("[smoke-framework-v200-real-tts-web-audio-output-evidence] ERROR")
        return 1

    print("[smoke-framework-v200-real-tts-web-audio-output-evidence] OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
