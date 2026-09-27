"""The bot: button states in, nothing written."""

import pytest

from client_helpers import put

from pixwars_client.bot import BRIDGE_BLOCKS, decide
from pixwars_sim import Buttons, Team, new_match, step
from pixwars_sim import constants as C


@pytest.fixture
def world():
    return new_match()


def test_decide_returns_buttons_and_writes_nothing(world):
    before = world.copy()
    result = decide(world, 1)
    assert isinstance(result, Buttons)
    assert world == before


def test_decide_is_deterministic(world):
    a, b = world.copy(), world.copy()
    assert decide(a, 1) == decide(b, 1)
    for _ in range(50):
        step(a, {1: decide(a, 1)})
        step(b, {1: decide(b, 1)})
    assert decide(a, 1) == decide(b, 1)


def test_decide_on_a_dead_or_missing_player(world):
    from pixwars_sim.combat import kill

    kill(world, world.players[1], None)
    assert decide(world, 1) == Buttons()
    assert decide(world, 999) == Buttons()


def test_the_bot_attacks_an_enemy_in_reach(world):
    bot, human = world.players[1], world.players[0]
    bot.blocks = BRIDGE_BLOCKS
    bot.has_sword = True
    put(bot, 31, 20)
    put(human, 30, 20)
    for tx in range(28, 34):
        world.set_tile(tx, 22, C.TERRAIN)
    buttons = decide(world, 1)
    assert buttons.attack
    assert buttons.facing_left


def test_the_bot_shops_before_setting_off(world):
    bot = world.players[1]
    bot.iron = C.PRICE_BLOCKS
    x0, y0, x1, _ = world.teams[Team.BLUE].shop_zone
    put(bot, x0, y0)
    assert decide(world, 1).buy == 1

    bot.blocks = BRIDGE_BLOCKS
    bot.iron = C.PRICE_SWORD
    assert decide(world, 1).buy == 2


def test_the_bot_waits_in_the_shop_with_no_iron(world):
    bot = world.players[1]
    bot.iron = 0
    x0, y0, _, _ = world.teams[Team.BLUE].shop_zone
    put(bot, x0, y0)
    assert decide(world, 1) == Buttons()


def test_a_match_with_no_bot_involvement_runs_normally(world):
    for _ in range(100):
        step(world, {0: Buttons(right=True), 1: Buttons(left=True, facing_left=True)})
    assert world.tick == 100


def test_the_bot_finishes_the_game_against_an_idle_player(world):
    """The whole win condition, headless, with no keyboard and no window."""
    for tick in range(6000):
        step(world, {1: decide(world, 1)})
        if world.over:
            break
    assert world.over, (
        f"unfinished after {world.tick} ticks: "
        f"bot at {world.players[1].x // C.SUBPIXEL}, "
        f"blocks={world.players[1].blocks}, "
        f"red bed intact={world.teams[Team.RED].bed_intact}"
    )
    assert world.winner is Team.BLUE
    assert world.players[1].beds_broken == 1
    assert world.players[1].kills >= 1
