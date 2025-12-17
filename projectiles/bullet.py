import math
import pygame
from settings import SCALE, BULLET_COLOR, MAX_TOWER_LEVEL, TARGET_FIRST, TARGET_MODES, SMALL_FONT, TARGET_STRONG, screen


# ================== BULLET ==================
class Bullet:
    def __init__(self, x, y, target, damage, effect=None):
        self.x, self.y = x, y
        self.target = target
        self.damage = damage
        self.effect = effect  # ("slow", factor, ticks) / ("poison", dps, ticks)
        self.speed = max(5, int(7 * SCALE))

    def move(self):
        dx, dy = self.target.x - self.x, self.target.y - self.y
        d = math.hypot(dx, dy)
        if d:
            self.x += self.speed * dx / d
            self.y += self.speed * dy / d

    def draw(self):
        pygame.draw.circle(screen, BULLET_COLOR, (int(self.x), int(self.y)), max(3, int(5 * SCALE)))

# ================== TOWERS ==================
class TowerBase:
    def __init__(self, x, y, cost, color):
        self.x, self.y = x, y
        self.level = 1
        self.max_level = MAX_TOWER_LEVEL

        self.cooldown = 0
        self.dragging = False  # exploit fix: geen aanvallen tijdens drag/merge

        self.base_cost = cost
        self.total_value = cost
        self.color = color

        self.target_mode = TARGET_FIRST

        # elke subclass zet deze:
        self.range = int(150 * SCALE)
        self.fire_rate = 30
        self.damage = 10

    def cycle_target_mode(self):
        idx = TARGET_MODES.index(self.target_mode)
        self.target_mode = TARGET_MODES[(idx + 1) % len(TARGET_MODES)]

    def can_upgrade(self):
        return self.level < self.max_level

    def upgrade_stats_one_level(self):
        # overridden
        return False

    def draw_base(self):
        r = max(10, int((15 + self.level) * SCALE))
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), r)
        txt = SMALL_FONT.render(str(self.level), True, (0, 0, 0))
        screen.blit(txt, (int(self.x - txt.get_width()/2), int(self.y - txt.get_height()/2)))

    def choose_target(self, enemies):
        in_range = [e for e in enemies if math.hypot(e.x - self.x, e.y - self.y) <= self.range]
        if not in_range:
            return None

        if self.target_mode == TARGET_FIRST:
            # jouw eis: "altijd de eerste cirkel in de rij" = meest progress
            return max(in_range, key=lambda e: e.progress())
        elif self.target_mode == TARGET_STRONG:
            return max(in_range, key=lambda e: e.hp)
        else:
            return min(in_range, key=lambda e: math.hypot(e.x - self.x, e.y - self.y))

    def shoot(self, enemies, bullets):
        # exploit fix: geen aanvallen tijdens drag/merge
        if self.dragging:
            return

        if self.cooldown > 0:
            self.cooldown -= 1
            return

        target = self.choose_target(enemies)
        if not target:
            return

        bullets.append(Bullet(self.x, self.y, target, self.damage))
        self.cooldown = self.fire_rate
