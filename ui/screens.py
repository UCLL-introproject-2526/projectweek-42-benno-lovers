# apparte schermen ( startmenu, instructies, level select)


import pygame
from settings import WIDTH, HEIGHT, BG_COLOR, FONT, SMALL_FONT, BIG_FONT, screen, TEXT_COLOR, SELL_REFUND, MAX_TOWER_LEVEL
from ui.hud import draw_hud


# ================== UI SCREENS ==================
def instructions_screen():
    viewing = True
    while viewing:
        screen.fill(BG_COLOR)
        title = BIG_FONT.render("Instructies", True, TEXT_COLOR)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, int(0.08 * HEIGHT)))

        lines = [
            "Plaatsen (klik INHOUDEN):",
            "LMB = Normal",
            "S + LMB = Sniper",
            "A + LMB = Slow",
            "D + LMB = Poison",
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
    selecting = True
    while selecting:
        screen.fill(BG_COLOR)
        title = BIG_FONT.render("Tower Defence", True, TEXT_COLOR)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, int(0.10 * HEIGHT)))

        mx, my = pygame.mouse.get_pos()
        entries = ["Level 1 - Resaurant", "Level 2 - Aula", "Level 3","Level 4 - Classroom", "Instructies"]
        rects = []
        y0 = int(0.36 * HEIGHT)
        step = int(0.11 * HEIGHT)

        for i, name in enumerate(entries):
            text = FONT.render(name, True, (255, 255, 0))
            rect = text.get_rect(center=(WIDTH // 2, y0 + i * step))
            if rect.collidepoint(mx, my):
                pygame.draw.rect(screen, (255, 255, 150), rect.inflate(30, 16), border_radius=8)
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
                            return int(name.split()[1])

