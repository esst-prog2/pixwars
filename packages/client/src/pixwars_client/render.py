"""Drawing a world. The text the screen shows is computed by pure functions, so
what the header and the scoreboard say can be checked without a window."""

import pygame

from pixwars_sim import Team, World
from pixwars_sim import constants as C
from pixwars_sim.mapgen import in_shop_zone

HEADER_H = 52
WINDOW_W = C.MAP_W * C.TILE
WINDOW_H = C.MAP_H * C.TILE + HEADER_H

BACKGROUND = (24, 26, 34)
HEADER_BG = (14, 15, 20)
TERRAIN_COLOR = (88, 92, 104)
TEXT = (232, 234, 240)
DIM = (150, 154, 166)
GENERATOR = (226, 190, 84)
SHOP = (86, 168, 122)

TEAM_COLORS = {
    Team.RED: (214, 84, 88),
    Team.BLUE: (86, 132, 220),
}
BED_COLORS = {
    Team.RED: (246, 148, 150),
    Team.BLUE: (150, 186, 250),
}

SHOP_ITEMS = (
    (1, f"{C.BLOCKS_PER_PURCHASE} blocks", C.PRICE_BLOCKS),
    (2, "stone sword", C.PRICE_SWORD),
    (3, "leather armor", C.PRICE_ARMOR),
    (4, "pickaxe", C.PRICE_PICKAXE),
)


# --- the words on the screen ---------------------------------------------
def header_text(world: World, player_id: int) -> str:
    me = world.players.get(player_id)
    iron = me.iron if me is not None else 0
    broken = [t for t, s in world.teams.items() if not s.bed_intact]
    if broken:
        state = "  ".join(f"{t.name} BED DESTROYED" for t in sorted(broken))
    else:
        state = "both beds standing"
    return f"{state}      iron: {iron}"


def shop_lines(world: World, player_id: int) -> list[str]:
    me = world.players.get(player_id)
    if me is None or not me.alive or not in_shop_zone(world, me):
        return []
    return [f"[{key}] {name}  {price} iron" for key, name, price in SHOP_ITEMS]


def scoreboard_lines(world: World) -> list[str]:
    if not world.over or world.winner is None:
        return []
    lines = [f"{world.winner.name} WINS", ""]
    for pid, p in sorted(world.players.items()):
        lines.append(
            f"{p.team.name:<5} player {pid}   "
            f"beds {p.beds_broken}   kills {p.kills}   deaths {p.deaths}"
        )
    return lines


# --- pixels ---------------------------------------------------------------
def _font(size: int) -> pygame.font.Font:
    return pygame.font.SysFont("monospace", size, bold=True)


def draw(surface: pygame.Surface, world: World, player_id: int) -> None:
    surface.fill(BACKGROUND)
    _draw_tiles(surface, world)
    _draw_furniture(surface, world)
    _draw_players(surface, world)
    _draw_header(surface, world, player_id)
    _draw_shop(surface, world, player_id)
    if world.over:
        _draw_scoreboard(surface, world)


def _rect(tx: int, ty: int, w: int = 1, h: int = 1) -> pygame.Rect:
    return pygame.Rect(tx * C.TILE, ty * C.TILE + HEADER_H, w * C.TILE, h * C.TILE)


def _draw_tiles(surface, world: World) -> None:
    for ty in range(C.MAP_H):
        for tx in range(C.MAP_W):
            kind = world.tile(tx, ty)
            if kind == C.EMPTY:
                continue
            if kind == C.TERRAIN:
                color = TERRAIN_COLOR
            elif kind == C.PLACED:
                owner = world.tile_owner(tx, ty)
                color = TEAM_COLORS.get(Team(owner), TERRAIN_COLOR) if owner else TERRAIN_COLOR
            else:
                color = BED_COLORS[Team(world.tile_owner(tx, ty))]
            pygame.draw.rect(surface, color, _rect(tx, ty))


def _draw_furniture(surface, world: World) -> None:
    for team, state in world.teams.items():
        gx, gy = state.generator
        pygame.draw.rect(surface, GENERATOR, _rect(gx, gy).inflate(-6, -6))
        x0, y0, x1, y1 = state.shop_zone
        zone = _rect(x0, y0, x1 - x0 + 1, y1 - y0 + 1)
        pygame.draw.rect(surface, SHOP, zone, width=2)


def _draw_players(surface, world: World) -> None:
    for p in world.players.values():
        if not p.alive:
            continue
        rect = pygame.Rect(
            p.x * C.TILE // C.SUBPIXEL,
            p.y * C.TILE // C.SUBPIXEL + HEADER_H,
            C.PLAYER_W * C.TILE // C.SUBPIXEL,
            C.PLAYER_H * C.TILE // C.SUBPIXEL,
        )
        pygame.draw.rect(surface, TEAM_COLORS[p.team], rect)
        # a health pip above the head
        width = max(1, rect.width * p.health // C.MAX_HEALTH)
        pygame.draw.rect(surface, TEXT, pygame.Rect(rect.x, rect.y - 5, width, 3))


def _draw_header(surface, world: World, player_id: int) -> None:
    pygame.draw.rect(surface, HEADER_BG, pygame.Rect(0, 0, WINDOW_W, HEADER_H))
    label = _font(20).render(header_text(world, player_id), True, TEXT)
    surface.blit(label, (12, 8))
    me = world.players.get(player_id)
    if me is not None:
        kit = []
        if me.has_sword:
            kit.append("sword")
        if me.has_armor:
            kit.append("armor")
        if me.has_pickaxe:
            kit.append("pickaxe")
        detail = f"blocks: {me.blocks}   " + ("  ".join(kit) if kit else "no kit")
        surface.blit(_font(14).render(detail, True, DIM), (12, 31))


def _draw_shop(surface, world: World, player_id: int) -> None:
    lines = shop_lines(world, player_id)
    if not lines:
        return
    font = _font(16)
    for i, line in enumerate(lines):
        surface.blit(font.render(line, True, TEXT), (WINDOW_W - 220, HEADER_H + 12 + i * 20))


def _draw_scoreboard(surface, world: World) -> None:
    overlay = pygame.Surface((WINDOW_W, WINDOW_H))
    overlay.set_alpha(220)
    overlay.fill(HEADER_BG)
    surface.blit(overlay, (0, 0))
    lines = scoreboard_lines(world)
    big, small = _font(40), _font(18)
    y = WINDOW_H // 2 - 80
    for i, line in enumerate(lines):
        if i == 0:
            label = big.render(line, True, TEAM_COLORS[world.winner])
        else:
            label = small.render(line, True, TEXT)
        surface.blit(label, (WINDOW_W // 2 - label.get_width() // 2, y))
        y += label.get_height() + 8
