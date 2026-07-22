"""Smoke check for the v0.31.0 local framework import boundary.

The DRC framework adapter imports a package named ``framework`` from
FRAMEWORK_ROOT. This check proves that a stale or unrelated already-imported
``framework`` module cannot be reused accidentally.

It uses two temporary fake framework roots:
- stale_root: intentionally cached first and returns an invalid session.
- target_root: configured as FRAMEWORK_ROOT and expected to be used.

No real AI Character Framework checkout, API key, or provider call is required.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.config import AppConfig  # noqa: E402
from app.engines.framework_engine import FrameworkConversationEngine  # noqa: E402


def main() -> int:
    with TemporaryDirectory(prefix="drc_fw_import_boundary_") as temp_dir:
        temp_path = Path(temp_dir)
        stale_root = temp_path / "stale_fw"
        target_root = temp_path / "target_fw"

        _write_fake_framework(
            stale_root,
            marker="stale",
            advice="[stale-framework] this module should not be used",
        )
        _write_fake_framework(
            target_root,
            marker="target",
            advice="[target-framework] local_import boundary OK",
        )

        _import_stale_framework(stale_root)

        config = AppConfig(
            conversation_engine="framework",
            framework_project_root=str(target_root),
            framework_preset="text_chat",
            framework_character="default",
            framework_adapter_mode="local_import",
            sleep_provider="mock",
        )
        engine = FrameworkConversationEngine(config=config)
        session = engine._get_or_create_session("default")  # noqa: SLF001
        message = session.ask("boundary smoke prompt")

        if "[target-framework]" not in message:
            raise AssertionError(
                "FrameworkConversationEngine reused a stale framework module."
            )

        imported_framework = sys.modules.get("framework")
        imported_path = Path(getattr(imported_framework, "__file__", "")).resolve()
        if target_root not in imported_path.parents:
            raise AssertionError(
                "framework module was not imported from configured FRAMEWORK_ROOT: "
                f"{imported_path}"
            )

    sys.modules.pop("framework", None)
    sys.modules.pop("framework.facade", None)
    importlib.invalidate_caches()

    print(
        "[framework-local-import-boundary-smoke-v0.31.0] OK: "
        "stale framework module was ignored and configured FRAMEWORK_ROOT was used."
    )
    return 0


def _write_fake_framework(root: Path, *, marker: str, advice: str) -> None:
    package_root = root / "framework"
    package_root.mkdir(parents=True)
    (package_root / "facade.py").write_text(
        "\n".join(
            [
                f"MARKER = {marker!r}",
                "class FakeTextChatSession:",
                "    def ask(self, prompt):",
                f"        return {advice!r}",
                "",
                "def create_text_chat_session(*, preset, character_name):",
                "    if preset != 'text_chat':",
                "        raise RuntimeError('unexpected preset: ' + str(preset))",
                "    if character_name != 'default':",
                "        raise RuntimeError('unexpected character_name: ' + str(character_name))",
                "    return FakeTextChatSession()",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (package_root / "__init__.py").write_text(
        "from .facade import MARKER, create_text_chat_session\n",
        encoding="utf-8",
    )


def _import_stale_framework(stale_root: Path) -> None:
    sys.modules.pop("framework", None)
    sys.modules.pop("framework.facade", None)
    sys.path.insert(0, str(stale_root))
    importlib.invalidate_caches()
    imported = importlib.import_module("framework")
    if getattr(imported, "MARKER", None) != "stale":
        raise AssertionError("failed to prepare stale framework module fixture")
    sys.path.remove(str(stale_root))


if __name__ == "__main__":
    raise SystemExit(main())
