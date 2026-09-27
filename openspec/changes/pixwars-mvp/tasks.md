# Tasks

## 1. Workspace and packaging

- [x] 1.1 Add a root `pyproject.toml` declaring a uv workspace over `packages/*`, and a `.gitignore` covering `__pycache__/`, `*.pyc`, `.pytest_cache/`, `.venv/`, `dist/`, `build/`, `*.egg-info/`
- [x] 1.2 Add `packages/sim/pyproject.toml` for `pixwars-sim` with an empty dependency list and a src layout, then verify `uv sync` succeeds and `uv run python -c "import pixwars_sim"` prints nothing and exits 0
- [x] 1.3 Add `packages/client/pyproject.toml` for `pixwars-client` depending on `pygame-ce` and the workspace `pixwars-sim`, then verify `uv sync` resolves and `uv run python -c "import pygame; print(pygame.version.ver)"` prints a version
- [x] 1.4 Add `pytest` as a root dev dependency and verify `uv run pytest --version` works; delete the stale `packages/**/__pycache__` directories and stop tracking `.pytest_cache`
- [x] 1.5 Leave `packages/server/` empty with no `pyproject.toml` and verify `uv sync` does not pick it up as a workspace member

## 2. World model and map

- [x] 2.1 Write `pixwars_sim/constants.py` with every value from the design's table (`SUBPIXEL`, `TICK_HZ`, speeds, gravity, damages, prices, break and respawn times) and nothing else
- [x] 2.2 Add a test asserting `max(WALK_SPEED, JUMP_SPEED, MAX_FALL) <= SUBPIXEL // 2`, so the half-tile-per-tick collision guarantee cannot be broken by later tuning
- [x] 2.3 Write `pixwars_sim/buttons.py` with the frozen `Buttons` dataclass (movement, jump, attack, place, break, `buy: int | None`, `facing_left`) and verify a test confirms it is frozen and has no position-bearing field
- [x] 2.4 Write `pixwars_sim/world.py` with `Team`, `Player`, `World`, `new_match(players)` and `World.copy()`; verify a test that a copied world is equal to but independent of the original
- [x] 2.5 Write `pixwars_sim/mapgen.py` building the five platforms, two beds, two generators and two shop zones into the flat `tiles`/`owner` bytearrays; verify a test that a new match has five platforms, one bed, one generator and one shop zone per team, and that every gap between platforms is wider than a jump
- [x] 2.6 Add a test that reads player positions, health, inventories, bed states and the outcome from a fresh world as plain data, covering the "match state is inspectable as a value" requirement

## 3. The step seam

- [x] 3.1 Write `pixwars_sim/step.py` with `step(world, inputs)` calling the phases in the design's fixed order (purchases, physics, building, combat, match, generators), with the later phases stubbed for now
- [x] 3.2 Add tests for input handling: a non-`Buttons` value such as a position is ignored and the player does not move; an unknown player id is ignored while other players still simulate; a missing player id is treated as no buttons held and the tick still completes
- [x] 3.3 Add a determinism test: apply a recorded sequence of button states to two copies of the same world and assert the results are equal tick for tick
- [x] 3.4 Add a test that steps a world 20 times and asserts elapsed tick count, not wall-clock time, drives every timed rule, and that `step` reads no clock
- [x] 3.5 Add a test that walks every module in `pixwars_sim` and asserts none of them imports `pygame`, `socket`, `asyncio` or `pixwars_client`, directly or transitively

## 4. Physics

- [x] 4.1 Write `pixwars_sim/physics.py` with axis-separated movement: apply horizontal velocity and resolve, then vertical velocity, gravity and `MAX_FALL` clamp, and resolve; set the grounded flag on landing
- [x] 4.2 Verify with tests: walking into a wall does not enter the tile; walking off an edge falls with increasing speed until landing; jumping while not grounded does nothing; a player cannot leave the map's left, right or top bounds
- [x] 4.3 Implement falling out of the bottom of the map as a death with no killer, and verify a test that the player dies and no kill is credited
- [x] 4.4 Add a test that a player at maximum horizontal and falling speed moves at most half a tile on each axis in one tick

## 5. Block building

- [x] 5.1 Write `pixwars_sim/building.py` place: consume one block, mark the target tile placed and owned by the placing team; verify tests for placing on air, placing with an empty stack, and placing into a tile that is solid or occupied by a player
- [x] 5.2 Implement break progress accumulation per player with hand and pickaxe break times; verify tests that a full hold breaks the tile with nothing returned to inventory, releasing early discards progress, and turning to a new target resets progress to zero
- [x] 5.3 Enforce that terrain tiles never break, with or without a pickaxe, and verify a test holding break against a platform tile for many times the bed break time
- [x] 5.4 Enforce the block stack limit, filling to the limit on an over-large purchase while still charging, and clear the stack on death; verify both with tests
- [x] 5.5 Add an integration test that a player repeatedly placing blocks ahead and walking forward crosses from a base platform to the adjacent middle platform

## 6. Economy

