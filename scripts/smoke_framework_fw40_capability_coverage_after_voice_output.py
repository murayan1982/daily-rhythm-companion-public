"""Day42 smoke for v1.9.0 FW4.0.0 coverage after voice output evidence.

This smoke is source-tree only. It does not start Flutter, open a browser, call
backend APIs, import AI Character Framework runtime/audio/motion modules,
create sessions, call ask, call ask_stream, call providers, process audio,
generate audio, play audio, connect to Live2D/VTS, or dispatch motion.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.services.framework_fw40_capability_coverage_after_voice_output import (
    build_v190_fw40_capability_coverage_after_voice_output_input,
    evaluate_v190_fw40_capability_coverage_after_voice_output,
    render_v190_fw40_capability_coverage_after_voice_output,
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
                "Public-safe coverage-after-voice-output output contained forbidden pattern: "
                + pattern
            )


def main() -> None:
    evidence = build_v190_fw40_capability_coverage_after_voice_output_input()
    result = evaluate_v190_fw40_capability_coverage_after_voice_output(evidence)
    lines = render_v190_fw40_capability_coverage_after_voice_output(result)
    output = "\n".join(lines)
    _assert_public_safe(output)

    if result.status != "text-chat-voice-input-and-voice-output-boundary-evidence-complete-motion-boundary-pending":
        raise AssertionError("Unexpected Day42 capability coverage status: " + result.status)
    if result.text_chat_status != "completed":
        raise AssertionError("LLM/text-chat status should stay completed")
    if result.voice_input_status != "boundary-evidence-recorded":
        raise AssertionError("Voice input boundary evidence should stay recorded")
    if result.voice_output_status != "boundary-evidence-recorded":
        raise AssertionError("Voice output boundary evidence should be recorded")
    if result.voice_input_configured_runtime_verified:
        raise AssertionError("Voice input configured runtime must remain unverified in Day42")
    if result.voice_output_configured_runtime_verified:
        raise AssertionError("Voice output configured runtime must remain unverified in Day42")
    if result.motion_status != "boundary-ready":
        raise AssertionError("Live2D/VTS motion boundary should remain ready and pending evidence")
    if result.evidence_recorded_count != 3:
        raise AssertionError("Expected three recorded evidence items after voice output")
    if result.remaining_boundary_evidence_count != 1:
        raise AssertionError("Expected one remaining boundary evidence item after voice output")
    if result.configured_runtime_verified_count != 1:
        raise AssertionError("Only LLM/text-chat live runtime should be counted as configured-runtime verified")
    if result.next_capability_focus != "live2d_vts_motion":
        raise AssertionError("Next focus should move to Live2D/VTS motion")

    print("[smoke-framework-fw40-capability-coverage-after-voice-output] OK")
    print(output)


if __name__ == "__main__":
    main()
