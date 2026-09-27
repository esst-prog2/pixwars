# Spec Delta

## Purpose

Lets players place and break blocks from a limited carried stack, which is the
only way to cross the gaps between platforms and the only way to reach an
opponent's bed.

## ADDED Requirements

### Requirement: Placing a block

A player holding blocks SHALL place one solid tile adjacent to themselves, in
the direction they face, when the place control is pressed. Placing SHALL consume
one block from the player's stack. A block SHALL NOT be placed into a tile that
is already solid, nor into a tile occupied by any player, nor outside the map.

#### Scenario: Placing a block on empty air

- **WHEN** a player with blocks presses place while facing an empty tile adjacent to them
- **THEN** that tile becomes solid, the player's block count drops by one, and the placed tile is recorded as belonging to the placing player's team

#### Scenario: Placing with an empty stack

- **WHEN** a player with no blocks presses place
- **THEN** no tile changes and nothing is consumed

#### Scenario: Placing into an occupied tile

- **WHEN** a player presses place while the target tile is already solid or contains a player
- **THEN** no tile changes and no block is consumed

#### Scenario: Bridging a gap

- **WHEN** a player repeatedly places blocks into the gap ahead of them and walks forward
- **THEN** the player crosses to the next platform

### Requirement: Breaking a block

A player SHALL break a placed block adjacent to themselves, in the direction they
face, by holding the break control for the block's break time. Breaking SHALL
remove the tile. A broken block SHALL NOT be returned to any player's stack.

#### Scenario: Breaking a placed block

- **WHEN** a player holds break against an adjacent placed block for its full break time
- **THEN** the tile becomes empty and no block is added to any inventory

#### Scenario: Releasing break early

- **WHEN** a player holds break against a block and releases before the break time elapses
- **THEN** the tile is unchanged and the accumulated progress is discarded

#### Scenario: Switching target mid-break

- **WHEN** a player breaking one block turns to face a different block before the first is broken
- **THEN** progress on the first block is discarded and progress on the new block starts from zero

### Requirement: Terrain cannot be broken

The tiles that make up the five platforms of the map SHALL NOT be breakable by
any player or tool. Only tiles placed by a player during the match, and beds,
SHALL be breakable.

#### Scenario: Attempting to break the map

- **WHEN** a player holds break against a tile that is part of a platform
- **THEN** the tile never breaks, no matter how long the control is held

### Requirement: A pickaxe speeds up breaking

A player carrying a pickaxe SHALL break breakable tiles in less time than a
player without one. The pickaxe SHALL NOT enable breaking anything that is
otherwise unbreakable.

#### Scenario: Breaking with and without a pickaxe

- **WHEN** two players break identical placed blocks, one carrying a pickaxe and one not
- **THEN** the player with the pickaxe finishes in fewer ticks

#### Scenario: A pickaxe against terrain

- **WHEN** a player with a pickaxe holds break against a platform tile
- **THEN** the tile still never breaks

### Requirement: Blocks are a limited carried stack

Blocks SHALL be carried as a counted stack, obtained only by purchase. The stack
SHALL have an upper limit, and a purchase that would exceed it SHALL fill to the
limit rather than overflow. A player's block stack SHALL be emptied on death.

#### Scenario: Buying past the stack limit

- **WHEN** a player at or near the block limit buys more blocks
- **THEN** their stack rises to at most the limit and the iron for the purchase is still spent

#### Scenario: Dying with blocks in hand

- **WHEN** a player carrying blocks dies
- **THEN** their block count is zero when they next exist in the match
