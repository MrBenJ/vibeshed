"""Cache of last-installed template contents — the merge base for ``update``.

When ``init`` or ``update`` writes a managed file, it also writes a verbatim
copy under ``.vibeshed/cache/<rel_path>``. That copy is the common ancestor
for future three-way merges, so we can reconstruct what the user started from
without shipping every historical version of every file.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

CACHE_DIR = ".vibeshed/cache"


def cache_path(project_root: Path, rel_path: str) -> Path:
    return project_root / CACHE_DIR / rel_path


def write(project_root: Path, rel_path: str, content: str) -> None:
    path = cache_path(project_root, rel_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def read(project_root: Path, rel_path: str) -> Optional[str]:
    path = cache_path(project_root, rel_path)
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")
