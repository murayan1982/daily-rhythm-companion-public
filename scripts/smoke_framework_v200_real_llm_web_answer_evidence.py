"""Smoke renderer and optional operator probe for v2.0.0 real LLM Web answer evidence.

Default mode is source-tree only and does not call the backend or any provider.

Optional operator mode can call a running DRC backend API when all of the
following are true:
- --require-running-backend is passed.
- DRC_V200_ENABLE_REAL_LLM_WEB_ANSWER_SMOKE=1 is set.
- The backend has already been started by the operator with configured real LLM
  / framework settings.

The optional probe prints only public-safe metadata. It never prints prompt
bodies, response bodies, provider payloads, API keys, LAN IPs, or local paths.
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

from backend.app.services.framework_v200_real_llm_web_answer_evidence import (  # noqa: E402
    build_v200_real_llm_web_answer_evidence,
    render_v200_real_llm_web_answer_evidence,
)


SAFE_DEFAULT_BASE_URL = "http://127.0.0.1:8000"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Render or optionally probe v2.0.0 real LLM Web answer evidence."
    )
    parser.add_argument(
        "--require-running-backend",
        action="store_true",
        help="Call a running backend only when the explicit opt-in env flag is enabled.",
    )
    parser.add_argument(
        "--base-url",
        default=os.getenv("DRC_BACKEND_API_BASE_URL", SAFE_DEFAULT_BASE_URL),
        help="Backend API base URL. Do not paste raw LAN IPs into committed logs.",
    )
    args = parser.parse_args()

    result = build_v200_real_llm_web_answer_evidence()
    print("[smoke-framework-v200-real-llm-web-answer-evidence] RESULT")
    print(render_v200_real_llm_web_answer_evidence(result))

    if not args.require_running_backend:
        print("[smoke-framework-v200-real-llm-web-answer-evidence] OK")
        print("No backend request, provider call, framework session, browser, or Web UI action was made.")
        return 0

    if not _enabled("DRC_V200_ENABLE_REAL_LLM_WEB_ANSWER_SMOKE"):
        print(
            "[smoke-framework-v200-real-llm-web-answer-evidence] SKIP: "
            "DRC_V200_ENABLE_REAL_LLM_WEB_ANSWER_SMOKE is not enabled."
        )
        return 0

    return _run_backend_probe(args.base_url)


def _enabled(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "on"}


def _run_backend_probe(base_url: str) -> int:
    normalized_base_url = base_url.rstrip("/")
    endpoint = normalized_base_url + "/advice"

    payload = {
        "character": {
            "character_id": "gentle_mina",
            "display_name": "ミナ",
            "personality_type": "gentle",
            "speaking_style": "casual",
            "advice_style": "rest_focused",
        },
        "sleep": {
            "date": "2026-05-23",
            "total_sleep_minutes": 390,
            "efficiency": 88,
            "deep_sleep_minutes": 80,
            "rem_sleep_minutes": 95,
            "awake_minutes": 20,
            "source": "operator_safe_shape",
            "available": True,
            "quality_label": "ok",
            "is_real_data": False,
        },
        "mood": "tired",
    }

    body = json.dumps(payload).encode("utf-8")
    backend_request = request.Request(
        endpoint,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with request.urlopen(backend_request, timeout=30) as response:
            response_body = response.read()
            status_code = response.status
    except error.URLError as exc:
        safe_error = exc.__class__.__name__
        print(
            "[smoke-framework-v200-real-llm-web-answer-evidence] ERROR: "
            f"backend request failed with {safe_error}."
        )
        return 1

    try:
        payload = json.loads(response_body.decode("utf-8"))
    except json.JSONDecodeError:
        print(
            "[smoke-framework-v200-real-llm-web-answer-evidence] ERROR: "
            "backend response was not JSON."
        )
        return 1

    message = payload.get("message")
    source = payload.get("source") or {}
    source_engine = source.get("engine")

    if status_code != 200:
        print(
            "[smoke-framework-v200-real-llm-web-answer-evidence] ERROR: "
            f"unexpected status code {status_code}."
        )
        return 1

    if not isinstance(message, str) or not message.strip():
        print(
            "[smoke-framework-v200-real-llm-web-answer-evidence] ERROR: "
            "message was empty."
        )
        return 1

    if source_engine != "framework":
        print(
            "[smoke-framework-v200-real-llm-web-answer-evidence] ERROR: "
            f"source.engine was {source_engine!r}, expected 'framework'."
        )
        return 1

    print("v200_real_llm_web_answer_operator_api_status: ok")
    print("v200_real_llm_web_answer_operator_source_engine: framework")
    print("v200_real_llm_web_answer_operator_message_non_empty: True")
    print("v200_real_llm_web_answer_operator_message_length: " + str(len(message.strip())))
    print("v200_real_llm_web_answer_operator_body_logged: False")
    print("v200_real_llm_web_answer_operator_provider_payload_logged: False")
    print("[smoke-framework-v200-real-llm-web-answer-evidence] OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
