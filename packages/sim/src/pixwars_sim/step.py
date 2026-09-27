"""The simulation's only public entry point.

The phase order matters and is part of the design:

    1. purchases   -- before movement, so a block bought this tick can be placed
    2. physics     -- x, then y, then landing
    3. building    -- place, break progress, beds
    4. combat      -- swings, damage, deaths
    5. match       -- respawn timers, elimination, the winner
    6. generators  -- living players only

Combat before the match phase is what makes a killing blow and the elimination
it causes land on the same tick.
"""

from . import building, combat, economy, match, physics
from .buttons import Buttons
from .world import World


def step(world: World, inputs: dict[int, Buttons] | None = None) -> World:
    """Advance the match by exactly one tick and return it.

    `inputs` maps player id to Buttons. Anything else -- a position, a number,
    an unknown player id -- is ignored: button states are the only way to
    affect the world.
    """
    if world.over:
        return world

    clean: dict[int, Buttons] = {}
    for pid, buttons in (inputs or {}).items():
        if pid in world.players and isinstance(buttons, Buttons):
            clean[pid] = buttons

    world.tick += 1

    economy.purchases(world, clean)
    physics.step_players(world, clean)
    building.resolve(world, clean)
    combat.resolve_attacks(world, clean)
    match.resolve(world)
    economy.generators(world)

    return world
