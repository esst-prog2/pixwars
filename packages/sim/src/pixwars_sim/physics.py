"""Movement and tile collision.

Axes are resolved separately, and no velocity may exceed half a tile per tick
(see the assertion in the tests), so checking the destination box is enough --
nothing can tunnel through a tile.
"""

from . import constants as C
from .buttons import Buttons
from .combat import kill
from .world import Player, World


def _rows(y: int) -> range:
    return range(y // C.SUBPIXEL, (y + C.PLAYER_H - 1) // C.SUBPIXEL + 1)


def _cols(x: int) -> range:
    return range(x // C.SUBPIXEL, (x + C.PLAYER_W - 1) // C.SUBPIXEL + 1)


def _move_x(world: World, p: Player) -> None:
    if p.vx == 0:
        return
    nx = p.x + p.vx
    if p.vx > 0:
        edge = nx + C.PLAYER_W - 1
        tx = edge // C.SUBPIXEL
        if any(world.is_solid(tx, ty) for ty in _rows(p.y)):
            nx = tx * C.SUBPIXEL - C.PLAYER_W
            p.vx = 0
    else:
        tx = nx // C.SUBPIXEL
        if any(world.is_solid(tx, ty) for ty in _rows(p.y)):
            nx = (tx + 1) * C.SUBPIXEL
            p.vx = 0
    p.x = nx


def _move_y(world: World, p: Player) -> None:
    ny = p.y + p.vy
    if p.vy > 0:
        edge = ny + C.PLAYER_H - 1
        ty = edge // C.SUBPIXEL
        if any(world.is_solid(tx, ty) for tx in _cols(p.x)):
            ny = ty * C.SUBPIXEL - C.PLAYER_H
            p.vy = 0
            p.grounded = True
    elif p.vy < 0:
        ty = ny // C.SUBPIXEL
        if any(world.is_solid(tx, ty) for tx in _cols(p.x)):
            ny = (ty + 1) * C.SUBPIXEL
            p.vy = 0
    p.y = ny


def step_players(world: World, inputs: dict[int, Buttons]) -> None:
    for pid, p in sorted(world.players.items()):
        if not p.alive:
            continue
        b = inputs.get(pid)

        p.vx = 0
        if b is not None:
            if b.left and not b.right:
                p.vx = -C.WALK_SPEED
            elif b.right and not b.left:
                p.vx = C.WALK_SPEED
            p.facing_left = b.facing_left
            if b.jump and p.grounded:
                p.vy = -C.JUMP_SPEED
                p.grounded = False

        p.vy = min(p.vy + C.GRAVITY, C.MAX_FALL)

        was_grounded = p.grounded
        p.grounded = False
        _move_x(world, p)
        _move_y(world, p)

        # still standing on something? (walking off an edge clears it)
        if not p.grounded and was_grounded and p.vy >= 0:
            below = (p.y + C.PLAYER_H) // C.SUBPIXEL
            p.grounded = any(world.is_solid(tx, below) for tx in _cols(p.x))

        if p.y > C.MAP_H * C.SUBPIXEL:
            kill(world, p, None)
