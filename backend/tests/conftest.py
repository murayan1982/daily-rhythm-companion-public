"""Shared mock-safe test configuration for backend regression tests."""

from __future__ import annotations

import os
from pathlib import Path
import sys

import pytest

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

# Keep collection and runtime independent from backend/.env and real providers.
os.environ["DRC_SKIP_BACKEND_DOTENV"] = "1"
os.environ["CONVERSATION_ENGINE"] = "mock"
os.environ["SLEEP_PROVIDER"] = "mock"

_REAL_EXECUTION_ENV_KEYS = (
    "OPENAI_API_KEY",
    "GEMINI_API_KEY",
    "XAI_API_KEY",
    "ELEVENLABS_API_KEY",
    "FRAMEWORK_ROOT",
    "FRAMEWORK_PROJECT_ROOT",
    "GOOGLE_HEALTH_CREDENTIALS_FILE",
    "GOOGLE_HEALTH_REAL_API_OPT_IN",
    "GOOGLE_HEALTH_ENABLE_REAL_API_REQUESTS",
    "VOICE_OUTPUT_REAL_TTS_ENABLED",
)


@pytest.fixture(autouse=True)
def mock_safe_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """Force every normal regression test onto credential-free local paths."""

    monkeypatch.setenv("DRC_SKIP_BACKEND_DOTENV", "1")
    monkeypatch.setenv("CONVERSATION_ENGINE", "mock")
    monkeypatch.setenv("SLEEP_PROVIDER", "mock")
    for key in _REAL_EXECUTION_ENV_KEYS:
        monkeypatch.delenv(key, raising=False)
