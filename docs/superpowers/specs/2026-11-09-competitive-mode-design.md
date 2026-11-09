# Design Spec: Competitive Mode (Default Skin Interceptor)

## 1. Overview & Motivation
In competitive League of Legends (Ranked Solo/Duo, Flex, Clash, Tournament Draft), certain champion skins have visual effects, animations, or hitboxes that are notoriously hard to read (often referred to as "pay-to-win" skins, e.g., iBlitzcrank, Steel Legion Lux, Project: Ashe).

**Competitive Mode** allows players to eliminate in-game visual clutter by selectively overriding other players' skins to their clean, standard default/base skins (`skin0`), while preserving the player's own selected skin/chroma.

---

## 2. Supported Game Modes & Constraints
Competitive Mode relies on champion uniqueness in the match so that overriding an opponent's skin never affects the player's own champion.

* **Supported Modes (Active):**
  * Ranked Solo / Duo (`queueId: 420`)
  * Ranked Flex (`queueId: 440`)
  * Normal Draft (`queueId: 400`)
  * Clash (`queueId: 700`)
  * Custom Tournament Draft
* **Unsupported Modes (Disabled / Greyed Out):**
  * Blind Pick / Quickplay (where mirror matches can occur)
  * ARAM & Arena (where enemy champions are hidden in Champ Select until loading screen)

When an unsupported mode is detected, the UI control in Champ Select automatically becomes semi-transparent and disabled with a tooltip explaining that Competitive Mode is active only in Draft/Ranked queues.

---

## 3. User Interface (Pengu Loader Plugin: `ROSE-CompetitiveMode`)

### 3.1 Champ Select Control
* **Placement:** Placed directly adjacent to the dice roll controls under the champion loadout carousel in Champ Select.
* **Control Visual:** A sleek SVG shield icon reflecting the current state:
  * **Muted Grey Shield:** `Off` (Default disabled).
  * **Crimson / Red Shield with Crossed Swords:** `Enemy Only` (Only enemy champions overridden to base skins).
  * **Golden Shield with Star:** `All Except Me & Party` (All other players except the local user and active party members overridden).

### 3.2 Popover Menu
Clicking the shield icon opens a compact, dark League-styled popover with three options:
1. `Off` - Standard Rose behavior; all player skins rendered as picked.
2. `Enemy Only` (Recommended for Ranked) - Forces the 5 enemy champions to base skins.
3. `All Except Me & Party` - Forces everyone to base skins except the player and active Rose Party members.

### 3.3 Persistence
Any selection made in the popover immediately broadcasts over the WebSocket bridge to the Rose backend and is persisted in `config.ini`:
```ini
[Competitive]
mode = enemy_only  # off | enemy_only | all_except_party
```
The selection remains active across all future matches until toggled.

---

## 4. Backend Architecture & Target Resolution

### 4.1 State Management
* `SharedState.competitive_mode`: Holds current active setting (`"off"`, `"enemy_only"`, `"all_except_party"`).
* `SharedState.competitive_supported`: Boolean flag updated by gameflow queue inspection.

### 4.2 Target Resolution in `InjectionTrigger` (T-10s Countdown)
During the countdown phase at `T-10s` before the match launches (in `threads/handlers/injection_trigger.py`):
1. Check if `state.competitive_mode != "off"` and `state.competitive_supported == True`.
2. Retrieve current session loadout data:
   * `their_team = session.get("theirTeam") or []`
   * `my_team = session.get("myTeam") or []`
3. Resolve target champion IDs:
   * If `mode == "enemy_only"`:
     `target_ids = {p["championId"] for p in their_team if p.get("championId")}`
   * If `mode == "all_except_party"`:
     `all_ids = {p["championId"] for p in (their_team + my_team) if p.get("championId")}`
     `party_ids = {member.champion_id for member in state.party_state.synced_members}`
     `target_ids = all_ids - party_ids`
4. **Hard Security Invariant:**
   `target_ids.discard(state.locked_champ_id or state.hovered_champ_id)`
   The player's own champion is guaranteed never to be included in the override list.

---

## 5. Override Generator & Cache System

### 5.1 Asset Override Mechanism (PropBin Aliasing)
Rather than copying gigabytes of 3D models and textures, League of Legends character configurations are defined in `assets/characters/{champ}/skins/skin{N}.bin`.
* A base skin override package for a champion contains copies of `skin0.bin` mapped to every non-zero skin path:
  `assets/characters/{champ}/skins/skin1.bin`
  `assets/characters/{champ}/skins/skin2.bin`
  ...
  `assets/characters/{champ}/skins/skinN.bin`
* When an opponent picks any skin, the game engine reads the redirected `.bin` file, which references the default base mesh, skeleton, and textures from the core game install.
* Total package size per champion: **15 KB - 30 KB**.
* Payload for 5 champions: **~100 KB - 150 KB**.

### 5.2 Cache Storage (`%LOCALAPPDATA%\Rose\competitive_cache\`)
* Generated packages are stored as lightweight `.fantome` packages:
  `base_override_{champion_id}.fantome`
* **First encounter:** Rose reads the champion's base WAD from `League/Game/DATA/FINAL/Champions/{Champ}.wad.client` using `injection.baseskin.wad`, duplicates `skin0.bin` for each known skin index, and saves to cache (~30-50ms).
* **Subsequent matches:** Loaded from disk in 0ms.
* **Game Patch Invalidation:** When League's build/version changes, the cache folder is wiped to regenerate against the latest patch schemas.

### 5.3 LTK Manager Staging
The resolved `.fantome` packages are appended to the staging list in `InjectionTrigger` alongside the player's own selected skin/chroma. LTK Manager mounts the resulting combined virtual overlay.

---

## 6. Edge Cases & Resilience

1. **WAD Read Failure / Locked File:**
   If extracting `skin0.bin` for a specific champion raises an exception, the error is logged as a warning, and that single champion is omitted from `target_ids`. The match and the player's skin load unaffected.
2. **Game Reconnect:**
   LTK patcher retains the staged overlay for the entire lifetime of `League of Legends.exe`. Reconnecting to a match restores default skins seamlessly.
3. **LTK Manager Anti-Skinhack Validation:**
   LTK Manager's validator penalizes `SkinhackDetected` when `skin0` references paid assets. Redirecting paid skins (`skinN`) to `skin0` is an authorized downgrade to base and passes integrity checks cleanly.

---

## 7. Verification & Testing Plan

1. **Unit Tests (`injection/tests/test_competitive_mode.py`):**
   * Target resolution logic (filtering self, party, and enemies).
   * Generator verification (confirming `skin0.bin` content is mapped across all target skin paths).
   * Queue eligibility detection (ensuring draft queues are flagged supported, blind/ARAM unsupported).
2. **Fast In-Game Verification (60 Seconds):**
   * Create a Custom Game with Tournament Draft.
   * Invite a test participant who selects an easily recognizable skin (e.g. Mecha / Project).
   * Activate Competitive Mode (`Enemy Only`).
   * Enter game, confirm participant appears on base skin on fountain.
   * Exit (`Alt + F4`).
