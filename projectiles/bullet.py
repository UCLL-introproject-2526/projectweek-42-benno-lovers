import math
import pygame
from settings import SCALE, BULLET_COLOR, MAX_TOWER_LEVEL, TARGET_FIRST, TARGET_MODES, SMALL_FONT, TARGET_STRONG, screen


# ================== BULLET ==================BULLET_IMAGE = pygame.image.load("bullet.png").convert_alpha()
BULLET_IMAGE = pygame.image.load("assets/images/bullet.png").convert_alpha()
BULLET_IMAGE = pygame.transform.scale(
    BULLET_IMAGE,
    (int(10 * SCALE), int(10 * SCALE))
)


class Bullet:
    def __init__(self, x, y, target, damage, effect=None):
        self.x, self.y = x, y
        self.target = target
        self.damage = damage
        self.effect = effect
        self.speed = max(5, int(7 * SCALE))

        self.image = BULLET_IMAGE
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def move(self):
        dx, dy = self.target.x - self.x, self.target.y - self.y
        d = math.hypot(dx, dy)
        if d:
            self.x += self.speed * dx / d
            self.y += self.speed * dy / d
            self.rect.center = (self.x, self.y)

    def draw(self):
        screen.blit(self.image, self.rect)


