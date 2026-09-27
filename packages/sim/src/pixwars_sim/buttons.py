"""The only thing a caller may hand to the simulation.

There is deliberately no field on this class that could carry a position, a
velocity, a health value or an inventory: the rule that a client cannot tell
the host where it is holds because there is nowhere to put it, not because
something validates it away.
"""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Buttons:
    """The controls held down by one player for one tick."""

    left: bool = False
    right: bool = False
    jump: bool = False
    attack: bool = False
    place: bool = False
    break_: bool = False
    buy: int | None = None       # 1..4, or None for no purchase this tick
    facing_left: bool = False    # a direction, not a coordinate


NO_BUTTONS = Buttons()
