"""Keys in, one Buttons per tick out.

A key pressed and released entirely inside one tick would be invisible to
pygame's held-key snapshot, so presses are latched here and cleared once they
have been reported.
"""

import pygame

from pixwars_sim import Buttons

LEFT_KEYS = (pygame.K_a, pygame.K_LEFT)
RIGHT_KEYS = (pygame.K_d, pygame.K_RIGHT)
JUMP_KEYS = (pygame.K_SPACE, pygame.K_w, pygame.K_UP)
ATTACK_KEYS = (pygame.K_j,)
PLACE_KEYS = (pygame.K_k,)
BREAK_KEYS = (pygame.K_l,)

NUMBER_KEYS = {
    pygame.K_1: 1,
    pygame.K_2: 2,
    pygame.K_3: 3,
    pygame.K_4: 4,
}


class Keyboard:
    """Accumulates presses between ticks and reports them as button states.

    `held` is anything indexable by key code -- pygame.key.get_pressed(), or a
    plain dict in a test.
    """

    def __init__(self) -> None:
        self._tapped: set[int] = set()
        self.facing_left = False
        self.selected_slot = 1

    def key_down(self, key: int) -> None:
        self._tapped.add(key)

    @staticmethod
    def _any(held, keys) -> bool:
        return any(bool(held[k]) for k in keys)

    def _down(self, held, keys) -> bool:
        return self._any(held, keys) or any(k in self._tapped for k in keys)

    def buttons(self, held, in_shop: bool) -> Buttons:
        """The button state for the next tick. Clears the latched presses."""
        left = self._down(held, LEFT_KEYS)
        right = self._down(held, RIGHT_KEYS)
        if left and not right:
            self.facing_left = True
        elif right and not left:
            self.facing_left = False

        buy = None
        for key, slot in NUMBER_KEYS.items():
            if self._down(held, (key,)):
                if in_shop:
                    buy = slot
                else:
                    self.selected_slot = slot
                break

        result = Buttons(
            left=left,
            right=right,
            jump=self._down(held, JUMP_KEYS),
            attack=self._down(held, ATTACK_KEYS),
            place=self._down(held, PLACE_KEYS),
            break_=self._down(held, BREAK_KEYS),
            buy=buy,
            facing_left=self.facing_left,
        )
        self._tapped.clear()
        return result
