"""The collision guarantee, as an assertion rather than a comment."""

from pixwars_sim import constants as C


def test_no_speed_exceeds_half_a_tile_per_tick():
    # physics.py resolves each axis by checking only the destination box, which
    # is sound exactly while nothing can move a whole tile in one tick.
    assert max(C.WALK_SPEED, C.JUMP_SPEED, C.MAX_FALL) <= C.SUBPIXEL // 2


def test_jump_clears_one_block_but_not_a_platform():
    # a jump must be able to climb a single placed block...
    peak = 0
    v = C.JUMP_SPEED
    while v > 0:
        peak += v
        v -= C.GRAVITY
    assert peak > C.SUBPIXEL
    # ...and must not be able to climb to the platform above
    assert peak < 5 * C.SUBPIXEL
