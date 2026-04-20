"""Parse and replace framework-managed sections delimited by sentinel markers.

Two comment styles are supported, chosen by file type:

* HTML/Markdown:  ``<!-- vibeshed:managed:start vX.Y.Z -->`` ... ``<!-- vibeshed:managed:end -->``
* Hash comments:  ``# vibeshed:managed:start vX.Y.Z``       ... ``# vibeshed:managed:end``

Content outside the markers is user-owned and is preserved across updates.
Marker styles are matched flexibly so `vibeshed update` can re-stamp the
version on each successful update.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

START_KEYWORD = "vibeshed:managed:start"
END_KEYWORD = "vibeshed:managed:end"


@dataclass
class MarkerStyle:
    name: str
    start_pattern: str
    end_pattern: str
    start_template: str
    end_template: str


_HTML_STYLE = MarkerStyle(
    name="html",
    start_pattern=rf"<!--\s*{re.escape(START_KEYWORD)}(?:\s+v[\w.\-+]+)?\s*-->",
    end_pattern=rf"<!--\s*{re.escape(END_KEYWORD)}\s*-->",
    start_template="<!-- vibeshed:managed:start v{version} -->",
    end_template="<!-- vibeshed:managed:end -->",
)

_HASH_STYLE = MarkerStyle(
    name="hash",
    start_pattern=rf"#\s*{re.escape(START_KEYWORD)}(?:\s+v[\w.\-+]+)?\s*",
    end_pattern=rf"#\s*{re.escape(END_KEYWORD)}\s*",
    start_template="# vibeshed:managed:start v{version}",
    end_template="# vibeshed:managed:end",
)

_STYLES = (_HTML_STYLE, _HASH_STYLE)


class MarkerError(ValueError):
    """Raised when marker parsing or replacement fails."""


def detect_style(text: str) -> Optional[MarkerStyle]:
    """Return the marker style present in ``text``, or ``None`` if none found."""
    for style in _STYLES:
        if re.search(style.start_pattern, text):
            return style
    return None


def style_for_path(rel_path: str) -> MarkerStyle:
    """Return the marker style appropriate for a file path."""
    if rel_path.endswith((".md", ".html", ".htm")):
        return _HTML_STYLE
    return _HASH_STYLE


def extract_managed(text: str) -> str:
    """Return the content between the start and end markers (markers excluded)."""
    style = detect_style(text)
    if style is None:
        raise MarkerError("No vibeshed markers found in file")
    match = re.search(
        rf"{style.start_pattern}\n?(?P<body>.*?)\n?{style.end_pattern}",
        text,
        re.DOTALL,
    )
    if match is None:
        raise MarkerError("Found start marker but no matching end marker")
    return match.group("body")


def replace_managed(local_text: str, new_managed_body: str, version: str) -> str:
    """Replace the managed section in ``local_text`` with ``new_managed_body``."""
    style = detect_style(local_text) or style_for_path("")
    pattern = re.compile(
        rf"{style.start_pattern}\n?.*?\n?{style.end_pattern}",
        re.DOTALL,
    )
    replacement = (
        style.start_template.format(version=version)
        + "\n"
        + new_managed_body.rstrip("\n")
        + "\n"
        + style.end_template
    )
    if not pattern.search(local_text):
        raise MarkerError("No managed section to replace; user may have stripped markers")
    return pattern.sub(lambda _: replacement, local_text, count=1)


def strip_markers(text: str) -> str:
    """Remove all vibeshed marker lines, leaving the content in place."""
    style = detect_style(text)
    if style is None:
        return text
    text = re.sub(rf"{style.start_pattern}\n?", "", text)
    text = re.sub(rf"{style.end_pattern}\n?", "", text)
    return text
