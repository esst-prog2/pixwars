# Proposal

## Why

PixWars is described in `README.md` but does not exist: `packages/sim`,
`packages/server` and `packages/client` are empty directories. The README's
"first useful version" bundles seven systems at once, and one of them —
the authoritative host/client split — is the only technique in the project the
author has not written before. Section 5 of the README already concludes that
the local game must come first and the network layer must be a port rather than
a foundation, with week six as the checkpoint.

This change builds that local game: the complete PixWars loop — bridging,
economy, combat, beds, a winner — running in one process with no sockets in it.
It is the smallest version that is genuinely playable and can perform the demo
the README narrates, and it makes the network layer a later change request that
replaces one caller instead of a foundation everything else rests on.

## What Changes

- **A pure simulation package** (`pixwars_sim`) holding the only copy of the
  world: a fixed 20 Hz tick, advanced by `step(world, {player_id: buttons})`.
  It imports neither `pygame` nor `socket`, so it can be stepped in a test with
  no window open.
- **Button states as the only input.** Even locally, nothing outside the
  simulation may move a player or edit a tile directly. This is the seam the
  network layer will later sit on: a client that sends a position rather than a
  button state must be unable to affect the world by construction.
- **A hardcoded map of five platforms** — two bases roughly 25 tiles apart, two
  middle platforms, one center island — each base carrying a bed, an iron
  generator and a shop zone.
- **Block placing and breaking** from a limited stack, so bridging is how a
  player crosses the gaps between platforms.
- **One resource and one shop.** An iron generator ticks on each base; a
  walk-in shop zone sells four items (blocks, stone sword, leather armor,
  pickaxe) bought with number keys 1-4.
- **Beds.** While a team's bed stands, its dead players respawn after 5 seconds
  with an empty inventory; once it is broken, death is final. The match ends
  when a team's last living player dies, and the winner plus a scoreboard of
  beds broken, kills and deaths is reported.
- **Melee combat only.** Swing, damage reduced by armor, death.
- **A bot opponent** that produces the same button-state struct a keyboard
  produces, so the simulation cannot tell it from a human and the bot deletes
  cleanly when real clients arrive. No AI inside the simulation.
- **A pygame client** rendering at 60 fps from the latest simulated world, with
  the header (iron count, `RED BED DESTROYED`) and the end-of-match scoreboard
  the README's demo describes.
- **A uv workspace**: one `pyproject.toml` per package plus a root workspace, so
  the sim's import boundary is enforced by packaging rather than convention, and
  `python main.py` at the repo root starts the game. The client depends on
  `pygame-ce` rather than upstream `pygame` — same `import pygame` API, but
  Python 3.14.7 is unlikely to have upstream wheels.

Not in this change: anything involving a socket. `packages/server` stays empty.

## Capabilities

### New Capabilities

- `match-simulation`: the world model, the fixed-tick `step` function, movement
  and tile collision, and the rule that button states are the only way to
  affect the world. Includes the hardcoded five-platform map and spawns.
- `block-building`: placing and breaking tiles from a limited stack, including
  what may be broken and how fast.
- `resource-economy`: the iron generator, iron as a carried resource, and the
  walk-in shop with its four items.
- `beds-and-elimination`: respawn while your bed stands, final death once it is
  broken, match end, the winner, and the scoreboard counters.
- `melee-combat`: swinging, reach, damage, armor reduction, and death.
- `bot-opponent`: a policy that reads a world and returns button states for one
  player, driven from outside the simulation.
- `game-client`: the pygame window — keyboard mapping, rendering at 60 fps
  decoupled from the 20 Hz tick, the header, and the end-of-match scoreboard.

### Modified Capabilities

None. The project has no specs yet (`openspec list --specs` reports none).

## Impact

- **New code**: `packages/sim/src/pixwars_sim/`,
  `packages/client/src/pixwars_client/`, `main.py`, and headless tests under
  `packages/sim/tests/`.
- **Untouched**: `packages/server/` stays empty until the networking change.
- **New dependencies**: `pygame-ce` (client only), `pytest` (dev only). The sim
  package has no dependencies at all, by design — that is what makes the
  import-boundary test meaningful.
- **New files at the root**: `pyproject.toml` (uv workspace), `main.py`,
  `.gitignore`. The stale `__pycache__` directories under `packages/` and the
  committed-by-accident `.pytest_cache` go away.
- **README**: no change. This change implements a subset of what it already
  describes; the parts left out are already listed there as deferred.

## Later levels

These are the change requests of the coming weeks, in the order they make sense.
They are deliberately **not** specified here — no spec files, no tasks:

1. **Loopback networking.** Split the host out into `pixwars_server`; client and
   host as two processes over `127.0.0.1`, clients sending button states and
   receiving the world 20 times a second.
2. **Lobby and join code.** A 6-character code, host/join screens, a player list,
   team pick, and a start button that unlocks at 4 players — over LAN.
3. **Disconnect handling.** Removing a dropped player within one tick without
   stalling the remaining clients.
4. **4v4 and matches over the internet.** A relay with a public address and NAT
   traversal. Infrastructure, and its own project.
5. **Client-side prediction and interpolation.** Hiding the 20 Hz tick rate.
6. **Resource tiers and upgrades.** Diamond and emerald, generator upgrades,
   team upgrades.
7. **Projectiles and knockback.** Bows and arrows — these break the guarantee
   that nothing moves more than half a tile per tick, so collision has to be
   revisited with them.
8. **Reconnecting** mid-match.
9. **Sound, music, animated sprites, particles.**
10. **More than one map**, loaded from files rather than hardcoded.
11. **Stats that survive closing the game.**
