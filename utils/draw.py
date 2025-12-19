import pygame
from settings import screen, PATH_COLOR, SCALE
import math

def hp_bar(x, y, hp, max_hp, w, h=6):
    ratio = 0 if max_hp <= 0 else max(0, min(1, hp / max_hp))
    pygame.draw.rect(screen, (255, 0, 0), (x - w//2, y, w, h))
    pygame.draw.rect(screen, (0, 255, 0), (x - w//2, y, int(w * ratio), h))

def draw_path(surface, path, width, alpha=120):

    temp = pygame.Surface(surface.get_size(), pygame.SRCALPHA)

    color = (*PATH_COLOR, alpha) 

    for i in range(len(path) - 1):
        pygame.draw.line(temp, color, path[i], path[i + 1], width)
        pygame.draw.circle(temp, color, path[i], width // 2)

    pygame.draw.circle(temp, color, path[-1], width // 2)

    # Blit naar main surface
    surface.blit(temp, (0, 0))


# ================== PATH PREVIEW ==================
def draw_enemy_path_preview(paths, tick, spacing_px=None):
    if spacing_px is None:
        spacing_px = max(26, int(34 * SCALE))  # afstand cirkels


    def lerp(a, b, t):
        return a + (b - a) * t

    for path in paths:
        # loop segments en leg ghost-cirkels op vaste afstanden
        for i in range(len(path) - 1):
            x1, y1 = path[i]
            x2, y2 = path[i + 1]
            dx, dy = x2 - x1, y2 - y1
            seg_len = math.hypot(dx, dy)
            if seg_len <= 0:
                continue

            # verschuiving, pixels bewegen
            offset = (-tick * max(1.0, 2.2 * SCALE)) % spacing_px

            
            s = -offset  #hoever je van segment bent
            while s < seg_len:
                t = max(0.0, min(1.0, s / seg_len))
                px = lerp(x1, x2, t)
                py = lerp(y1, y2, t)

                pygame.draw.circle(
                    screen,
                    (160, 160, 160),
                    (int(px), int(py)), # middelpunt
                    max(6, int(8 * SCALE)), #straal
                    1
                )
                s += spacing_px