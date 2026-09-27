"""The one map every match is played on.

    y=16                           [ CENTER  28..35 ]
    y=22          [ mid 14..19 ]                      [ mid 44..49 ]
    y=27  [ RED BASE 1..11 ]                            [ BLUE BASE 52..62 ]
          bed gen shop                                    shop gen bed

The five platforms and the two bases are placed so that the route from one
base to the other cannot be walked or jumped: every gap along it is either
too wide to clear or too high to climb.  Crossing means building, which is the
point of the block stack.  Dropping back down onto your own base is allowed
and is meant to be -- it never brings a player any closer to the enemy bed.
"""

from . import constants as C
from .world import Team, TeamState, World

# (x0, x1) inclusive, surface row, thickness in rows
PLATFORMS = (
    (1, 11, 27, 3),     # red base
    (14, 19, 22, 3),    # red-side middle platform
    (28, 35, 16, 3),    # center island
    (44, 49, 22, 3),    # blue-side middle platform
    (52, 62, 27, 3),    # blue base
)

BASE_PLATFORMS = {Team.RED: 0, Team.BLUE: 4}

# per team: bed tiles, spawn tile, generator tile, shop zone (x0, y0, x1, y1)
_RED = {
    "bed": ((3, 26), (4, 26)),
    "spawn": (7, 25),
    "generator": (6, 26),
    "shop": (9, 25, 11, 26),
}
_BLUE = {
    "bed": ((59, 26), (60, 26)),
    "spawn": (56, 25),
    "generator": (57, 26),
    "shop": (52, 25, 54, 26),
}


def build_map(world: World) -> None:
    """Fill a fresh world's tiles and team state. Called once per match."""
    for x0, x1, surface, thickness in PLATFORMS:
        for tx in range(x0, x1 + 1):
            for ty in range(surface, surface + thickness):
                world.set_tile(tx, ty, C.TERRAIN)

    for team, spec in ((Team.RED, _RED), (Team.BLUE, _BLUE)):
        owner = C.OWNER_RED if team is Team.RED else C.OWNER_BLUE
        for tx, ty in spec["bed"]:
            world.set_tile(tx, ty, C.BED, owner)
        sx, sy = spec["spawn"]
        world.teams[team] = TeamState(
            team=team,
            bed_intact=True,
            bed_tiles=tuple(spec["bed"]),
            spawn=(sx * C.SUBPIXEL, sy * C.SUBPIXEL),
            generator=spec["generator"],
            shop_zone=spec["shop"],
        )


def in_shop_zone(world: World, player) -> bool:
    """True when this player stands inside their OWN team's shop zone."""
    x0, y0, x1, y1 = world.teams[player.team].shop_zone
    tx = player.x // C.SUBPIXEL
    ty = player.y // C.SUBPIXEL
    return x0 <= tx <= x1 and y0 <= ty <= y1 + 1
