"""Beds, respawning, elimination and the winner."""

from pixwars_sim import Buttons, Team, new_match, step
from pixwars_sim import constants as C
from pixwars_sim.combat import kill

from sim_helpers import put


def _next_to_bed(world, pid, victim_team):
    """Stand a player immediately to the left of victim_team's bed."""
    p = world.players[pid]
    bed_x = min(tx for tx, _ in world.teams[victim_team].bed_tiles)
    ty = world.teams[victim_team].bed_tiles[0][1]
    put(p, bed_x - 1, ty - 1)
    return p


def test_respawn_with_the_bed_intact(world):
    red = world.players[0]
    red.iron, red.blocks, red.has_sword = 9, 9, True
    kill(world, red, None)
    for _ in range(C.RESPAWN_TICKS - 1):
        step(world, {})
    assert not red.alive
    step(world, {})
    assert red.alive
    assert red.health == C.MAX_HEALTH
    assert (red.x, red.y) == world.teams[Team.RED].spawn
    assert (red.iron, red.blocks) == (0, 0)
    assert not red.has_sword


def test_a_dead_player_is_untargetable_during_the_delay(world):
    red, blue = world.players[0], world.players[1]
    put(red, 30, 20)
    put(blue, 31, 20)
    for tx in range(28, 34):
        world.set_tile(tx, 22, C.TERRAIN)
    kill(world, red, None)
    for _ in range(C.ATTACK_COOLDOWN_TICKS * 2):
        step(world, {1: Buttons(attack=True, facing_left=True)})
    assert blue.kills == 0
    assert red.deaths == 1


def test_breaking_the_enemy_bed(world):
    red = _next_to_bed(world, 0, Team.BLUE)
    for _ in range(C.BED_BREAK_HAND - 1):
        step(world, {0: Buttons(break_=True)})
    assert world.teams[Team.BLUE].bed_intact
    step(world, {0: Buttons(break_=True)})
    assert not world.teams[Team.BLUE].bed_intact
    assert red.beds_broken == 1
    for tx, ty in world.teams[Team.BLUE].bed_tiles:
        assert world.tile(tx, ty) == C.EMPTY


def test_you_cannot_break_your_own_bed(world):
    red = _next_to_bed(world, 0, Team.RED)
    for _ in range(C.BED_BREAK_HAND * 4):
        step(world, {0: Buttons(break_=True)})
    assert world.teams[Team.RED].bed_intact
    assert red.beds_broken == 0


def test_a_broken_bed_stays_broken(world):
    _next_to_bed(world, 0, Team.BLUE)
    for _ in range(C.BED_BREAK_HAND):
        step(world, {0: Buttons(break_=True)})
    assert not world.teams[Team.BLUE].bed_intact
    p = world.players[0]
    p.blocks = 10
    for _ in range(60):
        step(world, {0: Buttons(place=True)})
    assert not world.teams[Team.BLUE].bed_intact


def test_a_pickaxe_breaks_a_bed_faster(world):
    slow, fast = world.copy(), world.copy()
    _next_to_bed(slow, 0, Team.BLUE)
    p = _next_to_bed(fast, 0, Team.BLUE)
    p.has_pickaxe = True

    def ticks(w):
        for n in range(1, 300):
            step(w, {0: Buttons(break_=True)})
            if not w.teams[Team.BLUE].bed_intact:
                return n
        raise AssertionError("never broke")

    assert ticks(fast) < ticks(slow)


def test_death_is_final_once_the_bed_is_broken():
    w = new_match({0: Team.RED, 1: Team.RED, 2: Team.BLUE})
    w.teams[Team.RED].bed_intact = False
    red = w.players[0]
    kill(w, red, None)
    for _ in range(C.RESPAWN_TICKS * 3):
        step(w, {})
    assert not red.alive


def test_a_bed_broken_mid_respawn_cancels_it():
    w = new_match({0: Team.BLUE, 1: Team.BLUE, 2: Team.RED})
    waiting = w.players[0]
    kill(w, waiting, None)
    assert waiting.respawn_at is not None

    breaker = _next_to_bed(w, 2, Team.BLUE)
    for _ in range(C.BED_BREAK_HAND):
        step(w, {2: Buttons(break_=True)})
    assert not w.teams[Team.BLUE].bed_intact
    assert waiting.respawn_at is None

    for _ in range(C.RESPAWN_TICKS * 2):
        step(w, {})
    assert not waiting.alive
    assert not w.over            # a living teammate keeps the match going


def test_the_match_ends_on_the_tick_the_last_player_dies(world):
    red, blue = world.players[0], world.players[1]
    put(red, 30, 20)
    put(blue, 31, 20)
    for tx in range(28, 34):
        world.set_tile(tx, 22, C.TERRAIN)
    world.teams[Team.BLUE].bed_intact = False
    blue.health = 1

    assert not world.over
    step(world, {0: Buttons(attack=True)})
    assert world.over
    assert world.winner is Team.RED
    assert red.kills == 1


def test_all_dead_but_the_bed_stands_is_not_the_end(world):
    red = world.players[0]
    kill(world, red, None)
    assert world.living(Team.RED) == []
    step(world, {})
    assert not world.over
    for _ in range(C.RESPAWN_TICKS):
        step(world, {})
    assert red.alive
    assert not world.over


def test_stepping_a_finished_match_changes_nothing(world):
    world.teams[Team.BLUE].bed_intact = False
    kill(world, world.players[1], None)
    step(world, {})
    assert world.over and world.winner is Team.RED

    frozen = world.copy()
    everything = Buttons(left=True, right=True, jump=True, attack=True,
                         place=True, break_=True, buy=1)
    for _ in range(100):
        step(world, {0: everything, 1: everything})
    assert world == frozen
    assert world.winner is Team.RED


def test_counters_survive_a_respawn(world):
    red = world.players[0]
    red.kills, red.beds_broken = 3, 1
    kill(world, red, None)
    for _ in range(C.RESPAWN_TICKS + 1):
        step(world, {})
    assert red.alive
    assert (red.kills, red.beds_broken, red.deaths) == (3, 1, 1)


def test_the_final_scoreboard_is_readable(world):
    world.teams[Team.BLUE].bed_intact = False
    kill(world, world.players[1], None)
    step(world, {})
    assert world.over
    assert world.winner is Team.RED
    for p in world.players.values():
        assert isinstance(p.beds_broken, int)
        assert isinstance(p.kills, int)
        assert isinstance(p.deaths, int)
