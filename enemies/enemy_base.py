import pygame
import math
from settings import SCALE, BOSS_COLOR, STRONG_ENEMY_COLOR, ENEMY_COLOR, FPS, screen
from utils.draw import hp_bar


from enemies.enemy_types import ENEMY_TYPES
from settings import SCALE

class Enemy:
    def __init__(self, path, enemy_type="normal"):
        t = ENEMY_TYPES[enemy_type]

        self.path = path
        self.x, self.y = path[0]
        self.i = 1

        self.max_hp = t["hp"]
        self.hp = self.max_hp
        self.damage = t["damage"]

        self.base_speed = t["speed"] * SCALE
        self.speed = self.base_speed

        self.radius = max(8, int(t["radius"] * SCALE))
        self.color = t["color"]

        self.reward_money = t["reward_money"]
        self.reward_score = t["reward_score"]

        self.is_boss = (enemy_type == "boss")

        # status effects
        self.slow_ticks = 0
        self.slow_factor = 1.0

        self.poison_ticks = 0
        self.poison_dps = 0.0

        # targeting helper
        self.segment_frac = 0.0

    def progress(self):
        return self.i + self.segment_frac

    def apply_slow(self, factor, ticks):
        if factor < self.slow_factor or self.slow_ticks <= 0:
            self.slow_factor = factor
        self.slow_ticks = max(self.slow_ticks, ticks)

    def apply_poison(self, dps, ticks):
        self.poison_dps = max(self.poison_dps, dps)
        self.poison_ticks = max(self.poison_ticks, ticks)

    def update_effects(self):
        # slow
        if self.slow_ticks > 0:
            self.slow_ticks -= 1
            self.speed = self.base_speed * self.slow_factor
        else:
            self.slow_factor = 1.0
            self.speed = self.base_speed

        # poison (FIX: poison kan nu écht killen + stopt correct)
        if self.poison_ticks > 0:
            self.poison_ticks -= 1
            self.hp -= (self.poison_dps / FPS)
            if self.hp <= 0:
                self.hp = 0
                return True  # <- DIED FROM POISON
        else:
            self.poison_dps = 0.0
        return False

    def move(self):
        died_from_poison = self.update_effects()
        if died_from_poison:
            return "DEAD"  # speciale status voor de loop

        if self.i >= len(self.path):
            return True  # reached end

        tx, ty = self.path[self.i]
        dx, dy = tx - self.x, ty - self.y
        d = math.hypot(dx, dy)

        self.segment_frac = 1.0 - min(1.0, d / max(1.0, 220 * SCALE))

        if d < max(0.001, self.speed):
            self.x, self.y = tx, ty
            self.i += 1
            self.segment_frac = 0.0
        else:
            self.x += self.speed * dx / d
            self.y += self.speed * dy / d

        return False

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        bar_w = max(44, int((70 if self.is_boss else 55) * SCALE))
        hp_bar(int(self.x), int(self.y - 30 * SCALE), self.hp, self.max_hp, bar_w, h=max(6, int(8 * SCALE)))
