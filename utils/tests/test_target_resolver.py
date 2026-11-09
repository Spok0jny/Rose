#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest

from utils.competitive.target_resolver import resolve_competitive_targets


class TestTargetResolver(unittest.TestCase):
    def setUp(self):
        self.session = {
            "myTeam": [
                {"cellId": 0, "championId": 103},  # Ahri (me)
                {"cellId": 1, "championId": 64},   # Lee Sin (friend in party)
                {"cellId": 2, "championId": 222},  # Jinx (random ally)
                {"cellId": 3, "championId": 89},   # Leona (random ally)
                {"cellId": 4, "championId": 86},   # Garen (random ally)
            ],
            "theirTeam": [
                {"cellId": 5, "championId": 81},   # Ezreal
                {"cellId": 6, "championId": 22},   # Ashe
                {"cellId": 7, "championId": 53},   # Blitzcrank
                {"cellId": 8, "championId": 157},  # Yasuo
                {"cellId": 9, "championId": 412},  # Thresh
            ],
        }
        self.my_champ_id = 103
        self.party_champ_ids = {64}

    def test_mode_off_returns_empty_set(self):
        targets = resolve_competitive_targets("off", self.session, self.my_champ_id, self.party_champ_ids)
        self.assertEqual(targets, set())

    def test_mode_enemy_only_returns_enemies_and_strictly_excludes_self(self):
        targets = resolve_competitive_targets("enemy_only", self.session, self.my_champ_id, self.party_champ_ids)
        self.assertEqual(targets, {81, 22, 53, 157, 412})
        self.assertNotIn(self.my_champ_id, targets)

    def test_mode_enemy_only_even_if_self_id_in_enemy_list_is_discarded(self):
        # Edge case: mirror or buggy session where my_champ_id appears in theirTeam
        buggy_session = {
            "myTeam": [{"cellId": 0, "championId": 103}],
            "theirTeam": [{"cellId": 1, "championId": 103}, {"cellId": 2, "championId": 81}]
        }
        targets = resolve_competitive_targets("enemy_only", buggy_session, 103)
        self.assertEqual(targets, {81})
        self.assertNotIn(103, targets)

    def test_mode_all_except_party_excludes_self_and_party(self):
        targets = resolve_competitive_targets("all_except_party", self.session, self.my_champ_id, self.party_champ_ids)
        # Expected: all 5 enemies + 3 random allies (Jinx 222, Leona 89, Garen 86)
        expected = {81, 22, 53, 157, 412, 222, 89, 86}
        self.assertEqual(targets, expected)
        self.assertNotIn(self.my_champ_id, targets)
        self.assertNotIn(64, targets)  # Lee Sin in party

    def test_empty_session_returns_empty_set(self):
        self.assertEqual(resolve_competitive_targets("enemy_only", {}, self.my_champ_id), set())
        self.assertEqual(resolve_competitive_targets("all_except_party", None, self.my_champ_id), set())


if __name__ == "__main__":
    unittest.main()
