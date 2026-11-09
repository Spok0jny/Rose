#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Competitive Mode injection hook.

Integrates competitive base skin overrides with injector mod preparation.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from injection.mods.mod_manager import ModManager
from utils.core.junction import is_junction
from utils.core.logging import get_logger

from .override_generator import get_or_create_base_override
from .target_resolver import resolve_competitive_targets

log = get_logger()


def prepare_competitive_mods(
    state,
    injector,
    mods_dir: Optional[Path] = None,
    lcu_client: Optional[object] = None,
) -> List[str]:
    """Prepare base skin override packages in *mods_dir* (injector.mods_dir by default).

    Args:
        state: SharedState instance.
        injector: SkinInjector instance.
        mods_dir: Destination mods directory.
        lcu_client: Optional LCU client.

    Returns:
        List of prepared mod folder names.
    """
    mode = getattr(state, "competitive_mode", "off")
    supported = getattr(state, "competitive_supported", False)
    if mode == "off" or not supported:
        return []

    lcu = lcu_client or getattr(state, "lcu", None)
    session = getattr(lcu, "session", None) if lcu else None

    target_ids = set()
    if session:
        my_champ = getattr(state, "locked_champ_id", None) or getattr(state, "hovered_champ_id", None)

        party_champ_ids = set()
        party_manager = getattr(state, "party_manager", None)
        if party_manager and getattr(party_manager, "enabled", False):
            try:
                party_champ_ids = {s.champion_id for s in party_manager.get_party_skins()}
            except Exception:
                pass

        target_ids = resolve_competitive_targets(
            mode=mode,
            session=session,
            my_champ_id=my_champ,
            party_champ_ids=party_champ_ids,
        )

    target_mods_dir = Path(mods_dir) if mods_dir is not None else injector.mods_dir
    mod_manager = ModManager(target_mods_dir)
    prepared_names: List[str] = []

    game_path = getattr(injector, "game_dir", None)
    packages_to_link: List[Path] = []

    if target_ids:
        for target_id in sorted(target_ids):
            pkg = get_or_create_base_override(
                target_id,
                game_path=game_path,
                lcu_client=lcu,
            )
            if pkg and pkg.is_file():
                packages_to_link.append(pkg)
        try:
            state.competitive_override_packages = list(packages_to_link)
        except Exception:
            pass
    else:
        # Fallback to cached packages planned during countdown/staging if session is unavailable
        cached_packages = getattr(state, "competitive_override_packages", None)
        if cached_packages:
            packages_to_link = [Path(p) for p in cached_packages if p and Path(p).is_file()]

    for pkg in packages_to_link:
        folder = mod_manager.link_archive(pkg)
        if folder and (folder.exists() or is_junction(folder)):
            prepared_names.append(folder.name)

    return prepared_names
