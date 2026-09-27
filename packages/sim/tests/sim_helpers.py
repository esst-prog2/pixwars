"""Helpers shared by the simulation tests."""

from pixwars_sim import constants as C


def put(p, tx: int, ty: int) -> None:
    """Stand a player with their top-left corner at a tile coordinate."""
    p.x = tx * C.SUBPIXEL
    p.y = ty * C.SUBPIXEL
    p.vx = 0
    p.vy = 0
    p.grounded = True


def tile_of(p) -> tuple[int, int]:
    return p.x // C.SUBPIXEL, p.y // C.SUBPIXEL
