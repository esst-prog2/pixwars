"""The keyboard: held keys and taps become one Buttons per tick."""

import pygame

from pixwars_client.input import Keyboard
from pixwars_sim import Team
from pixwars_sim import constants as C

from client_helpers import Held


def test_holding_a_movement_key(match):
    kb = Keyboard()
    held = Held({pygame.K_d: True})
    for _ in range(5):
        b = kb.buttons(held, in_shop=False)
        assert b.right and not b.left
        assert not b.facing_left
        assert b.buy is None


def test_a_press_and_release_inside_one_tick_is_not_lost(match):
    kb = Keyboard()
    kb.key_down(pygame.K_SPACE)              # pressed and released already
    b = kb.buttons(Held(), in_shop=False)
    assert b.jump
    # and it is only reported once
    assert not kb.buttons(Held(), in_shop=False).jump


def test_facing_persists_when_no_key_is_held(match):
    kb = Keyboard()
    kb.buttons(Held({pygame.K_a: True}), in_shop=False)
    assert kb.facing_left
    b = kb.buttons(Held(), in_shop=False)
    assert b.facing_left
    assert not b.left and not b.right


def test_number_keys_buy_inside_the_shop_zone(match):
    kb = Keyboard()
    b = kb.buttons(Held({pygame.K_2: True}), in_shop=True)
    assert b.buy == 2
    assert kb.selected_slot == 1              # unchanged


def test_number_keys_select_a_slot_outside_the_shop_zone(match):
    kb = Keyboard()
    b = kb.buttons(Held({pygame.K_3: True}), in_shop=False)
    assert b.buy is None
    assert kb.selected_slot == 3


def test_the_keyboard_only_produces_buttons(match):
    """It never touches the world."""
    kb = Keyboard()
    before = match.copy()
    kb.buttons(Held({pygame.K_d: True, pygame.K_j: True}), in_shop=False)
    assert match == before
