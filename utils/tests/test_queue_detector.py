#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest

from utils.competitive.queue_detector import is_draft_mode, DRAFT_QUEUE_IDS


class TestQueueDetector(unittest.TestCase):
    def test_known_draft_queues(self):
        for qid in (400, 420, 440, 700, 3110, 3130):
            session = {"gameData": {"queue": {"id": qid}}}
            self.assertTrue(is_draft_mode(session), f"Queue {qid} should be draft")

    def test_direct_queue_id(self):
        self.assertTrue(is_draft_mode(queue_id=420))
        self.assertTrue(is_draft_mode(queue_id=3110))
        self.assertTrue(is_draft_mode(queue_id=3130))
        self.assertTrue(is_draft_mode(3110))
        self.assertFalse(is_draft_mode(queue_id=430))
        self.assertFalse(is_draft_mode(queue_id=3100))

    def test_direct_session_queue_id(self):
        self.assertTrue(is_draft_mode({"queueId": 3110}))
        self.assertTrue(is_draft_mode({"queue": {"id": 3130}}))
        self.assertFalse(is_draft_mode({"queueId": 3100}))

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
        for qid in (430, 450, 490, 1700, 830, 840, 850, 3100):
            session = {"gameData": {"queue": {"id": qid}}}
            self.assertFalse(is_draft_mode(session), f"Queue {qid} should not be draft")

    def test_empty_or_malformed_session(self):
        self.assertFalse(is_draft_mode({}))
        self.assertFalse(is_draft_mode(None))
        self.assertFalse(is_draft_mode({"gameData": None}))


if __name__ == "__main__":
    unittest.main()
