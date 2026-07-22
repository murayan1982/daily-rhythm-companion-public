from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.services.google_health_api_client import (
    build_google_health_provider_error_summary,
)


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    response_data = {
        "error": {
            "code": 403,
            "message": "Request had insufficient authentication scopes.",
            "status": "PERMISSION_DENIED",
            "details": [
                {
                    "@type": "type.googleapis.com/google.rpc.ErrorInfo",
                    "reason": "ACCESS_TOKEN_SCOPE_INSUFFICIENT",
                    "domain": "googleapis.com",
                    "metadata": {
                        "method": "google.health.v4.UsersDataTypesDataPoints.List",
                        "service": "health.googleapis.com",
                    },
                }
            ],
        }
    }

    summary = build_google_health_provider_error_summary(
        status_code=403,
        response_data=response_data,
        www_authenticate='Bearer error="insufficient_scope", scope="health"',
    )

    _assert(summary is not None, "summary should be built for a 403 provider error")
    _assert(summary.http_status_code == 403, "HTTP status code should be preserved")
    _assert(summary.provider_error_code == 403, "provider error code should be preserved")
    _assert(
        summary.provider_error_status == "PERMISSION_DENIED",
        "provider error status should be extracted",
    )
    _assert(
        summary.provider_error_reason == "ACCESS_TOKEN_SCOPE_INSUFFICIENT",
        "ErrorInfo reason should be extracted",
    )
    _assert(
        summary.suggested_cause == "token_scope_or_reauthorization_required",
        "scope-related 403 should suggest token reauthorization/scope diagnostics",
    )

    serialized = json.dumps(summary.__dict__, sort_keys=True).lower()
    for forbidden in ("ya29.", "refresh-token-secret", "client-secret"):
        _assert(forbidden not in serialized, f"summary leaked {forbidden}")

    print("[google-health-provider-error-summary-check] OK")


if __name__ == "__main__":
    main()
