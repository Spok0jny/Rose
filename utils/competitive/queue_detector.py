#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Queue eligibility detector for Competitive Mode."""

from typing import Any, Dict, Optional, Union

# Supported draft queues:
# 400: 5v5 Draft Pick (Normal)
# 420: 5v5 Ranked Solo/Duo
# 440: 5v5 Ranked Flex
# 700: Clash
# 3110: Custom Game (Draft Mode)
# 3130: Custom Game (Tournament Draft)
DRAFT_QUEUE_IDS = {400, 420, 440, 700, 3110, 3130}


def is_draft_mode(session: Optional[Union[Dict[str, Any], int]] = None, queue_id: Optional[int] = None) -> bool:
    """Determine whether the current LCU session or queue ID represents a draft queue."""
    if queue_id is not None:
        try:
            if int(queue_id) in DRAFT_QUEUE_IDS:
                return True
        except (ValueError, TypeError):
            pass

    if isinstance(session, int):
        return session in DRAFT_QUEUE_IDS

    if not session or not isinstance(session, dict):
        return False

    # Check session directly for queueId or queue.id (e.g. gameflow / champ-select payloads)
    direct_qid = session.get("queueId")
    if direct_qid is None and isinstance(session.get("queue"), dict):
        direct_qid = session["queue"].get("id") or session["queue"].get("queueId")

    if direct_qid is not None:
        try:
            if int(direct_qid) in DRAFT_QUEUE_IDS:
                return True
        except (ValueError, TypeError):
            pass

    game_data = session.get("gameData")
    if isinstance(game_data, dict):
        queue = game_data.get("queue") or {}
        g_queue_id = queue.get("id") or queue.get("queueId") or game_data.get("queueId")
        if g_queue_id is not None:
            try:
                if int(g_queue_id) in DRAFT_QUEUE_IDS:
                    return True
            except (ValueError, TypeError):
                pass

        # Check for custom tournament draft / draft mode
        if game_data.get("isCustomGame"):
            mutators = game_data.get("mutators") or {}
            if mutators.get("tournamentDraft") or mutators.get("draftMode"):
                return True

    return False
