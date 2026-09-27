"""Every tunable number in PixWars, and nothing else.

Positions and velocities are integers in subpixels: SUBPIXEL units to a tile.
Nothing here is referenced by a spec scenario, so any of it can be retuned
without that being a change in behaviour -- with one exception, guarded by a
test: no speed may exceed half a tile per tick, because the collision code
depends on it.
"""

# --- space and time -------------------------------------------------------
SUBPIXEL = 256          # position units per tile
TICK_HZ = 20            # simulation ticks per second
TILE = 16               # pixels per tile; used by the client only

MAP_W = 64
MAP_H = 36

# --- movement -------------------------------------------------------------
WALK_SPEED = 51         # 0.20 tile/tick  ->  4.0 tiles/s
JUMP_SPEED = 128        # 0.50 tile/tick upward
GRAVITY = 12            # added to downward velocity each tick
MAX_FALL = 120          # 0.47 tile/tick; this clamp IS the collision guarantee

PLAYER_W = SUBPIXEL     # 1 tile wide
PLAYER_H = 2 * SUBPIXEL  # 2 tiles tall

# --- combat ---------------------------------------------------------------
MAX_HEALTH = 20
FIST_DAMAGE = 2
SWORD_DAMAGE = 5
ARMOR_REDUCTION = 2
MIN_DAMAGE = 1                  # armor can never absorb a hit completely
ATTACK_COOLDOWN_TICKS = 5       # 0.25 s
ATTACK_REACH = 3 * SUBPIXEL // 2  # 1.5 tiles

# --- breaking -------------------------------------------------------------
BLOCK_BREAK_HAND = 12   # 0.60 s
BLOCK_BREAK_PICK = 4    # 0.20 s
BED_BREAK_HAND = 30     # 1.50 s
BED_BREAK_PICK = 10     # 0.50 s

# --- economy --------------------------------------------------------------
GEN_TICKS = 40          # 2.0 s between iron grants
RESPAWN_TICKS = 100     # 5.0 s

BLOCK_STACK_LIMIT = 64
BLOCKS_PER_PURCHASE = 16

PRICE_BLOCKS = 4
PRICE_SWORD = 8
PRICE_ARMOR = 6
PRICE_PICKAXE = 10

# --- tile and owner byte values -------------------------------------------
EMPTY = 0
TERRAIN = 1       # part of the map; never breakable
PLACED = 2        # put there by a player during the match
BED = 3           # breakable, but only by the other team

OWNER_NONE = 0
OWNER_RED = 1
OWNER_BLUE = 2