- [x] 6.1 Write `pixwars_sim/economy.py` generator tick: every `GEN_TICKS`, grant one iron to each living player of the generator's own team; verify tests that iron accrues over several intervals, a dead player gains none while living teammates do, and the red generator never changes blue's iron
- [x] 6.2 Implement shop-zone membership and the four purchases bound to `buy` values 1-4; verify tests for buying blocks and for buying each of sword, armor and pickaxe
- [x] 6.3 Enforce that purchases only work inside the player's own shop zone; verify tests for standing in the enemy zone and for walking out of the zone
- [x] 6.4 Refuse purchases with insufficient iron, changing nothing; refuse duplicate weapon/armor/tool purchases without charging; verify both with tests
- [x] 6.5 Clear iron and all purchased equipment on death, and verify a test that a respawned player carries nothing

## 7. Combat

- [x] 7.1 Write `pixwars_sim/combat.py` swing resolution: nearest living opponent within `ATTACK_REACH` in the faced direction, damage by weapon; verify tests for hitting an opponent in reach, swinging at nothing, and a sword dealing more than a fist
- [x] 7.2 Enforce no friendly fire and no self-damage, and verify a test swinging with only a teammate in reach
- [x] 7.3 Implement the attack cooldown and verify a test that holding attack for many ticks deals damage at most once per cooldown
- [x] 7.4 Implement armor reduction with a damage floor of one, and verify tests that an armored target loses less health and that a fully-absorbed hit still removes one point
- [x] 7.5 Implement death at zero or below with kill and death credit, and verify tests for a killing blow crediting both counters and for attacking an already-dead player crediting nothing
- [x] 7.6 Ignore every control for a dead player, and verify a test holding all controls for a dead player over many ticks changes nothing attributable to them

## 8. Beds, respawn and the end of a match

- [x] 8.1 Write `pixwars_sim/match.py` respawn: a player whose own bed stands returns at their spawn after `RESPAWN_TICKS` with full health and an empty inventory; verify tests for the respawn itself and for being still dead and untargetable partway through the delay
- [x] 8.2 Implement bed breaking with its own break time and bed-broken credit, refusing to break your own team's bed and never restoring a broken one; verify all three with tests
- [x] 8.3 Implement final death once a team's bed is broken, including the case where the bed breaks while a player is already waiting out the respawn delay; verify both with tests
- [x] 8.4 Implement elimination and the winner: the match ends on the tick the last living player of a bedless team dies; verify tests for that tick, for all players dead while the bed stands (match continues, players respawn), and for stepping a finished match changing nothing
- [x] 8.5 Implement the per-player beds-broken, kills and deaths counters; verify tests that they survive a respawn and that the winner and full scoreboard are readable after the match ends

## 9. Bot opponent

- [x] 9.1 Write `pixwars_client/bot.py` with `decide(world, player_id) -> Buttons`, reading the world only; verify a test that the world is unchanged after a call and that the return value is a `Buttons`
- [x] 9.2 Implement the policy: move toward the enemy bed, place a block when the tile ahead-and-below is empty, attack when an opponent is in reach, hold break when the enemy bed is in reach; verify a test that the attack control is set when an opponent is within reach
- [x] 9.3 Add a headless integration test that steps a match with the bot against an idle human player and asserts the match ends within a bounded number of ticks with the bot's team winning
- [x] 9.4 Add tests that `decide` is deterministic across two identical worlds, and that a match stepped with no bot involvement runs normally

## 10. The pygame client

- [x] 10.1 Write `pixwars_client/input.py` translating held keys into `Buttons` once per tick, with press latching so a key pressed and released between ticks is still reported; verify a unit test of the latch with a fake key-state source
- [x] 10.2 Make the number keys buy while inside the player's own shop zone and select an inventory slot otherwise, and verify a unit test of both branches against a world fixture
- [x] 10.3 Write `pixwars_client/render.py` drawing tiles, beds, generators, shop zones and players as colored rectangles from a world value, and verify it runs against a dummy video driver with no window
- [x] 10.4 Draw the header with the player's iron and, once a bed is broken, the team that lost it, and verify against a world fixture with a broken bed that the header text names that team
- [x] 10.5 Draw the in-zone shop list of four items with prices and keys, without pausing the match, and verify a test that entering and leaving the zone shows and hides it while ticks keep advancing
- [x] 10.6 Draw the end-of-match screen with the winning team and every player's beds, kills and deaths, and verify against a finished-world fixture
- [x] 10.7 Write `pixwars_client/game.py` with the accumulator loop — up to 60 fps drawing, exactly 20 ticks a second, no tick skipped on a slow frame — and a clean exit on window close; verify a headless test that drives the loop with a fake clock and asserts the tick count over simulated time and that a long frame still yields the right number of ticks
- [x] 10.8 Add `main.py` at the repo root starting a match with one human and one bot, and document `uv run python main.py` in `README.md`

## 11. Integration

- [x] 11.1 Run the full suite with `uv run pytest` and verify it passes with no window opened and no network access
- [x] 11.2 Play the README's demo end to end in the real window: collect iron, buy blocks and a sword, bridge to the center, break the bot's bed, see the header change, kill the bot and reach the scoreboard
- [x] 11.3 Append one line per decision made during implementation to `PLANNING_LOG.md`, marking who decided
