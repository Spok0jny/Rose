#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interactive Friend Simulator for Rose Party Mode
Tests token decoding, direct WebSocket connection, member join, and skin broadcasting
directly from the same machine without needing a second PC or LoL account.
"""

import asyncio
import json
import random
import sys
from pathlib import Path

# Ensure Rose project root is on sys.path
sys.path.insert(0, str(Path(__file__).parent.absolute()))

import websockets
from party.protocol.token_codec import PartyToken


async def main():
    print("=" * 65)
    print("   ROSE PARTY MODE - FRIEND SIMULATOR (DEV TEST TOOL)")
    print("=" * 65)
    print()
    print("This script simulates a connecting party member (peer).")
    print("Paste your Rose party token, or press Enter to connect")
    print("directly via ws://127.0.0.1:7865.")
    print()

    token_input = input("Paste token ROSE:... (or press Enter for localhost): ").strip()

    host_ip = "127.0.0.1"
    host_port = 7865
    rand_num = random.randint(1, 99)
    friend_name = f"FriendBot_{rand_num}"
    friend_id = 999000000 + rand_num

    if token_input:
        try:
            token = PartyToken.decode(token_input)
            print(f"\n[OK] Decoded token v{token.version}!")
            print(f"     Host IP:   {token.host_ip or '127.0.0.1'}")
            print(f"     Host Port: {token.host_port}")
            print(f"     Host Summoner ID: {token.summoner_id}")
            if token.host_ip:
                host_ip = token.host_ip
            host_port = token.host_port
        except Exception as e:
            print(f"\n[WARN] Failed to decode token: {e}")
            print("Falling back to default 127.0.0.1:7865...")

    url = f"ws://{host_ip}:{host_port}"
    print(f"\n[>>] Connecting to Rose at: {url} ...")

    try:
        ws = await websockets.connect(url, max_size=65536)
    except Exception as e:
        print(f"\n[ERROR] Could not connect to {url}!")
        print(f"Details: {e}")
        print("\nMake sure Party Mode is enabled in Rose before connecting.")
        input("\nPress Enter to exit...")
        return

    print(f"[OK] Successfully connected to Party Mode server!")

    # Join room
    join_payload = {
        "type": "join",
        "summoner_id": friend_id,
        "summoner_name": friend_name,
    }
    await ws.send(json.dumps(join_payload))
    print(f"[OK] Joined room as '{friend_name}' (ID: {friend_id})")
    print("\n>>> Check Party Mode in League Client! <<<")
    print(f"Peer '{friend_name}' should now appear under Connected Friends.\n")

    # Background listener for room updates
    async def listen_loop():
        try:
            async for message in ws:
                data = json.loads(message)
                if data.get("type") == "members":
                    members = data.get("members", [])
                    names = [m.get("summoner_name") for m in members]
                    print(f"\n[SERVER] Active room members ({len(members)}): {names}")
        except Exception:
            pass

    listener_task = asyncio.create_task(listen_loop())

    # Interactive test menu
    skins = [
        {"name": "Spirit Blossom Ahri", "champion_id": 103, "skin_id": 103027},
        {"name": "PROJECT: Vayne", "champion_id": 67, "skin_id": 67011},
        {"name": "Star Guardian Jinx", "champion_id": 222, "skin_id": 222004},
        {"name": "God-King Darius", "champion_id": 122, "skin_id": 122015},
    ]

    print("-" * 65)
    print("Test Options:")
    for idx, s in enumerate(skins, 1):
        print(f"  [{idx}] Set peer skin: {s['name']}")
    print("  [q] Disconnect peer and exit")
    print("-" * 65)

    loop = asyncio.get_running_loop()

    while True:
        try:
            choice = await loop.run_in_executor(None, input, "\nSelect option (1-4 or q): ")
            choice = choice.strip().lower()

            if choice == "q":
                print("\nDisconnecting...")
                break

            if choice in ("1", "2", "3", "4"):
                selected = skins[int(choice) - 1]
                skin_payload = {
                    "type": "skin",
                    "skin": {
                        "champion_id": selected["champion_id"],
                        "skin_id": selected["skin_id"],
                    }
                }
                await ws.send(json.dumps(skin_payload))
                print(f"[OK] Broadcast skin selection: {selected['name']} (ID: {selected['skin_id']})")
            else:
                print("Invalid choice.")
        except (KeyboardInterrupt, EOFError):
            break

    listener_task.cancel()
    await ws.close()
    print("[OK] Disconnected.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nInterrupted.")
