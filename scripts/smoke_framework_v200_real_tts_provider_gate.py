"""Smoke renderer and optional operator status probe for Day53 TTS provider gate.

Default mode is source-tree only. It does not call the backend, AI Character
Framework, ElevenLabs, OpenAI TTS, audio generation, audio playback, or Web UI.

Optional operator mode can query a running backend's voice-output status when
all of the following are true:
- --require-running-backend is passed.
- DRC_V200_ENABLE_REAL_TTS_PROVIDER_GATE_SMOKE=1 is set.
- The backend has already been started by the operator.

The optional status probe is intentionally not a real synthesis check. It only
verifies that the voice-output boundary can be inspected without logging
private text, provider payloads, API keys, audio URLs, or local paths.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
from urllib import error, request


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.app.services.framework_v200_real_tts_provider_gate import (  # noqa: E402
    build_v200_real_tts_provider_gate,
    render_v200_real_tts_provider_gate,
)


SAFE_DEFAULT_BASE_URL = "http://127.0.0.1:8000"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Render or optionally probe v2.0.0 real TTS provider gate evidence."
    )
    parser.add_argument(
        "--require-running-backend",
        action="store_true",
        help="Call a running backend status endpoint only when the explicit opt-in env flag is enabled.",
    )
    parser.add_argument(
        "--base-url",
        default=os.getenv("DRC_BACKEND_API_BASE_URL", SAFE_DEFAULT_BASE_URL),
        help="Backend API base URL. Do not paste raw LAN IPs into committed logs.",
    )
    args = parser.parse_args()

    result = build_v200_real_tts_provider_gate()
    print("[smoke-framework-v200-real-tts-provider-gate] RESULT")
    print(render_v200_real_tts_provider_gate(result))

    if not args.require_running_backend:
        print("[smoke-framework-v200-real-tts-provider-gate] OK")
        print(
            "No backend request, provider call, framework voice output call, "
            "audio generation, audio playback, audio artifact, browser, or Web UI action was made."
        )
        return 0

    if not _enabled("DRC_V200_ENABLE_REAL_TTS_PROVIDER_GATE_SMOKE"):
        print(
            "[smoke-framework-v200-real-tts-provider-gate] SKIP: "
            "DRC_V200_ENABLE_REAL_TTS_PROVIDER_GATE_SMOKE is not enabled."
        )
        return 0

    return _run_backend_status_probe(args.base_url)


def _enabled(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "on"}


def _run_backend_status_probe(base_url: str) -> int:
    normalized_base_url = base_url.rstrip("/")
    endpoint = normalized_base_url + "/demo/voice-output/status"

    backend_request = request.Request(
        endpoint,
        headers={"Accept": "application/json"},
        method="GET",
    )

    try:
        with request.urlopen(backend_request, timeout=15) as response:
            response_body = response.read()
            status_code = response.status
    except error.URLError as exc:
        safe_error = exc.__class__.__name__
        print(
            "[smoke-framework-v200-real-tts-provider-gate] ERROR: "
            f"backend status request failed with {safe_error}."
        )
        return 1

    try:
        payload = json.loads(response_body.decode("utf-8"))
    except json.JSONDecodeError:
        print(
            "[smoke-framework-v200-real-tts-provider-gate] ERROR: "
            "backend response was not JSON."
        )
        return 1

    if status_code != 200:
        print(
            "[smoke-framework-v200-real-tts-provider-gate] ERROR: "
            f"unexpected status code {status_code}."
        )
        return 1

    status = str(payload.get("status") or payload.get("capability_status") or "unknown")
    provider = str(payload.get("provider") or payload.get("provider_name") or "hidden")
    synthesis_status = str(payload.get("synthesis_status") or payload.get("audio_generation") or "not-confirmed")

    print("v200_real_tts_provider_operator_status_probe: ok")
    print("v200_real_tts_provider_operator_backend_status: " + _safe_token(status))
    print("v200_real_tts_provider_operator_provider_label: " + _safe_token(provider))
    print("v200_real_tts_provider_operator_synthesis_status: " + _safe_token(synthesis_status))
    print("v200_real_tts_provider_operator_private_text_logged: False")
    print("v200_real_tts_provider_operator_audio_url_logged: False")
    print("v200_real_tts_provider_operator_provider_payload_logged: False")
    print("[smoke-framework-v200-real-tts-provider-gate] OK")
    return 0


def _safe_token(value: str) -> str:
    normalized = value.strip().lower().replace(" ", "-")
    allowed = []
    for ch in normalized:
        if ch.isalnum() or ch in {"-", "_", "."}:
            allowed.append(ch)
    return "".join(allowed)[:80] or "unknown"


if __name__ == "__main__":
    raise SystemExit(main())
