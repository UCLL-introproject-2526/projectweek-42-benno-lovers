import pygame
from settings import WIDTH, HEIGHT, FONT, SMALL_FONT
from world.base import Base
from utils.draw import hp_bar
from settings import TOWER_COST, SNIPER_TOWER_COST, SLOW_TOWER_COST, POISON_TOWER_COST, screen

def draw_hud(money, score, base_hp, wave, max_waves):
    screen.blit(FONT.render(f"Score: {score}", True, (255, 255, 255)), (10, 10))
    screen.blit(FONT.render(f"Base HP: {base_hp}", True, (255, 255, 255)), (10, 40))
    screen.blit(FONT.render(f"Money: {money}", True, (0, 220, 0)), (10, 70))
    screen.blit(FONT.render(f"Wave: {wave}/{max_waves}", True, (255, 255, 255)), (10, 100))

    rx = WIDTH - 380
    screen.blit(FONT.render(f"LMB = Normal ({TOWER_COST}$)", True, (200, 200, 200)), (rx, 10))
    screen.blit(FONT.render(f"S + LMB = Sniper ({SNIPER_TOWER_COST}$)", True, (200, 200, 200)), (rx, 35))
    screen.blit(FONT.render(f"A + LMB = Slow ({SLOW_TOWER_COST}$)", True, (200, 200, 200)), (rx, 60))
    screen.blit(FONT.render(f"D + LMB = Poison ({POISON_TOWER_COST}$)", True, (200, 200, 200)), (rx, 85))

    hint = SMALL_FONT.render(
        "Hold+Release to place | Drag=merge | T=target | X=sell | ESC=menu",
        True,
        (170, 170, 170)
    )
    screen.blit(hint, (10, HEIGHT - hint.get_height() - 10))
