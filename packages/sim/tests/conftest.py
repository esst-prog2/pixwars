import pytest

from pixwars_sim import World, new_match


@pytest.fixture
def world() -> World:
    return new_match()
