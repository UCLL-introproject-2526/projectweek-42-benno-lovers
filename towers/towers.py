import math
import pygame

from projectiles.bullet import Bullet
from settings import (
    TOWER_COLOR, TOWER_COST, SNIPER_TOWER_COST, SLOW_TOWER_COST, POISON_TOWER_COST,
    SCALE, MAX_TOWER_LEVEL, TARGET_FIRST, TARGET_MODES, TARGET_STRONG,
    SMALL_FONT, screen
)
def blit_text_outline(surface, text_surf, x, y, outline_color=(255,255,255)):
    # 1px outline rondom
    for ox, oy in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,-1),(-1,1),(1,1)]:
        surface.blit(text_surf, (x + ox, y + oy))
    # main text erover (normale kleur zit al in text_surf)
    surface.blit(text_surf, (x, y))

# ================== SOUND EFFECTS ================== 
SHOOT_SOUND = pygame.mixer.Sound("assets\\sounds\\SHOTGUN_FINAL.mp3") 
SHOOT_SOUND.set_volume(1) 
SNIPER_SOUND = pygame.mixer.Sound("assets\\sounds\\SNIPER_SCHOT_ FINAL.mp3") 
SNIPER_SOUND.set_volume(1) 
SLOW_SHOOT_SOUND = pygame.mixer.Sound("assets\\sounds\\EXPLOSIE_FINAL.mp3") 
SLOW_SHOOT_SOUND.set_volume(1) 
POISON_SHOOT_SOUND = pygame.mixer.Sound("assets\\sounds\\SHOTGUN_FINAL.mp3") 
POISON_SHOOT_SOUND.set_volume(1) 
SHOOT_CHANNEL = pygame.mixer.Channel(0) 
SNIPER_CHANNEL = pygame.mixer.Channel(1) 
SLOW_CHANNEL = pygame.mixer.Channel(2) 
POISON_CHANNEL = pygame.mixer.Channel(3)
# ================== SPRITE LOADER ==================
def load_sprite_row(path: str, columns: int):
    """
    Laadt een spritesheet met 1 rij en `columns` frames.
    """
    sheet = pygame.image.load(path).convert_alpha()
    w, h = sheet.get_size()
    frame_w = w // columns

    frames = []
    for i in range(columns):
        rect = pygame.Rect(i * frame_w, 0, frame_w, h)
        frames.append(sheet.subsurface(rect).copy())
    return frames


# ================== SPRITES ==================
NORMAL_IDLE_FRAMES = load_sprite_row("assets/images/NormalIdle.png", 5)
NORMAL_SHOOTING_FRAMES = load_sprite_row("assets/images/NormalShooting.png", 2)

SNIPER_IDLE_FRAMES = load_sprite_row("assets/images/SniperIdle.png", 1)
SNIPER_SHOOTING_FRAMES = load_sprite_row("assets/images/SniperShooting.png", 4)

SLOW_IDLE_FRAMES = load_sprite_row("assets/images/SlowIdle.png", 5)
SLOW_SHOOTING_FRAMES = load_sprite_row("assets/images/SlowShooting.png", 2)


