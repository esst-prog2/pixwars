"""Iron generators and the shop."""

from . import constants as C
from .buttons import Buttons
from .mapgen import in_shop_zone
from .world import Player, World


def generators(world: World) -> None:
    """Every GEN_TICKS, each team's generator grants one iron per living player."""
    if world.tick == 0 or world.tick % C.GEN_TICKS != 0:
        return
    for team in world.teams:
        for p in world.living(team):
            p.iron += 1


def _buy(p: Player, slot: int) -> None:
    if slot == 1:
        if p.iron < C.PRICE_BLOCKS or p.blocks >= C.BLOCK_STACK_LIMIT:
            return
        p.iron -= C.PRICE_BLOCKS
        p.blocks = min(p.blocks + C.BLOCKS_PER_PURCHASE, C.BLOCK_STACK_LIMIT)
    elif slot == 2:
        if p.has_sword or p.iron < C.PRICE_SWORD:
            return
        p.iron -= C.PRICE_SWORD
        p.has_sword = True
    elif slot == 3:
        if p.has_armor or p.iron < C.PRICE_ARMOR:
            return
        p.iron -= C.PRICE_ARMOR
        p.has_armor = True
    elif slot == 4:
        if p.has_pickaxe or p.iron < C.PRICE_PICKAXE:
            return
        p.iron -= C.PRICE_PICKAXE
        p.has_pickaxe = True


def purchases(world: World, inputs: dict[int, Buttons]) -> None:
    for pid, p in sorted(world.players.items()):
        if not p.alive:
            continue
        b = inputs.get(pid)
        if b is None or b.buy is None:
            continue
        if not in_shop_zone(world, p):
            continue
        _buy(p, b.buy)
