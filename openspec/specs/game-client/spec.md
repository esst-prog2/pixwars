# game-client Specification

## Purpose

Puts the match on screen and turns a keyboard into button states, so that PixWars
can actually be played and the demo in the README can be performed from one
window.

## Requirements

### Requirement: Rendering is decoupled from the tick rate

The client SHALL draw at up to 60 frames a second while the match advances at its
own fixed 20 ticks a second. A frame SHALL draw the most recently simulated
world. The client SHALL NOT advance the match in order to draw a frame, and SHALL
NOT skip ticks in order to keep up with drawing.

#### Scenario: Frames outnumber ticks

- **WHEN** the client runs for one second under no load
- **THEN** roughly 60 frames have been drawn and exactly 20 ticks have been simulated

#### Scenario: A slow frame

- **WHEN** drawing a frame takes longer than one tick's duration
- **THEN** the match still advances by the number of ticks the elapsed time calls for, and no tick is skipped

### Requirement: The keyboard produces button states

The client SHALL translate held keys into the button state the simulation accepts,
once per tick: move left, move right, jump, attack, place, break, and the four
purchase controls. The client SHALL NOT act on the world in any other way — it
SHALL NOT move a player, edit a tile, or change an inventory directly.

#### Scenario: Holding a movement key

- **WHEN** the player holds the move-right key
- **THEN** every button state the client produces while it is held has move-right set, and the client changes nothing else

#### Scenario: A key pressed and released between ticks

- **WHEN** a key is pressed and released entirely within one tick's duration
- **THEN** the press is still reported in the next button state rather than being lost

### Requirement: The number keys select and buy

The number keys one through four SHALL buy the corresponding shop item while the
player is inside their own shop zone, and SHALL select the corresponding
inventory slot otherwise.

#### Scenario: Pressing a number key in the shop zone

- **WHEN** the player is inside their own shop zone and presses a number key
- **THEN** the corresponding purchase is attempted

#### Scenario: Pressing a number key elsewhere

- **WHEN** the player is outside their shop zone and presses a number key
- **THEN** the corresponding inventory slot becomes the selected one and nothing is bought

### Requirement: The shop zone shows its items and prices

While the player stands in their own shop zone, the client SHALL show the four
items, their prices and their number keys. It SHALL NOT pause the match or block
input while doing so.

#### Scenario: Entering the shop zone

- **WHEN** the player walks into their own shop zone
- **THEN** the four items, prices and keys are visible, and the match keeps advancing

#### Scenario: Leaving the shop zone

- **WHEN** the player walks out of the shop zone
- **THEN** the item list is no longer shown

### Requirement: The header shows match state

The client SHALL show a header carrying the player's current iron and the state of
the beds. When a bed is broken, the header SHALL say so, naming the team that lost
it.

#### Scenario: Iron changes

- **WHEN** the player's iron changes
- **THEN** the header shows the new amount on the next frame

#### Scenario: A bed is broken

- **WHEN** a team's bed is broken
- **THEN** the header states that that team's bed is destroyed, and keeps stating it for the rest of the match

### Requirement: The end of a match is shown

When the match ends, the client SHALL show the winning team and a scoreboard
listing every player's beds broken, kills and deaths, and SHALL keep showing it
until the player closes the window.

#### Scenario: A team wins

- **WHEN** the match ends
- **THEN** the winning team and the per-player beds, kills and deaths are on screen

#### Scenario: After the match has ended

- **WHEN** the player keeps pressing keys after the match has ended
- **THEN** the final screen stays on screen and the world does not change

### Requirement: The window can be closed at any time

The client SHALL exit cleanly when the window is closed, at any point before,
during or after a match, without leaving the process running.

#### Scenario: Closing mid-match

- **WHEN** the window is closed while a match is running
- **THEN** the process exits without error
