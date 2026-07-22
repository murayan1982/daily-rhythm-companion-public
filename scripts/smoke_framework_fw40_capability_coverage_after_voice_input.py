"""Day39 smoke for v1.9.0 FW4.0.0 capability coverage after voice input.

This smoke is source-tree only. It does not start Flutter, open a browser, call
backend APIs, import AI Character Framework runtime modules, create framework
sessions, call ask or ask_stream, touch microphones, read or upload audio,
generate audio, connect to Live2D/VTS, or call providers.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.services.framework_fw40_capability_coverage_after_voice_input import (
    build_v190_fw40_capability_coverage_after_voice_input_input,
    evaluate_v190_fw40_capability_coverage_after_voice_input,
    render_v190_fw40_capability_coverage_after_voice_input,
)


def _assert_public_safe(text: str) -> None:
    forbidden_patterns = [
        r"sk-[A-Za-z0-9_\-]{12,}",
        r"AIza[0-9A-Za-z_\-]{20,}",
        r"xai-[A-Za-z0-9_\-]{12,}",
        r"Bearer\s+[A-Za-z0-9_\-\.]{12,}",
        r"Authorization:\s*Bearer",
        r"refresh_token\s*[:=]\s*['\"][^'\"]+",
        r"access_token\s*[:=]\s*['\"][^'\"]+",
        r"client_secret\s*[:=]\s*['\"][^'\"]+",
        r"[A-Za-z]:\\Users\\",
        r"192\.168\.\d+\.\d+",
        r"10\.\d+\.\d+\.\d+",
        r"172\.(1[6-9]|2\d|3[0-1])\.\d+\.\d+",
    ]
    for pattern in forbidden_patterns:
        if re.search(pattern, text, flags=re.IGNORECASE):
            raise AssertionError(
                "Public-safe FW4.0.0 coverage-after-voice-input output contained forbidden pattern: "
                + pattern
            )


def main() -> None:
    evidence = build_v190_fw40_capability_coverage_after_voice_input_input()
    result = evaluate_v190_fw40_capability_coverage_after_voice_input(evidence)
    rendered = "\n".join(render_v190_fw40_capability_coverage_after_voice_input(result))
    _assert_public_safe(rendered)
    required = [
        "v190_fw40_capability_coverage_after_voice_input_status: text-chat-and-voice-input-boundary-evidence-complete-remaining-boundaries-pending",
        "v190_fw40_capability_coverage_after_voice_input_llm_text_chat_status: completed",
        "v190_fw40_capability_coverage_after_voice_input_stt_voice_input_status: boundary-evidence-recorded",
        "v190_fw40_capability_coverage_after_voice_input_stt_voice_input_configured_runtime_verified: False",
        "v190_fw40_capability_coverage_after_voice_input_tts_voice_output_status: boundary-ready",
        "v190_fw40_capability_coverage_after_voice_input_live2d_vts_motion_status: boundary-ready",
        "v190_fw40_capability_coverage_after_voice_input_next_focus: tts_voice_output",
    ]
    for needle in required:
        if needle not in rendered:
            raise AssertionError(f"Missing Day39 coverage marker: {needle}")
    print("[smoke-framework-fw40-capability-coverage-after-voice-input] OK")


if __name__ == "__main__":
    main()
