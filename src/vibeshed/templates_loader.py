"""Access bundled framework templates via :mod:`importlib.resources`.

The list of files VibeShed installs into a user repo is defined here, along
with the update mode for each (``"full"`` for a whole-file overwrite/merge,
``"marker"`` for replacing only the content between sentinel markers).

``job_template/`` files are intentionally excluded — they are scaffolding
sources for ``vibeshed new``, copied once and never tracked by the manifest.
"""

from __future__ import annotations

from importlib.resources import as_file, files
from pathlib import Path
from typing import Dict, Iterator, Tuple

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


def template_text(rel_path: str) -> str:
    """Read a bundled template file as text."""
    resource = files("vibeshed.templates").joinpath(rel_path)
    return resource.read_text(encoding="utf-8")


def template_bytes(rel_path: str) -> bytes:
    """Read a bundled template file as bytes."""
    resource = files("vibeshed.templates").joinpath(rel_path)
    return resource.read_bytes()


def iter_job_template_files() -> Iterator[Tuple[str, str]]:
    """Yield ``(relative_path, text)`` for every file under ``job_template/``."""
    root = files("vibeshed.templates").joinpath(JOB_TEMPLATE_ROOT)
    with as_file(root) as root_path:
        root_path = Path(root_path)
        for path in sorted(root_path.rglob("*")):
            if path.is_file():
                rel = path.relative_to(root_path).as_posix()
                yield rel, path.read_text(encoding="utf-8")
