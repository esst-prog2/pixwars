# Spec Delta

## Purpose

Supplies an opponent for a single human player by deciding button states for a
bot each tick, so the whole match — including the win condition — can be played
and demonstrated before any networking exists.

## ADDED Requirements

### Requirement: The bot produces button states, nothing else

The bot SHALL be given a readable world and the id of the player it controls, and
SHALL return a button state of exactly the kind a keyboard produces. It SHALL NOT
modify the world, and SHALL NOT be invoked from inside the simulation.

#### Scenario: Asking the bot for a decision

- **WHEN** the bot is given a world and a player id
- **THEN** it returns a button state for that player and the world it was given is unchanged

#### Scenario: The simulation cannot distinguish bot from human

- **WHEN** a match is stepped with a bot-produced button state and a keyboard-produced button state
- **THEN** the simulation applies both by the same rules, with no special case for either

### Requirement: The bot plays toward the objective

The bot SHALL act so that a match against it can end: it SHALL move toward the
opposing team's bed, break it when within reach of it, and attack a living
opponent that is within its reach on the way.

#### Scenario: A bot left alone finishes the game

- **WHEN** a match is stepped with a bot opponent and a human player who takes no action at all
- **THEN** the match reaches an end within a bounded number of ticks, with the bot's team winning

#### Scenario: An opponent in reach

- **WHEN** a living opponent is within the bot's attack reach
- **THEN** the bot's returned button state includes the attack control

### Requirement: The bot is deterministic

Given the same world and player id, the bot SHALL return the same button state.
It SHALL NOT use unseeded randomness or wall-clock time, so that a match against
it can be replayed in a test.

#### Scenario: Asking twice

- **WHEN** the bot is asked for a decision twice from identical worlds
- **THEN** it returns the same button state both times

### Requirement: The bot is removable

The bot SHALL be usable or not usable per player, decided outside the simulation.
Removing the bot SHALL NOT require any change to the simulation's rules.

#### Scenario: A match with no bot at all

- **WHEN** a match is stepped with button states for every player coming from somewhere other than the bot
- **THEN** the match runs normally and no bot code is involved
