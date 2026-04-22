#!/usr/bin/env python3
"""Entry point for {{JOB_SLUG}}.

Invoked by ``vibeshed run {{JOB_SLUG}} -- <params>``; everything after ``--``
is forwarded here as ``sys.argv``. Also runs directly with
``JOB_SLUG={{JOB_SLUG}} python jobs/{{JOB_SLUG}}/scripts/main.py <params>``.
"""

from __future__ import annotations

import argparse
import sys

from shared import logging


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="{{JOB_SLUG}}")
    # TODO: declare the params this job expects. Mirror them in sequence.md's Inputs section.
    # parser.add_argument("--example", required=True, help="Describe me.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    logger = logging.get_logger(__name__)
    args = parse_args(sys.argv[1:] if argv is None else argv)
    logger.info("Starting {{JOB_SLUG}} with args=%s", vars(args))

    try:
        # TODO: implement the job's action here.
        logger.info("{{JOB_SLUG}} completed successfully")
        return 0
    except Exception as exc:
        logger.error("Job failed: %s", exc, exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
