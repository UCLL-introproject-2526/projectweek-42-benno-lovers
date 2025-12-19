import math
from settings import SCALE, PATH_WIDTH

from pygame.math import Vector2

from pygame.math import Vector2

def dist_point_to_segment(px, py, x1, y1, x2, y2):
    p = Vector2(px, py)
    a = Vector2(x1, y1)
    b = Vector2(x2, y2)

    ab = b - a
    ap = p - a
    bp = p - b


    if ap.dot(ab) <= 0:
        return (p - a).length()

    if bp.dot(-ab) <= 0:
        return (p - b).length()

    
    t = ap.dot(ab) / ab.length_squared() 
    closest = a.lerp(b, t)
    return (p - closest).length()


def is_on_path(x, y, path):
    for i in range(len(path) - 1):
        if dist_point_to_segment(x, y, *path[i], *path[i + 1]) <= PATH_WIDTH // 2 + max(4, int(5 * SCALE)):
            return True
    return False