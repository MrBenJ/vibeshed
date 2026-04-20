"""Three-way text merge using ``git merge-file``.

The system ``git`` binary is used so the merge algorithm matches what users
already get from their version control. Conflicts are returned with standard
``<<<<<<<`` / ``=======`` / ``>>>>>>>`` markers; the caller decides how to
surface them.
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path


class MergeError(RuntimeError):
    """Raised when the merge tool itself fails (not a content conflict)."""


@dataclass
class MergeResult:
    text: str
    had_conflict: bool


def merge(local: str, base: str, remote: str) -> MergeResult:
    """Three-way merge ``local`` and ``remote`` against common ancestor ``base``."""
    if not shutil.which("git"):
        raise MergeError("git is required for `vibeshed update` (not found on PATH)")

    with tempfile.TemporaryDirectory(prefix="vibeshed-merge-") as tmp:
        tmp_path = Path(tmp)
        local_path = tmp_path / "local"
        base_path = tmp_path / "base"
        remote_path = tmp_path / "remote"
        local_path.write_text(local, encoding="utf-8")
        base_path.write_text(base, encoding="utf-8")
        remote_path.write_text(remote, encoding="utf-8")

        result = subprocess.run(
            [
                "git",
                "merge-file",
                "-L", "local",
                "-L", "base",
                "-L", "incoming",
                "--marker-size=7",
                str(local_path),
                str(base_path),
                str(remote_path),
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode < 0:
            raise MergeError(f"git merge-file failed: {result.stderr.strip()}")

        return MergeResult(
            text=local_path.read_text(encoding="utf-8"),
            had_conflict=result.returncode > 0,
        )
