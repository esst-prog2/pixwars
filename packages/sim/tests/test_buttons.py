from dataclasses import FrozenInstanceError, fields

import pytest

from pixwars_sim import Buttons


def test_buttons_are_frozen():
    b = Buttons(left=True)
    with pytest.raises(FrozenInstanceError):
        b.left = False


def test_buttons_carry_no_position():
    # the "a client cannot send a position" rule holds because there is nowhere
    # on this class to put one
    names = {f.name for f in fields(Buttons)}
    assert names == {
        "left", "right", "jump", "attack", "place", "break_", "buy", "facing_left",
    }
    for forbidden in ("x", "y", "vx", "vy", "health", "iron", "position"):
        assert forbidden not in names


def test_default_buttons_hold_nothing():
    b = Buttons()
    assert not any([b.left, b.right, b.jump, b.attack, b.place, b.break_])
    assert b.buy is None
