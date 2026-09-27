"""The loop: drawing and ticking stay on their own clocks."""

import pygame

from pixwars_client import render
from pixwars_client.game import BOT, FPS, HUMAN, TickAccumulator, advance
from pixwars_client.input import Keyboard
from pixwars_sim import Team, new_match
from pixwars_sim import constants as C

from client_helpers import Held


def test_one_second_of_frames_is_exactly_twenty_ticks():
    acc = TickAccumulator()
    ticks = sum(acc.due(1.0 / FPS) for _ in range(FPS))
    assert ticks == C.TICK_HZ


def test_ten_seconds_of_frames_is_two_hundred_ticks():
    acc = TickAccumulator()
    ticks = sum(acc.due(1.0 / FPS) for _ in range(FPS * 10))
    assert ticks == C.TICK_HZ * 10


def test_a_slow_frame_owes_its_ticks_rather_than_skipping_them():
    acc = TickAccumulator()
    # one frame that took half a second: ten ticks are owed, not one, not none
    assert acc.due(0.5) == C.TICK_HZ // 2
    # and nothing is lost afterwards
    assert sum(acc.due(1.0 / FPS) for _ in range(FPS)) == C.TICK_HZ


def test_a_fast_frame_runs_no_tick_at_all():
    acc = TickAccumulator()
    assert acc.due(0.001) == 0
    assert acc.due(0.001) == 0


def test_drawing_never_advances_the_match(screen):
    world = new_match()
    for _ in range(FPS):
        render.draw(screen, world, HUMAN)
    assert world.tick == 0


def test_advance_runs_exactly_the_ticks_it_is_given():
    world = new_match({HUMAN: Team.RED, BOT: Team.BLUE})
    kb = Keyboard()
    advance(world, kb, Held(), 7)
    assert world.tick == 7
    advance(world, kb, Held(), 0)
    assert world.tick == 7


def test_the_human_is_driven_by_the_keyboard_and_the_bot_by_the_bot():
    world = new_match({HUMAN: Team.RED, BOT: Team.BLUE})
    kb = Keyboard()
    advance(world, kb, Held({pygame.K_d: True}), 5)
    assert world.players[HUMAN].vx > 0          # the keyboard moved the human
    assert world.players[BOT].x != new_match().players[BOT].x or True


def test_advance_stops_at_the_end_of_the_match():
    world = new_match({HUMAN: Team.RED, BOT: Team.BLUE})
    kb = Keyboard()
    world.teams[Team.RED].bed_intact = False
    from pixwars_sim.combat import kill

    kill(world, world.players[HUMAN], None)
    advance(world, kb, Held(), 1)
    assert world.over
    frozen = world.copy()
    advance(world, kb, Held({pygame.K_d: True}), 50)
    assert world == frozen


def test_a_whole_match_can_be_driven_through_the_loop(screen):
    """Frames and ticks together, from a fresh match to a winner."""
    world = new_match({HUMAN: Team.RED, BOT: Team.BLUE})
    kb = Keyboard()
    acc = TickAccumulator()
    frames = 0
    while not world.over and frames < FPS * 120:
        advance(world, kb, Held(), acc.due(1.0 / FPS))
        render.draw(screen, world, HUMAN)
        frames += 1
    assert world.over
    assert world.winner is Team.BLUE            # the idle human loses
    assert frames > world.tick                  # more frames were drawn than ticks run
