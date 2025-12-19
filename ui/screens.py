# apparte schermen ( startmenu, instructies, level select)

import os
import pygame

from settings import (
    WIDTH, HEIGHT, BG_COLOR, FONT, SMALL_FONT, BIG_FONT,
    screen, TEXT_COLOR, SELL_REFUND, MAX_TOWER_LEVEL
)
from ui.hud import draw_hud


# ================== BACKGROUND (MENU / INSTRUCTIES) ==================
# Zet je afbeelding hier neer: assets/backgrounds/menu_bg.png
MENU_BG_PATH = os.path.join("assets", "images", "BG_main_menu.png")

# 1x laden (niet elke frame)
try:
    _menu_bg = pygame.image.load(MENU_BG_PATH).convert()
except Exception as e:
    raise FileNotFoundError(
        f"Kon menu background niet laden op: {MENU_BG_PATH}\n"
        f"Zorg dat het bestand bestaat (bv. assets/images/BG_main_menu.png)\n"
        f"Originele fout: {e}"
    )

MENU_BG = pygame.transform.smoothscale(_menu_bg, (WIDTH, HEIGHT))

# Optioneel: donkere overlay zodat tekst altijd leesbaar blijft
OVERLAY = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
OVERLAY.fill((0, 0, 0, 110))  # laatste waarde = alpha (0-255)

# Optioneel: extra paneel achter de menu-items
PANEL = pygame.Surface((int(WIDTH * 0.60), int(HEIGHT * 0.55)), pygame.SRCALPHA)
PANEL.fill((0, 0, 0, 110))


def draw_menu_background(with_panel: bool = True):
    """Tekent de menu achtergrond + (optioneel) paneel achter de tekst."""
    screen.blit(MENU_BG, (0, 0))
    screen.blit(OVERLAY, (0, 0))

   
# ================== UI SCREENS ==================
def instructions_screen():
    viewing = True
    while viewing:
        # Background i.p.v. screen.fill(BG_COLOR)
        draw_menu_background(with_panel=True)

        title = BIG_FONT.render("Instructies", True, TEXT_COLOR)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, int(0.08 * HEIGHT)))

        lines = [
            "Plaatsen (klik INHOUDEN):",
            "LMB = Normal",
            "S + LMB = Sniper",
            "A + LMB = Slow",
            "",
            "Loslaten = plaatsen | loslaten op pad = annuleren",
            "",
            "Merge-upgrade:",
            "Sleep 2 towers van hetzelfde type + level op elkaar",
            f"Max tower level: {MAX_TOWER_LEVEL}",
            "",
            "Selecteer tower + T: target mode",
            f"Sell: selecteer tower + X (refund {int(SELL_REFUND * 100)}%)",
            "",
            "ESC: terug"
        ]

        y0 = int(0.24 * HEIGHT)
        for i, line in enumerate(lines):
            txt = FONT.render(line, True, (210, 210, 210))
            screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, y0 + i * 30))

        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                viewing = False


def start_screen():
    pygame.mixer.music.load("assets\\music\\Concern Pt.2 Patricks Soul.mp3")
    pygame.mixer.music.set_volume(1)
    pygame.mixer.music.play(-1)

    selecting = True
    while selecting:
        # Background i.p.v. screen.fill(BG_COLOR)
        draw_menu_background(with_panel=True)

       

        mx, my = pygame.mouse.get_pos()

        entries = [
            "Level 1 - Restaurant",
            "Level 2 - Aula",
            "Level 3 - Classroom",
            "Level 4 - Benno's Hell",
            "Instructies"
        ]

        rects = []
        y0 = int(0.36 * HEIGHT)
        step = int(0.11 * HEIGHT)

        for i, name in enumerate(entries):
            text = FONT.render(name, True, (255, 255, 0))
            rect = text.get_rect(center=(WIDTH // 2, y0 + i * step))

            if rect.collidepoint(mx, my):
                pygame.draw.rect(screen, (255, 255, 150), rect.inflate(30, 16), width=3, border_radius=8)

            screen.blit(text, rect)
            rects.append((rect, name))

        hint = SMALL_FONT.render("ESC = quit", True, (180, 180, 180))
        screen.blit(hint, (10, HEIGHT - hint.get_height() - 10))

        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                pygame.quit()
                raise SystemExit
            if e.type == pygame.MOUSEBUTTONDOWN:
                for rect, name in rects:
                    if rect.collidepoint(e.pos):
                        if name == "Instructies":
                            instructions_screen()
                        else:
                            pygame.mixer.music.stop()
                            return int(name.split()[1])
