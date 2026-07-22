"""Day36 smoke for v1.9.0 FW4.0.0 capability coverage checkpoint.

This source-tree evidence renderer does not start Flutter, open a browser, import
AI Character Framework, create sessions, call ask/ask_stream, call providers,
touch microphones, generate audio, connect to VTube Studio, or dispatch motion.
It only records public-safe capability coverage labels after the Day35 text-chat
completion evidence.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.services.framework_fw40_capability_coverage_checkpoint import (
    build_v190_fw40_capability_evidence,
    evaluate_v190_fw40_capability_coverage,
    render_v190_fw40_capability_coverage,
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
                "Public-safe capability coverage evidence contained forbidden pattern: "
                + pattern
            )


def main() -> None:
    checkpoint = evaluate_v190_fw40_capability_coverage(
        build_v190_fw40_capability_evidence()
    )
    rendered = "\n".join(render_v190_fw40_capability_coverage(checkpoint))
    _assert_public_safe(rendered)

    if checkpoint.status != "text-chat-complete-boundary-capabilities-pending":
        raise AssertionError("Unexpected capability coverage status: " + checkpoint.status)
    if checkpoint.next_capability_focus != "stt_voice_input":
        raise AssertionError("Expected STT / voice input to be the next capability focus")
    if checkpoint.completed_count != 1:
        raise AssertionError("Expected exactly one completed capability")
    if checkpoint.boundary_ready_count != 3:
        raise AssertionError("Expected three boundary-ready capabilities")

    print("[smoke-framework-fw40-capability-coverage-checkpoint] OK")


if __name__ == "__main__":
    main()
