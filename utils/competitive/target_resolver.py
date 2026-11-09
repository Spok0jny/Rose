#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Competitive Mode target champion resolver."""

from typing import Any, Dict, Optional, Set


def resolve_competitive_targets(
    mode: str,
    session: Optional[Dict[str, Any]],
    my_champ_id: Optional[int],
    party_champ_ids: Optional[Set[int]] = None,
) -> Set[int]:
    """Resolve champion IDs that should have default base skins applied.

    Args:
        mode: Active competitive mode ('off', 'enemy_only', 'all_except_party')
        session: ChampSelect/Gameflow session payload
        my_champ_id: The local player's locked or hovered champion ID
        party_champ_ids: Set of champion IDs picked by friends in Rose Party Mode

    Returns:
        Set of champion IDs to override to base skin (strictly excluding my_champ_id).
    """
    if not mode or mode == "off" or not session or not isinstance(session, dict):
        return set()

    normalized_mode = mode.lower().strip()
    if normalized_mode not in ("enemy_only", "all_except_party"):
        return set()

    party_ids: Set[int] = set()
    if party_champ_ids:
        party_ids = {int(cid) for cid in party_champ_ids if cid}

    their_team = session.get("theirTeam") or []
    my_team = session.get("myTeam") or []

    def _extract_cids(players: list) -> Set[int]:
        cids = set()
        for p in players:
            if isinstance(p, dict):
                cid = p.get("championId")
                if cid:
                    try:
                        cid_int = int(cid)
                        if cid_int > 0:
                            cids.add(cid_int)
                    except (ValueError, TypeError):
                        pass
        return cids

    enemy_cids = _extract_cids(their_team)

    if normalized_mode == "enemy_only":
        targets = enemy_cids
    elif normalized_mode == "all_except_party":
        ally_cids = _extract_cids(my_team)
        targets = (enemy_cids | ally_cids) - party_ids
    else:
        return set()

    # Hard security invariant: Never override the local player's own champion
    if my_champ_id:
        try:
            targets.discard(int(my_champ_id))
        except (ValueError, TypeError):
            pass

    return targets
