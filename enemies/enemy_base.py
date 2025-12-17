import pygame
import math
from settings import SCALE, BOSS_COLOR, STRONG_ENEMY_COLOR, ENEMY_COLOR, FPS, screen
from utils.draw import hp_bar


class Enemy:
    def __init__(self, path, strong=False, boss=False):
        self.path = path
        self.x, self.y = path[0]
        self.i = 1  # next waypoint index

        self.base_speed = ((1.5 if strong else 2.2) * SCALE)
        self.speed = self.base_speed

        if boss:
            self.max_hp = 1800
            self.damage = 60
            self.reward_money = 250
            self.reward_score = 250
            self.color = BOSS_COLOR
            self.radius = max(18, int(26 * SCALE))
            self.is_boss = True
        else:
            self.max_hp = 300 if strong else 100
            self.damage = 25 if strong else 10
            self.reward_money = 25 if strong else 10
            self.reward_score = 30 if strong else 10
            self.color = STRONG_ENEMY_COLOR if strong else ENEMY_COLOR
            self.radius = max(12, int((20 if strong else 14) * SCALE))
            self.is_boss = False

        self.hp = self.max_hp

        # status effects
        self.slow_ticks = 0
        self.slow_factor = 1.0

        # poison
        self.poison_ticks = 0
        self.poison_dps = 0.0

        # for smoother FIRST targeting: fraction progress on current segment
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
