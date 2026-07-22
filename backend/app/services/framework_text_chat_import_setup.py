from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
import sys


def framework_text_chat_sys_path_roots(project_root: Path) -> tuple[Path, ...]:
    """Return the narrow sys.path roots needed for FW text chat imports.

    Day23 showed that the real vendored FW v4.0.0 checkout resolves both the
    public ``framework`` package and the top-level ``registry`` package from the
    configured project root. Some temporary smoke checkouts expose a legacy
    top-level ``registry`` name from ``framework/registry.py`` instead, so this
    helper adds the package directory only as a fallback for that layout.

    The helper only computes import roots. It does not import framework modules,
    create sessions, call ask/ask_stream, or touch provider runtime paths.
    """

    roots: list[Path] = []
    if project_root.exists():
        roots.append(project_root)

    framework_dir = project_root / "framework"
    root_exposes_registry = _has_registry_module(project_root)
    framework_dir_exposes_registry = _has_registry_module(framework_dir)

    if (
        framework_dir.exists()
        and framework_dir_exposes_registry
        and not root_exposes_registry
    ):
        roots.append(framework_dir)

    return _deduplicate_paths(tuple(roots))


@contextmanager
def framework_text_chat_import_context(project_root: Path):
    """Temporarily expose the configured FW import layout on ``sys.path``.

    Keep this context active for the whole import/session-creation preflight,
    not only for ``import framework``. FW facade code may perform lazy imports
    while creating a session, so removing the configured root immediately after
    importing the public package can surface false ``ModuleNotFoundError``
    results for top-level helper modules such as ``registry``.
    """

    added: list[str] = []
    for path in reversed(framework_text_chat_sys_path_roots(project_root)):
        path_text = str(path)
        if path_text not in sys.path:
            sys.path.insert(0, path_text)
            added.append(path_text)
    try:
        yield
    finally:
        for path_text in added:
            try:
                sys.path.remove(path_text)
            except ValueError:
                pass


def framework_text_chat_import_layout_summary(project_root: Path) -> tuple[str, ...]:
    """Return public-safe names for the sys.path layout selected by the helper."""

    summary: list[str] = []
    for path in framework_text_chat_sys_path_roots(project_root):
        try:
            relative = path.relative_to(project_root)
        except ValueError:
            summary.append("<external-path>")
            continue
        if str(relative) == ".":
            summary.append("configured-root-only")
        elif relative.as_posix() == "framework":
            summary.append("framework-package-dir-fallback")
        else:
            summary.append("configured-subdir")
    return tuple(summary)


def _has_registry_module(path: Path) -> bool:
    return (path / "registry.py").exists() or (path / "registry" / "__init__.py").exists()


def _deduplicate_paths(paths: tuple[Path, ...]) -> tuple[Path, ...]:
    seen: set[str] = set()
    deduplicated: list[Path] = []
    for path in paths:
        key = str(path)
        if key in seen:
            continue
        seen.add(key)
        deduplicated.append(path)
    return tuple(deduplicated)
