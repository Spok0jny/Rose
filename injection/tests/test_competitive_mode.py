#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""End-to-end integration tests for Competitive Mode subsystem."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock

from injection.baseskin.wad import ModWad, path_hash
from injection.core.stage_plan import CompetitiveStep, SkinStep, prepare_plan
from injection.mods.mod_files import ModFiles
from state.core.shared_state import SharedState
from threads.handlers.injection_trigger import InjectionTrigger
from utils.competitive.override_generator import get_or_create_base_override
from utils.competitive.queue_detector import is_draft_mode
from utils.competitive.target_resolver import resolve_competitive_targets


class TestCompetitiveModeEndToEnd(unittest.TestCase):
    """End-to-end integration tests for competitive base skin overrides."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_root = Path(self.temp_dir.name)
        self.cache_dir = self.test_root / "cache"
        self.game_dir = self.test_root / "game"
        self.wad_dir = self.game_dir / "DATA" / "FINAL" / "Champions"
        self.wad_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        self.temp_dir.cleanup()

    def _create_champion_wad(self, alias: str, char_name: str, skin_count: int = 5) -> Path:
        wad_path = self.wad_dir / f"{alias}.wad.client"
        empty_header = b"RW\x03\x00" + bytes(268)
        mw = ModWad(empty_header)
        base_bin_data = f"BASE_SKIN_PROP_BIN_{alias}".encode()

        mw.put(path_hash(f"data/characters/{char_name}/skins/skin0.bin"), base_bin_data)
        for i in range(1, skin_count + 1):
            mw.put(path_hash(f"data/characters/{char_name}/skins/skin{i}.bin"), f"PAID_SKIN_{alias}_{i}".encode())

        wad_path.write_bytes(mw.to_bytes())
        return wad_path

    def test_full_competitive_pipeline_draft_enemy_only(self):
        # 1. Setup mock champion WADs for player (Aatrox 266), enemy 1 (Ahri 103), enemy 2 (Zed 238)
        self._create_champion_wad("Aatrox", "aatrox", skin_count=5)
        self._create_champion_wad("Ahri", "ahri", skin_count=8)
        self._create_champion_wad("Zed", "zed", skin_count=6)

        # 2. Verify queue eligibility
        draft_session = {
            "gameData": {"queue": {"id": 420}},  # Ranked Solo/Duo
            "myTeam": [{"cellId": 0, "championId": 266}],
            "theirTeam": [
                {"cellId": 5, "championId": 103},
                {"cellId": 6, "championId": 238},
            ],
        }
        self.assertTrue(is_draft_mode(draft_session))

        # 3. Resolve targets
        targets = resolve_competitive_targets(
            mode="enemy_only",
            session=draft_session,
            my_champ_id=266,
            party_champ_ids=set(),
        )
        self.assertEqual(targets, {103, 238})
        self.assertNotIn(266, targets)  # Security invariant: player champ never targeted

        # 4. Generate/Cache override packages
        pkg_ahri = get_or_create_base_override(103, game_path=self.game_dir, cache_dir=self.cache_dir)
        pkg_zed = get_or_create_base_override(238, game_path=self.game_dir, cache_dir=self.cache_dir)

        self.assertIsNotNone(pkg_ahri)
        self.assertIsNotNone(pkg_zed)
        self.assertTrue(pkg_ahri.is_file())
        self.assertTrue(pkg_zed.is_file())

        # Verify Ahri's override maps all 8 skins to base skin bin
        with ModFiles(pkg_ahri) as mf:
            mw = ModWad(mf.read("WAD/Ahri.wad.client"))
            for i in range(1, 9):
                h = path_hash(f"data/characters/ahri/skins/skin{i}.bin")
                self.assertIn(h, mw)
                self.assertEqual(mw.get(h).data, b"BASE_SKIN_PROP_BIN_Ahri")

        # 5. Staging plan integration with InjectionTrigger
        state = SharedState()
        state.local_cell_id = 0
        state.locked_champ_id = 266
        state.competitive_mode = "enemy_only"
        state.competitive_supported = True

        mock_lcu = MagicMock()
        mock_lcu.session = draft_session

        mock_injector = MagicMock()
        mock_injector.game_dir = self.game_dir
        mock_injector.prepare_skin_mods.return_value = ["aatrox_skin_mod"]

        mock_injection_manager = MagicMock()
        mock_injection_manager.injector = mock_injector

        trigger = InjectionTrigger(
            lcu=mock_lcu,
            state=state,
            injection_manager=mock_injection_manager,
        )

        # Trigger staging for player's Blood Moon Aatrox (skin_266001)
        plan = trigger.staging_plan("skin_266001", cname="Aatrox")
        self.assertIsNotNone(plan)

        # Confirm player gets their chosen skin and opponents get base overrides
        skin_steps = [s for s in plan.steps if isinstance(s, SkinStep)]
        comp_steps = [s for s in plan.steps if isinstance(s, CompetitiveStep)]

        self.assertEqual(len(skin_steps), 1)
        self.assertEqual(skin_steps[0].skin_name, "skin_266001")

        self.assertEqual(len(comp_steps), 2)
        comp_champion_ids = {s.champion_id for s in comp_steps}
        self.assertEqual(comp_champion_ids, {103, 238})

        # 6. Physical staging into mock overlay target directory
        overlay_mods_dir = self.test_root / "overlay_mods"
        prepared_mods = prepare_plan(mock_injector, plan, overlay_mods_dir)

        self.assertIsNotNone(prepared_mods)
        # Should contain player skin mod + both competitive override mods
        self.assertIn("aatrox_skin_mod", prepared_mods)
        self.assertIn("base_override_103", prepared_mods)
        self.assertIn("base_override_238", prepared_mods)

        # Confirm linked archives exist on disk
        self.assertTrue((overlay_mods_dir / "base_override_103").exists())
        self.assertTrue((overlay_mods_dir / "base_override_238").exists())


if __name__ == "__main__":
    unittest.main()
