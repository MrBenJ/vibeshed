"""Shared utilities for VibeShed automations.

Import the submodules you need — they're loaded lazily so jobs that don't use
``api_clients`` don't pay the cost of importing ``requests``:

    from shared import logging, state, notifications, api_clients
"""

from importlib import import_module

__all__ = ["logging", "state", "notifications", "api_clients"]


def __getattr__(name: str):
    if name in __all__:
        module = import_module(f"{__name__}.{name}")
        globals()[name] = module
        return module
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
