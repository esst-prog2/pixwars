"""The match: plain data a caller can read, and only the simulation may write."""

from dataclasses import dataclass, field, replace
from enum import IntEnum

from . import constants as C


class Team(IntEnum):
    RED = C.OWNER_RED
    BLUE = C.OWNER_BLUE

    @property
    def other(self) -> "Team":
        return Team.BLUE if self is Team.RED else Team.RED


@dataclass(slots=True)
class Player:
    id: int
    team: Team
    x: int = 0               # subpixels, left edge of a 1x2 tile box
    y: int = 0               # subpixels, top edge
    vx: int = 0
    vy: int = 0
    facing_left: bool = False
    grounded: bool = False

    alive: bool = True
    health: int = C.MAX_HEALTH
    respawn_at: int | None = None     # tick the player comes back on

    iron: int = 0
    blocks: int = 0
    has_sword: bool = False
    has_armor: bool = False
    has_pickaxe: bool = False

    attack_ready_at: int = 0
    break_target: tuple[int, int] | None = None
    break_progress: int = 0

    kills: int = 0
    deaths: int = 0
    beds_broken: int = 0


@dataclass(slots=True)
class TeamState:
    team: Team
    bed_intact: bool = True
    bed_tiles: tuple[tuple[int, int], ...] = ()
    spawn: tuple[int, int] = (0, 0)          # subpixels
    generator: tuple[int, int] = (0, 0)      # tile coords, for drawing
    shop_zone: tuple[int, int, int, int] = (0, 0, 0, 0)   # x0, y0, x1, y1 tiles


@dataclass(slots=True)
class World:
    tick: int = 0
    tiles: bytearray = field(default_factory=lambda: bytearray(C.MAP_W * C.MAP_H))
    owner: bytearray = field(default_factory=lambda: bytearray(C.MAP_W * C.MAP_H))
    players: dict[int, Player] = field(default_factory=dict)
    teams: dict[Team, TeamState] = field(default_factory=dict)
    over: bool = False
    winner: Team | None = None

    # --- tile access ------------------------------------------------------
    def tile(self, tx: int, ty: int) -> int:
        if ty >= C.MAP_H:
            return C.EMPTY          # below the map is open; you fall out of it
        if not (0 <= tx < C.MAP_W and 0 <= ty):
            return C.TERRAIN        # the sides and the ceiling are solid rock
        return self.tiles[ty * C.MAP_W + tx]

    def tile_owner(self, tx: int, ty: int) -> int:
        if not (0 <= tx < C.MAP_W and 0 <= ty < C.MAP_H):
            return C.OWNER_NONE
        return self.owner[ty * C.MAP_W + tx]

    def set_tile(self, tx: int, ty: int, kind: int, owner: int = C.OWNER_NONE) -> None:
        if 0 <= tx < C.MAP_W and 0 <= ty < C.MAP_H:
            self.tiles[ty * C.MAP_W + tx] = kind
            self.owner[ty * C.MAP_W + tx] = owner

    def is_solid(self, tx: int, ty: int) -> bool:
        return self.tile(tx, ty) != C.EMPTY

    # --- queries ----------------------------------------------------------
    def team_players(self, team: Team) -> list[Player]:
        return [p for p in self.players.values() if p.team is team]

    def living(self, team: Team) -> list[Player]:
        return [p for p in self.team_players(team) if p.alive]

    def copy(self) -> "World":
        """An independent copy, for replaying a match in a test."""
        return World(
            tick=self.tick,
            tiles=bytearray(self.tiles),
            owner=bytearray(self.owner),
            players={pid: replace(p) for pid, p in self.players.items()},
            teams={t: replace(s) for t, s in self.teams.items()},
            over=self.over,
            winner=self.winner,
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, World):
            return NotImplemented
        return (
            self.tick == other.tick
            and self.tiles == other.tiles
            and self.owner == other.owner
            and self.players == other.players
            and self.teams == other.teams
            and self.over == other.over
            and self.winner == other.winner
        )


def new_match(teams: dict[int, Team] | None = None) -> World:
    """A fresh match on the standard map.

    `teams` maps player id to team; the default is one player per team, which
    is the MVP's human-versus-bot arrangement.
    """
    from .mapgen import build_map

    if teams is None:
        teams = {0: Team.RED, 1: Team.BLUE}

    world = World()
    build_map(world)
    for pid, team in teams.items():
        spawn = world.teams[team].spawn
        world.players[pid] = Player(
            id=pid,
            team=team,
            x=spawn[0],
            y=spawn[1],
            facing_left=(team is Team.BLUE),
            grounded=True,      # a spawn point puts your feet on the surface
        )
    return world
