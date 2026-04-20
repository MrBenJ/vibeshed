"""Read, write, and reason about ``.vibeshed/manifest.json``.

The manifest records, per managed file, the SHA256 of the framework version
that was last installed plus the version it shipped in. ``vibeshed update``
uses this to detect drift and pick the right merge strategy.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional

from vibeshed import __version__
from vibeshed.templates_loader import MANAGED_FILES, template_bytes

MANIFEST_DIR = ".vibeshed"
MANIFEST_FILENAME = "manifest.json"


@dataclass
class FileEntry:
    sha: str
    shipped_in: str
    mode: str

    def to_dict(self) -> dict:
        return {"sha": self.sha, "shipped_in": self.shipped_in, "mode": self.mode}

    @classmethod
    def from_dict(cls, data: dict) -> "FileEntry":
        return cls(sha=data["sha"], shipped_in=data["shipped_in"], mode=data["mode"])


@dataclass
class Manifest:
    framework_version: str
    files: Dict[str, FileEntry] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "framework_version": self.framework_version,
            "files": {path: entry.to_dict() for path, entry in self.files.items()},
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Manifest":
        return cls(
            framework_version=data["framework_version"],
            files={
                path: FileEntry.from_dict(entry)
                for path, entry in data.get("files", {}).items()
            },
        )


def manifest_path(project_root: Path) -> Path:
    return project_root / MANIFEST_DIR / MANIFEST_FILENAME


def load(project_root: Path) -> Optional[Manifest]:
    """Load the manifest for a project, or return ``None`` if not present."""
    path = manifest_path(project_root)
    if not path.exists():
        return None
    return Manifest.from_dict(json.loads(path.read_text(encoding="utf-8")))


def save(project_root: Path, manifest: Manifest) -> None:
    """Persist the manifest to ``.vibeshed/manifest.json``."""
    path = manifest_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(manifest.to_dict(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def fresh_manifest() -> Manifest:
    """Build a manifest reflecting the current bundled templates."""
    entries = {
        rel: FileEntry(
            sha=sha256_bytes(template_bytes(rel)),
            shipped_in=__version__,
            mode=mode,
        )
        for rel, mode in MANAGED_FILES.items()
    }
    return Manifest(framework_version=__version__, files=entries)
