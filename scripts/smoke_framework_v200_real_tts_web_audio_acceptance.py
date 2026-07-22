"""Render or validate v2.0.0 D-3 real TTS Web audio acceptance evidence.

Default mode is source-tree only. It does not call TTS providers, call AI
Character Framework, start the DRC backend, open a browser, synthesize audio,
play audio, inspect screenshots, read audio files, record audio URLs, or create
release artifacts.

Optional validation combines three local marker-only JSON files created after a
private configured operator run: Day54 output evidence, Day65 execution
evidence, and Day77 screenshot evidence.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Mapping


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.app.services.framework_v200_real_tts_web_audio_acceptance import (  # noqa: E402
    build_v200_real_tts_web_audio_acceptance_contract,
    render_v200_real_tts_web_audio_acceptance_contract,
    render_v200_real_tts_web_audio_acceptance_validation,
    validate_v200_real_tts_web_audio_acceptance,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--day54-json",
        type=Path,
        help="Marker-only Day54 real TTS Web audio output evidence JSON.",
    )
    parser.add_argument(
        "--day65-json",
        type=Path,
        help="Marker-only Day65 real TTS Web audio execution evidence JSON.",
    )
    parser.add_argument(
        "--day77-json",
        type=Path,
        help="Marker-only Day77 real TTS Web audio screenshot evidence JSON.",
    )
    args = parser.parse_args()

    contract = build_v200_real_tts_web_audio_acceptance_contract()
    print("[smoke-framework-v200-real-tts-web-audio-acceptance] RESULT")
    print(render_v200_real_tts_web_audio_acceptance_contract(contract))

    evidence_paths = (args.day54_json, args.day65_json, args.day77_json)
    if all(path is None for path in evidence_paths):
        print("[smoke-framework-v200-real-tts-web-audio-acceptance] OK")
        print(
            "No provider call, framework voice output call, backend request, browser, "
            "audio generation, audio playback, screenshot inspection, audio artifact, "
            "or release artifact was made."
        )
        return 0

    if any(path is None for path in evidence_paths):
        print(
            "[smoke-framework-v200-real-tts-web-audio-acceptance] ERROR: "
            "--day54-json, --day65-json, and --day77-json must be supplied together."
        )
        return 1

    day54 = _read_json_object(args.day54_json, "day54")
    day65 = _read_json_object(args.day65_json, "day65")
    day77 = _read_json_object(args.day77_json, "day77")
    if day54 is None or day65 is None or day77 is None:
        return 1

    validation = validate_v200_real_tts_web_audio_acceptance(
        day54_output_evidence=day54,
        day65_execution_evidence=day65,
        day77_screenshot_evidence=day77,
    )
    print(render_v200_real_tts_web_audio_acceptance_validation(validation))

    if validation.status != "accepted":
        print("[smoke-framework-v200-real-tts-web-audio-acceptance] INCOMPLETE")
        return 1

    print("[smoke-framework-v200-real-tts-web-audio-acceptance] OK")
    return 0


def _read_json_object(path: Path | None, label: str) -> Mapping[str, object] | None:
    if path is None:
        return None

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        print(
            "[smoke-framework-v200-real-tts-web-audio-acceptance] ERROR: "
            f"could not read {label} evidence JSON: {exc.__class__.__name__}."
        )
        return None
    except json.JSONDecodeError:
        print(
            "[smoke-framework-v200-real-tts-web-audio-acceptance] ERROR: "
            f"{label} evidence JSON was not valid JSON."
        )
        return None

    if not isinstance(payload, dict):
        print(
            "[smoke-framework-v200-real-tts-web-audio-acceptance] ERROR: "
            f"{label} evidence JSON must be an object."
        )
        return None

    return payload


if __name__ == "__main__":
    raise SystemExit(main())
