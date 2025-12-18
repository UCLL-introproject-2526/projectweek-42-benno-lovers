import pygame
import math

from settings import SCALE, FPS, screen
from utils.draw import hp_bar
from enemies.enemy_types import ENEMY_TYPES

# ---------- SPRITE CACHE ----------
# key = (enemy_type, level_id)
_SPRITE_CACHE = {}


def _load_sprite_frames(enemy_type: str, level_id=None):
    t = ENEMY_TYPES.get(enemy_type, {})
    path = t.get("sprite_path")
    frame_w = t.get("sprite_frame_width")

    # ---- boss: sprite per level ----
    if isinstance(path, dict):
        path = path.get(level_id)
        if isinstance(frame_w, dict):
            frame_w = frame_w.get(level_id)

    if not path or not frame_w:
        return []

    # extensie fix
    if not path.lower().endswith((".png", ".jpg", ".jpeg")):
        path = path + ".png"

    cache_key = (enemy_type, level_id)
    if cache_key in _SPRITE_CACHE:
        return _SPRITE_CACHE[cache_key]

    sheet = pygame.image.load(path).convert_alpha()
    sheet_w, sheet_h = sheet.get_size()

    cols = max(1, sheet_w // frame_w)
    frames = []
    for i in range(cols):
        rect = pygame.Rect(i * frame_w, 0, frame_w, sheet_h)
        frames.append(sheet.subsurface(rect).copy())

    _SPRITE_CACHE[cache_key] = frames
    return frames


class Enemy:
    def __init__(self, path, enemy_type="normal", level_id=None):
        t = ENEMY_TYPES[enemy_type]

        self.enemy_type = enemy_type
        self.level_id = level_id

        self.path = path
        self.x, self.y = path[0]
        self.i = 1

        self.max_hp = t["hp"]
        self.hp = self.max_hp
        self.damage = t["damage"]

        self.base_speed = t["speed"] * SCALE
        self.speed = self.base_speed

        self.radius = max(6, int(t["radius"] * SCALE))
        self.color = t["color"]

        self.reward_money = t["reward_money"]
        self.reward_score = t["reward_score"]
        self.is_boss = (enemy_type == "boss")

        # status effects
        self.slow_ticks = 0
        self.slow_factor = 1.0
        self.poison_ticks = 0
        self.poison_dps = 0.0

        self.segment_frac = 0.0

        # ---------- SPRITE / ANIM ----------
        self.frames = _load_sprite_frames(enemy_type, level_id)
        self.anim_index = 0.0
        self.anim_speed = 0.18

        self.facing_left = False

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
        if self.slow_ticks > 0:
            self.slow_ticks -= 1
            self.speed = self.base_speed * self.slow_factor
        else:
            self.slow_factor = 1.0
            self.speed = self.base_speed

        if self.poison_ticks > 0:
            self.poison_ticks -= 1
            self.hp -= (self.poison_dps / FPS)
            if self.hp <= 0:
                self.hp = 0
                return True
        else:
            self.poison_dps = 0.0

        return False

    def move(self):
        if self.update_effects():
            return "DEAD"

        if self.i >= len(self.path):
            return True

        tx, ty = self.path[self.i]
        dx, dy = tx - self.x, ty - self.y
        d = math.hypot(dx, dy)

        if dx < 0:
            self.facing_left = True
        elif dx > 0:
            self.facing_left = False

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
        cx, cy = int(self.x), int(self.y)

        if self.frames:
            self.anim_index = (self.anim_index + self.anim_speed) % len(self.frames)
            frame = self.frames[int(self.anim_index)]

            target_h = max(1, int(self.radius * 2.2))
            scale = target_h / frame.get_height()

            new_w = max(1, int(frame.get_width() * scale))
            new_h = max(1, int(frame.get_height() * scale))

            sprite = pygame.transform.scale(frame, (new_w, new_h))

            if self.facing_left:
                sprite = pygame.transform.flip(sprite, True, False)

            rect = sprite.get_rect(center=(cx, cy))
            screen.blit(sprite, rect)
        else:
            pygame.draw.circle(screen, self.color, (cx, cy), self.radius)

        bar_w = max(44, int((70 if self.is_boss else 55) * SCALE))
        hp_bar(cx, int(cy - 30 * SCALE), self.hp, self.max_hp, bar_w,
               h=max(6, int(8 * SCALE)))
