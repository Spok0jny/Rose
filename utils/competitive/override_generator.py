#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Competitive Mode base skin override generator and cache storage.

Generates lightweight base-skin overrides by aliasing skinN.bin -> skin0.bin
using PropBin structures inside a ModWad packaged as a .fantome archive.
"""

from __future__ import annotations

import json
import uuid
import zipfile
from pathlib import Path
from typing import Dict, Optional

from config import get_config_option
from injection.baseskin.package import character_names
from injection.baseskin.wad import GameWad, ModWad, path_hash
from utils.core.logging import get_logger
from utils.core.paths import get_user_data_dir

log = get_logger()

# Complete mapping of League of Legends Champion IDs to canonical aliases
CHAMPION_ID_TO_ALIAS: Dict[int, str] = {
    1: "Annie", 2: "Olaf", 3: "Galio", 4: "TwistedFate", 5: "XinZhao",
    6: "Urgot", 7: "Leblanc", 8: "Vladimir", 9: "Fiddlesticks", 10: "Kayle",
    11: "MasterYi", 12: "Alistar", 13: "Ryze", 14: "Sion", 15: "Sivir",
    16: "Soraka", 17: "Teemo", 18: "Tristana", 19: "Warwick", 20: "Nunu",
    21: "MissFortune", 22: "Ashe", 23: "Tryndamere", 24: "Jax", 25: "Morgana",
    26: "Zilean", 27: "Singed", 28: "Evelynn", 29: "Twitch", 30: "Karthus",
    31: "Chogath", 32: "Amumu", 33: "Rammus", 34: "Anivia", 35: "Shaco",
    36: "DrMundo", 37: "Sona", 38: "Kassadin", 39: "Irelia", 40: "Janna",
    41: "Gangplank", 42: "Corki", 43: "Karma", 44: "Taric", 45: "Veigar",
    48: "Trundle", 50: "Swain", 51: "Caitlyn", 53: "Blitzcrank", 54: "Malphite",
    55: "Katarina", 56: "Nocturne", 57: "Maokai", 58: "Renekton", 59: "JarvanIV",
    60: "Elise", 61: "Orianna", 62: "MonkeyKing", 63: "Brand", 64: "LeeSin",
    67: "Vayne", 68: "Rumble", 69: "Cassiopeia", 72: "Skarner", 74: "Heimerdinger",
    75: "Nasus", 76: "Nidalee", 77: "Udyr", 78: "Poppy", 79: "Gragas",
    80: "Pantheon", 81: "Ezreal", 82: "Mordekaiser", 83: "Yorick", 84: "Akali",
    85: "Kennen", 86: "Garen", 89: "Leona", 90: "Malzahar", 91: "Talon",
    92: "Riven", 96: "KogMaw", 98: "Shen", 99: "Lux", 101: "Xerath",
    102: "Shyvana", 103: "Ahri", 104: "Graves", 105: "Fizz", 106: "Volibear",
    107: "Rengar", 110: "Varus", 111: "Nautilus", 112: "Viktor", 113: "Sejuani",
    114: "Fiora", 115: "Ziggs", 117: "Lulu", 119: "Draven", 120: "Hecarim",
    121: "Khazix", 122: "Darius", 126: "Jayce", 127: "Lissandra", 131: "Diana",
    133: "Quinn", 134: "Syndra", 136: "AurelionSol", 141: "Kayn", 142: "Zoe",
    143: "Zyra", 145: "Kaisa", 147: "Seraphine", 150: "Gnar", 154: "Zac",
    157: "Yasuo", 161: "Velkoz", 163: "Taliyah", 164: "Camille", 166: "Akshan",
    200: "Belveth", 201: "Braum", 202: "Jhin", 203: "Kindred", 221: "Zeri",
    222: "Jinx", 223: "TahmKench", 233: "Briar", 234: "Viego", 235: "Senna",
    236: "Lucian", 238: "Zed", 240: "Kled", 245: "Ekko", 246: "Qiyana",
    254: "Vi", 266: "Aatrox", 267: "Nami", 268: "Azir", 350: "Yuumi",
    360: "Samira", 412: "Thresh", 420: "Illaoi", 421: "RekSai", 427: "Ivern",
    429: "Kalista", 432: "Bard", 497: "Rakan", 498: "Xayah", 516: "Ornn",
    517: "Sylas", 518: "Neeko", 523: "Aphelios", 526: "Rell", 555: "Pyke",
    711: "Vex", 777: "Yone", 799: "Ambessa", 800: "Mel", 875: "Sett",
    876: "Lillia", 887: "Gwen", 888: "Renata", 893: "Aurora", 895: "Nilah",
    897: "KSante", 901: "Smolder", 902: "Milio", 910: "Hwei", 950: "Naafiri",
}


def get_champion_alias(champion_id: int, lcu_client: Optional[object] = None) -> Optional[str]:
    """Resolve champion ID to internal champion alias.

    Args:
        champion_id: The numeric champion ID.
        lcu_client: Optional LCU client for live query fallback.

    Returns:
        Canonical champion alias (e.g. 'Aatrox', 'MonkeyKing') or None.
    """
    try:
        cid = int(champion_id)
    except (TypeError, ValueError):
        return None

    alias = CHAMPION_ID_TO_ALIAS.get(cid)
    if alias:
        return alias

    if lcu_client and hasattr(lcu_client, "get"):
        try:
            data = lcu_client.get(f"/lol-game-data/assets/v1/champions/{cid}.json", timeout=1.0)
            if isinstance(data, dict):
                live_alias = data.get("alias")
                if live_alias:
                    return str(live_alias)
        except Exception as e:
            log.debug(f"[COMPETITIVE] Failed to resolve champion {cid} via LCU: {e}")

    return None


def get_competitive_cache_dir(custom_base: Optional[Path] = None) -> Path:
    """Return and create the directory used for competitive override packages."""
    if custom_base is not None:
        cache_dir = Path(custom_base)
    else:
        cache_dir = get_user_data_dir() / "competitive_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def find_champion_wad(game_path: Path, alias: str) -> Optional[Path]:
    """Find the main .wad.client file for a champion within League's game folder."""
    game_path = Path(game_path)
    candidate_dirs = [
        game_path / "DATA" / "FINAL" / "Champions",
        game_path / "Game" / "DATA" / "FINAL" / "Champions",
    ]

    for cdir in candidate_dirs:
        if not cdir.is_dir():
            continue
        exact = cdir / f"{alias}.wad.client"
        if exact.is_file():
            return exact
        alias_lower = f"{alias.lower()}.wad.client"
        for entry in cdir.iterdir():
            if entry.is_file() and entry.name.lower() == alias_lower:
                return entry

    return None


