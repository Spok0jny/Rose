# Competitive Mode Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement Competitive Mode in Rose to selectively override opponent (and optionally ally) skins to default base skins in Draft/Ranked matches while preserving the player's own selected skin/chroma and party members' skins.

**Architecture:** A Pengu Loader UI plugin (`ROSE-CompetitiveMode`) provides a shield control and popover in Champ Select next to the dice roller. The setting (`off`, `enemy_only`, `all_except_party`) is persisted in `config.ini` and tracked in `SharedState`. In Draft modes, during the T-10s countdown, Rose resolves target champion IDs, generates or retrieves cached lightweight base skin override packages (`skinXX.bin -> skin0.bin`), and stages them into the LTK Manager overlay alongside the player's selected skin.

**Tech Stack:** Python 3.12+, JavaScript (ES6 / Pengu Loader plugin), `injection.baseskin.wad` (WAD v3 reader/writer), `configparser`, `unittest`.

**Spec:** `docs/superpowers/specs/2026-11-09-competitive-mode-design.md`

## Global Constraints
- Target game modes: Ranked Solo/Duo (`420`), Ranked Flex (`440`), Normal Draft (`400`), Clash (`700`), Custom Tournament Draft.
- Non-draft queues (Blind Pick, Quickplay, ARAM, Arena) must disable the UI control.
- Hard security invariant: the player's own champion (`locked_champ_id`) is strictly excluded from `target_ids`.
- Zero 3D asset copying: only metadata/property `.bin` files are mapped to keep total payload size under ~150 KB.
- Cache directory: `%LOCALAPPDATA%\Rose\competitive_cache\`.
- All Python changes must pass `python -m ruff check . --select E9,F63,F7,F82` and `python -m unittest`.
- All Pengu plugin JS must pass `node --check`.

## Review Focus
1. Player's champion accidentally targeted: `target_ids.discard(locked_champ_id)` must prevent player from turning into base skin.
2. Missing or locked base champion WAD: Graceful error handling must skip the failing champion and not block match startup.
3. Party member skins in `all_except_party` mode: Synced party member champion IDs must be preserved.
4. Non-draft queue detection: Unsupported queues must cleanly disable the UI button with a descriptive tooltip.
5. League client patch change: Outdated cached `.bin` files must be purged when client version changes.

---

### Task 1: Configuration & SharedState Integration

**Files:**
- Modify: `config.py:150-180`
- Modify: `state/core/shared_state.py:75-90`
- Test: `test/test_competitive_config.py`

**Interfaces:**
- Consumes: `config.get_config_option`, `config.set_config_option`
- Produces: `SharedState.competitive_mode`, `SharedState.competitive_supported`

- [ ] **Step 1: Write the failing test**
Create `test/test_competitive_config.py` testing default mode `"off"`, reading/writing valid modes (`"off"`, `"enemy_only"`, `"all_except_party"`), and rejecting/falling back on invalid strings.

- [ ] **Step 2: Run test to verify it fails**
Run: `python -m unittest test/test_competitive_config.py -v`
Expected: FAIL (missing competitive mode attributes or helpers).

- [ ] **Step 3: Implement config options and state fields**
In `config.py`, define `COMPETITIVE_MODES = ("off", "enemy_only", "all_except_party")`, add `get_competitive_mode() -> str` and `set_competitive_mode(mode: str) -> None`.
In `state/core/shared_state.py`, add `competitive_mode: str = "off"` and `competitive_supported: bool = False` to `SharedState`.

- [ ] **Step 4: Run test to verify it passes**
Run: `python -m unittest test/test_competitive_config.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**
```bash
git add config.py state/core/shared_state.py test/test_competitive_config.py
git commit -m "feat(competitive): add configuration and shared state for competitive mode"
```

---

### Task 2: Draft Queue Detection

**Files:**
- Create: `utils/competitive/queue_detector.py`
- Modify: `threads/handlers/phase_handler.py:110-140`
- Test: `test/test_queue_detector.py`

**Interfaces:**
- Consumes: LCU session gameData (`queue.id`, `queue.gameMode`, `isCustomGame`, `mutators`)
- Produces: `is_draft_mode(session: dict) -> bool`

- [ ] **Step 1: Write the failing test**
Create `test/test_queue_detector.py` testing queue IDs `420`, `440`, `400`, `700`, and tournament draft custom games return `True`; test `430` (Blind), `450` (ARAM), `1700` (Arena), and bot games return `False`.

- [ ] **Step 2: Run test to verify it fails**
Run: `python -m unittest test/test_queue_detector.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'utils.competitive'`.

