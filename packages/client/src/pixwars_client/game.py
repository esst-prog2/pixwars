"""The loop: 60 frames a second drawing a match that advances 20 times a second.

The two rates are kept apart by an accumulator. Drawing never advances the
match, and a slow frame never causes a tick to be skipped -- the time it took is
owed and gets paid back as whole ticks on the next pass.
"""

import pygame

from pixwars_sim import Team, World, new_match, step
from pixwars_sim import constants as C
from pixwars_sim.mapgen import in_shop_zone

from . import render
from .bot import decide
from .input import Keyboard

HUMAN = 0
BOT = 1
FPS = 60


NS = 1_000_000_000


class TickAccumulator:
    """Turns elapsed real seconds into a whole number of owed ticks.

    The running total is kept in integer nanoseconds rather than seconds: a tick
    of 1/20 s is not exactly representable in binary, and accumulating it as a
    float loses a tick every so often (0.5 // 0.05 is 9, not 10).
    """

    def __init__(self, tick_hz: int = C.TICK_HZ) -> None:
        self.tick_ns = NS // tick_hz
        self._owed_ns = 0

    @property
    def tick_seconds(self) -> float:
        return self.tick_ns / NS

    def due(self, elapsed: float) -> int:
        self._owed_ns += round(elapsed * NS)
        ticks = self._owed_ns // self.tick_ns
        self._owed_ns -= ticks * self.tick_ns
        return ticks


def advance(world: World, keyboard: Keyboard, held, ticks: int) -> None:
    """Run `ticks` ticks of the match. The only place inputs are gathered."""
    for _ in range(ticks):
        if world.over:
            return
        me = world.players.get(HUMAN)
        in_shop = me is not None and me.alive and in_shop_zone(world, me)
        inputs = {
            HUMAN: keyboard.buttons(held, in_shop),
            BOT: decide(world, BOT),
        }
        step(world, inputs)


def run() -> None:
    pygame.init()
    pygame.display.set_caption("PixWars")
    screen = pygame.display.set_mode((render.WINDOW_W, render.WINDOW_H))
    clock = pygame.time.Clock()

    world = new_match({HUMAN: Team.RED, BOT: Team.BLUE})
    keyboard = Keyboard()
    accumulator = TickAccumulator()

    running = True
    while running:
        elapsed = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                else:
                    keyboard.key_down(event.key)

        advance(world, keyboard, pygame.key.get_pressed(), accumulator.due(elapsed))
        render.draw(screen, world, HUMAN)
        pygame.display.flip()

    pygame.quit()
