"""PixWars simulation: the rules of a match, and nothing else.

This package imports only the standard library -- no rendering, no networking --
so a whole match can be played out in a test with no window open.
"""

from .buttons import NO_BUTTONS, Buttons
from .step import step
from .world import Player, Team, TeamState, World, new_match

__all__ = [
    "Buttons",
    "NO_BUTTONS",
    "Player",
    "Team",
    "TeamState",
    "World",
    "new_match",
    "step",
]