- [ ] **Step 3: Implement `is_draft_mode`**
In `utils/competitive/queue_detector.py`:
Implement `is_draft_mode(session_data: dict) -> bool` evaluating `queueId in {400, 420, 440, 700}` or custom game with tournament draft mutators.
In `threads/handlers/phase_handler.py`, when entering `ChampSelect`, evaluate `self.state.competitive_supported = is_draft_mode(session)`.

- [ ] **Step 4: Run test to verify it passes**
Run: `python -m unittest test/test_queue_detector.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**
```bash
git add utils/competitive/queue_detector.py threads/handlers/phase_handler.py test/test_queue_detector.py
git commit -m "feat(competitive): add draft queue detection for competitive eligibility"
```

---

### Task 3: Competitive Target Resolver

**Files:**
- Create: `utils/competitive/target_resolver.py`
- Test: `test/test_target_resolver.py`

**Interfaces:**
- Consumes: `session` (myTeam, theirTeam), `locked_champ_id: Optional[int]`, `party_members: list`
- Produces: `resolve_competitive_targets(mode: str, session: dict, my_champ_id: Optional[int], party_champ_ids: set[int]) -> set[int]`

- [ ] **Step 1: Write the failing test**
Create `test/test_target_resolver.py` testing:
1. `mode == "off"` returns empty set.
2. `mode == "enemy_only"` returns only enemy champion IDs; self champion excluded even if in enemy list.
3. `mode == "all_except_party"` returns enemies and non-party allies; excludes self and party members.

- [ ] **Step 2: Run test to verify it fails**
Run: `python -m unittest test/test_target_resolver.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'utils.competitive.target_resolver'`.

- [ ] **Step 3: Implement `resolve_competitive_targets`**
In `utils/competitive/target_resolver.py`:
Implement resolution logic with strict `target_ids.discard(my_champ_id)` safety invariant and party filtering.

- [ ] **Step 4: Run test to verify it passes**
Run: `python -m unittest test/test_target_resolver.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**
```bash
git add utils/competitive/target_resolver.py test/test_target_resolver.py
git commit -m "feat(competitive): implement target resolution logic with self and party exclusion"
```

---

### Task 4: Base Skin Override Generator & Cache

**Files:**
- Create: `utils/competitive/override_generator.py`
- Test: `test/test_override_generator.py`

**Interfaces:**
- Consumes: `champion_id: int`, `game_path: Path`, `cache_dir: Path`
- Produces: `get_or_create_base_override(champion_id: int, game_path: Path, cache_dir: Path) -> Optional[Path]`

- [ ] **Step 1: Write the failing test**
Create `test/test_override_generator.py` using a mock WAD file with `assets/characters/testchamp/skins/skin0.bin` and non-zero skin entries, verifying:
1. Generates `.fantome` package in `cache_dir`.
2. Package contains `skin1.bin` .. `skinN.bin` matching `skin0.bin` bytes.
3. Subsequent call returns existing cached file without re-parsing.

- [ ] **Step 2: Run test to verify it fails**
Run: `python -m unittest test/test_override_generator.py -v`
Expected: FAIL.

- [ ] **Step 3: Implement `override_generator.py`**
In `utils/competitive/override_generator.py`:
Read champion WAD via `injection.baseskin.wad.GameWad`. Extract `skin0.bin`. Discover existing skin hashes from table of contents. Create `ModWad` containing `skin{N}.bin` mapping to `skin0.bin` content. Package as `.fantome` zip with simple metadata into `cache_dir`. Handle missing or corrupt WAD gracefully by returning `None`.

- [ ] **Step 4: Run test to verify it passes**
Run: `python -m unittest test/test_override_generator.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**
```bash
git add utils/competitive/override_generator.py test/test_override_generator.py
git commit -m "feat(competitive): implement base skin override generator and cache storage"
```

---

### Task 5: Injection Pipeline Integration

**Files:**
- Modify: `threads/handlers/injection_trigger.py:530-580, 1020-1060`
- Test: `test/test_competitive_injection_trigger.py`

**Interfaces:**
- Consumes: `resolve_competitive_targets`, `get_or_create_base_override`
- Produces: Extra `.fantome` override paths appended to `injector` staging mod list

- [ ] **Step 1: Write the failing test**
Create `test/test_competitive_injection_trigger.py` verifying that when `competitive_mode == "enemy_only"` during countdown, `InjectionTrigger` resolves targets, acquires override paths, and passes them to the injector staging list without replacing player's selected skin.

- [ ] **Step 2: Run test to verify it fails**
Run: `python -m unittest test/test_competitive_injection_trigger.py -v`
Expected: FAIL.

- [ ] **Step 3: Integrate with `InjectionTrigger`**
In `threads/handlers/injection_trigger.py`:
During countdown staging (around line 530 and line 1020), if `self.state.competitive_mode != "off"` and `self.state.competitive_supported`:
Resolve target champion IDs using `resolve_competitive_targets`.
Generate or retrieve cached override packages for each target.
Add valid override `.fantome` files into the mod list staged by LTK Manager.

- [ ] **Step 4: Run test to verify it passes**
Run: `python -m unittest test/test_competitive_injection_trigger.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**
```bash
git add threads/handlers/injection_trigger.py test/test_competitive_injection_trigger.py
git commit -m "feat(competitive): integrate competitive overrides into injection trigger staging"
```

