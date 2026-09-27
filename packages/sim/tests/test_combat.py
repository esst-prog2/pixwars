"""Swinging, armor, cooldown and death."""

from pixwars_sim import Buttons, Team, new_match, step
from pixwars_sim import constants as C
from pixwars_sim.combat import kill

from sim_helpers import put


def _face_off(world, gap=1):
    """Red at tile 30, an enemy one tile to its right, both on solid floor."""
    red, blue = world.players[0], world.players[1]
    put(red, 30, 20)
    put(blue, 30 + gap, 20)
    for tx in range(28, 36):
        world.set_tile(tx, 22, C.TERRAIN)
    return red, blue


def test_hitting_an_opponent_in_reach(world):
    red, blue = _face_off(world)
    step(world, {0: Buttons(attack=True)})
    assert blue.health < C.MAX_HEALTH


def test_swinging_at_nothing(world):
    red, blue = _face_off(world, gap=10)
    step(world, {0: Buttons(attack=True)})
    assert blue.health == C.MAX_HEALTH


def test_swinging_the_wrong_way(world):
    red, blue = _face_off(world)
    step(world, {0: Buttons(attack=True, facing_left=True)})
    assert blue.health == C.MAX_HEALTH


def test_a_sword_hits_harder(world):
    bare, armed = world.copy(), world.copy()
    _face_off(bare)
    _face_off(armed)
    armed.players[0].has_sword = True
    step(bare, {0: Buttons(attack=True)})
    step(armed, {0: Buttons(attack=True)})
    assert armed.players[1].health < bare.players[1].health


def test_no_friendly_fire():
    w = new_match({0: Team.RED, 1: Team.RED})
    a, b = w.players[0], w.players[1]
    put(a, 30, 20)
    put(b, 31, 20)
    for tx in range(28, 34):
        w.set_tile(tx, 22, C.TERRAIN)
    step(w, {0: Buttons(attack=True)})
    assert b.health == C.MAX_HEALTH
    assert a.health == C.MAX_HEALTH


def test_attack_cooldown_limits_the_rate(world):
    red, blue = _face_off(world)
    red.has_sword = False
    held = Buttons(attack=True)
    for _ in range(C.ATTACK_COOLDOWN_TICKS):
        step(world, {0: held})
    assert blue.health == C.MAX_HEALTH - C.FIST_DAMAGE      # one hit, not five
    step(world, {0: held})
    assert blue.health == C.MAX_HEALTH - 2 * C.FIST_DAMAGE


def test_armor_reduces_damage(world):
    bare, armored = world.copy(), world.copy()
    _face_off(bare)
    _face_off(armored)
    armored.players[1].has_armor = True
    step(bare, {0: Buttons(attack=True)})
    step(armored, {0: Buttons(attack=True)})
    assert armored.players[1].health > bare.players[1].health


def test_armor_never_absorbs_a_hit_completely(world):
    red, blue = _face_off(world)
    blue.has_armor = True
    red.has_sword = False
    assert C.FIST_DAMAGE - C.ARMOR_REDUCTION <= 0       # this hit is fully absorbed
    step(world, {0: Buttons(attack=True)})
    assert blue.health == C.MAX_HEALTH - C.MIN_DAMAGE


def test_a_killing_blow_credits_both_counters(world):
    red, blue = _face_off(world)
    blue.health = 1
    step(world, {0: Buttons(attack=True)})
    assert not blue.alive
    assert red.kills == 1
    assert blue.deaths == 1


def test_attacking_a_dead_player_credits_nothing(world):
    red, blue = _face_off(world)
    kill(world, blue, None)
    before = red.kills
    for _ in range(C.ATTACK_COOLDOWN_TICKS * 3):
        step(world, {0: Buttons(attack=True)})
    assert red.kills == before


def test_a_dead_player_does_nothing(world):
    red, blue = _face_off(world)
    kill(world, red, None)
    snapshot = world.copy()
    everything = Buttons(
        left=True, right=True, jump=True, attack=True,
        place=True, break_=True, buy=1,
    )
    for _ in range(C.RESPAWN_TICKS - 1):
        step(world, {0: everything})
    assert not red.alive
    assert red.x == snapshot.players[0].x and red.y == snapshot.players[0].y
    assert blue.health == C.MAX_HEALTH
    assert world.tiles == snapshot.tiles
