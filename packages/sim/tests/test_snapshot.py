"""A world survives being turned into bytes and back."""

from pixwars_sim import Buttons, decode, encode, new_match, step

RIGHT = {0: Buttons(right=True), 1: Buttons(left=True, jump=True)}


def test_a_fresh_match_round_trips(world):
    assert decode(encode(world)) == world


def test_encoding_leaves_the_world_alone(world):
    before = world.copy()
    encode(world)
    assert world == before


def test_a_match_in_progress_round_trips_and_stays_in_step():
    world = new_match()
    for _ in range(100):                 # long enough to walk, jump and earn iron
        step(world, RIGHT)
    twin = decode(encode(world))
    assert twin == world
    for _ in range(100):
        step(world, RIGHT)
        step(twin, RIGHT)
    assert twin == world
