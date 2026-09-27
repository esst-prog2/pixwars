# Design

## Context

Greenfield: `packages/sim`, `packages/server` and `packages/client` exist as empty
directories with stale `__pycache__` in them, and there is no Python source in the
repository. Python is 3.14.7 and `uv` 0.12.2 is available; the venv is empty.

See `proposal.md` — Why for the motivation. The one constraint that shapes
everything below is that this change must not make the networking change (later
level 1) a rewrite. See `specs/match-simulation/spec.md` for the requirements
that encode that.

## Goals / Non-Goals

**Goals:**

- One seam, `step(world, inputs) -> world`, with button states as the only input,
  so the networking change replaces the *caller* of `step` and nothing else.
- The simulation is importable and fully exercisable with no display and no
  dependencies beyond the standard library.
- Integer-friendly, deterministic arithmetic, so replays in tests are exact.

**Non-Goals:**

- Performance work. A 20 Hz tick over a map of a few thousand tiles and four
  players has enormous headroom; clarity wins every time here.
- Any abstraction whose only justification is a later level. No transport
  interface, no serialization format, no plugin points. The later changes add
  those when they need them.
- Sprites or art. Colored rectangles.

## Decisions

### The world is a mutable dataclass, stepped in place, and copyable

`step(world, inputs)` mutates a `World` dataclass and returns it, rather than
building a new world each tick. Alternative considered: a frozen world with a pure
`step` returning a new value. Rejected — the determinism and replay requirements
are satisfied just as well by a mutable world plus an explicit `copy()`, the code
is far shorter, and a frozen tile grid would mean reallocating the whole map every
tick for the handful of tiles that change.

Purity is enforced at the *boundary*, not by immutability: nothing outside
`pixwars_sim` is allowed to write to a `World`, and the tests assert the rules
that make that visible (a caller cannot supply a position; ticking a finished
match changes nothing).

### Button states are a frozen dataclass of booleans

```python
@dataclass(frozen=True, slots=True)
class Buttons:
    left: bool = False;  right: bool = False;  jump: bool = False
    attack: bool = False; place: bool = False; break_: bool = False
    buy: int | None = None      # 1..4, or None
    facing_left: bool = False   # direction, not a position
```

`inputs` is a `dict[int, Buttons]`. A frozen dataclass rather than a dict or an
int bitmask: it is self-documenting, cheap to construct, and — the point — there
is no field on it that could carry a position, so the "clients cannot send a
position" requirement holds by construction rather than by validation. `step`
type-checks its inputs and ignores anything that is not a `Buttons`, which is what
makes that spec scenario testable.

`facing_left` is a direction, not a coordinate; it is derived from the last
movement key the client saw. Deriving facing inside the sim from velocity was the
alternative, and it makes it impossible to face into a gap while standing still,
which bridging needs.

### Fixed-point positions: integer subpixels, 256 per tile

Positions and velocities are `int`, in units of 1/256 of a tile. Floats were the
alternative and are rejected: the determinism requirement is much easier to hold
with integers, and the half-a-tile-per-tick collision guarantee becomes a plain
integer assertion rather than an epsilon argument.

```
SUBPIXEL   = 256          # units per tile
TILE       = 32           # pixels per tile, client only
TICK_HZ    = 20
WALK_SPEED = 102          # 0.40 tile/tick  ->  8.0 tiles/s
JUMP_SPEED = 128          # 0.50 tile/tick upward
GRAVITY    = 12           # per tick
MAX_FALL   = 120          # 0.47 tile/tick  -- under the 0.5 guarantee
```

`MAX_FALL` is clamped below `SUBPIXEL // 2` deliberately: that clamp *is* the
collision guarantee. A unit test asserts `max(WALK_SPEED, JUMP_SPEED, MAX_FALL) <=
SUBPIXEL // 2`, so a later tuning change cannot silently break collision.

### Collision: axis-separated, one tile-step at a time

Move on X, resolve; move on Y, resolve. Each resolution samples the tiles
overlapping the player's 1x2-tile box and pushes out of the first solid one.
Because no step exceeds half a tile, sampling the destination box alone is
sufficient — no swept-volume test, no raycast. This is the concrete reason the
speed clamp above is a hard rule and not a preference.

### The map is a flat `bytearray` grid plus a team-ownership grid

```
MAP_W, MAP_H = 64, 36
tiles  : bytearray   # 0 empty, 1 terrain, 2 placed, 3 bed
owner  : bytearray   # 0 none, 1 red, 2 blue  -- parallel to tiles
```

A flat `bytearray` indexed `y * MAP_W + x` over a list of lists: fewer
allocations, trivially copyable for replay tests, and `owner` gives "you cannot
break your own bed" and "terrain is unbreakable" as a byte comparison instead of a
lookup table. Beds occupy two tiles each and are both typed `3`.

The layout is built by one function from a literal table of platform rectangles.
Not parsed from a file — `more than one map, loaded from files` is later level 10,
and a parser now would be an abstraction with one caller.

```
        y=8     [mid]              [CENTER]              [mid]
        y=16
        y=24  [BASE red]                            [BASE blue]
              bed gen shop                          shop gen bed
              x=4..14        <-- ~25 tiles -->        x=50..60
```

### Rules live in separate modules, all called from one `step`

