from pixwars_sim import Team, new_match
from pixwars_sim import constants as C

from sim_helpers import put


def test_copy_is_equal_but_independent(world):
    twin = world.copy()
    assert twin == world

    twin.players[0].x += C.SUBPIXEL
    twin.set_tile(30, 10, C.PLACED, C.OWNER_RED)
    twin.teams[Team.RED].bed_intact = False

    assert twin != world
    assert world.players[0].x != twin.players[0].x
    assert world.tile(30, 10) == C.EMPTY
    assert world.teams[Team.RED].bed_intact is True


def test_match_start_state(world):
    for p in world.players.values():
        spawn = world.teams[p.team].spawn
        assert (p.x, p.y) == spawn
        assert p.health == C.MAX_HEALTH
        assert p.iron == 0
        assert p.blocks == 0
        assert not (p.has_sword or p.has_armor or p.has_pickaxe)
        assert p.alive


def test_world_is_readable_as_plain_data(world):
    # everything a renderer or a test needs, without calling simulation logic
    p = world.players[0]
    assert isinstance(p.x, int) and isinstance(p.y, int)
    assert isinstance(p.health, int)
    assert isinstance(p.blocks, int)
    assert world.teams[Team.RED].bed_intact in (True, False)
    assert world.teams[Team.BLUE].bed_intact in (True, False)
    assert world.over is False
    assert world.winner is None
    assert (p.kills, p.deaths, p.beds_broken) == (0, 0, 0)
    assert isinstance(world.tiles, bytearray) and len(world.tiles) == C.MAP_W * C.MAP_H


def test_two_teams_with_one_player_each(world):
    assert {p.team for p in world.players.values()} == {Team.RED, Team.BLUE}
    assert len(world.team_players(Team.RED)) == 1
    assert len(world.team_players(Team.BLUE)) == 1


def test_custom_roster():
    w = new_match({0: Team.RED, 1: Team.RED, 2: Team.BLUE, 3: Team.BLUE})
    assert len(w.team_players(Team.RED)) == 2
    assert len(w.team_players(Team.BLUE)) == 2
