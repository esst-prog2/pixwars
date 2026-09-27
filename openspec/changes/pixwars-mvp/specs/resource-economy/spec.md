# Spec Delta

## Purpose

Gives each team a trickle of iron from a generator on its own base and one shop
to spend it in, so that the blocks a player bridges with and the sword they fight
with have to be earned during the match.

## ADDED Requirements

### Requirement: Iron generators

Each base SHALL have one iron generator belonging to that base's team. At a fixed
interval, the generator SHALL grant one iron to every living player of its own
team. A generator SHALL NOT grant iron to the opposing team, and SHALL NOT grant
iron to a dead player.

#### Scenario: Iron accrues over time

- **WHEN** a match runs for several generator intervals with one living player per team
- **THEN** each player's iron has increased by one per elapsed interval

#### Scenario: A dead player earns nothing

- **WHEN** a generator interval elapses while a player is dead
- **THEN** that player gains no iron for that interval, and their living teammates still do

#### Scenario: Generators are per team

- **WHEN** the red generator grants iron
- **THEN** no blue player's iron changes

### Requirement: Iron is carried and lost on death

Iron SHALL be held per player, not per team. A player's iron SHALL be lost
entirely when that player dies.

#### Scenario: Dying with iron

- **WHEN** a player holding iron dies
- **THEN** their iron is zero when they next exist in the match, and their teammate's iron is unaffected

### Requirement: The shop is a zone on your own base

Each base SHALL have a shop zone. While a living player stands inside their own
team's shop zone, the four purchasable items and their prices SHALL be available
to that player. Outside the zone, and inside the opposing team's zone, no
purchase SHALL be possible.

#### Scenario: Standing in your own shop

- **WHEN** a living player stands inside their own team's shop zone
- **THEN** the shop is available to them and a purchase control buys the corresponding item

#### Scenario: Standing in the enemy shop

- **WHEN** a player stands inside the opposing team's shop zone
- **THEN** no purchase is possible

#### Scenario: Leaving the zone

- **WHEN** a player walks out of their shop zone
- **THEN** the shop is no longer available and further purchase controls do nothing

### Requirement: Four purchasable items

The shop SHALL offer exactly four items, each at a fixed iron price: a batch of
blocks, a stone sword, leather armor, and a pickaxe. Each item SHALL be bound to
one of the purchase controls one through four, and that binding SHALL be stable
for the whole match.

#### Scenario: Buying blocks

- **WHEN** a player in their shop zone with enough iron presses the purchase control bound to blocks
- **THEN** the batch of blocks is added to their stack and the price is deducted from their iron

#### Scenario: Buying a weapon or tool

- **WHEN** a player in their shop zone with enough iron buys the stone sword, the leather armor, or the pickaxe
- **THEN** they are carrying that item and the price is deducted from their iron

### Requirement: Purchases require sufficient iron

A purchase SHALL be refused when the player's iron is less than the item's price.
A refused purchase SHALL change nothing — no iron spent, no item granted.

#### Scenario: Not enough iron

- **WHEN** a player in their shop zone with less iron than an item's price attempts to buy it
- **THEN** no iron is deducted and the item is not granted

### Requirement: Buying a duplicate item

Buying an item the player already carries SHALL NOT stack a second copy of a
weapon, armor or tool, and SHALL NOT charge for it.

#### Scenario: Buying a second sword

- **WHEN** a player already carrying a stone sword buys the stone sword again
- **THEN** their iron is unchanged and they still carry exactly one stone sword

### Requirement: Purchased equipment is lost on death

A player's weapon, armor and tool SHALL be lost on death; a respawning player
SHALL start with an empty inventory and buy again.

#### Scenario: Respawning after buying

- **WHEN** a player carrying a sword, armor and a pickaxe dies while their bed stands
- **THEN** the player that respawns carries none of them
