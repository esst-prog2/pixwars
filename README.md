# PixWars

A small side-view multiplayer game: two teams on separate platforms, each
defending a bed. Break the other team's bed and they stop respawning.

## 0. Running it

```sh
uv sync
uv run python main.py          # one human against one bot, in one window
uv run pytest                  # the rules, headless: no window, no network
```

| key | |
|---|---|
| `A` / `D`, or the arrows | move |
| `SPACE` / `W` | jump |
| `J` | attack |
| `K` | place a block |
| `L` | break |
| `1`-`4` | buy, while standing in your shop zone; otherwise select a slot |
| `ESC` | quit |

What exists today is the local game: the full loop -- iron, shop, bridging,
combat, beds, a winner -- in one process, with a bot opponent and no sockets in
it. The networking described below is the next change request, not yet built.
See `openspec/changes/pixwars-mvp/` for the change request it was built from and
`PLANNING_LOG.md` for the decisions along the way.

## 1. The demo

I run `python main.py` and click **Host**. I type the name `neobytes`, and the lobby
shows the code `K7P2QM` and `1/4 players`. On a second laptop on the same wifi a
friend clicks **Join**, types the code and the name `johnwick`, and appears in the
lobby; two more join and the start button unlocks. We pick red or blue and spawn
on two platforms about 25 tiles apart, each with a bed on it. I collect iron
from the generator on my island, buy 16 blocks and a stone sword from the shop,
and bridge toward the center island. `johnwick` reaches our base first and breaks our
bed — the header changes to `RED BED DESTROYED`. I die to his sword and do not
respawn, and when my last teammate dies the match ends with `BLUE WINS` and a
scoreboard of beds broken, kills and deaths.

## 2. The shape

```
in     button states from up to 4 players, sent to the host 60 times a second
out    a finished match: a winning team and a scoreboard
on screen   a fixed map of five platforms; each player moves, places and breaks
            blocks, buys from a shop on their island, attacks, and defends one bed
```

The host holds the only real copy of the world. Clients send which keys are
down, never where they are, and draw whatever the host sends back.

## 3. The size

### First useful version

* 2v2 on one local network. The host runs the server inside their own process; others join with a 6-character code.
* One hand-built map: two base platforms, two middle platforms, one center island.
* Authoritative host: clients send button states, the host simulates and broadcasts the world 20 times a second.
* Placing and breaking blocks, from a limited stack, so bridging between islands is how you cross.
* One resource. An iron generator on each base, and one shop with four items: blocks, a stone sword, leather armor, a pickaxe.
* Beds. While your bed stands you respawn after 5 seconds with an empty inventory; once it is broken, death is final. Last team alive wins.
* Melee combat only.

### Not this term

* **4v4, and matches over the internet.** A join code that works between two
  houses needs a relay server with a public address and NAT traversal. That is
  infrastructure, not gameplay, and it is its own project.
* **Client-side prediction and interpolation.** The first version accepts
  visibly steppy movement at 20 ticks a second rather than hiding the tick rate.
* Diamond and emerald tiers, generator upgrades, team upgrades.
* Bows, projectiles and knockback. These break the guarantee that nothing moves
  more than half a tile per tick, which is what keeps collision simple.
* Reconnecting. A player who drops is gone for that match.
* Sound, music, animated sprites, particles.
* More than one map.
* Stats that survive closing the game.

## 4. How we would know it works

* Given a client that sends a position rather than a button state, the host
  ignores it and that player does not move. The host is the only authority on
  where anyone is.
* Given a team whose bed has been broken, a player of that team who dies does
  not respawn, and the match ends the moment their last living player dies.
* Given a client that disconnects mid-match, the host removes that player within
  one tick and the remaining clients keep receiving updates without stalling.

The simulation is a separate module that imports neither pygame nor sockets, so
all three can be checked by stepping a world in a test, with no window open and
no second machine.

## 5. What could stop this

* **Networking is the technique I have not used before.** Everything else here
  is a variation on things I have written; the host/client split is not. This is
  why the first version is LAN-only and why interpolation is deferred: I would
  rather ship something correct and slightly jerky than debug smoothing on top of
  a sync bug.
* **Testing needs four clients and I am one person.** Because the simulation
  runs headless, most of it can be tested without the network at all, and the
  remainder by running several clients against a host on one machine.
* Nothing external. No data, no API, no accounts, no personal data, nothing to
  deploy. The demo is two or more laptops on the room's wifi, and it degrades to
  several windows on one laptop if the wifi does not cooperate.
* **The real risk is size.** A networked multiplayer game is more than eight
  weeks of work if every part of it is required, so the plan is to build the
  game locally first and treat the network layer as a port, not a foundation.
  The checkpoint is week six: if the local 2v2 game is not finished and the
  simulation is not cleanly separated by then, the network layer does not get
  started, and the term's deliverable is the local game with bot opponents.
* **"A port, not a foundation" is now measured rather than assumed.** A spike
  (`spike/net/`, 2 October) sent a live `World` snapshot at 20 Hz over UDP for
  60 s and timed the reply, on my home wifi from the laptop to a phone. Raw
  pickle (5.4 kB, four IP fragments): p50 10.9 ms, p99 61.2 ms, loss 0.00%.
  zlib-compressed (about 620 bytes, one datagram): p50 9.8 ms, p99 81.4 ms,
  loss 0.00%. The typical round trip is a fifth of a tick and nothing was lost,
  so the port goes ahead. The tail is over one 50 ms tick at both sizes, so two
  things are fixed before any network code exists: the client never waits for a
  snapshot -- one that is a tick or two late shows as a stutter, not a stall --
  and snapshots are sent compressed, so that one lost fragment cannot cost a
  whole snapshot. Still open: the same run on the room's wifi between two
  laptops.
* **It solves no one's problem but mine.** This is a game I would open next
  semester rather than a tool someone is waiting for, which I take to be within
  "choose something you want to use" but is worth naming rather than dressing up.
