# Spec Delta

## Purpose

Lets players hurt and kill each other at close range, which is what makes a
broken bed matter and what ends a match.

## ADDED Requirements

### Requirement: Swinging at an opponent

A living player SHALL damage one living opponent within reach, in the direction
they face, when the attack control is pressed. Damage SHALL be higher for a
player carrying a stone sword than for a player carrying nothing.

#### Scenario: Hitting an opponent in reach

- **WHEN** a player presses attack while a living opponent is within reach in front of them
- **THEN** the opponent's health is reduced

#### Scenario: Swinging at nothing

- **WHEN** a player presses attack with no opponent within reach
- **THEN** no health changes anywhere in the match

#### Scenario: A sword hits harder

- **WHEN** two players with identical targets attack, one carrying a stone sword and one empty-handed
- **THEN** the sword-carrier's target loses more health

### Requirement: Attacks cannot hurt your own team

An attack SHALL NOT reduce the health of a player on the attacker's own team, and
SHALL NOT reduce the attacker's own health.

#### Scenario: Swinging at a teammate

- **WHEN** a player presses attack while a teammate is the only player within reach
- **THEN** no health changes

### Requirement: Attack cooldown

After a successful attack, a player SHALL be unable to damage anyone again until
a fixed cooldown has elapsed. Holding the attack control down SHALL NOT deal
damage faster than the cooldown allows.

#### Scenario: Holding the attack control

- **WHEN** a player holds the attack control against an opponent in reach for many ticks
- **THEN** damage is dealt at most once per cooldown period

### Requirement: Armor reduces incoming damage

A player carrying leather armor SHALL take less damage from each hit than the
same player without it. Damage SHALL never be reduced below one point, so armor
alone SHALL NOT make a player unkillable.

#### Scenario: Hitting an armored opponent

- **WHEN** identical attacks land on an armored and an unarmored opponent
- **THEN** the armored opponent loses less health

#### Scenario: Armor against a weak hit

- **WHEN** an attack whose reduced damage would fall to zero or below lands on an armored opponent
- **THEN** the opponent still loses one point of health

### Requirement: Death at zero health

A player whose health reaches zero or below SHALL die: they SHALL stop moving,
stop acting, and SHALL NOT be a valid target for attacks. The kill SHALL be
credited to the player who dealt the final damage, if there was one.

#### Scenario: A killing blow

- **WHEN** an attack reduces an opponent's health to zero or below
- **THEN** that opponent is dead, the attacker is credited with a kill, and the dead player is credited with a death

#### Scenario: Attacking a corpse

- **WHEN** a player presses attack while the only player in reach is already dead
- **THEN** nothing happens and no further kill is credited

### Requirement: Dead players do not act

A dead player SHALL NOT move, jump, place, break, buy or attack, regardless of
the button states supplied for them.

#### Scenario: Buttons held while dead

- **WHEN** every control is held for a dead player over many ticks
- **THEN** the world changes in no way attributable to that player
