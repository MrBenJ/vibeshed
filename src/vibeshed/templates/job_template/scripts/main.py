#!/usr/bin/env python3
"""Entry point for {{JOB_SLUG}}.

This script is invoked by ``vibeshed run {{JOB_SLUG}}``. It also runs directly
with ``JOB_SLUG={{JOB_SLUG}} python jobs/{{JOB_SLUG}}/scripts/main.py``.
"""

from __future__ import annotations

import sys

from shared import logging


def main() -> int:
    logger = logging.get_logger(__name__)
    logger.info("Starting {{JOB_SLUG}}")

    try:
        # TODO: implement the job's action here.
        logger.info("{{JOB_SLUG}} completed successfully")
        return 0
    except Exception as exc:
        logger.error("Job failed: %s", exc, exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
