#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unit tests for competitive mode base skin override generator and cache."""

import os
import tempfile
import time
import unittest
from pathlib import Path

from injection.baseskin.wad import ModWad, path_hash
from injection.mods.mod_files import ModFiles
from utils.competitive.override_generator import (
    adapt_skin_bin,
    get_champion_alias,
    get_competitive_cache_dir,
    get_or_create_base_override,
)


class TestOverrideGenerator(unittest.TestCase):
    """Test base skin override generation and cache behavior."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_root = Path(self.temp_dir.name)
        self.cache_dir = self.test_root / "cache"
        self.game_dir = self.test_root / "game"
        self.wad_dir = self.game_dir / "DATA" / "FINAL" / "Champions"
        self.wad_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        self.temp_dir.cleanup()

    def _create_mock_wad(self, alias: str, characters: list, skin_count: int = 3) -> Path:
        """Create a minimal valid WAD archive simulating champion data."""
        wad_path = self.wad_dir / f"{alias}.wad.client"
        empty_header = b"RW\x03\x00" + bytes(268)
        mw = ModWad(empty_header)

        # Mock bin content for skin0
        mock_skin0 = b"PROP_BIN_MOCK_DATA_SKIN0_DEFAULT_MESH_TEXTURE"

        for char in characters:
            # skin0
            mw.put(path_hash(f"data/characters/{char}/skins/skin0.bin"), mock_skin0)
            # skin1..skinN
            for i in range(1, skin_count + 1):
                mw.put(path_hash(f"data/characters/{char}/skins/skin{i}.bin"), f"MOCK_SKIN_{i}".encode("utf-8"))

        wad_path.write_bytes(mw.to_bytes())
        return wad_path

    def test_get_competitive_cache_dir(self):
        custom = self.test_root / "custom_cache"
        result = get_competitive_cache_dir(custom)
        self.assertEqual(result, custom)
        self.assertTrue(result.is_dir())

    def test_get_champion_alias(self):
        self.assertEqual(get_champion_alias(266), "Aatrox")
        self.assertEqual(get_champion_alias(1), "Annie")
        self.assertEqual(get_champion_alias(62), "MonkeyKing")
        self.assertEqual(get_champion_alias(99), "Lux")
        self.assertIsNone(get_champion_alias(999999))

    def test_create_and_cache_base_override(self):
        # Setup mock WAD for Aatrox (ID 266)
        self._create_mock_wad("Aatrox", ["aatrox"], skin_count=4)

        # First call: generates .fantome
        override_path = get_or_create_base_override(
            champion_id=266,
            game_path=self.game_dir,
            cache_dir=self.cache_dir,
        )

        self.assertIsNotNone(override_path)
        self.assertTrue(override_path.is_file())
        self.assertEqual(override_path.name, "base_override_266.fantome")

        # Inspect generated package contents
        with ModFiles(override_path) as mf:
            files = mf.files_under()
            self.assertIn("META/info.json", files)
            self.assertIn("metadata.json", files)
            self.assertIn("WAD/Aatrox.wad.client", files)

            # Check that ModWad contains overridden skin bins
            wad_bytes = mf.read("WAD/Aatrox.wad.client")
            mod_wad = ModWad(wad_bytes)
            # skin1..skin4 should be mapped to skin0 content
            for i in range(1, 5):
                h = path_hash(f"data/characters/aatrox/skins/skin{i}.bin")
                self.assertIn(h, mod_wad)
                self.assertEqual(mod_wad.get(h).data, b"PROP_BIN_MOCK_DATA_SKIN0_DEFAULT_MESH_TEXTURE")

        # Second call: cache hit (mtime untouched)
        mtime_before = override_path.stat().st_mtime_ns
        cached_path = get_or_create_base_override(
            champion_id=266,
            game_path=self.game_dir,
            cache_dir=self.cache_dir,
        )
        self.assertEqual(cached_path, override_path)
        self.assertEqual(cached_path.stat().st_mtime_ns, mtime_before)

    def test_cache_invalidation_when_wad_updated(self):
        wad_path = self._create_mock_wad("Aatrox", ["aatrox"], skin_count=2)
        override_path = get_or_create_base_override(266, self.game_dir, self.cache_dir)
        self.assertIsNotNone(override_path)

        # Artificially age the cached file
        past_time = time.time() - 100
        os.utime(override_path, (past_time, past_time))
        new_wad_time = time.time()
        os.utime(wad_path, (new_wad_time, new_wad_time))

        # Re-fetching should detect stale cache and regenerate
        regenerated_path = get_or_create_base_override(266, self.game_dir, self.cache_dir)
        self.assertIsNotNone(regenerated_path)
        self.assertGreaterEqual(regenerated_path.stat().st_mtime, new_wad_time - 1)

    def test_missing_wad_graceful_failure(self):
        # Champion 99999 has no alias or WAD
        result = get_or_create_base_override(99999, self.game_dir, self.cache_dir)
        self.assertIsNone(result)

        # Champion 266 with missing WAD file
        empty_game_dir = self.test_root / "empty_game"
        empty_game_dir.mkdir(parents=True, exist_ok=True)
        result = get_or_create_base_override(266, empty_game_dir, self.cache_dir)
        self.assertIsNone(result)

    def test_adapt_skin_bin_with_prop_structure(self):
        import struct
        from injection.baseskin.propbin import Bin, fnv1a_lower

        # Build a minimal valid PROP file with SkinCharacterDataProperties
        skin_data_class = 0x9B67E9F6
        base_path_hash = fnv1a_lower("Characters/aatrox/Skins/Skin0")
        target_path_hash = fnv1a_lower("Characters/aatrox/Skins/Skin5")

        # Entry 0 body: 4-byte path_hash + 2-byte field count (0 fields)
        entry_body = struct.pack("<IH", base_path_hash, 0)
        entry_bytes = struct.pack("<I", len(entry_body)) + entry_body

        prop_header = b"PROP\x02\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00" + struct.pack("<I", skin_data_class)
        raw_prop = prop_header + entry_bytes

        adapted = adapt_skin_bin(raw_prop, "aatrox", 5, 266)
        adapted_bin = Bin(adapted)
        adapted_entry = adapted_bin.find_entry(skin_data_class)
        self.assertIsNotNone(adapted_entry)
        self.assertEqual(adapted_entry.path_hash, target_path_hash)


if __name__ == "__main__":
    unittest.main()
