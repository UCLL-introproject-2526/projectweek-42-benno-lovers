import math
from settings import SCALE, PATH_WIDTH

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

def is_on_path(x, y, path):
    for i in range(len(path) - 1):
        if dist_point_to_segment(x, y, *path[i], *path[i + 1]) <= PATH_WIDTH // 2 + max(4, int(5 * SCALE)):
            return True
    return False