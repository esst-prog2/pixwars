"""Placing and breaking tiles.

Placing prefers the floor directly under the player's leading edge, then the
floor just beyond it. That order is what makes bridging work while walking: a
player straddling two columns supports the one they are about to stand on
before reaching further out, so they never step into the hole they left.
"""

from . import constants as C
from .buttons import Buttons
from .world import Player, World


def _lead_col(p: Player) -> int:
    """The player's own column on the side they face."""
    if p.facing_left:
        return p.x // C.SUBPIXEL
    return (p.x + C.PLAYER_W - 1) // C.SUBPIXEL


def _ahead(p: Player) -> int:
    """The column just beyond the player's box, on the side they face."""
    lead = _lead_col(p)
    return lead - 1 if p.facing_left else lead + 1


def _feet_row(p: Player) -> int:
    return (p.y + C.PLAYER_H) // C.SUBPIXEL


def _body_rows(p: Player) -> tuple[int, int]:
    return p.y // C.SUBPIXEL, (p.y + C.PLAYER_H - 1) // C.SUBPIXEL


def _occupied_by_player(world: World, tx: int, ty: int) -> bool:
    for p in world.players.values():
        if not p.alive:
            continue
        cols = range(p.x // C.SUBPIXEL, (p.x + C.PLAYER_W - 1) // C.SUBPIXEL + 1)
        rows = range(p.y // C.SUBPIXEL, (p.y + C.PLAYER_H - 1) // C.SUBPIXEL + 1)
        if tx in cols and ty in rows:
            return True
    return False


def place_target(world: World, p: Player) -> tuple[int, int] | None:
    feet = _feet_row(p)
    upper, lower = _body_rows(p)
    beyond = _ahead(p)
    candidates = (
        (_lead_col(p), feet),   # the floor under my own leading edge
        (beyond, feet),         # the floor one step further on
        (beyond, lower),
        (beyond, upper),
    )
    for col, row in candidates:
        if world.tile(col, row) == C.EMPTY and not _occupied_by_player(world, col, row):
            return col, row
    return None


def break_target(world: World, p: Player) -> tuple[int, int] | None:
    col = _ahead(p)
    upper, lower = _body_rows(p)
    for row in (lower, upper, _feet_row(p)):
        kind = world.tile(col, row)
        if kind == C.PLACED:
            return col, row
        if kind == C.BED and world.tile_owner(col, row) != int(p.team):
            return col, row
    return None


def break_ticks(world: World, p: Player, target: tuple[int, int]) -> int:
    kind = world.tile(*target)
    if kind == C.BED:
        return C.BED_BREAK_PICK if p.has_pickaxe else C.BED_BREAK_HAND
    return C.BLOCK_BREAK_PICK if p.has_pickaxe else C.BLOCK_BREAK_HAND


def _finish_break(world: World, p: Player, target: tuple[int, int]) -> None:
    kind = world.tile(*target)
    if kind == C.BED:
        victim_team = None
        for team, state in world.teams.items():
            if target in state.bed_tiles:
                victim_team = team
                break
        if victim_team is not None:
            for tx, ty in world.teams[victim_team].bed_tiles:
                world.set_tile(tx, ty, C.EMPTY, C.OWNER_NONE)
            world.teams[victim_team].bed_intact = False
            p.beds_broken += 1
            # anyone of that team already waiting to respawn never comes back
            for other in world.team_players(victim_team):
                if not other.alive:
                    other.respawn_at = None
    else:
        world.set_tile(*target, C.EMPTY, C.OWNER_NONE)


def resolve(world: World, inputs: dict[int, Buttons]) -> None:
    for pid, p in sorted(world.players.items()):
        if not p.alive:
            p.break_target = None
            p.break_progress = 0
            continue
        b = inputs.get(pid)

        if b is not None and b.place and p.blocks > 0:
            target = place_target(world, p)
            if target is not None:
                world.set_tile(*target, C.PLACED, int(p.team))
                p.blocks -= 1

        if b is None or not b.break_:
            p.break_target = None
            p.break_progress = 0
            continue

        target = break_target(world, p)
        if target is None:
            p.break_target = None
            p.break_progress = 0
            continue

        if target != p.break_target:
            p.break_target = target
            p.break_progress = 0

        p.break_progress += 1
        if p.break_progress >= break_ticks(world, p, target):
            _finish_break(world, p, target)
            p.break_target = None
            p.break_progress = 0
