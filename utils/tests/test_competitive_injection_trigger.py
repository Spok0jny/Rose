#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unit tests for competitive mode injection trigger and stage plan integration."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from injection.core.stage_plan import (
    PARTY_SKINS_LABEL,
    CompetitiveStep,
    SkinStep,
    StagePlan,
    prepare_plan,
)
from state.core.shared_state import SharedState
from threads.handlers.injection_trigger import InjectionTrigger


class TestCompetitiveInjectionTrigger(unittest.TestCase):
    """Test injection trigger staging and plan generation with competitive overrides."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_root = Path(self.temp_dir.name)
        self.fake_override_path = self.test_root / "base_override_103.fantome"
        self.fake_override_path.write_text("MOCK FANTOME")

        self.state = SharedState()
        self.state.local_cell_id = 0
        self.state.locked_champ_id = 266  # Aatrox
        self.state.competitive_mode = "enemy_only"
        self.state.competitive_supported = True

        self.mock_lcu = MagicMock()
        self.mock_lcu.session = {
            "myTeam": [{"cellId": 0, "championId": 266}],
            "theirTeam": [{"cellId": 5, "championId": 103}],  # Ahri
        }

        self.mock_injection_manager = MagicMock()
        self.mock_injection_manager.injector = MagicMock()
        self.mock_injection_manager.injector.game_dir = Path("C:/FakeGame")

        self.trigger = InjectionTrigger(
            lcu=self.mock_lcu,
            state=self.state,
            injection_manager=self.mock_injection_manager,
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    @patch("utils.competitive.override_generator.get_or_create_base_override")
    def test_staging_plan_includes_competitive_overrides(self, mock_get_override):
        mock_get_override.return_value = self.fake_override_path

        # Player picks Blood Moon Aatrox (skin ID 266001)
        plan = self.trigger.staging_plan("skin_266001", cname="Aatrox")

        self.assertIsNotNone(plan)
        # Should have SkinStep for Aatrox
        skin_steps = [s for s in plan.steps if isinstance(s, SkinStep)]
        self.assertEqual(len(skin_steps), 1)
        self.assertEqual(skin_steps[0].skin_name, "skin_266001")

        # Should have CompetitiveStep for Ahri (103), strictly NOT for Aatrox (266)
        comp_steps = [s for s in plan.steps if isinstance(s, CompetitiveStep)]
        self.assertEqual(len(comp_steps), 1)
        self.assertEqual(comp_steps[0].champion_id, 103)
        self.assertEqual(comp_steps[0].package_path, self.fake_override_path)

    @patch("utils.competitive.override_generator.get_or_create_base_override")
    def test_staging_plan_omits_competitive_when_mode_off(self, mock_get_override):
        self.state.competitive_mode = "off"
        plan = self.trigger.staging_plan("skin_266001", cname="Aatrox")

        self.assertIsNotNone(plan)
        comp_steps = [s for s in plan.steps if isinstance(s, CompetitiveStep)]
        self.assertEqual(len(comp_steps), 0)
        mock_get_override.assert_not_called()

    @patch("utils.competitive.override_generator.get_or_create_base_override")
    def test_staging_plan_omits_competitive_when_unsupported(self, mock_get_override):
        self.state.competitive_supported = False
        plan = self.trigger.staging_plan("skin_266001", cname="Aatrox")

        self.assertIsNotNone(plan)
        comp_steps = [s for s in plan.steps if isinstance(s, CompetitiveStep)]
        self.assertEqual(len(comp_steps), 0)
        mock_get_override.assert_not_called()

    @patch("utils.competitive.override_generator.get_or_create_base_override")
    def test_staging_plan_default_skin_with_competitive_returns_plan(self, mock_get_override):
        mock_get_override.return_value = self.fake_override_path

        # Player picks default base skin (skin_266000)
        plan = self.trigger.staging_plan("skin_266000", cname="Aatrox")

        self.assertIsNotNone(plan)
        self.assertEqual(plan.label, PARTY_SKINS_LABEL)
        comp_steps = [s for s in plan.steps if isinstance(s, CompetitiveStep)]
        self.assertEqual(len(comp_steps), 1)
        self.assertEqual(comp_steps[0].champion_id, 103)

    def test_prepare_plan_links_competitive_packages(self):
        with tempfile.TemporaryDirectory() as td:
            target_dir = Path(td)
            fake_pkg = target_dir / "base_override_103.fantome"
            fake_pkg.write_text("FAKE FANTOME CONTENT")

            plan = StagePlan("test_plan", (CompetitiveStep(champion_id=103, package_path=fake_pkg),))
            injector = MagicMock()

            names = prepare_plan(injector, plan, target_dir)
            self.assertIsNotNone(names)
            self.assertEqual(len(names), 1)
            self.assertEqual(names[0], "base_override_103")


if __name__ == "__main__":
    unittest.main()
