#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interactive Friend Simulator for Rose Party Mode
Tests token decoding, direct WebSocket connection, member join, and skin broadcasting
directly from the same machine without needing a second PC or LoL account.
"""

import asyncio
import json
import sys
from pathlib import Path

# Ensure Rose project root is on sys.path
sys.path.insert(0, str(Path(__file__).parent.absolute()))

import websockets
from party.protocol.token_codec import PartyToken


async def main():
    print("=" * 65)
    print("   ROSE PARTY MODE - SYMULATOR ZNAJOMEGO (TEST NA 1 PC)")
    print("=" * 65)
    print()
    print("Ten skrypt udaje drugiego gracza (Twojego kumpla).")
    print("Wklej swoj token wygenerowany w Rose lub wcisnij Enter, aby")
    print("polaczyc sie domyslnie pod ws://127.0.0.1:7865.")
    print()

    token_input = input("Wklej token ROSE:... (albo wcisnij Enter dla 127.0.0.1): ").strip()

    host_ip = "127.0.0.1"
    host_port = 7865
    friend_name = "ZiomekTestowy"
    friend_id = 999123456

    if token_input:
        try:
            token = PartyToken.decode(token_input)
            print(f"\n[OK] Rozkodowano token v{token.version}!")
            print(f"     Host IP:   {token.host_ip or '127.0.0.1'}")
            print(f"     Host Port: {token.host_port}")
            print(f"     Host Summoner ID: {token.summoner_id}")
            if token.host_ip:
                host_ip = token.host_ip
            host_port = token.host_port
        except Exception as e:
            print(f"\n[BLAD] Nie udalo sie rozkodowac tokenu: {e}")
            print("Uzywam domyslnego adresu 127.0.0.1:7865...")

    url = f"ws://{host_ip}:{host_port}"
    print(f"\n[>>] Laczenie do Twojego Rose pod adresem: {url} ...")

    try:
        ws = await websockets.connect(url, max_size=65536)
    except Exception as e:
        print(f"\n[BLAD] Nie mozna polaczyc sie z {url}!")
        print(f"Szczegoly: {e}")
        print("\nUpewnij sie, ze Party Mode w Rose jest WLACZONE (przycisk 'Enable Party Mode').")
        input("\nWcisnij Enter, aby zakonczyc...")
        return

    print(f"[OK] Polaczono pomyslnie z serwerem Party Mode!")

    # Dolacz do pokoju
    join_payload = {
        "type": "join",
        "summoner_id": friend_id,
        "summoner_name": friend_name,
    }
    await ws.send(json.dumps(join_payload))
    print(f"[OK] Wyslano dolaczenie jako gracz '{friend_name}' (ID: {friend_id})")
    print("\n>>> SPOJRZ TERAZ NA OKIENKO PARTY MODE W KLIENCIE LOLA! <<<")
    print("Licznik znajomych powinien zmienic sie na: CONNECTED FRIENDS (1)")
    print(f"Na liscie powinien pojawic sie: {friend_name}\n")

    # Zadanie nasluchiwania odpowiedzi w tle
    async def listen_loop():
        try:
            async for message in ws:
                data = json.loads(message)
                if data.get("type") == "members":
                    members = data.get("members", [])
                    names = [m.get("summoner_name") for m in members]
                    print(f"\n[SERWER] Aktualna lista graczy w pokoju ({len(members)}): {names}")
        except Exception:
            pass

    listener_task = asyncio.create_task(listen_loop())

    # Menu interaktywne
    skins = [
        {"name": "Spirit Blossom Ahri", "champion_id": 103, "skin_id": 103027},
        {"name": "PROJECT: Vayne", "champion_id": 67, "skin_id": 67011},
        {"name": "Star Guardian Jinx", "champion_id": 222, "skin_id": 222004},
        {"name": "God-King Darius", "champion_id": 122, "skin_id": 122014},
    ]

    print("-" * 65)
    print("Opcje testowe:")
    for idx, s in enumerate(skins, 1):
        print(f"  [{idx}] Ustaw skin znajomego: {s['name']}")
    print("  [q] Rozlacz znajomego i zakoncz test")
    print("-" * 65)

    loop = asyncio.get_running_loop()

    while True:
        try:
            choice = await loop.run_in_executor(None, input, "\nWybierz opcje (1-4 lub q): ")
            choice = choice.strip().lower()

            if choice == "q":
                print("\nRozlaczanie...")
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
                print(f"[OK] Wyslano wybor skina: {selected['name']} (ID: {selected['skin_id']})")
                print("Sprawdz w kliencie LoL czy pojawila sie informacja o skinie!")
            else:
                print("Niepoprawny wybor.")
        except (KeyboardInterrupt, EOFError):
            break

    listener_task.cancel()
    await ws.close()
    print("[OK] Rozlaczono. W LoLu licznik znajomych powinien wrocic do (0).")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nPrzerwano.")
