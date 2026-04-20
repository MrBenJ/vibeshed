"""Auto-routing logger for VibeShed jobs.

Each call to ``get_logger`` returns a logger that writes to
``logs/{job-slug}/{YYYY-MM-DD}/run_{HH-MM-SS}.log``.

The job slug is determined from (in priority order):
  1. The ``JOB_SLUG`` environment variable.
  2. The calling file's path, if it lives under ``jobs/{slug}/scripts/``.
  3. ``"unknown"`` (with a warning logged to stderr).
"""

from __future__ import annotations

import inspect
import logging as _stdlib_logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
_RUN_TIMESTAMP = datetime.now().strftime("%H-%M-%S")
_DATE_STAMP = datetime.now().strftime("%Y-%m-%d")


def get_logger(name: str) -> _stdlib_logging.Logger:
    """Return a logger that writes to the correct log folder for the current job."""
    logger = _stdlib_logging.getLogger(name)

    if any(getattr(h, "_vibeshed", False) for h in logger.handlers):
        return logger

    job_slug = os.getenv("JOB_SLUG") or _detect_job_from_stack() or "unknown"
    log_dir = _get_log_directory(job_slug)
    log_file = log_dir / f"run_{_RUN_TIMESTAMP}.log"

    file_handler = _stdlib_logging.FileHandler(log_file)
    file_handler.setFormatter(_stdlib_logging.Formatter(_LOG_FORMAT))
    file_handler._vibeshed = True  # type: ignore[attr-defined]
    logger.addHandler(file_handler)

    stream_handler = _stdlib_logging.StreamHandler(sys.stderr)
    stream_handler.setFormatter(_stdlib_logging.Formatter(_LOG_FORMAT))
    stream_handler._vibeshed = True  # type: ignore[attr-defined]
    logger.addHandler(stream_handler)

    logger.setLevel(_stdlib_logging.INFO)
    logger.propagate = False
    return logger


def _detect_job_from_stack() -> Optional[str]:
    """Walk the call stack to find a file path matching ``jobs/{slug}/scripts/``."""
    for frame_info in inspect.stack():
        path = Path(frame_info.filename).resolve()
        parts = path.parts
        try:
            jobs_idx = parts.index("jobs")
        except ValueError:
            continue
        if jobs_idx + 2 < len(parts) and parts[jobs_idx + 2] == "scripts":
            return parts[jobs_idx + 1]
    return None


def _get_log_directory(job_slug: str) -> Path:
    log_dir = Path("logs") / job_slug / _DATE_STAMP
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir
