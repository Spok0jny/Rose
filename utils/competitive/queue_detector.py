#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Queue eligibility detector for Competitive Mode."""

from typing import Any, Dict, Optional

# Supported draft queues:
# 400: 5v5 Draft Pick (Normal)
# 420: 5v5 Ranked Solo/Duo
# 440: 5v5 Ranked Flex
# 700: Clash
DRAFT_QUEUE_IDS = {400, 420, 440, 700}


def is_draft_mode(session: Optional[Dict[str, Any]]) -> bool:
    """Determine whether the current LCU session represents a draft queue."""
    if not session or not isinstance(session, dict):
        return False

    game_data = session.get("gameData")
    if not game_data or not isinstance(game_data, dict):
        return False

    queue = game_data.get("queue") or {}
    queue_id = queue.get("id") or queue.get("queueId")
    if queue_id is not None:
        try:
            if int(queue_id) in DRAFT_QUEUE_IDS:
                return True
        except (ValueError, TypeError):
            pass

    # Check for custom tournament draft
    if game_data.get("isCustomGame"):
        mutators = game_data.get("mutators") or {}
        if mutators.get("tournamentDraft") or mutators.get("draftMode"):
            return True

    return False
