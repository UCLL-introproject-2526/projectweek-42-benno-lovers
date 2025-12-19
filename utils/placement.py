import math
from settings import MIN_TOWER_DISTANCE, SCALE, SNIPER_COLOR, SLOW_COLOR, TOWER_COLOR
from towers.towers import SniperTower, SlowTower
from .geometry import is_on_path
from world.maps import level_paths

def is_on_any_path(level, x, y):
    return any(is_on_path(x, y, p) for p in level_paths[level.level])

def too_close_to_tower(towers, x, y):
    for t in towers:
        if math.hypot(t.x - x, t.y - y) < MIN_TOWER_DISTANCE:
            return True
    return False

def tower_at_pos(towers, mx, my):
    for t in reversed(towers):
        rad = max(18, int((26 + t.level) * SCALE))
        if math.hypot(mx - t.x, my - t.y) <= rad:
            return t
    return None

def same_tower_type(a, b):
    return type(a) is type(b)

def tower_type_name(t):
    if isinstance(t, SniperTower): return "SNIPER"
    if isinstance(t, SlowTower): return "SLOW"
    return "NORMAL"

def preview_stats_for_type(ttype):
    if ttype == "SNIPER":
        return SNIPER_COLOR, int(350 * SCALE)
    if ttype == "SLOW":
        return SLOW_COLOR, int(170 * SCALE)
    return TOWER_COLOR, int(150 * SCALE)