def create_base_override(
    champion_id: int,
    game_path: Optional[Path] = None,
    cache_dir: Optional[Path] = None,
    lcu_client: Optional[object] = None,
) -> Optional[Path]:
    """Extract skin0.bin from champion's WAD and package base skin override .fantome.

    Args:
        champion_id: Champion numeric ID.
        game_path: League game folder (defaults to config General.game_path).
        cache_dir: Directory to save generated package.
        lcu_client: Optional LCU client.

    Returns:
        Path to generated .fantome package, or None on failure.
    """
    alias = get_champion_alias(champion_id, lcu_client=lcu_client)
    if not alias:
        log.warning(f"[COMPETITIVE] Unknown champion ID {champion_id}, cannot create base override")
        return None

    if game_path is None:
        raw_path = get_config_option("General", "game_path", r"C:\Riot Games\League of Legends\Game")
        game_path = Path(raw_path) if raw_path else Path(r"C:\Riot Games\League of Legends\Game")

    wad_path = find_champion_wad(game_path, alias)
    if not wad_path or not wad_path.is_file():
        log.warning(f"[COMPETITIVE] WAD for champion '{alias}' not found in {game_path}")
        return None

    target_cache_dir = get_competitive_cache_dir(cache_dir)
    dest_path = target_cache_dir / f"base_override_{champion_id}.fantome"

    try:
        game_wad = GameWad(wad_path)
        empty_header = b"RW\x03\x00" + bytes(268)
        mod_wad = ModWad(empty_header)

        characters = character_names(alias)
        mapped_count = 0

        for char in characters:
            p0 = f"data/characters/{char}/skins/skin0.bin"
            if not game_wad.has_path(p0):
                p0 = f"assets/characters/{char}/skins/skin0.bin"
            if not game_wad.has_path(p0):
                continue

            skin0_data = game_wad.read_path(p0)
            if not skin0_data:
                continue

            for skin_idx in range(1, 150):
                pn = f"data/characters/{char}/skins/skin{skin_idx}.bin"
                if game_wad.has_path(pn):
                    mod_wad.put(path_hash(pn), skin0_data)
                    mapped_count += 1
                else:
                    pn_assets = f"assets/characters/{char}/skins/skin{skin_idx}.bin"
                    if game_wad.has_path(pn_assets):
                        mod_wad.put(path_hash(pn_assets), skin0_data)
                        mapped_count += 1

        if mapped_count == 0:
            log.warning(f"[COMPETITIVE] No valid skin bins found to override for {alias}")
            return None

        # Package into .fantome archive
        temp_path = dest_path.with_name(f"{dest_path.stem}_{uuid.uuid4().hex[:8]}.tmp")
        with zipfile.ZipFile(temp_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=1) as zf:
            info = {
                "Author": "ROSE",
                "Description": f"Competitive Mode Base Skin Override for {alias}",
                "Name": f"ROSE - Base {alias}",
                "Version": "1.0.0",
            }
            meta_json = json.dumps(info, indent=2, ensure_ascii=False)
            zf.writestr("META/info.json", meta_json)
            zf.writestr("metadata.json", meta_json)
            # Store WAD uncompressed (ZIP_STORED) for direct seekability
            zf.writestr(f"WAD/{wad_path.name}", mod_wad.to_bytes(), compress_type=zipfile.ZIP_STORED)

        temp_path.replace(dest_path)
        log.info(f"[COMPETITIVE] Created base skin override for {alias} ({mapped_count} skins mapped) -> {dest_path.name}")
        return dest_path

    except Exception as e:
        log.warning(f"[COMPETITIVE] Failed creating base override for {alias} (ID {champion_id}): {e}")
        return None


