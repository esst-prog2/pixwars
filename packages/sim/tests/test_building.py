"""Placing and breaking."""

from pixwars_sim import Buttons, Team, step
from pixwars_sim import constants as C

from sim_helpers import put


def _standing(world, pid=0, tx=30, ty=20):
    p = world.players[pid]
    put(p, tx, ty)
    for x in range(tx - 2, tx + 3):
        world.set_tile(x, ty + 2, C.TERRAIN)
    return p


def test_placing_a_block_on_air_consumes_one(world):
    p = _standing(world)
    p.blocks = 5
    world.set_tile(31, 22, C.EMPTY)          # a hole in the floor ahead
    step(world, {0: Buttons(place=True)})
    assert world.tile(31, 22) == C.PLACED
    assert world.tile_owner(31, 22) == int(Team.RED)
    assert p.blocks == 4


def test_placing_with_an_empty_stack_does_nothing(world):
    p = _standing(world)
    p.blocks = 0
    world.set_tile(31, 22, C.EMPTY)
    step(world, {0: Buttons(place=True)})
    assert world.tile(31, 22) == C.EMPTY
    assert p.blocks == 0


def test_placing_into_a_solid_tile_does_nothing(world):
    p = _standing(world)
    p.blocks = 3
    # every candidate tile ahead is already solid
    for row in (20, 21, 22):
        world.set_tile(31, row, C.TERRAIN)
    step(world, {0: Buttons(place=True)})
    assert p.blocks == 3


def test_placing_into_a_tile_occupied_by_a_player(world):
    p = _standing(world, 0, 30, 20)
    other = world.players[1]
    put(other, 31, 20)
    p.blocks = 3
    world.set_tile(31, 22, C.TERRAIN)        # floor is there, so candidates are body rows
    step(world, {0: Buttons(place=True)})
    assert p.blocks == 3
    assert world.tile(31, 20) == C.EMPTY
    assert world.tile(31, 21) == C.EMPTY


def test_breaking_a_placed_block_takes_its_full_time(world):
    p = _standing(world)
    world.set_tile(31, 21, C.PLACED, int(Team.BLUE))
    for _ in range(C.BLOCK_BREAK_HAND - 1):
        step(world, {0: Buttons(break_=True)})
    assert world.tile(31, 21) == C.PLACED
    step(world, {0: Buttons(break_=True)})
    assert world.tile(31, 21) == C.EMPTY
    assert p.blocks == 0                     # nothing is returned to inventory


def test_releasing_break_discards_progress(world):
    p = _standing(world)
    world.set_tile(31, 21, C.PLACED, int(Team.BLUE))
    for _ in range(C.BLOCK_BREAK_HAND - 1):
        step(world, {0: Buttons(break_=True)})
    step(world, {0: Buttons()})               # let go
    assert p.break_progress == 0
    assert p.break_target is None
    step(world, {0: Buttons(break_=True)})
    assert world.tile(31, 21) == C.PLACED     # has to start over


def test_switching_target_resets_progress(world):
    p = _standing(world)
    world.set_tile(31, 21, C.PLACED, int(Team.BLUE))
    world.set_tile(29, 21, C.PLACED, int(Team.BLUE))
    for _ in range(C.BLOCK_BREAK_HAND - 1):
        step(world, {0: Buttons(break_=True)})
    step(world, {0: Buttons(break_=True, facing_left=True)})
    assert p.break_target == (29, 21)
    assert p.break_progress == 1
    assert world.tile(31, 21) == C.PLACED


def test_terrain_never_breaks(world):
    _standing(world)
    world.set_tile(31, 21, C.TERRAIN)
    for _ in range(C.BED_BREAK_HAND * 5):
        step(world, {0: Buttons(break_=True)})
    assert world.tile(31, 21) == C.TERRAIN


def test_terrain_never_breaks_with_a_pickaxe(world):
    p = _standing(world)
    p.has_pickaxe = True
    world.set_tile(31, 21, C.TERRAIN)
    for _ in range(C.BED_BREAK_HAND * 5):
        step(world, {0: Buttons(break_=True)})
    assert world.tile(31, 21) == C.TERRAIN


def test_a_pickaxe_breaks_faster(world):
    bare = world.copy()
    picked = world.copy()
    for w, pick in ((bare, False), (picked, True)):
        p = _standing(w)
        p.has_pickaxe = pick
        w.set_tile(31, 21, C.PLACED, int(Team.BLUE))

    def ticks_to_break(w):
        for n in range(1, 200):
            step(w, {0: Buttons(break_=True)})
            if w.tile(31, 21) == C.EMPTY:
                return n
        raise AssertionError("never broke")

    assert ticks_to_break(picked) < ticks_to_break(bare)


def test_block_stack_limit_fills_and_still_charges(world):
    p = _standing(world)
    x0, y0, _, _ = world.teams[Team.RED].shop_zone
    put(p, x0, y0)
    p.blocks = C.BLOCK_STACK_LIMIT - 2
    p.iron = 50
    step(world, {0: Buttons(buy=1)})
    assert p.blocks == C.BLOCK_STACK_LIMIT
    assert p.iron == 50 - C.PRICE_BLOCKS


def test_blocks_are_lost_on_death(world):
    p = _standing(world)
    p.blocks = 20
    from pixwars_sim.combat import kill
    kill(world, p, None)
    assert p.blocks == 0
