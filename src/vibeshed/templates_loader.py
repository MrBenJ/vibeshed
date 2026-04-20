"""Access bundled framework templates via :mod:`importlib.resources`.

The list of files VibeShed installs into a user repo is defined here, along
with the update mode for each (``"full"`` for a whole-file overwrite/merge,
``"marker"`` for replacing only the content between sentinel markers).

``job_template/`` files are intentionally excluded — they are scaffolding
sources for ``vibeshed new``, copied once and never tracked by the manifest.
"""

from __future__ import annotations

from importlib.resources import files
from typing import Any, Dict, Iterator, Tuple

MANAGED_FILES: Dict[str, str] = {
    "AGENTS.md": "marker",
    "CLAUDE.md": "marker",
    ".gitignore": "marker",
    "requirements.txt": "marker",
    "shared/__init__.py": "full",
    "shared/logging.py": "full",
    "shared/state.py": "full",
    "shared/notifications.py": "full",
    "shared/api_clients.py": "full",
}

UNMANAGED_INIT_FILES: Tuple[str, ...] = ("registry.yaml",)

INIT_DIRECTORIES: Tuple[str, ...] = ("state", "logs", "jobs")

JOB_TEMPLATE_ROOT = "job_template"


def _templates_root() -> Any:
    """Anchor on the ``vibeshed`` package and joinpath into ``templates/``.

    ``templates`` is a plain directory (no ``__init__.py``), so we cannot pass
    it directly to ``files()`` on Python 3.9. ``files("vibeshed").joinpath(...)``
    works uniformly across 3.9–3.12.
    """
    return files("vibeshed").joinpath("templates")


def template_text(rel_path: str) -> str:
    """Read a bundled template file as text."""
    return _resolve(rel_path).read_text(encoding="utf-8")


def template_bytes(rel_path: str) -> bytes:
    """Read a bundled template file as bytes."""
    return _resolve(rel_path).read_bytes()


def iter_job_template_files() -> Iterator[Tuple[str, str]]:
    """Yield ``(relative_path, text)`` for every file under ``job_template/``."""
    root = _templates_root().joinpath(JOB_TEMPLATE_ROOT)
    yield from _walk_files(root, prefix="")


def _resolve(rel_path: str) -> Any:
    node = _templates_root()
    for part in rel_path.split("/"):
        node = node.joinpath(part)
    return node


def _walk_files(node: Any, prefix: str) -> Iterator[Tuple[str, str]]:
    for child in sorted(node.iterdir(), key=lambda c: c.name):
        rel = f"{prefix}{child.name}"
        if child.is_file():
            yield rel, child.read_text(encoding="utf-8")
        elif child.is_dir():
            yield from _walk_files(child, prefix=f"{rel}/")
