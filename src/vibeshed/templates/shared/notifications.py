"""Notification helpers.

Set ``NOTIFICATION_CHANNEL`` to choose a channel: ``console`` (default),
``telegram``, or ``discord``. Channel-specific config is read from env vars
(``TELEGRAM_BOT_TOKEN`` + ``TELEGRAM_CHAT_ID``, ``DISCORD_WEBHOOK_URL``).
"""

from __future__ import annotations

import os
from typing import Optional


def send(message: str, title: Optional[str] = None) -> None:
    """Send a notification via the configured channel."""
    channel = os.getenv("NOTIFICATION_CHANNEL", "console").lower()
    if channel == "console":
        _send_console(message, title)
    elif channel == "telegram":
        _send_telegram(message, title)
    elif channel == "discord":
        _send_discord(message, title)
    else:
        raise ValueError(f"Unknown NOTIFICATION_CHANNEL: {channel!r}")


def send_error(title: str, error: str) -> None:
    """Send an error notification."""
    send(f"ERROR: {error}", title=f"❌ {title}")


def _send_console(message: str, title: Optional[str]) -> None:
    if title:
        bar = "=" * 40
        print(f"\n{bar}\n  {title}\n{bar}")
    print(message)
    print()


def _send_telegram(message: str, title: Optional[str]) -> None:
    import requests

    token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]
    text = f"*{title}*\n\n{message}" if title else message
    requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"},
        timeout=15,
    ).raise_for_status()


def _send_discord(message: str, title: Optional[str]) -> None:
    import requests

    webhook = os.environ["DISCORD_WEBHOOK_URL"]
    content = f"**{title}**\n{message}" if title else message
    requests.post(webhook, json={"content": content}, timeout=15).raise_for_status()
