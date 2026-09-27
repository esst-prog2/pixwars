"""The map, and the invariant that makes the block stack necessary."""

from pixwars_sim import Buttons, Team, step
from pixwars_sim import constants as C
from pixwars_sim.mapgen import BASE_PLATFORMS, PLATFORMS, in_shop_zone

from sim_helpers import put


def _platform_of_column(tx: int, ty_surface: int) -> int | None:
    for i, (x0, x1, surface, _) in enumerate(PLATFORMS):
        if x0 <= tx <= x1 and surface == ty_surface:
            return i
    return None


def test_five_platforms_exist(world):
    assert len(PLATFORMS) == 5
    for x0, x1, surface, thickness in PLATFORMS:
        for tx in range(x0, x1 + 1):
            for ty in range(surface, surface + thickness):
                assert world.is_solid(tx, ty), (tx, ty)


def test_each_team_has_one_bed_one_generator_one_shop(world):
    for team in (Team.RED, Team.BLUE):
        state = world.teams[team]
        assert len(state.bed_tiles) == 2
        for tx, ty in state.bed_tiles:
            assert world.tile(tx, ty) == C.BED
            assert world.tile_owner(tx, ty) == int(team)
        assert state.bed_intact
        gx, gy = state.generator
        assert 0 <= gx < C.MAP_W and 0 <= gy < C.MAP_H
        x0, y0, x1, y1 = state.shop_zone
        assert x0 <= x1 and y0 <= y1

    # each team's furniture sits on its own base platform
    for team, index in BASE_PLATFORMS.items():
        x0, x1, _, _ = PLATFORMS[index]
        for tx, _ in world.teams[team].bed_tiles:
            assert x0 <= tx <= x1
        assert x0 <= world.teams[team].generator[0] <= x1
        assert x0 <= world.teams[team].shop_zone[0] <= x1


def test_spawn_is_on_your_own_base(world):
    for team, index in BASE_PLATFORMS.items():
        x0, x1, surface, _ = PLATFORMS[index]
        sx, sy = world.teams[team].spawn
        assert x0 <= sx // C.SUBPIXEL <= x1
        assert world.is_solid(sx // C.SUBPIXEL, surface)
        assert (sy + C.PLAYER_H) // C.SUBPIXEL == surface


def test_shop_zone_membership(world):
    red = world.players[0]
    x0, y0, x1, y1 = world.teams[Team.RED].shop_zone
    put(red, x0, y0)
    assert in_shop_zone(world, red)
    put(red, x1 + 2, y0)
    assert not in_shop_zone(world, red)
    # and the blue zone is not red's zone
    bx0, by0, _, _ = world.teams[Team.BLUE].shop_zone
    put(red, bx0, by0)
    assert not in_shop_zone(world, red)


def test_enemy_base_cannot_be_reached_without_building(world):
    """Running and jumping forever never leaves your own base platform."""
    for pid, toward_right in ((0, True), (1, False)):
        w = world.copy()
        me = w.players[pid]
        own = PLATFORMS[BASE_PLATFORMS[me.team]]
        buttons = Buttons(
            right=toward_right, left=not toward_right,
            jump=True, facing_left=not toward_right,
        )
        for _ in range(1200):          # a full minute of trying
            step(w, {pid: buttons})
            me = w.players[pid]
            if not me.alive or not me.grounded:
                continue
            tx = me.x // C.SUBPIXEL
            surface = (me.y + C.PLAYER_H) // C.SUBPIXEL
            landed = _platform_of_column(tx, surface)
            if landed is None:
                continue               # standing on a bed tile on their own base
            assert landed == BASE_PLATFORMS[me.team], (
                f"{me.team.name} reached platform {landed} without building"
            )


def test_a_bridge_crosses_the_first_gap(world):
    """Placing blocks ahead and walking forward reaches the next platform."""
    red = world.players[0]
    own_x0, own_x1, own_surface, _ = PLATFORMS[BASE_PLATFORMS[Team.RED]]
    put(red, own_x1, own_surface - 2)      # on the right edge of the red base
    red.blocks = C.BLOCK_STACK_LIMIT
    buttons = Buttons(right=True, place=True)

    for _ in range(400):
        step(world, {0: buttons})
        red = world.players[0]
        if not red.alive:
            break
        if red.x // C.SUBPIXEL > own_x1 + 1:
            break

    assert red.alive, "the player fell off while bridging"
    assert red.x // C.SUBPIXEL > own_x1, "the player never left their own base"
    assert red.blocks < C.BLOCK_STACK_LIMIT, "no blocks were consumed"
