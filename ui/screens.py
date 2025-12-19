# apparte schermen ( startmenu, instructies, level select, credits)

import os
import pygame

from settings import (
    WIDTH, HEIGHT, BG_COLOR, FONT, SMALL_FONT, BIG_FONT,
    screen, TEXT_COLOR, SELL_REFUND, MAX_TOWER_LEVEL
)
from ui.hud import draw_hud


# ================== BACKGROUND (MENU / INSTRUCTIES / CREDITS) ==================
# Zet je afbeelding hier neer: assets/images/BG_main_menu.png
MENU_BG_PATH = os.path.join("assets", "images", "BG_main_menu.png")

try:
    _menu_bg = pygame.image.load(MENU_BG_PATH).convert()
except Exception as e:
    raise FileNotFoundError(
        f"Kon menu background niet laden op: {MENU_BG_PATH}\n"
        f"Zorg dat het bestand bestaat (bv. assets/images/BG_main_menu.png)\n"
        f"Originele fout: {e}"
    )

MENU_BG = pygame.transform.smoothscale(_menu_bg, (WIDTH, HEIGHT))

# Basis overlay voor leesbaarheid (menu/instructies)
OVERLAY = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
OVERLAY.fill((0, 0, 0, 90))  # verlaag/verhoog voor minder/meer donker

# Extra overlay voor credits (meer leesbaar, geen kader)
CREDITS_OVERLAY = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
CREDITS_OVERLAY.fill((0, 0, 0, 150))


def draw_menu_background():
    screen.blit(MENU_BG, (0, 0))
    screen.blit(OVERLAY, (0, 0))


def draw_credits_background():
    screen.blit(MENU_BG, (0, 0))
    screen.blit(CREDITS_OVERLAY, (0, 0))


def draw_shadow_centered(text_surf, y, shadow_offset=2):
    """Tekent een tekstsurface gecentreerd met een subtiele schaduw."""
    x = WIDTH // 2 - text_surf.get_width() // 2
    shadow = pygame.Surface(text_surf.get_size(), pygame.SRCALPHA)
    shadow.blit(text_surf, (0, 0))
    # Schaduw: render opnieuw in zwart (simpel en performant)
    # (We renderen liever rechtstreeks opnieuw dan pixels manipuleren)
    # -> daarom hieronder in de call zelf bij strings.
    screen.blit(text_surf, (x, y))


def blit_centered_with_shadow(text, font, color, y, shadow_offset=2):
    """Render text + schaduw en blit gecentreerd."""
    shadow = font.render(text, True, (0, 0, 0))
    main = font.render(text, True, color)

    x_main = WIDTH // 2 - main.get_width() // 2
    x_shadow = WIDTH // 2 - shadow.get_width() // 2

    screen.blit(shadow, (x_shadow + shadow_offset, y + shadow_offset))
    screen.blit(main, (x_main, y))


# ================== UI SCREENS ==================
def instructions_screen():
    viewing = True
    while viewing:
        draw_menu_background()

        blit_centered_with_shadow("Instructies", BIG_FONT, TEXT_COLOR, int(0.08 * HEIGHT), shadow_offset=3)

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
            f"Sell: selecteer tower + X (refund {int(SELL_REFUND*100)}%)",
            "",
            "ESC: terug"
        ]

        y0 = int(0.24 * HEIGHT)
        for i, line in enumerate(lines):
            blit_centered_with_shadow(line, FONT, (210, 210, 210), y0 + i * 30, shadow_offset=2)

        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                viewing = False


def credits_screen():
    viewing = True
    while viewing:
        # Donkerder (maar zonder kader) zodat credits altijd leesbaar zijn
        draw_credits_background()

        blit_centered_with_shadow("Credits", BIG_FONT, TEXT_COLOR, int(0.08 * HEIGHT), shadow_offset=3)

        # Hou de credit inhoud EXACT zoals jij ze had
        lines = [
            "Lead developer and lead A3 knipper: Killian Van Acker",
            
            "Head of marketing and poster provider: Killian Van Acker",
            
            "Fixer of broken code: Killian Van Acker",
            
            "Candy provider and junior map designer: Killian Van Acker",
            
            "Senior art and animation director: Bram Switters",

            "Professional gooner and junior programmer: Bram Switters",
            "Lead map designer: Bram Switters",
            

            "Music Maestro and general sound design: Alexander Rijnders",
            
            "Publisher and junior programmer: Alexander Rijnders",
            
            "Fulltime motivator and lead A4 knipper: Staf Tuyaerts",

             "Minesweeper expert: Staf Tuyaerts",

            "Difficulty manager: Staf Tuyaerts",
            
             "Laptop cable manager: Staf Tuyaerts",
            
            "Poster designer: ChatGPT plus from Killian's girlfriend Zahra",
            
            "Concept designer and junior programmer: Artan Helewaut",
            
             "Pair programmer: Artan Helewaut",
            
            "Special thanks: Benno Debals for inspiration and signing Killian's poster twice",
        
            "ESC: terug"
        ]

        y0 = int(0.22 * HEIGHT)
        line_step = 30

        for i, line in enumerate(lines):
            # lege regels iets minder “hoog” laten pakken voelt netter
            if line.strip() == "":
                continue
            blit_centered_with_shadow(line, FONT, (230, 230, 230), y0 + i * line_step, shadow_offset=2)

        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                viewing = False


def start_screen():
    music_started = False
    pygame.mixer.music.load("assets/music/Concern Pt.2 Patricks Soul.mp3")
    pygame.mixer.music.set_volume(1)
    

    selecting = True
    while selecting:
        draw_menu_background()


        mx, my = pygame.mouse.get_pos()

        entries = [
            "Level 1 - Restaurant",
            "Level 2 - Aula",
            "Level 3 - Classroom",
            "Level 4 - Benno's Hell",
            "Instructies",
            "Credits"
        ]

        rects = []
        y0 = int(0.34 * HEIGHT)
        step = int(0.095 * HEIGHT)

        for i, name in enumerate(entries):
            text = FONT.render(name, True, (255, 255, 0))
            rect = text.get_rect(center=(WIDTH // 2, y0 + i * step))

            if rect.collidepoint(mx, my):
                pygame.draw.rect(
                    screen,
                    (255, 255, 150),
                    rect.inflate(30, 16),
                    width=3,
                    border_radius=8
                )

            # subtiele schaduw onder de menu entries
            shadow = FONT.render(name, True, (0, 0, 0))
            shadow_rect = shadow.get_rect(center=(WIDTH // 2 + 2, y0 + i * step + 2))
            screen.blit(shadow, shadow_rect)

            screen.blit(text, rect)
            rects.append((rect, name))

        hint = SMALL_FONT.render("ESC = quit", True, (220, 220, 220))
        # schaduw hint
        hint_shadow = SMALL_FONT.render("ESC = quit", True, (0, 0, 0))
        screen.blit(hint_shadow, (10 + 2, HEIGHT - hint.get_height() - 10 + 2))
        screen.blit(hint, (10, HEIGHT - hint.get_height() - 10))

        pygame.display.flip()

        for e in pygame.event.get():
            if e.type in (pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN):
                if not music_started:
                    pygame.mixer.music.play(-1)
                    music_started = True
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
                        elif name == "Credits":
                            credits_screen()
                        else:
                            pygame.mixer.music.stop()
                            return int(name.split()[1])
