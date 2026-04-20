"""Persistent state for VibeShed jobs, with file locking for concurrency safety.

State is stored as JSON at ``state/{job-slug}.json``. A sibling ``.lock`` file
guards each operation. Locks are acquired per-call, not held across calls.
For multi-step atomic updates, use ``get_all`` then write each key.
"""

from __future__ import annotations

import fcntl
import json
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator


class StateManager:
    """Manage persistent state for a job."""

    def __init__(self, job_slug: str, root: Path | str = "state"):
        self.job_slug = job_slug
        self._root = Path(root)
        self.state_file = self._root / f"{job_slug}.json"
        self.lock_file = self._root / f"{job_slug}.lock"

    @contextmanager
    def _locked(self) -> Iterator[None]:
        self._root.mkdir(parents=True, exist_ok=True)
        with open(self.lock_file, "w") as lock_fd:
            fcntl.flock(lock_fd.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(lock_fd.fileno(), fcntl.LOCK_UN)

    def _load(self) -> dict:
        if self.state_file.exists():
            return json.loads(self.state_file.read_text())
        return {}

    def _save(self, state: dict) -> None:
        self.state_file.write_text(json.dumps(state, indent=2, sort_keys=True))

    def get(self, key: str, default: Any = None) -> Any:
        with self._locked():
            return self._load().get(key, default)

    def set(self, key: str, value: Any) -> None:
        with self._locked():
            state = self._load()
            state[key] = value
            self._save(state)

    def delete(self, key: str) -> None:
        with self._locked():
            state = self._load()
            if key in state:
                del state[key]
                self._save(state)

    def get_all(self) -> dict:
        with self._locked():
            return self._load()
