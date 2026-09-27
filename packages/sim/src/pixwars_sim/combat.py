"""Swinging, damage, armor and death."""

from . import constants as C
from .buttons import Buttons
from .world import Player, World


def damage_of(attacker: Player) -> int:
    return C.SWORD_DAMAGE if attacker.has_sword else C.FIST_DAMAGE


def incoming(raw: int, victim: Player) -> int:
    if victim.has_armor:
        raw -= C.ARMOR_REDUCTION
    return max(raw, C.MIN_DAMAGE)


def kill(world: World, victim: Player, killer: Player | None) -> None:
    """Kill a player. `killer` is None for a fall or any other unattributed death."""
    if not victim.alive:
        return
    victim.alive = False
    victim.health = 0
    victim.vx = 0
    victim.vy = 0
    victim.grounded = False
    victim.break_target = None
    victim.break_progress = 0
    victim.deaths += 1

    # everything a player carries is lost on death
    victim.iron = 0
    victim.blocks = 0
    victim.has_sword = False
    victim.has_armor = False
    victim.has_pickaxe = False

    if killer is not None and killer is not victim:
        killer.kills += 1

    if world.teams[victim.team].bed_intact:
        victim.respawn_at = world.tick + C.RESPAWN_TICKS
    else:
        victim.respawn_at = None        # death is final


def _reachable(attacker: Player, victim: Player) -> bool:
    dx = (victim.x + C.PLAYER_W // 2) - (attacker.x + C.PLAYER_W // 2)
    dy = (victim.y + C.PLAYER_H // 2) - (attacker.y + C.PLAYER_H // 2)
    if abs(dy) > C.PLAYER_H:
        return False
    if attacker.facing_left and dx > 0:
        return False
    if not attacker.facing_left and dx < 0:
        return False
    return abs(dx) <= C.ATTACK_REACH


def resolve_attacks(world: World, inputs: dict[int, Buttons]) -> None:
    for pid, player in sorted(world.players.items()):
        if not player.alive:
            continue
        buttons = inputs.get(pid)
        if buttons is None or not buttons.attack:
            continue
        if world.tick < player.attack_ready_at:
            continue

        target = None
        best = None
        for other in sorted(world.players.values(), key=lambda p: p.id):
            if other.id == pid or other.team is player.team or not other.alive:
                continue
            if not _reachable(player, other):
                continue
            dist = abs(other.x - player.x)
            if best is None or dist < best:
                best, target = dist, other

        if target is None:
            continue

        target.health -= incoming(damage_of(player), target)
        player.attack_ready_at = world.tick + C.ATTACK_COOLDOWN_TICKS
        if target.health <= 0:
            kill(world, target, player)
