"""Tests for marker parsing and replacement."""

from __future__ import annotations

import pytest

from vibeshed import markers


HTML_FILE = """<!-- vibeshed:managed:start v0.1.0 -->
managed body
<!-- vibeshed:managed:end -->

custom user content
"""

HASH_FILE = """# vibeshed:managed:start v0.1.0
managed body
# vibeshed:managed:end

# user content
"""


def test_extract_managed_html() -> None:
    assert markers.extract_managed(HTML_FILE) == "managed body"


def test_extract_managed_hash() -> None:
    assert markers.extract_managed(HASH_FILE) == "managed body"


def test_replace_preserves_user_content() -> None:
    out = markers.replace_managed(HTML_FILE, "new managed body", "0.2.0")
    assert "new managed body" in out
    assert "custom user content" in out
    assert "v0.2.0" in out
    assert "managed body\n" not in out.replace("new managed body\n", "")


def test_replace_handles_hash_style() -> None:
    out = markers.replace_managed(HASH_FILE, "new body line", "0.2.0")
    assert "new body line" in out
    assert "# user content" in out
    assert "# vibeshed:managed:start v0.2.0" in out


def test_strip_markers() -> None:
    stripped = markers.strip_markers(HTML_FILE)
    assert "vibeshed:managed" not in stripped
    assert "managed body" in stripped
    assert "custom user content" in stripped


def test_extract_raises_when_missing() -> None:
    with pytest.raises(markers.MarkerError):
        markers.extract_managed("no markers here")
