
#regelt alle tijdelijke teksten (“Wave 1 starting!”, “Level Completed!”, of “Game Over”)


import pygame
from settings import screen, BIG_FONT, FPS, SCALE, SNIPER_COLOR, SLOW_COLOR, TOWER_COLOR
from towers.towers import SniperTower, SlowTower
# overlay = {"text": str, "color": (r,g,b), "frames": int}
overlay = None

def start_overlay(text, color=(255, 255, 0), duration_sec=1.4):
    """Start een overlay-tekst die automatisch fade-out doet."""
    global overlay
    overlay = {"text": text, "color": color, "frames": int(duration_sec * FPS)}

def draw_overlay():
    """Moet elke frame aangeroepen worden tijdens level loop."""
    global overlay
    if not overlay:
        return

    fade = int(0.45 * FPS)
    alpha = 255 if overlay["frames"] > fade else int(255 * (overlay["frames"] / fade))
    
    surf = BIG_FONT.render(overlay["text"], True, overlay["color"]).convert_alpha()
    surf.set_alpha(max(0, min(255, alpha)))

    # center op scherm
    screen.blit(surf, (screen.get_width() // 2 - surf.get_width() // 2,
                       screen.get_height() // 2 - surf.get_height() // 2))

    overlay["frames"] -= 1
    if overlay["frames"] <= 0:
        overlay = None

def preview_stats_for_type(ttype):
    if ttype == "SNIPER":
        return SNIPER_COLOR, int(350 * SCALE)
    if ttype == "SLOW":
        return SLOW_COLOR, int(170 * SCALE)

def same_tower_type(a, b):
    return type(a) is type(b)

def tower_type_name(t):
    if isinstance(t, SniperTower): return "SNIPER"
    if isinstance(t, SlowTower): return "SLOW"
    return "NORMAL"