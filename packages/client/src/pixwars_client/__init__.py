"""PixWars client: a window, a keyboard, and a bot opponent."""

from .bot import decide
from .game import run

__all__ = ["decide", "run"]
