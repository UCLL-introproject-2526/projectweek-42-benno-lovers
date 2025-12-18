import math
import pygame
from settings import SCALE, screen

# ---------- SPRITE ----------
# Probeer eerst lightning-orb.png te laden, anders fallback op cirkel
try:
    ORB_IMAGE = pygame.image.load("assets/images/lightning_orb.png").convert_alpha()
    ORB_IMAGE = pygame.transform.scale(ORB_IMAGE, (int(26 * SCALE), int(26 * SCALE)))
except Exception:
    ORB_IMAGE = None


class LightningOrb:
    def __init__(self, x, y, target, speed=5.0, damage=15):
        self.x, self.y = float(x), float(y)
        self.target = target
        self.speed = speed
        self.damage = damage
        self.alive = True

        if ORB_IMAGE:
            self.image = ORB_IMAGE.copy()
            self.rect = self.image.get_rect(center=(self.x, self.y))
        else:
            self.image = None
            self.rect = pygame.Rect(self.x - 5, self.y - 5, 10, 10)

    def update(self):
        """Beweeg richting target. Markeer dood als target verdwijnt of geraakt is."""
        if not self.target or not hasattr(self.target, "x"):
            self.alive = False
            return

        dx = self.target.x - self.x
        dy = self.target.y - self.y
        dist = math.hypot(dx, dy)

        if dist < 5:
            # ⚡ Tower geraakt
            self.alive = False
            return

        if dist:
            self.x += (dx / dist) * self.speed
            self.y += (dy / dist) * self.speed

        if self.image:
            self.rect.center = (self.x, self.y)
        else:
            self.rect.center = (int(self.x), int(self.y))

    def draw(self):
        """Teken het projectile."""
        if self.image:
            screen.blit(self.image, self.rect)
        else:
            # fallback: simpel blauwe orb
            pygame.draw.circle(screen, (80, 200, 255), (int(self.x), int(self.y)), int(10 * SCALE))
            pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), int(5 * SCALE))
