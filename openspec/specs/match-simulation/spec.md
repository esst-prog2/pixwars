# match-simulation Specification

## Purpose

Holds the only authoritative copy of a PixWars match and advances it one fixed
tick at a time from player button states, so the whole game can be played out in
a test with no window open and no second machine.

## Requirements

### Requirement: Button states are the only input

The simulation SHALL accept, per tick, a mapping from player id to a button
state — the set of controls held down that tick — and nothing else. It SHALL NOT
accept a position, velocity, health, inventory or tile edit from any caller.
There SHALL be no supported way for a caller to change the world except by
supplying button states and advancing a tick.

#### Scenario: A caller supplies a position instead of a button state

- **WHEN** a caller attempts to advance the match with a player position rather than a button state
- **THEN** the attempt is rejected and that player's position is unchanged from the previous tick

#### Scenario: Unknown player id

- **WHEN** a button state arrives for a player id that is not in the match
- **THEN** it is ignored and every other player is simulated normally for that tick

#### Scenario: Missing button state

- **WHEN** no button state is supplied for a player in the match
- **THEN** that player is simulated as holding no buttons, and the tick still completes

### Requirement: Fixed tick rate

The match SHALL advance in discrete ticks of a fixed duration of 1/20 of a
second. The simulation SHALL NOT read a wall clock, a frame time or a delta time
from its caller; tick number SHALL be the only measure of time inside the match.

#### Scenario: Timing is independent of how fast ticks are requested

- **WHEN** the same sequence of button states is applied to two matches that start identically, one stepped as fast as possible and one stepped slowly
- **THEN** both matches reach an identical world state after the same number of ticks

#### Scenario: Durations are counted in ticks

- **WHEN** a rule is specified in seconds, such as a five-second respawn
- **THEN** it takes effect after the corresponding whole number of ticks, independent of real elapsed time

### Requirement: Determinism

Advancing a match SHALL be deterministic: the same starting world and the same
sequence of button states SHALL always produce the same resulting world. The
simulation SHALL NOT use unseeded randomness, wall-clock time, iteration order
over unordered collections, or any input outside the world and the button states.

#### Scenario: Replay produces an identical result

- **WHEN** a recorded sequence of button states is applied twice to copies of the same starting world
- **THEN** the two resulting worlds are equal, tick for tick

### Requirement: The simulation has no rendering or transport dependencies

The simulation SHALL depend on nothing but the Python standard library. It SHALL
NOT import a graphics, windowing, audio or networking library, directly or
transitively, so that it can be exercised headlessly.

#### Scenario: Importing the simulation in a bare environment

- **WHEN** the simulation package is imported in an environment where no graphics or networking library is installed
- **THEN** the import succeeds and a match can be created and stepped

### Requirement: Movement and tile collision

A player SHALL move left and right, jump when standing on a solid tile, and fall
under gravity. Players SHALL NOT pass through solid tiles, and SHALL NOT leave
the bounds of the map. No entity SHALL move more than half a tile in either axis
within a single tick, so that collision can be resolved per tick without
tunnelling.

#### Scenario: Walking into a wall

- **WHEN** a player holds the left button while a solid tile is immediately to their left
- **THEN** the player does not move left and does not enter the tile

#### Scenario: Walking off an edge

- **WHEN** a player walks past the last solid tile of a platform
- **THEN** the player falls, gaining downward speed each tick until they land on a solid tile or leave the bottom of the map

#### Scenario: Jumping in mid-air

- **WHEN** a player holds the jump button while not standing on a solid tile
- **THEN** the player does not gain upward speed

#### Scenario: Falling out of the map

- **WHEN** a player falls below the bottom of the map
- **THEN** the player dies, exactly as if killed by another player, and the death is attributed to no killer

#### Scenario: Speed stays within the collision guarantee

- **WHEN** a player is at maximum horizontal speed and maximum falling speed
- **THEN** the distance moved in that tick is at most half a tile on each axis

### Requirement: The match map

Every match SHALL use the same fixed map: two base platforms roughly 25 tiles
apart, two intermediate platforms between them, and one center platform. Each
base SHALL carry one bed, one iron generator and one shop zone, belonging to the
team that spawns there. The route from either base toward the other SHALL NOT be
passable unaided: every gap along it SHALL be either too wide to clear or too
high to climb, so crossing requires building. Dropping back down onto your own
base MAY be possible unaided, since it brings a player no closer to the opposing
bed.

#### Scenario: Map layout at match start

- **WHEN** a new match is created
- **THEN** the world contains five platforms, and each of the two teams has exactly one bed, one generator and one shop zone on its own base

#### Scenario: The enemy base cannot be reached without building

- **WHEN** a player only runs and jumps, for any length of time, without ever placing a block
- **THEN** the player never stands on any platform other than their own base

#### Scenario: Crossing requires a bridge

- **WHEN** a player places blocks into the gap ahead of them and walks across
- **THEN** the player reaches the next platform toward the opposing base

### Requirement: Two teams with spawn points

A match SHALL have exactly two teams, red and blue, each with a spawn point on
its own base. Every player SHALL belong to exactly one team and SHALL start at
that team's spawn point with an empty inventory and full health.

#### Scenario: Match start state

- **WHEN** a match is created with one player per team
- **THEN** each player stands at their own team's spawn point with full health, no iron, and no items

### Requirement: Match state is inspectable as a value

The world SHALL be readable by a caller as plain data — player positions,
health, inventories, tiles, bed states, scores and the match outcome — so that a
renderer or a test can read it without calling into simulation logic.

#### Scenario: A caller reads the world after a tick

- **WHEN** a tick completes
- **THEN** the caller can read every player's position, health and inventory, the state of both beds, and whether the match has ended, from the world value alone