# ================== BASE TOWER ==================
class TowerBase:
    def __init__(self, x, y, cost, color):
        self.x, self.y = x, y
        self.level = 1
        self.max_level = MAX_TOWER_LEVEL
        self.sprite_scale = 1.25 
        self.cooldown = 0
        self.dragging = False

        self.base_cost = cost
        self.total_value = cost
        self.color = color

        self.range = int(150 * SCALE)
        self.fire_rate = 30
        self.damage = 15

        self.target_mode = TARGET_FIRST

        # 🔥 sprites (worden door subclasses overschreven)
        self.idle_frames = NORMAL_IDLE_FRAMES
        self.firing_frames = NORMAL_SHOOTING_FRAMES

        self.anim_index = 0.0
        self.anim_speed = 0.12

    # ---------------- TARGETING ----------------
    def cycle_target_mode(self):
        idx = TARGET_MODES.index(self.target_mode)
        self.target_mode = TARGET_MODES[(idx + 1) % len(TARGET_MODES)]

    def choose_target(self, enemies):
        in_range = [e for e in enemies if math.hypot(e.x - self.x, e.y - self.y) <= self.range]
        if not in_range:
            return None

        if self.target_mode == TARGET_FIRST:
            return max(in_range, key=lambda e: e.progress())
        elif self.target_mode == TARGET_STRONG:
            return max(in_range, key=lambda e: e.hp)
        else:
            return min(in_range, key=lambda e: math.hypot(e.x - self.x, e.y - self.y))

    # ---------------- DRAW ----------------
    def draw_base(self, enemies):
        target = self.choose_target(enemies)

        frames = self.firing_frames if target else self.idle_frames

        self.anim_index = (self.anim_index + self.anim_speed) % len(frames)
        frame = frames[int(self.anim_index)]

        if target and target.x < self.x:
            frame = pygame.transform.flip(frame, True, False)

        scale = self.sprite_scale * SCALE
        sprite = pygame.transform.scale(
            frame,
            (int(frame.get_width() * scale), int(frame.get_height() * scale))
        )

        rect = sprite.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(sprite, rect)

                # level badge (duidelijk leesbaar)
        label = f"Lv {self.level}"
        txt_main = SMALL_FONT.render(label, True, (0, 0, 0))        # zwart
        txt_outline = SMALL_FONT.render(label, True, (255, 255, 255))  # wit rand

        pad = 4
        bx = int(self.x) - txt_main.get_width() // 2
        by = int(self.y) - int(36 * SCALE)  # iets boven de tower

        # donker achtergrondje
        pygame.draw.rect(
            screen,
            (20, 20, 20),
            (bx - pad, by - pad, txt_main.get_width() + 2*pad, txt_main.get_height() + 2*pad),
            border_radius=6
        )

        # witte outline (8 richtingen)
        for ox, oy in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,-1),(-1,1),(1,1)]:
            screen.blit(txt_outline, (bx + ox, by + oy))

        # zwarte tekst bovenop
        screen.blit(txt_main, (bx, by))


    # ---------------- SHOOT ----------------
    def shoot(self, enemies, bullets):
        if self.dragging:
            return

        if self.cooldown > 0:
            self.cooldown -= 1
            return

        target = self.choose_target(enemies)
        if not target:
            return

        bullets.append(Bullet(self.x, self.y, target, self.damage))
        SHOOT_CHANNEL.play(SHOOT_SOUND)
        self.cooldown = self.fire_rate

    # ---------------- UPGRADE ----------------
    def can_upgrade(self):
        return self.level < self.max_level

    def upgrade_stats_one_level(self):
        if not self.can_upgrade():
            return False

        self.level += 1
        self.damage += 22
        self.range += int(26 * SCALE)
        self.fire_rate = max(7, self.fire_rate - 4)
        return True


# ================== NORMAL TOWER ==================
class Tower(TowerBase):
    def __init__(self, x, y):
        super().__init__(x, y, TOWER_COST, TOWER_COLOR)


# ================== SNIPER TOWER ==================
class SniperTower(Tower):
    def __init__(self, x, y):
        super().__init__(x, y)

        self.range = int(350 * SCALE)
        self.damage = 100
        self.fire_rate = 85
        self.base_cost = SNIPER_TOWER_COST
        self.total_value = SNIPER_TOWER_COST
        self.sprite_scale = 0.60
        self.idle_frames = SNIPER_IDLE_FRAMES
        self.firing_frames = SNIPER_SHOOTING_FRAMES
        self.anim_speed = 0.05

    def shoot(self, enemies, bullets):
        if self.dragging or self.cooldown > 0:
            self.cooldown -= 1
            return

        target = self.choose_target(enemies)
        if not target:
            return

        bullets.append(Bullet(self.x, self.y, target, self.damage))
        SNIPER_CHANNEL.play(SNIPER_SOUND)
        self.cooldown = self.fire_rate


# ================== SLOW TOWER ==================
class SlowTower(Tower):
    def __init__(self, x, y):
        super().__init__(x, y)

        self.range = int(170 * SCALE)
        self.damage = 5
        self.fire_rate = 45
        self.base_cost = SLOW_TOWER_COST
        self.total_value = SLOW_TOWER_COST

        self.idle_frames = SLOW_IDLE_FRAMES
        self.firing_frames = SLOW_SHOOTING_FRAMES
        self.anim_speed = 0.14

    def shoot(self, enemies, bullets):
        if self.dragging or self.cooldown > 0:
            self.cooldown -= 1
            return

        target = self.choose_target(enemies)
        if not target:
            return

        bullets.append(Bullet(self.x, self.y, target, self.damage, effect=("slow", 0.5, 120)))
        SLOW_CHANNEL.play(SLOW_SHOOT_SOUND)
        self.cooldown = self.fire_rate


# ================== POISON TOWER ==================
class PoisonTower(Tower):
    def __init__(self, x, y):
        super().__init__(x, y)

        self.range = int(160 * SCALE)
        self.damage = 5
        self.fire_rate = 45
        self.base_cost = POISON_TOWER_COST
        self.total_value = POISON_TOWER_COST

    def shoot(self, enemies, bullets):
        if self.dragging or self.cooldown > 0:
            self.cooldown -= 1
            return

        target = self.choose_target(enemies)
        if not target:
            return

        bullets.append(Bullet(self.x, self.y, target, self.damage, effect=("poison", 2, 180)))
        SHOOT_CHANNEL.play(SHOOT_SOUND)
        self.cooldown = self.fire_rate
