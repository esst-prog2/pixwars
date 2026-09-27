import os

# every client test runs without a real window
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pytest

from pixwars_sim import new_match


@pytest.fixture(scope="session", autouse=True)
def _pygame():
    import pygame

    pygame.init()
    yield
    pygame.quit()


@pytest.fixture
def screen():
    import pygame

    from pixwars_client import render

    return pygame.display.set_mode((render.WINDOW_W, render.WINDOW_H))


@pytest.fixture
def match():
    return new_match()
