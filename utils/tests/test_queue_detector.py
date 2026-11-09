#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest

from utils.competitive.queue_detector import is_draft_mode, DRAFT_QUEUE_IDS


class TestQueueDetector(unittest.TestCase):
    def test_known_draft_queues(self):
        for qid in (400, 420, 440, 700):
            session = {"gameData": {"queue": {"id": qid}}}
            self.assertTrue(is_draft_mode(session), f"Queue {qid} should be draft")

    def test_custom_tournament_draft(self):
        session = {
            "gameData": {
                "isCustomGame": True,
                "queue": {"id": 0},
                "gameMode": "CLASSIC",
                "mutators": {"tournamentDraft": True}
            }
        }
        self.assertTrue(is_draft_mode(session))

    def test_unsupported_queues(self):
        for qid in (430, 450, 490, 1700, 830, 840, 850):
            session = {"gameData": {"queue": {"id": qid}}}
            self.assertFalse(is_draft_mode(session), f"Queue {qid} should not be draft")

    def test_empty_or_malformed_session(self):
        self.assertFalse(is_draft_mode({}))
        self.assertFalse(is_draft_mode(None))
        self.assertFalse(is_draft_mode({"gameData": None}))


if __name__ == "__main__":
    unittest.main()
