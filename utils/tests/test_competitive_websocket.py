#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unit tests for competitive mode WebSocket messaging and broadcaster."""

import json
import unittest
from unittest.mock import MagicMock, patch

from pengu.communication.broadcaster import Broadcaster
from pengu.communication.message_handler import MessageHandler
from state.core.shared_state import SharedState


class TestCompetitiveWebSocket(unittest.TestCase):
    """Test message handler and broadcaster for competitive mode."""

    def setUp(self):
        self.state = SharedState()
        self.state.competitive_mode = "off"
        self.state.competitive_supported = True

        self.mock_ws_server = MagicMock()
        self.mock_ws_server.loop = MagicMock()
        self.mock_ws_server.connections = {MagicMock()}

        self.broadcaster = Broadcaster(
            websocket_server=self.mock_ws_server,
            shared_state=self.state,
            skin_mapping=MagicMock(),
        )

        self.mock_broadcaster = MagicMock()
        self.handler = MessageHandler(
            shared_state=self.state,
            websocket_server=self.mock_ws_server,
            broadcaster=self.mock_broadcaster,
            skin_processor=MagicMock(),
            flow_controller=MagicMock(),
        )

    @patch("config.set_competitive_mode")
    def test_handle_update_competitive_mode_valid(self, mock_set_config):
        msg = json.dumps({"type": "update-competitive-mode", "mode": "enemy_only"})
        self.handler.handle_message(msg)

        self.assertEqual(self.state.competitive_mode, "enemy_only")
        mock_set_config.assert_called_once_with("enemy_only")
        self.mock_broadcaster.broadcast_competitive_state.assert_called_once_with(
            mode="enemy_only",
            supported=True,
        )

    @patch("config.set_competitive_mode")
    def test_handle_update_competitive_mode_underscore_type(self, mock_set_config):
        msg = json.dumps({"type": "update_competitive_mode", "mode": "all_except_party"})
        self.handler.handle_message(msg)

        self.assertEqual(self.state.competitive_mode, "all_except_party")
        mock_set_config.assert_called_once_with("all_except_party")

    @patch("config.set_competitive_mode")
    def test_handle_update_competitive_mode_invalid_ignored(self, mock_set_config):
        msg = json.dumps({"type": "update-competitive-mode", "mode": "god_mode"})
        self.handler.handle_message(msg)

        self.assertEqual(self.state.competitive_mode, "off")
        mock_set_config.assert_not_called()
        self.mock_broadcaster.broadcast_competitive_state.assert_not_called()

    def test_handle_request_competitive_state(self):
        self.state.competitive_mode = "enemy_only"
        self.state.competitive_supported = True

        msg = json.dumps({"type": "request-competitive-state"})
        self.handler.handle_message(msg)

        self.mock_broadcaster.broadcast_competitive_state.assert_called_once_with(
            mode="enemy_only",
            supported=True,
        )

    def test_broadcast_competitive_state_payload(self):
        with patch.object(self.broadcaster, "_send_message") as mock_send:
            self.broadcaster.broadcast_competitive_state(mode="all_except_party", supported=True)

            mock_send.assert_called_once()
            raw_json = mock_send.call_args[0][0]
            payload = json.loads(raw_json)

            self.assertEqual(payload.get("type"), "competitive-state")
            self.assertEqual(payload.get("mode"), "all_except_party")
            self.assertTrue(payload.get("supported"))


if __name__ == "__main__":
    unittest.main()
