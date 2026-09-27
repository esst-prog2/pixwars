"""Respawning, elimination, and the end of a match."""

from . import constants as C
from .world import World


def _respawn(world: World) -> None:
    for p in sorted(world.players.values(), key=lambda p: p.id):
        if p.alive:
            continue
        if not world.teams[p.team].bed_intact:
            p.respawn_at = None          # death is final without a bed
            continue
        if p.respawn_at is None or world.tick < p.respawn_at:
            continue
        spawn = world.teams[p.team].spawn
        p.alive = True
        p.health = C.MAX_HEALTH
        p.x, p.y = spawn
        p.vx = p.vy = 0
        p.grounded = True       # a spawn point puts your feet on the surface
        p.respawn_at = None
        p.iron = 0
        p.blocks = 0
        p.has_sword = p.has_armor = p.has_pickaxe = False
        p.break_target = None
        p.break_progress = 0


def _eliminate(world: World) -> None:
    for team, state in world.teams.items():
        if state.bed_intact:
            continue
        if world.living(team):
            continue
        if not world.team_players(team):
            continue
        world.over = True
        world.winner = team.other
        return


def resolve(world: World) -> None:
    _respawn(world)
    _eliminate(world)
