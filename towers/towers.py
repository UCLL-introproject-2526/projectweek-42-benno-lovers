import math
import pygame
from projectiles.bullet import Bullet
from utils.draw import hp_bar
from settings import TOWER_COLOR, TOWER_COST, SNIPER_TOWER_COST, SLOW_TOWER_COST, POISON_TOWER_COST, SCALE, MAX_TOWER_LEVEL, TARGET_FIRST, TARGET_MODES, SMALL_FONT, TARGET_STRONG, TEXT_COLOR, screen


# ================== TURRET IDLE SPRITE ==================
TURRET_IDLE_RAW = pygame.image.load(r"assets/images/TurretIdle.png").convert_alpha()

TURRET_FRAME_W = 42
TURRET_FRAME_H = TURRET_IDLE_RAW.get_height()
TURRET_FRAMES = []

for i in range(5):  # 210px / 42px = 5 frames
    frame = TURRET_IDLE_RAW.subsurface(
        pygame.Rect(i * TURRET_FRAME_W, 0, TURRET_FRAME_W, TURRET_FRAME_H)
    )
    TURRET_FRAMES.append(frame)

# ================== TURRET FIRING SPRITE ==================
TURRET_FIRING_RAW = pygame.image.load(r"assets/images/TurretFiring.png").convert_alpha()
FIRING_COLS = 2
FIRING_ROWS = 1
FRAME_W = TURRET_FIRING_RAW.get_width() // FIRING_COLS
FRAME_H = TURRET_FIRING_RAW.get_height() // FIRING_ROWS
TURRET_FIRING_FRAMES = []

for row in range(FIRING_ROWS):
    for col in range(FIRING_COLS):
        rect = pygame.Rect(col * FRAME_W, row * FRAME_H, FRAME_W, FRAME_H)
        frame = TURRET_FIRING_RAW.subsurface(rect)
        TURRET_FIRING_FRAMES.append(frame)


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

    def draw_base(self, enemies):
        # Vind de eerste enemy in range (als er meerdere zijn, is het genoeg)
        target = None
        for e in enemies:
            if math.hypot(e.x - self.x, e.y - self.y) <= self.range:
                target = e
                break

        # Kies sprite frames: idle of firing
        frames = TURRET_FIRING_FRAMES if target else TURRET_FRAMES

        # Update animatie index
        self.anim_index += self.anim_speed
        if self.anim_index >= len(frames):
            self.anim_index = 0
        frame = frames[int(self.anim_index)]

        # Flip sprite horizontaal afhankelijk van enemy positie
        if target and target.x < self.x:
            frame = pygame.transform.flip(frame, True, False)

        # Schaal frame
        scale = 1.25 * SCALE
        sprite = pygame.transform.scale(frame, (int(frame.get_width() * scale), int(frame.get_height() * scale)))

        # Teken sprite gecentreerd
        rect = sprite.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(sprite, rect)

        # Teken level text
        txt = SMALL_FONT.render(str(self.level), True, (255,0,0))
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
# Basis Tower class waar alle specifieke towers van erven
class Tower(TowerBase):
    def __init__(self, x, y):
        super().__init__(x, y, TOWER_COST, TOWER_COLOR)
        self.range = int(150 * SCALE)
        self.fire_rate = 30
        self.damage = 25

        self.anim_frames = TURRET_FRAMES
        self.anim_index = 0.0
        self.anim_speed = 0.12

    def upgrade_stats_one_level(self):
        if not self.can_upgrade():
            return False
        self.level += 1
        # merge moet hard voelen
        self.damage += 22
        self.range += int(26 * SCALE)
        self.fire_rate = max(7, self.fire_rate - 4)
        return True

# Specifieke tower types (uitbreidbaar)
class SniperTower(Tower):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.range = int(350 * SCALE)
        self.damage = 50
        self.fire_rate = 90
        self.base_cost = SNIPER_TOWER_COST
        self.total_value = SNIPER_TOWER_COST

class SlowTower(Tower):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.range = int(170 * SCALE)
        self.damage = 5
        self.fire_rate = 45
        self.base_cost = SLOW_TOWER_COST
        self.total_value = SLOW_TOWER_COST

    def shoot(self, enemies, bullets):
        if self.dragging:
            return
        if self.cooldown > 0:
            self.cooldown -= 1
            return

        target = self.choose_target(enemies)
        if not target:
            return

        bullets.append(Bullet(self.x, self.y, target, self.damage, effect=("slow", 0.5, 120)))
        self.cooldown = self.fire_rate


class PoisonTower(Tower):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.range = int(160 * SCALE)
        self.damage = 5
        self.fire_rate = 45
        self.base_cost = POISON_TOWER_COST
        self.total_value = POISON_TOWER_COST

    def shoot(self, enemies, bullets):
        if self.dragging:
            return
        if self.cooldown > 0:
            self.cooldown -= 1
            return

        target = self.choose_target(enemies)
        if not target:
            return

        bullets.append(Bullet(self.x, self.y, target, self.damage, effect=("poison", 2, 180)))
        self.cooldown = self.fire_rate
