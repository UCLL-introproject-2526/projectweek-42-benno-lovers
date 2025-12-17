import pygame
from settings import SCALE, screen, BASE_COLOR
from utils.draw import hp_bar

class Base:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.max_hp = 100
        self.hp = self.max_hp

    def take_damage(self, dmg):
        self.hp -= dmg
        if self.hp < 0:
            self.hp = 0

    def is_destroyed(self):
        return self.hp <= 0

    def draw(self):
        size = max(40, int(55 * SCALE))
        pygame.draw.rect(
            screen,
            BASE_COLOR,
            (int(self.x - size / 2), int(self.y - size / 2), size, size)
        )

        hp_bar(
            int(self.x),
            int(self.y - size / 2 - 10),
            self.hp,
            self.max_hp,
            max(70, int(95 * SCALE)),
            h=max(6, int(8 * SCALE))
        )