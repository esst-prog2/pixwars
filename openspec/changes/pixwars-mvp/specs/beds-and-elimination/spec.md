# Spec Delta

## Purpose

Makes a team's bed the thing that keeps it alive: while the bed stands its players
come back, and once the bed is gone every death is permanent, which is how a
PixWars match is won.

## ADDED Requirements

### Requirement: Respawn while your bed stands

A player who dies while their own team's bed is intact SHALL return to play at
their team's spawn point after a fixed delay of five seconds, with full health and
an empty inventory — no iron, no blocks, no weapon, no armor, no tool.

#### Scenario: Dying with the bed intact

- **WHEN** a player dies while their team's bed stands
- **THEN** after the respawn delay they are alive at their own spawn point with full health and nothing in their inventory

#### Scenario: During the respawn delay

- **WHEN** fewer ticks than the respawn delay have elapsed since a player's death
- **THEN** the player is still dead, cannot be attacked, and cannot act

### Requirement: Breaking a bed

A player SHALL break the opposing team's bed by holding the break control against
it until its break time elapses. A player SHALL NOT break their own team's bed. A
broken bed SHALL stay broken for the rest of the match, and the break SHALL be
credited to the player who finished it.

#### Scenario: Breaking the enemy bed

- **WHEN** a player holds break against the opposing team's bed for its full break time
- **THEN** that bed is broken, and the player is credited with one bed broken

#### Scenario: Breaking your own bed

- **WHEN** a player holds break against their own team's bed for any length of time
- **THEN** the bed is not broken

#### Scenario: A broken bed cannot be restored

- **WHEN** a bed has been broken
- **THEN** no action by any player during the match makes it intact again

### Requirement: Death is final once the bed is broken

A player who dies while their own team's bed is broken SHALL NOT respawn. They
SHALL remain dead for the rest of the match.

#### Scenario: Dying after losing the bed

- **WHEN** a player dies while their team's bed is broken
- **THEN** the player is still dead after the respawn delay has elapsed, and after any further number of ticks

#### Scenario: A player already waiting to respawn when the bed breaks

- **WHEN** a player is dead and waiting out the respawn delay, and their team's bed is broken before the delay elapses
- **THEN** the player does not respawn

### Requirement: The match ends when a team is eliminated

A team SHALL be eliminated when its bed is broken and all of its players are dead.
The match SHALL end on the tick that condition becomes true, and the other team
SHALL be the winner. Once the match has ended, further button states SHALL NOT
change the world.

#### Scenario: The last player of a bedless team dies

- **WHEN** the final living player of a team whose bed is broken dies
- **THEN** the match is over on that same tick and the opposing team is recorded as the winner

#### Scenario: All players dead but the bed stands

- **WHEN** every player of a team is dead but that team's bed is intact
- **THEN** the match is not over, and those players respawn as normal

#### Scenario: Ticking a finished match

- **WHEN** button states are supplied after the match has ended
- **THEN** nothing in the world changes and the recorded winner stays the same

### Requirement: Scoreboard counters

For every player, the match SHALL count beds broken, kills and deaths, from the
start of the match. These counters SHALL be readable while the match is running
and after it has ended, and SHALL NOT be reset by death or respawn.

#### Scenario: Counters survive a respawn

- **WHEN** a player with recorded kills and beds broken dies and respawns
- **THEN** their kill and bed counters are unchanged and their death counter has increased by one

#### Scenario: Reading the final scoreboard

- **WHEN** the match has ended
- **THEN** the winner and every player's beds broken, kills and deaths can be read from the world
