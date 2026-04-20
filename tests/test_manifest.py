"""Tests for manifest read/write/diff."""

from __future__ import annotations

from pathlib import Path

from vibeshed import __version__, manifest as manifest_mod
from vibeshed.templates_loader import MANAGED_FILES


def test_fresh_manifest_covers_all_managed_files() -> None:
    m = manifest_mod.fresh_manifest()
    assert m.framework_version == __version__
    assert set(m.files.keys()) == set(MANAGED_FILES.keys())
    for rel, mode in MANAGED_FILES.items():
        entry = m.files[rel]
        assert entry.mode == mode
        assert entry.shipped_in == __version__
        assert len(entry.sha) == 64  # sha256 hex


def test_save_load_roundtrip(tmp_path: Path) -> None:
    original = manifest_mod.fresh_manifest()
    manifest_mod.save(tmp_path, original)
    loaded = manifest_mod.load(tmp_path)
    assert loaded is not None
    assert loaded.framework_version == original.framework_version
    assert {k: v.to_dict() for k, v in loaded.files.items()} == {
        k: v.to_dict() for k, v in original.files.items()
    }


def test_load_returns_none_when_absent(tmp_path: Path) -> None:
    assert manifest_mod.load(tmp_path) is None
