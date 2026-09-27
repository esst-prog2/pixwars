"""Helpers shared by the client tests."""

from pixwars_sim import constants as C


class Held(dict):
    """Stands in for pygame.key.get_pressed()."""

    def __missing__(self, key):
        return False


def put(p, tx: int, ty: int) -> None:
    p.x = tx * C.SUBPIXEL
    p.y = ty * C.SUBPIXEL
    p.vx = p.vy = 0
    p.grounded = True
