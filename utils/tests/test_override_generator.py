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

    def test_adapt_skin_bin_with_resource_resolver_and_animations(self):
        import struct
        from injection.baseskin.propbin import Bin, Embed, Field, Value, fnv1a_lower
        from utils.competitive.override_generator import (
            ANIMATION_GRAPH_DATA_CLASS,
            PROP_ANIMATION_GRAPH_DATA,
            PROP_PATH_HASH,
            PROP_RESOURCE_RESOLVER,
            PROP_SKIN_ID,
            RESOURCE_RESOLVER_CLASS,
            SKIN_DATA_CLASS,
            TYPE_LINK,
            adapt_animation_bin,
            adapt_skin_bin,
        )

        char = "ekko"
        skin_idx = 19
        champ_id = 245

        base_skin_hash = fnv1a_lower("Characters/ekko/Skins/Skin0")
        base_res_hash = fnv1a_lower("Characters/ekko/Skins/Skin0/Resources")
        base_anim_hash = fnv1a_lower("Characters/ekko/Animations/Skin0")

        # 1. Build SkinCharacterDataProperties
        anim_embed = Embed(PROP_ANIMATION_GRAPH_DATA, [Field(ANIMATION_GRAPH_DATA_CLASS, Value(TYPE_LINK, struct.pack("<I", base_anim_hash)))])
        skin_fields = [
            Field(PROP_PATH_HASH, Value(17, struct.pack("<I", base_skin_hash))),
            Field(PROP_SKIN_ID, Value(6, struct.pack("<I", 245000))),
            Field(PROP_RESOURCE_RESOLVER, Value(TYPE_LINK, struct.pack("<I", base_res_hash))),
            Field(PROP_ANIMATION_GRAPH_DATA, Value(131, anim_embed)),
        ]
        skin_entry = from_fields(SKIN_DATA_CLASS, base_skin_hash, skin_fields)

        # 2. Build ResourceResolver entry
        res_fields = [Field(PROP_PATH_HASH, Value(17, struct.pack("<I", base_res_hash)))]
        res_entry = from_fields(RESOURCE_RESOLVER_CLASS, base_res_hash, res_fields)

        from injection.baseskin.propbin import build
        raw_skin0 = build([skin_entry, res_entry])

        # Adapt skin bin with custom animations enabled
        adapted_raw = adapt_skin_bin(raw_skin0, char, skin_idx, champ_id, has_custom_anim=True)
        adapted_bin = Bin(adapted_raw)

        expected_skin_hash = fnv1a_lower(f"Characters/{char}/Skins/Skin{skin_idx}")
        expected_res_hash = fnv1a_lower(f"Characters/{char}/Skins/Skin{skin_idx}/Resources")
        expected_anim_hash = fnv1a_lower(f"Characters/{char}/Animations/Skin{skin_idx}")

        # Check SkinCharacterDataProperties
        e_skin = adapted_bin.find_entry(SKIN_DATA_CLASS)
        self.assertEqual(e_skin.path_hash, expected_skin_hash)
        self.assertEqual(struct.unpack("<I", e_skin.find_field(PROP_PATH_HASH).value.v)[0], expected_skin_hash)
        self.assertEqual(struct.unpack("<I", e_skin.find_field(PROP_SKIN_ID).value.v)[0], 245019)
        self.assertEqual(struct.unpack("<I", e_skin.find_field(PROP_RESOURCE_RESOLVER).value.v)[0], expected_res_hash)

        f_anim = e_skin.find_field(PROP_ANIMATION_GRAPH_DATA)
        sub_anim = f_anim.value.v.find_field(ANIMATION_GRAPH_DATA_CLASS)
        self.assertEqual(struct.unpack("<I", sub_anim.value.v)[0], expected_anim_hash)

        # Check ResourceResolver entry
        e_res = adapted_bin.find_entry(RESOURCE_RESOLVER_CLASS)
        self.assertEqual(e_res.path_hash, expected_res_hash)
        self.assertEqual(struct.unpack("<I", e_res.find_field(PROP_PATH_HASH).value.v)[0], expected_res_hash)

        # 3. Test adapt_animation_bin
        anim_fields = [Field(PROP_PATH_HASH, Value(17, struct.pack("<I", base_anim_hash)))]
        raw_anim0 = build([from_fields(ANIMATION_GRAPH_DATA_CLASS, base_anim_hash, anim_fields)])

        adapted_anim = adapt_animation_bin(raw_anim0, char, skin_idx)
        adapted_anim_bin = Bin(adapted_anim)
        e_anim = adapted_anim_bin.find_entry(ANIMATION_GRAPH_DATA_CLASS)
        self.assertEqual(e_anim.path_hash, expected_anim_hash)
        self.assertEqual(struct.unpack("<I", e_anim.find_field(PROP_PATH_HASH).value.v)[0], expected_anim_hash)


def from_fields(type_hash, path_hash, fields):
    from injection.baseskin.propbin import Entry
    return Entry(type_hash, path_hash, fields)


if __name__ == "__main__":
    unittest.main()