```
pixwars_sim/
  constants.py   every tunable number, nothing else
  buttons.py     Buttons
  world.py       World, Player, Team, new_match(), copy()
  mapgen.py      the five platforms, beds, generators, shop zones
  physics.py     movement + collision
  building.py    place / break, break progress
  economy.py     generator ticks, shop purchases
  combat.py      swing, damage, armor, death
  match.py       respawn, bed breaking, elimination, winner
  step.py        step(world, inputs) -- the only public entry point
```

Order within a tick is fixed and is itself a design decision, because several
specs depend on it:

```
1. purchases      (shop zone, iron) ....... before movement, so a bought
                                             block can be placed the same tick
2. physics        (x, then y, then landing)
3. building       (place / break progress / bed progress)
4. combat         (swings, damage, deaths)
5. match          (respawn timers, elimination, winner)
6. generators     (every GEN_TICKS, living players only)
```

Combat before match means a killing blow and the resulting elimination land on the
same tick, which `specs/beds-and-elimination` requires ("the match is over on that
same tick").

### The bot is a function in the client package, not the sim

`pixwars_client/bot.py` exposes `decide(world, player_id) -> Buttons`. It lives in
the client because the client is what owns "who supplies input for which player";
`pixwars_sim` must not import it, and a test asserts the sim package has no
reference to it. When real clients arrive the bot is simply not consulted.

Policy: walk toward the enemy bed, place a block into a gap directly ahead when
there is floor missing, attack when an enemy is in reach, hold break when the
enemy bed is in reach. Purely a function of the world — no internal state, which
is what makes it deterministic per the spec.

### `main.py` owns the loop; the accumulator pattern keeps the rates separate

```python
acc += clock.tick(60) / 1000
while acc >= 1 / TICK_HZ:
    world = step(world, gather_inputs(world))
    acc -= 1 / TICK_HZ
draw(world)
```

The client's own `Buttons` are latched: a key pressed and released between ticks
still sets its flag for the next tick, then clears. This is what
`specs/game-client` means by a press not being lost — pygame's `get_pressed()`
alone would drop it.

### `pygame-ce`, not `pygame`

Same `import pygame`. Upstream pygame has historically lagged new CPython
releases by months, and this project is on 3.14.7 today; a source build needs SDL
development headers. If upstream publishes a 3.14 wheel later, the swap is one
line in `packages/client/pyproject.toml`. Recorded in `PLANNING_LOG.md`.

### uv workspace, three packages, `sim` with zero dependencies

```
pyproject.toml              [tool.uv.workspace] members = ["packages/*"]
packages/sim/               no dependencies at all
packages/client/            pygame-ce, depends on pixwars-sim
packages/server/            left empty (placeholder, no pyproject yet)
main.py                     -> pixwars_client.game.run()
```

The sim's empty dependency list is not decoration: it is what makes the
"no rendering or transport dependencies" requirement enforceable, and the test
that walks the sim package's imports has teeth because of it. `packages/server`
gets no `pyproject.toml` in this change — an empty package that declares itself is
worse than an empty directory.

### Numbers chosen for the MVP

| Rule | Value | Ticks |
|---|---|---|
| Tick | 20 Hz | — |
| Respawn delay | 5 s | 100 |
| Iron generator interval | 2 s | 40 |
| Attack cooldown | 0.25 s | 5 |
| Attack reach | 1.5 tiles | — |
| Full health | 20 | — |
| Fist damage | 2 | — |
| Stone sword damage | 5 | — |
| Leather armor | −2, floor 1 | — |
| Placed block break | hand 0.6 s / pickaxe 0.2 s | 12 / 4 |
| Bed break | hand 1.5 s / pickaxe 0.5 s | 30 / 10 |
| Block stack limit | 64 | — |
| Prices | blocks×16: 4, sword: 8, armor: 6, pickaxe: 10 | — |

These are a starting point, all in `constants.py`, and tuning them is not a spec
change — no scenario names a number.

## Risks / Trade-offs

- **No `pygame-ce` wheel for Python 3.14 either** → The sim and its whole test
  suite are unaffected, because they have no dependencies. The fallback is to pin
  the client to an older interpreter with `requires-python`, which touches one
  file and no simulation code. This is exactly why the client is a separate
  package.
- **The bot is good enough to end a match but not to be interesting** → Accepted.
  Its spec obligation is that a match against it terminates; it is a test fixture
  and a demo prop, and it is deleted by the networking change.
- **Mutating the world in place makes an accidental external write easy to miss**
  → The import-boundary test and the "a caller cannot supply a position" test
  catch the shapes of this that matter. A frozen world would catch more, at a cost
  the Goals reject.
- **Seven capabilities is a lot of spec for one change** → They are one game, and
  each one is small. The alternative was one `gameplay` spec whose requirements
  would then have to be split apart when later levels modify only combat or only
  the economy.
- **20 Hz will look steppy and someone will want to "just make it 60"** → That is
  the point (see `PLANNING_LOG.md`, 2026-09-27): living with it now means the
  network port changes nothing about feel. The constant is one line, and the
  collision-guarantee assertion will fail loudly if it is raised without also
  re-deriving the speed clamps.

## Migration Plan

Nothing to migrate — there is no existing code and no data. Two cleanups ride
along: delete the stale `packages/**/__pycache__` directories and stop tracking
`.pytest_cache`, both via a new `.gitignore`.

Rollback is `git revert`; no state lives outside the repository.