---

### Task 6: WebSocket Bridge & Events

**Files:**
- Modify: `pengu/communication/message_handler.py:120-160`
- Modify: `pengu/communication/broadcaster.py:40-70`
- Test: `test/test_competitive_websocket.py`

**Interfaces:**
- Consumes: Incoming message `update_competitive_mode`
- Produces: Outgoing broadcast `competitive_state` (`{mode: str, supported: bool}`)

- [ ] **Step 1: Write the failing test**
Create `test/test_competitive_websocket.py` testing message handler accepts `{"type": "update_competitive_mode", "mode": "enemy_only"}` and updates config and state; test broadcaster emits current competitive state.

- [ ] **Step 2: Run test to verify it fails**
Run: `python -m unittest test/test_competitive_websocket.py -v`
Expected: FAIL.

- [ ] **Step 3: Implement message handling and broadcasting**
In `pengu/communication/message_handler.py`, add handler for `update_competitive_mode` with validation.
In `pengu/communication/broadcaster.py`, add `broadcast_competitive_state(mode, supported)` to send on connect and when phase or setting changes.

- [ ] **Step 4: Run test to verify it passes**
Run: `python -m unittest test/test_competitive_websocket.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**
```bash
git add pengu/communication/message_handler.py pengu/communication/broadcaster.py test/test_competitive_websocket.py
git commit -m "feat(competitive): add WebSocket messaging and state broadcasting"
```

---

### Task 7: Pengu Loader UI Plugin (`ROSE-CompetitiveMode`)

**Files:**
- Create: `Pengu Loader/plugins/ROSE-CompetitiveMode/index.js`
- Test: Syntax check and party/plugin syntax CI test

**Interfaces:**
- Consumes: WebSocket messages `competitive_state`, DOM element `.skin-selection-view` or adjacent to `.dice-button`
- Produces: Shield button and popover menu in Champ Select

- [ ] **Step 1: Create plugin skeleton and syntax test**
Create `Pengu Loader/plugins/ROSE-CompetitiveMode/index.js`.
Verify syntax with `node --check "Pengu Loader/plugins/ROSE-CompetitiveMode/index.js"`.

- [ ] **Step 2: Implement Shield button & Popover component**
Implement:
1. Shield SVG icon styled to match League Client UI theme.
2. Status indicator (Grey = Off, Crimson/Red = Enemy Only, Gold = All Except Party).
3. Popover menu on click with radio options for the 3 modes.
4. Sending `update_competitive_mode` payload on change.
5. Disabled styling and tooltip when `supported === false`.

- [ ] **Step 3: Run node syntax checks**
Run: `node --check "Pengu Loader/plugins/ROSE-CompetitiveMode/index.js"`
Expected: Clean exit code 0.

- [ ] **Step 4: Commit**
```bash
git add "Pengu Loader/plugins/ROSE-CompetitiveMode/index.js"
git commit -m "feat(competitive-ui): add Pengu Loader plugin for competitive mode controls"
```

---

### Task 8: Full Verification & PyInstaller Spec Update

**Files:**
- Modify: `Rose.spec:230-245` (add `utils.competitive` modules to hiddenimports)
- Create: `injection/tests/test_competitive_mode.py` (comprehensive integration test)

- [ ] **Step 1: Add hidden imports in `Rose.spec`**
Add `'utils.competitive'`, `'utils.competitive.queue_detector'`, `'utils.competitive.target_resolver'`, `'utils.competitive.override_generator'` to `Rose.spec`.

- [ ] **Step 2: Run full lint and test suites**
Run: `python -m ruff check . --select E9,F63,F7,F82`
Run: `python -m unittest discover -s test -v`
Run: `node --test test/party_ui_reconnect.test.cjs`
Expected: ALL PASS.

- [ ] **Step 3: Commit**
```bash
git add Rose.spec injection/tests/test_competitive_mode.py
git commit -m "chore(competitive): register hiddenimports in Rose.spec and add integration suite"
```
