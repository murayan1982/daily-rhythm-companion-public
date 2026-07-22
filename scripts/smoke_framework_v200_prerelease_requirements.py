"""Smoke renderer for v2.0.0 pre-release requirements."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.app.services.framework_v200_prerelease_requirements import (
    build_v200_prerelease_requirements,
    render_v200_prerelease_requirements,
)


def main() -> None:
    result = build_v200_prerelease_requirements()
    print("[smoke-framework-v200-prerelease-requirements] RESULT")
    print(render_v200_prerelease_requirements(result))
    print("[smoke-framework-v200-prerelease-requirements] OK")
    print("No provider API, Google Health API, TTS synthesis, Web image load, release build, or network call was made.")


if __name__ == "__main__":
    main()
