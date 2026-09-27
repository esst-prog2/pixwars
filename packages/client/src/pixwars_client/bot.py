"""A bot opponent, expressed as button states.

`decide` reads a world and returns exactly the kind of Buttons a keyboard
produces, so the simulation cannot tell a bot from a human and needs no special
case for one. It lives here rather than in pixwars_sim because deciding who
supplies input for which player is the client's job -- when real clients arrive,
the bot is simply not consulted.

It keeps no state: everything it needs is in the world it is handed, which is
what makes it deterministic and replayable in a test.
"""

from pixwars_sim import Buttons, Player, Team, World
from pixwars_sim import constants as C
from pixwars_sim.building import break_target, place_target
from pixwars_sim.mapgen import in_shop_zone

#: Enough blocks to bridge from one base to the other, with slack.
BRIDGE_BLOCKS = 48

NOTHING = Buttons()


def _centre(p: Player) -> int:
    return p.x + C.PLAYER_W // 2


def _lead_col(p: Player, facing_left: bool) -> int:
    if facing_left:
        return p.x // C.SUBPIXEL
    return (p.x + C.PLAYER_W - 1) // C.SUBPIXEL


def _enemy_in_reach(world: World, me: Player, facing_left: bool) -> bool:
    for other in world.players.values():
        if other.team is me.team or not other.alive or other.id == me.id:
            continue
        dx = _centre(other) - _centre(me)
        dy = other.y - me.y
        if abs(dy) > C.PLAYER_H:
            continue
        if facing_left and dx > 0:
            continue
        if not facing_left and dx < 0:
            continue
        if abs(dx) <= C.ATTACK_REACH:
            return True
    return False


def _objective_x(world: World, me: Player) -> int | None:
    """Where the bot is trying to get to, in subpixels."""
    enemy = me.team.other
    state = world.teams.get(enemy)
    if state is not None and state.bed_intact and state.bed_tiles:
        tx = sum(t[0] for t in state.bed_tiles) // len(state.bed_tiles)
        return tx * C.SUBPIXEL
    alive = [p for p in world.players.values() if p.team is enemy and p.alive]
    if not alive:
        return None
    nearest = min(alive, key=lambda p: (abs(_centre(p) - _centre(me)), p.id))
    return _centre(nearest)


def _shop_x(world: World, me: Player) -> int:
    x0, _, x1, _ = world.teams[me.team].shop_zone
    return ((x0 + x1) // 2) * C.SUBPIXEL


def _on_own_base(world: World, me: Player) -> bool:
    """Still close enough to home to be worth shopping."""
    x0, _, x1, _ = world.teams[me.team].shop_zone
    col = me.x // C.SUBPIXEL
    return x0 - 6 <= col <= x1 + 6


def _shopping_list(me: Player) -> int | None:
    if me.blocks < BRIDGE_BLOCKS and me.iron >= C.PRICE_BLOCKS:
        return 1
    if not me.has_sword and me.iron >= C.PRICE_SWORD:
        return 2
    if not me.has_pickaxe and me.iron >= C.PRICE_PICKAXE and me.blocks >= BRIDGE_BLOCKS:
        return 4
    return None


def _started_bridging(world: World, me: Player) -> bool:
    """True once this team has placed a block anywhere on the map.

    The bot keeps no memory of its own, so "have I set off yet?" has to be a
    question about the world. Its own bridge is the answer.
    """
    mine = int(me.team)
    for i, kind in enumerate(world.tiles):
        if kind == C.PLACED and world.owner[i] == mine:
            return True
    return False


def _still_shopping(world: World, me: Player) -> bool:
    if not me.has_sword:
        return True
    if me.blocks == 0:
        return True
    # placing blocks drops the stack below the target; that is not a reason to
    # walk back to the shop once the bridge is under way
    return me.blocks < BRIDGE_BLOCKS and not _started_bridging(world, me)


def decide(world: World, player_id: int) -> Buttons:
    """The button state this bot holds down for this tick. Never writes."""
    me = world.players.get(player_id)
    if me is None or not me.alive or world.over:
        return NOTHING

    # --- stock up at home before setting off -----------------------------
    if _still_shopping(world, me) and _on_own_base(world, me):
        if in_shop_zone(world, me):
            slot = _shopping_list(me)
            if slot is not None:
                return Buttons(buy=slot)
            return NOTHING              # wait for the generator
        goal = _shop_x(world, me)
    else:
        goal = _objective_x(world, me)
        if goal is None:
            return NOTHING

    facing_left = goal < _centre(me)
    arrived = abs(goal - _centre(me)) <= C.SUBPIXEL // 2

    attack = _enemy_in_reach(world, me, facing_left)

    probe = Player(
        id=me.id, team=me.team, x=me.x, y=me.y,
        facing_left=facing_left, has_pickaxe=me.has_pickaxe,
    )
    # the bot only ever breaks beds: breaking its own bridge would strand it
    target = break_target(world, probe)
    breaking = target is not None and world.tile(*target) == C.BED

    # is the floor I am about to stand on there?
    feet = (me.y + C.PLAYER_H) // C.SUBPIXEL
    lead = _lead_col(me, facing_left)
    ahead = lead - 1 if facing_left else lead + 1
    need_floor = (
        me.grounded
        and not arrived
        and world.tile(lead, feet) == C.EMPTY
        or world.tile(ahead, feet) == C.EMPTY
    )
    place = (
        me.blocks > 0
        and me.grounded
        and need_floor
        and place_target(world, probe) is not None
    )

    # a wall in the way, at body height
    upper = me.y // C.SUBPIXEL
    lower = (me.y + C.PLAYER_H - 1) // C.SUBPIXEL
    blocked = world.is_solid(ahead, lower) or world.is_solid(ahead, upper)
    jump = me.grounded and blocked and not breaking

    # stop walking while laying the floor under yourself, or while breaking
    walking = not place and not breaking and not arrived

    return Buttons(
        left=walking and facing_left,
        right=walking and not facing_left,
        jump=jump,
        attack=attack,
        place=place,
        break_=breaking,
        facing_left=facing_left,
    )
