"""Framework advice success and fallback regression tests with local fakes."""

from __future__ import annotations

from pathlib import Path
import importlib
import sys
from types import SimpleNamespace

import pytest

from app.config import AppConfig
from app.engines.errors import FrameworkEngineError
from app.engines.framework_engine import FrameworkConversationEngine
from app.engines.mock_engine import MockConversationEngine
from app.models.advice import AdviceRequest
from app.models.character import CharacterContext
from app.models.sleep import SleepSummary


def _request() -> AdviceRequest:
    return AdviceRequest(
        character=CharacterContext(
            character_id="gentle_mina",
            display_name="ミナ",
            personality_type="gentle",
            speaking_style="casual",
            advice_style="rest_focused",
        ),
        sleep=SleepSummary(
            date="2026-07-22",
            total_sleep_minutes=410,
            efficiency=86,
            source="mock",
            available=True,
            quality_label="fair",
        ),
        mood="normal",
    )


def _write_fake_framework(root: Path, *, response_text: str) -> None:
    package_dir = root / "framework"
    package_dir.mkdir(parents=True)
    (package_dir / "__init__.py").write_text(
        "\n".join(
            [
                "from pathlib import Path",
                "",
                "class _Session:",
                "    def __init__(self, character_name):",
                "        self.character_name = character_name",
                "",
                "    def ask(self, text):",
                "        Path('observed_prompt.txt').write_text(text, encoding='utf-8')",
                f"        return {response_text!r}",
                "",
                "def create_text_chat_session(*, preset, character_name):",
                "    Path('observed_session.txt').write_text(",
                "        f'{preset}|{character_name}', encoding='utf-8'",
                "    )",
                "    return _Session(character_name)",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _clear_framework_modules() -> None:
    for module_name in list(sys.modules):
        if module_name == "framework" or module_name.startswith("framework."):
            sys.modules.pop(module_name, None)


def test_framework_engine_uses_public_facade_and_returns_framework_source(
    tmp_path: Path,
) -> None:
    framework_root = tmp_path / "fake_fw"
    _write_fake_framework(framework_root, response_text="今日はゆっくり始めよう。")
    _clear_framework_modules()

    engine = FrameworkConversationEngine(
        AppConfig(
            conversation_engine="framework",
            framework_project_root=str(framework_root),
            framework_preset="text_chat",
            framework_character="default",
            framework_adapter_mode="local_import",
        )
    )

    response = engine.create_advice(_request())

    assert response.message == "今日はゆっくり始めよう。"
    assert response.character_name == "ミナ"
    assert response.source is not None
    assert response.source.engine == "framework"
    assert response.source.framework_preset == "text_chat"
    assert response.source.framework_character == "default"
    assert response.source.framework_character_source == "mapped_default"
    assert (framework_root / "observed_session.txt").read_text(encoding="utf-8") == "text_chat|default"
    prompt = (framework_root / "observed_prompt.txt").read_text(encoding="utf-8")
    assert "Character ID: gentle_mina" in prompt
    assert "User mood: normal" in prompt


def test_framework_engine_rejects_empty_public_response(tmp_path: Path) -> None:
    framework_root = tmp_path / "fake_fw_empty"
    _write_fake_framework(framework_root, response_text="   ")
    _clear_framework_modules()
    engine = FrameworkConversationEngine(
        AppConfig(
            conversation_engine="framework",
            framework_project_root=str(framework_root),
        )
    )

    with pytest.raises(FrameworkEngineError, match="empty response"):
        engine.create_advice(_request())


class _FailingFrameworkEngine:
    def create_advice(self, request: AdviceRequest):
        raise FrameworkEngineError("fake framework failure")


def test_advice_boundary_marks_framework_failure_as_visible_fallback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Import the API module only after replacing its default persistence stores,
    # so this regression test never creates or reads backend/local_data.
    from app.services import advice_daily_record_saver as saver_module
    from app.services import recent_sleep_trend_service as trend_module

    monkeypatch.setattr(saver_module, "DailyRecordStore", lambda: SimpleNamespace())
    monkeypatch.setattr(trend_module, "DailyRecordStore", lambda: SimpleNamespace())
    sys.modules.pop("app.api.advice", None)
    advice_api = importlib.import_module("app.api.advice")

    monkeypatch.setattr(
        advice_api,
        "config",
        AppConfig(conversation_engine="framework"),
    )
    monkeypatch.setattr(advice_api, "conversation_engine", _FailingFrameworkEngine())
    monkeypatch.setattr(advice_api, "mock_conversation_engine", MockConversationEngine())

    response, engine_basis = advice_api._create_advice_with_engine_fallback(_request())

    assert engine_basis == "framework_fallback"
    assert response.source is not None
    assert response.source.engine == "framework_fallback"
    assert response.source.drc_character_id == "gentle_mina"
    assert response.source.drc_character_name == "ミナ"
    assert response.source.framework_preset is None
    assert response.source.framework_character is None
    assert "AI Character Framework" not in response.message
