from __future__ import annotations

import sys
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.config import AppConfig
from app.engines.base import ConversationEngine
from app.engines.errors import FrameworkEngineError
from app.engines.factory import create_conversation_engine
from app.engines.framework_engine import FrameworkConversationEngine
from app.engines.mock_engine import MockConversationEngine
from app.models.advice import AdviceRequest
from app.models.character import CharacterContext
from app.models.sleep import SleepSummary


def _sample_request() -> AdviceRequest:
    return AdviceRequest(
        character=CharacterContext(
            character_id="gentle_mina",
            display_name="ミナ",
            personality_type="gentle",
            speaking_style="casual",
            advice_style="rest_focused",
        ),
        sleep=SleepSummary(
            date="2026-05-09",
            total_sleep_minutes=420,
            quality_label="good",
            source="mock",
            available=True,
        ),
        mood="neutral",
    )


def _expect(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _check_mock_engine() -> None:
    engine = create_conversation_engine(AppConfig(conversation_engine="mock"))

    _expect(isinstance(engine, MockConversationEngine), "mock engine should be selected")
    _expect(isinstance(engine, ConversationEngine), "mock engine should implement ConversationEngine")

    response = engine.create_advice(_sample_request())

    _expect(response.message, "mock engine should return a message")
    _expect(response.character_name == "ミナ", "mock engine should preserve character display name")


def _check_framework_engine_selection() -> None:
    engine = create_conversation_engine(AppConfig(conversation_engine="framework"))

    _expect(
        isinstance(engine, FrameworkConversationEngine),
        "framework engine should be selected",
    )
    _expect(
        isinstance(engine, ConversationEngine),
        "framework engine should implement ConversationEngine",
    )


def _check_framework_config_guard() -> None:
    engine = FrameworkConversationEngine(
        config=AppConfig(conversation_engine="framework")
    )

    try:
        engine.create_advice(_sample_request())
    except FrameworkEngineError as exc:
        _expect(
            "FRAMEWORK_PROJECT_ROOT" in str(exc) or "FRAMEWORK_ROOT" in str(exc),
            "missing framework root should produce a config-facing error",
        )
    else:
        raise AssertionError("framework engine should fail safely when root is missing")


def _check_framework_root_validation() -> None:
    with TemporaryDirectory() as temp_dir:
        engine = FrameworkConversationEngine(
            config=AppConfig(
                conversation_engine="framework",
                framework_project_root=temp_dir,
                framework_preset="text_chat",
            )
        )

        try:
            engine.create_advice(_sample_request())
        except FrameworkEngineError as exc:
            _expect(
                "framework/facade.py" in str(exc),
                "invalid framework root should mention missing facade",
            )
        else:
            raise AssertionError("framework engine should validate framework/facade.py")


def _check_unknown_engine_rejected() -> None:
    try:
        create_conversation_engine(AppConfig(conversation_engine="invalid"))
    except ValueError as exc:
        _expect(
            "Unsupported conversation engine" in str(exc),
            "unknown engine error should be clear",
        )
    else:
        raise AssertionError("unknown conversation engine should be rejected")


def main() -> None:
    _check_mock_engine()
    _check_framework_engine_selection()
    _check_framework_config_guard()
    _check_framework_root_validation()
    _check_unknown_engine_rejected()

    print("[conversation-engine-boundary-check-v0.30.0] OK")


if __name__ == "__main__":
    main()