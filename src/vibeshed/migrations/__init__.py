"""Version-to-version migrations applied by ``vibeshed update``.

Each migration is a callable ``(project_root: Path) -> None`` registered for a
target version. ``apply_migrations`` runs every migration whose target version
is greater than the manifest's current version and ``<=`` the new version.

v0.1.0 ships with no migrations.
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable, Dict, List, Tuple

Migration = Callable[[Path], None]

_REGISTRY: Dict[str, List[Migration]] = {}


def register(target_version: str, migration: Migration) -> None:
    _REGISTRY.setdefault(target_version, []).append(migration)


def _version_tuple(version: str) -> Tuple[int, ...]:
    return tuple(int(part) for part in version.split("."))


def pending(from_version: str, to_version: str) -> List[Tuple[str, Migration]]:
    """Return migrations whose target is in ``(from_version, to_version]``."""
    lo, hi = _version_tuple(from_version), _version_tuple(to_version)
    pending_list: List[Tuple[str, Migration]] = []
    for target, migs in sorted(_REGISTRY.items(), key=lambda kv: _version_tuple(kv[0])):
        target_t = _version_tuple(target)
        if lo < target_t <= hi:
            pending_list.extend((target, m) for m in migs)
    return pending_list


def apply(project_root: Path, from_version: str, to_version: str) -> List[str]:
    """Apply all pending migrations and return the list of applied target versions."""
    applied: List[str] = []
    for target, migration in pending(from_version, to_version):
        migration(project_root)
        applied.append(target)
    return applied
