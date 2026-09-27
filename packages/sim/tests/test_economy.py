"""Generators and the shop."""

from pixwars_sim import Buttons, Team, step
from pixwars_sim import constants as C
from pixwars_sim.combat import kill

from sim_helpers import put


def _in_own_shop(world, pid):
    p = world.players[pid]
    x0, y0, _, _ = world.teams[p.team].shop_zone
    put(p, x0, y0)
    return p


def test_iron_accrues_once_per_interval(world):
    for intervals in range(1, 4):
        for _ in range(C.GEN_TICKS):
            step(world, {})
        assert world.players[0].iron == intervals
        assert world.players[1].iron == intervals


def test_a_dead_player_earns_no_iron(world):
    red, blue = world.players[0], world.players[1]
    kill(world, red, None)
    for _ in range(C.GEN_TICKS):
        step(world, {})
    assert red.iron == 0
    assert blue.iron == 1


def test_a_dead_players_living_teammate_still_earns():
    from pixwars_sim import new_match

    w = new_match({0: Team.RED, 1: Team.RED, 2: Team.BLUE})
    kill(w, w.players[0], None)
    for _ in range(C.GEN_TICKS):
        step(w, {})
    assert w.players[0].iron == 0
    assert w.players[1].iron == 1


def test_generators_are_per_team(world):
    # red's generator must never change blue's iron: grant one interval and
    # check each player only got their own team's iron
    for _ in range(C.GEN_TICKS):
        step(world, {})
    assert world.players[0].iron == 1 and world.players[1].iron == 1
    # kill blue; red keeps earning, blue does not
    kill(world, world.players[1], None)
    for _ in range(C.GEN_TICKS):
        step(world, {})
    assert world.players[0].iron == 2
    assert world.players[1].iron == 0


def test_buying_blocks(world):
    p = _in_own_shop(world, 0)
    p.iron = C.PRICE_BLOCKS
    step(world, {0: Buttons(buy=1)})
    assert p.blocks == C.BLOCKS_PER_PURCHASE
    assert p.iron == 0


def test_buying_each_item(world):
    for slot, price, attr in (
        (2, C.PRICE_SWORD, "has_sword"),
        (3, C.PRICE_ARMOR, "has_armor"),
        (4, C.PRICE_PICKAXE, "has_pickaxe"),
    ):
        w = world.copy()
        p = _in_own_shop(w, 0)
        p.iron = price
        step(w, {0: Buttons(buy=slot)})
        assert getattr(p, attr) is True
        assert p.iron == 0


def test_no_purchase_outside_your_shop_zone(world):
    p = world.players[0]
    put(p, 20, 20)
    p.iron = 99
    step(world, {0: Buttons(buy=2)})
    assert not p.has_sword
    assert p.iron == 99


def test_no_purchase_in_the_enemy_shop_zone(world):
    p = world.players[0]
    bx0, by0, _, _ = world.teams[Team.BLUE].shop_zone
    put(p, bx0, by0)
    p.iron = 99
    step(world, {0: Buttons(buy=2)})
    assert not p.has_sword
    assert p.iron == 99


def test_leaving_the_zone_stops_purchases(world):
    p = _in_own_shop(world, 0)
    p.iron = 99
    step(world, {0: Buttons(buy=2)})
    assert p.has_sword
    put(p, 20, 20)
    step(world, {0: Buttons(buy=4)})
    assert not p.has_pickaxe


def test_not_enough_iron_changes_nothing(world):
    p = _in_own_shop(world, 0)
    p.iron = C.PRICE_SWORD - 1
    step(world, {0: Buttons(buy=2)})
    assert not p.has_sword
    assert p.iron == C.PRICE_SWORD - 1


def test_buying_a_duplicate_does_not_charge(world):
    p = _in_own_shop(world, 0)
    p.iron = C.PRICE_SWORD * 3
    step(world, {0: Buttons(buy=2)})
    left = p.iron
    step(world, {0: Buttons(buy=2)})
    assert p.iron == left
    assert p.has_sword


def test_iron_and_equipment_are_lost_on_death(world):
    p = _in_own_shop(world, 0)
    p.iron = 40
    step(world, {0: Buttons(buy=2)})
    step(world, {0: Buttons(buy=3)})
    step(world, {0: Buttons(buy=4)})
    step(world, {0: Buttons(buy=1)})
    assert p.has_sword and p.has_armor and p.has_pickaxe and p.blocks

    kill(world, p, None)
    for _ in range(C.RESPAWN_TICKS + 1):
        step(world, {})
    assert p.alive
    assert (p.iron, p.blocks) == (0, 0)
    assert not (p.has_sword or p.has_armor or p.has_pickaxe)
