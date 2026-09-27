"""Movement, collision, and the guarantee that nothing tunnels."""

from pixwars_sim import Buttons, Team, step
from pixwars_sim import constants as C

from sim_helpers import put


def test_walking_into_a_wall_does_not_enter_it(world):
    p = world.players[0]
    put(p, 20, 20)
    world.set_tile(19, 20, C.TERRAIN)
    world.set_tile(19, 21, C.TERRAIN)
    world.set_tile(20, 22, C.TERRAIN)       # floor
    for _ in range(20):
        step(world, {0: Buttons(left=True, facing_left=True)})
    assert p.x // C.SUBPIXEL == 20
    assert not world.is_solid(19, 20) or p.x >= 20 * C.SUBPIXEL


def test_walking_off_an_edge_falls_with_increasing_speed(world):
    p = world.players[0]
    put(p, 20, 20)
    world.set_tile(20, 22, C.TERRAIN)       # a single floor tile
    speeds = []
    for _ in range(6):
        step(world, {0: Buttons(right=True)})
        speeds.append(p.vy)
    assert speeds == sorted(speeds)
    assert speeds[-1] > 0


def test_landing_stops_the_fall(world):
    p = world.players[0]
    put(p, 20, 10)
    p.grounded = False
    for ty in range(20, 23):
        for tx in range(18, 23):
            world.set_tile(tx, ty, C.TERRAIN)
    for _ in range(60):
        step(world, {0: Buttons()})
    assert p.grounded
    assert p.vy == 0
    assert (p.y + C.PLAYER_H) // C.SUBPIXEL == 20


def test_jumping_in_mid_air_does_nothing(world):
    p = world.players[0]
    put(p, 20, 10)
    p.grounded = False
    step(world, {0: Buttons(jump=True)})
    assert p.vy > 0                     # falling, not rising


def test_jumping_from_the_ground_rises(world):
    p = world.players[0]
    spawn_tx = world.teams[Team.RED].spawn[0] // C.SUBPIXEL
    step(world, {0: Buttons(jump=True)})
    assert p.vy < 0
    top = p.y
    for _ in range(30):
        step(world, {0: Buttons()})
        top = min(top, p.y)
    assert top < world.teams[Team.RED].spawn[1] - C.SUBPIXEL   # cleared one tile


def test_cannot_leave_the_sides_or_the_ceiling(world):
    p = world.players[0]
    put(p, 0, 20)
    world.set_tile(0, 22, C.TERRAIN)
    for _ in range(40):
        step(world, {0: Buttons(left=True, jump=True, facing_left=True)})
    assert p.x >= 0
    assert p.y >= 0


def test_falling_out_of_the_map_kills_with_no_killer(world):
    red, blue = world.players[0], world.players[1]
    put(red, 30, C.MAP_H - 3)
    red.grounded = False
    for _ in range(40):
        step(world, {0: Buttons()})
        if not red.alive:
            break
    assert not red.alive
    assert red.deaths == 1
    assert blue.kills == 0


def test_no_axis_moves_more_than_half_a_tile_in_a_tick(world):
    p = world.players[0]
    put(p, 30, 2)
    p.grounded = False
    p.vy = C.MAX_FALL
    for _ in range(30):
        before = (p.x, p.y)
        step(world, {0: Buttons(right=True)})
        if not p.alive:
            break
        assert abs(p.x - before[0]) <= C.SUBPIXEL // 2
        assert abs(p.y - before[1]) <= C.SUBPIXEL // 2
