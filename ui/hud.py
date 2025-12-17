import pygame
from settings import WIDTH, HEIGHT, FONT, SMALL_FONT, screen
from settings import TOWER_COST, SNIPER_TOWER_COST, SLOW_TOWER_COST


def render_text_outline(font, text, fg=(0, 0, 0), outline=(255, 255, 255), thickness=2):
    base = font.render(text, True, fg)
    w, h = base.get_width() + thickness * 2, base.get_height() + thickness * 2
    surf = pygame.Surface((w, h), pygame.SRCALPHA)

    # outline
    for dx in range(-thickness, thickness + 1):
        for dy in range(-thickness, thickness + 1):
            if dx == 0 and dy == 0:
                continue
            surf.blit(font.render(text, True, outline), (dx + thickness, dy + thickness))

    # main text
    surf.blit(base, (thickness, thickness))
    return surf


def draw_hud(money, score, base_hp, wave, max_waves):
    # Links boven (alles zwart met witte rand)
    screen.blit(render_text_outline(FONT, f"Score: {score}"), (10, 10))
    screen.blit(render_text_outline(FONT, f"Base HP: {base_hp}"), (10, 40))
    screen.blit(render_text_outline(FONT, f"Money: {money}"), (10, 70))
    screen.blit(render_text_outline(FONT, f"Wave: {wave}/{max_waves}"), (10, 100))

    # Rechts boven (tower controls + costs)
    rx = WIDTH - 380
    screen.blit(render_text_outline(FONT, f"LMB = Normal ({TOWER_COST}$)"), (rx, 10))
    screen.blit(render_text_outline(FONT, f"S + LMB = Sniper ({SNIPER_TOWER_COST}$)"), (rx, 35))
    screen.blit(render_text_outline(FONT, f"A + LMB = Slow ({SLOW_TOWER_COST}$)"), (rx, 60))


    # Onder hint
    hint = render_text_outline(
        SMALL_FONT,
        "Hold+Release to place | Drag=merge | T=target | X=sell | ESC=menu",
        thickness=2
    )
    screen.blit(hint, (10, HEIGHT - hint.get_height() - 10))
