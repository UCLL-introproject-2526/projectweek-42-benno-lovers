import math

from world.maps import level_paths

# ================== PATH HELPERS ==================
def dist_point_to_segment(px, py, x1, y1, x2, y2):
    vx, vy = x2 - x1, y2 - y1
    wx, wy = px - x1, py - y1

    c1 = vx * wx + vy * wy
    if c1 <= 0:
        return math.hypot(px - x1, py - y1)

    c2 = vx * vx + vy * vy
    if c2 <= c1:
        return math.hypot(px - x2, py - y2)

    b = c1 / c2
    bx, by = x1 + b * vx, y1 + b * vy
    return math.hypot(px - bx, py - by)


def is_on_path(x, y, path, path_width=40):
    for i in range(len(path) - 1):
        if dist_point_to_segment(
            x, y,
            path[i][0], path[i][1],
            path[i + 1][0], path[i + 1][1]
        ) <= path_width // 2:
            return True
    return False


# =================================================
# 🔥 BELANGRIJK: LEVEL_ID IS EEN INT
# =================================================
def is_on_any_path(level_id, x, y):
    """
    level_id = int (bv 1, 2, 3)
    """
    return any(
        is_on_path(x, y, path)
        for path in level_paths[level_id]
    )


# ================== TOWER PLACEMENT ==================
def too_close_to_tower(towers, x, y, min_dist=48):
    for t in towers:
        if math.hypot(t.x - x, t.y - y) < min_dist:
            return True
    return False


def tower_at_pos(towers, x, y):
    for t in reversed(towers):
        r = max(20, int((26 + t.level) * 1.0))
        if math.hypot(t.x - x, t.y - y) <= r:
            return t
    return None


def same_tower_type(a, b):
    return type(a) is type(b)