def get_or_create_base_override(
    champion_id: int,
    game_path: Optional[Path] = None,
    cache_dir: Optional[Path] = None,
    lcu_client: Optional[object] = None,
) -> Optional[Path]:
    """Retrieve cached base skin override package or generate if missing/stale.

    Args:
        champion_id: Champion numeric ID.
        game_path: League game folder.
        cache_dir: Storage directory.
        lcu_client: Optional LCU client.

    Returns:
        Path to .fantome package or None on error.
    """
    target_cache_dir = get_competitive_cache_dir(cache_dir)
    dest_path = target_cache_dir / f"base_override_{champion_id}.fantome"

    # Check if cached package already exists
    if dest_path.is_file():
        alias = get_champion_alias(champion_id, lcu_client=lcu_client)
        if alias:
            if game_path is None:
                raw_path = get_config_option("General", "game_path", r"C:\Riot Games\League of Legends\Game")
                game_path = Path(raw_path) if raw_path else Path(r"C:\Riot Games\League of Legends\Game")
            wad_path = find_champion_wad(game_path, alias)
            if wad_path and wad_path.is_file():
                if dest_path.stat().st_mtime >= wad_path.stat().st_mtime:
                    return dest_path
                log.info(f"[COMPETITIVE] Cache for {alias} is older than game WAD, regenerating...")

    return create_base_override(
        champion_id=champion_id,
        game_path=game_path,
        cache_dir=cache_dir,
        lcu_client=lcu_client,
    )
