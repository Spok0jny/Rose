#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest
from unittest.mock import patch

import config
from state.core.shared_state import SharedState


class TestCompetitiveConfig(unittest.TestCase):
    def test_default_competitive_mode_is_off(self):
        state = SharedState()
        self.assertEqual(state.competitive_mode, "off")
        self.assertFalse(state.competitive_supported)

    def test_get_and_set_competitive_mode(self):
        with patch("config.get_config_option", return_value="enemy_only"):
            mode = config.get_competitive_mode()
            self.assertEqual(mode, "enemy_only")

        with patch("config.get_config_option", return_value="invalid_mode"):
            mode = config.get_competitive_mode()
            self.assertEqual(mode, "off")

        with patch("config.set_config_option") as mock_set:
            config.set_competitive_mode("all_except_party")
            mock_set.assert_called_once_with("Competitive", "mode", "all_except_party")

    def test_set_invalid_competitive_mode_raises_or_defaults(self):
        with patch("config.set_config_option") as mock_set:
            config.set_competitive_mode("bogus")
            mock_set.assert_called_once_with("Competitive", "mode", "off")


if __name__ == "__main__":
    unittest.main()
