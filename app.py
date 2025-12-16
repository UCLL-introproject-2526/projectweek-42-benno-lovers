import pygame
import math
import random

pygame.init()

# ================== DISPLAY: BORDERLESS FULLSCREEN ==================
screen = pygame.display.set_mode((0, 0), pygame.NOFRAME)  # borderless fullscreen
pygame.display.set_caption("Tower Defence")
clock = pygame.time.Clock()
WIDTH, HEIGHT = screen.get_size()
FPS = 60

# ================== CONSTANTEN ==================
# Costs
TOWER_COST = 50
SNIPER_TOWER_COST = 120
SLOW_TOWER_COST = 90
POISON_TOWER_COST = 110

SELL_REFUND = 0.75
MAX_TOWER_LEVEL = 6

# Colors
BG_COLOR = (30, 30, 30)
PATH_COLOR = (100, 100, 100)
ENEMY_COLOR = (200, 50, 50)
STRONG_ENEMY_COLOR = (50, 50, 200)
BOSS_COLOR = (160, 60, 220)

TOWER_COLOR = (50, 200, 50)
SNIPER_COLOR = (50, 150, 255)
SLOW_COLOR = (90, 220, 220)
POISON_COLOR = (160, 220, 80)

BASE_COLOR = (200, 50, 50)
BULLET_COLOR = (255, 255, 0)
TEXT_COLOR = (240, 240, 240)

FONT = pygame.font.SysFont(None, 28)
SMALL_FONT = pygame.font.SysFont(None, 22)
BIG_FONT = pygame.font.SysFont(None, 72)

# ================== SCHALING (van 800x600 naar fullscreen) ==================
BASE_W, BASE_H = 800, 600
sx = WIDTH / BASE_W
sy = HEIGHT / BASE_H
SCALE = min(sx, sy)

def sp(p):
    return int(p[0] * sx), int(p[1] * sy)

def spath(path):
    return [sp(pt) for pt in path]

PATH_WIDTH = max(22, int(40 * SCALE))

# ================== MAPS (800x600 basis) ==================
_level_paths_base = {
    # Map 1 (klassiek)
    1: [(-50, 550), (50, 550), (50, 200), (200, 150),
        (300, 300), (600, 300), (600, 100), (450, 100), (450, 550)],

    # Map 2 (cool slingerpad)
    2: [(-50, 300),
        (150, 300),
        (150, 100),
        (650, 100),
        (650, 500),
        (300, 500),
        (300, 250),
        (550, 250),
        (550, 550)],

    # Map 3 multi-lane (2 paden tegelijk)
    # Lane A: links -> boven -> midden -> base
    31: [(-50, 180),
         (120, 180),
         (120, 80),
         (420, 80),
         (420, 260),
         (560, 260),
         (560, 550)],

    # Lane B: rechts -> beneden -> midden -> base
    32: [(850, 420),
         (680, 420),
         (680, 520),
         (260, 520),
         (260, 320),
         (560, 320),
         (560, 550)],
}

# geschaalde paden
level_paths = {
    1: [spath(_level_paths_base[1])],
    2: [spath(_level_paths_base[2])],
    3: [spath(_level_paths_base[31]), spath(_level_paths_base[32])],  # multi-lane
}

level_base = {
    1: sp((450, 550)),
    2: sp((550, 550)),
    3: sp((560, 550)),
}

level_wave_map = {1: 5, 2: 10, 3: 15}

# ================== OVERLAY (niet-blokkerend) ==================
overlay = None

def start_overlay(text, color=(255, 255, 0), duration_sec=1.6):
    global overlay
    overlay = {"text": text, "color": color, "frames": int(duration_sec * FPS)}

def draw_overlay():
    global overlay
    if not overlay:
        return
    fade = int(0.45 * FPS)
    alpha = 255 if overlay["frames"] > fade else int(255 * (overlay["frames"] / fade))
    surf = BIG_FONT.render(overlay["text"], True, overlay["color"]).convert_alpha()
    surf.set_alpha(max(0, min(255, alpha)))
    screen.blit(surf, (WIDTH // 2 - surf.get_width() // 2, HEIGHT // 2 - surf.get_height() // 2))
    overlay["frames"] -= 1
    if overlay["frames"] <= 0:
        overlay = None

# ================== PATH HELPERS ==================
def draw_path(surface, path, width):
    for i in range(len(path) - 1):
        pygame.draw.line(surface, PATH_COLOR, path[i], path[i + 1], width)
        pygame.draw.circle(surface, PATH_COLOR, path[i], width // 2)
    pygame.draw.circle(surface, PATH_COLOR, path[-1], width // 2)

def dist_point_to_segment(px, py, x1, y1, x2, y2):
    vx, vy = x2 - x1, y2 - y1
    wx, wy = px - x1, py - y1
    c1 = vx * wx + vy * wy
    if c1 <= 0:
        return math.hypot(px - x1, py - y1)
    c2 = vx * vx + vy * vy
    if c2 <= c1:
        return math.hypot(px - x2, py - y2)
    b = c1 / c2
    bx, by = x1 + b * vx, y1 + b * vy
    return math.hypot(px - bx, py - by)

def is_on_path(x, y, path):
    for i in range(len(path) - 1):
        if dist_point_to_segment(x, y, *path[i], *path[i + 1]) <= PATH_WIDTH // 2 + max(4, int(5 * SCALE)):
            return True
    return False

def is_on_any_path(level, x, y):
    for p in level_paths[level]:
        if is_on_path(x, y, p):
            return True
    return False

def hp_bar(x, y, hp, max_hp, w, h=6):
    ratio = 0 if max_hp <= 0 else max(0, min(1, hp / max_hp))
    pygame.draw.rect(screen, (255, 0, 0), (x - w//2, y, w, h))
    pygame.draw.rect(screen, (0, 255, 0), (x - w//2, y, int(w * ratio), h))

# ================== TARGETING MODES ==================
TARGET_FIRST = "FIRST"
TARGET_STRONG = "STRONG"
TARGET_CLOSEST = "CLOSEST"
TARGET_MODES = [TARGET_FIRST, TARGET_STRONG, TARGET_CLOSEST]

# ================== CLASSES ==================
class Enemy:
    def __init__(self, path, strong=False, boss=False):
        self.path = path
        self.x, self.y = path[0]
        self.i = 1  # next target index

        self.base_speed = (1.5 if strong else 2.2) * SCALE
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

        self.poison_ticks = 0
        self.poison_dps = 0.0  # damage per second

    def apply_slow(self, factor, ticks):
        # keep the stronger slow
        if factor < self.slow_factor or self.slow_ticks <= 0:
            self.slow_factor = factor
        self.slow_ticks = max(self.slow_ticks, ticks)

    def apply_poison(self, dps, ticks):
        # stack by taking max dps and extending duration
        self.poison_dps = max(self.poison_dps, dps)
        self.poison_ticks = max(self.poison_ticks, ticks)

    def update_effects(self):
        # Slow
        if self.slow_ticks > 0:
            self.slow_ticks -= 1
            self.speed = self.base_speed * self.slow_factor
        else:
            self.slow_factor = 1.0
            self.speed = self.base_speed

        # Poison (ticks are frames)
        if self.poison_ticks > 0:
            self.poison_ticks -= 1
            self.hp -= (self.poison_dps / FPS)  # per frame
            if self.hp < 0:
                self.hp = 0
        else:
            self.poison_dps = 0.0

    def progress(self):
        # Simple & reliable “first in line”: higher i means further along
        return self.i

    def move(self):
        # update status effects first
        self.update_effects()

        # reached end?
        if self.i >= len(self.path):
            return True

        tx, ty = self.path[self.i]
        dx, dy = tx - self.x, ty - self.y
        d = math.hypot(dx, dy)
        if d < max(0.001, self.speed):
            self.i += 1
        else:
            self.x += self.speed * dx / d
            self.y += self.speed * dy / d
        return False

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

        # hp bar
        bar_w = max(44, int((70 if self.is_boss else 55) * SCALE))
        hp_bar(int(self.x), int(self.y - 30 * SCALE), self.hp, self.max_hp, bar_w, h=max(6, int(8 * SCALE)))

        # little status indicator (subtle)
        if self.slow_ticks > 0:
            pygame.draw.circle(screen, SLOW_COLOR, (int(self.x), int(self.y)), max(2, int(4 * SCALE)), 0)
        if self.poison_ticks > 0:
            pygame.draw.circle(screen, POISON_COLOR, (int(self.x + 8 * SCALE), int(self.y)), max(2, int(4 * SCALE)), 0)

class Bullet:
    def __init__(self, x, y, target, damage, effect=None):
        self.x, self.y = x, y
        self.target = target
        self.damage = damage
        self.speed = max(5, int(7 * SCALE))
        self.effect = effect  # None / ("slow", factor, ticks) / ("poison", dps, ticks)

    def move(self):
        dx, dy = self.target.x - self.x, self.target.y - self.y
        d = math.hypot(dx, dy)
        if d:
            self.x += self.speed * dx / d
            self.y += self.speed * dy / d

    def draw(self):
        pygame.draw.circle(screen, BULLET_COLOR, (int(self.x), int(self.y)), max(3, int(5 * SCALE)))

class TowerBase:
    def __init__(self, x, y, cost, color):
        self.x, self.y = x, y
        self.level = 1
        self.max_level = MAX_TOWER_LEVEL

        self.cooldown = 0
        self.dragging = False

        self.base_cost = cost
        self.total_value = cost  # investment sum for sell
        self.color = color

        self.target_mode = TARGET_FIRST  # default: FIRST

    def cycle_target_mode(self):
        idx = TARGET_MODES.index(self.target_mode)
        self.target_mode = TARGET_MODES[(idx + 1) % len(TARGET_MODES)]

    def can_upgrade(self):
        return self.level < self.max_level

    def upgrade_stats_one_level(self):
        raise NotImplementedError

    def _select_target(self, enemies):
        # filter in range done in subclass using its range
        raise NotImplementedError

    def shoot(self, enemies, bullets):
        raise NotImplementedError

    def draw_base(self):
        r = max(10, int((15 + self.level) * SCALE))
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), r)
        lvl_txt = SMALL_FONT.render(str(self.level), True, (0, 0, 0))
        screen.blit(lvl_txt, (int(self.x - lvl_txt.get_width()/2), int(self.y - lvl_txt.get_height()/2)))

class Tower(TowerBase):
    def __init__(self, x, y):
        super().__init__(x, y, TOWER_COST, TOWER_COLOR)
        self.range = int(150 * SCALE)
        self.fire_rate = 30
        self.damage = 25

    def upgrade_stats_one_level(self):
        if not self.can_upgrade():
            return False
        self.level += 1
        self.damage += 15
        self.range += int(20 * SCALE)
        self.fire_rate = max(8, self.fire_rate - 3)
        return True

    def shoot(self, enemies, bullets):
        if self.dragging:
            return
        if self.cooldown > 0:
            self.cooldown -= 1
            return

        in_range = []
        for e in enemies:
            if math.hypot(e.x - self.x, e.y - self.y) <= self.range:
                in_range.append(e)

        if not in_range:
            return

        if self.target_mode == TARGET_FIRST:
            target = max(in_range, key=lambda e: e.progress())
        elif self.target_mode == TARGET_STRONG:
            target = max(in_range, key=lambda e: e.hp)
        else:  # CLOSEST
            target = min(in_range, key=lambda e: math.hypot(e.x - self.x, e.y - self.y))

        bullets.append(Bullet(self.x, self.y, target, self.damage))
        self.cooldown = self.fire_rate

class SniperTower(TowerBase):
    def __init__(self, x, y):
        super().__init__(x, y, SNIPER_TOWER_COST, SNIPER_COLOR)
        self.range = int(350 * SCALE)
        self.fire_rate = 90
        self.damage = 100

    def upgrade_stats_one_level(self):
        if not self.can_upgrade():
            return False
        self.level += 1
        self.damage += 35
        self.range += int(35 * SCALE)
        self.fire_rate = max(25, self.fire_rate - 8)
        return True

    def draw_base(self):
        r = max(14, int((22 + self.level) * SCALE))
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), r)
        lvl_txt = SMALL_FONT.render(str(self.level), True, (0, 0, 0))
        screen.blit(lvl_txt, (int(self.x - lvl_txt.get_width()/2), int(self.y - lvl_txt.get_height()/2)))

    def shoot(self, enemies, bullets):
        if self.dragging:
            return
        if self.cooldown > 0:
            self.cooldown -= 1
            return

        in_range = []
        for e in enemies:
            if math.hypot(e.x - self.x, e.y - self.y) <= self.range:
                in_range.append(e)
        if not in_range:
            return

        if self.target_mode == TARGET_FIRST:
            target = max(in_range, key=lambda e: e.progress())
        elif self.target_mode == TARGET_STRONG:
            target = max(in_range, key=lambda e: e.hp)
        else:
            target = min(in_range, key=lambda e: math.hypot(e.x - self.x, e.y - self.y))

        bullets.append(Bullet(self.x, self.y, target, self.damage))
        self.cooldown = self.fire_rate

class SlowTower(TowerBase):
    def __init__(self, x, y):
        super().__init__(x, y, SLOW_TOWER_COST, SLOW_COLOR)
        self.range = int(170 * SCALE)
        self.fire_rate = 45
        self.damage = 8
        self.slow_factor = 0.55  # 45% slower
        self.slow_duration = int(2.2 * FPS)

    def upgrade_stats_one_level(self):
        if not self.can_upgrade():
            return False
        self.level += 1
        self.damage += 4
        self.range += int(18 * SCALE)
        self.fire_rate = max(18, self.fire_rate - 4)
        # slightly stronger slow
        self.slow_factor = max(0.35, self.slow_factor - 0.03)
        self.slow_duration = int(min(4.0 * FPS, self.slow_duration + 0.4 * FPS))
        return True

    def shoot(self, enemies, bullets):
        if self.dragging:
            return
        if self.cooldown > 0:
            self.cooldown -= 1
            return

        in_range = [e for e in enemies if math.hypot(e.x - self.x, e.y - self.y) <= self.range]
        if not in_range:
            return

        if self.target_mode == TARGET_FIRST:
            target = max(in_range, key=lambda e: e.progress())
        elif self.target_mode == TARGET_STRONG:
            target = max(in_range, key=lambda e: e.hp)
        else:
            target = min(in_range, key=lambda e: math.hypot(e.x - self.x, e.y - self.y))

        effect = ("slow", self.slow_factor, self.slow_duration)
        bullets.append(Bullet(self.x, self.y, target, self.damage, effect=effect))
        self.cooldown = self.fire_rate

class PoisonTower(TowerBase):
    def __init__(self, x, y):
        super().__init__(x, y, POISON_TOWER_COST, POISON_COLOR)
        self.range = int(160 * SCALE)
        self.fire_rate = 40
        self.damage = 10
        self.poison_dps = 22.0
        self.poison_duration = int(2.5 * FPS)

    def upgrade_stats_one_level(self):
        if not self.can_upgrade():
            return False
        self.level += 1
        self.damage += 6
        self.range += int(18 * SCALE)
        self.fire_rate = max(16, self.fire_rate - 3)
        self.poison_dps += 6.0
        self.poison_duration = int(min(5.0 * FPS, self.poison_duration + 0.5 * FPS))
        return True

    def shoot(self, enemies, bullets):
        if self.dragging:
            return
        if self.cooldown > 0:
            self.cooldown -= 1
            return

        in_range = [e for e in enemies if math.hypot(e.x - self.x, e.y - self.y) <= self.range]
        if not in_range:
            return

        if self.target_mode == TARGET_FIRST:
            target = max(in_range, key=lambda e: e.progress())
        elif self.target_mode == TARGET_STRONG:
            target = max(in_range, key=lambda e: e.hp)
        else:
            target = min(in_range, key=lambda e: math.hypot(e.x - self.x, e.y - self.y))

        effect = ("poison", self.poison_dps, self.poison_duration)
        bullets.append(Bullet(self.x, self.y, target, self.damage, effect=effect))
        self.cooldown = self.fire_rate

class Base:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.max_hp = 220
        self.hp = self.max_hp

    def take_damage(self, dmg):
        self.hp -= dmg
        if self.hp < 0:
            self.hp = 0

    def draw(self):
        size = max(40, int(55 * SCALE))
        pygame.draw.rect(screen, BASE_COLOR, (int(self.x - size/2), int(self.y - size/2), size, size))

        bar_w = max(70, int(95 * SCALE))
        bar_h = max(6, int(8 * SCALE))
        ratio = self.hp / self.max_hp if self.max_hp else 0
        x = int(self.x - bar_w/2)
        y = int(self.y - size/2 - (bar_h + 8))
        pygame.draw.rect(screen, (255, 0, 0), (x, y, bar_w, bar_h))
        pygame.draw.rect(screen, (0, 255, 0), (x, y, int(bar_w * ratio), bar_h))

# ================== UI SCREENS ==================
def instructions_screen():
    viewing = True
    while viewing:
        screen.fill(BG_COLOR)
        title = BIG_FONT.render("Instructies", True, TEXT_COLOR)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, int(0.08 * HEIGHT)))

        lines = [
            "LMB: Normal tower",
            "S + LMB: Sniper tower",
            "A + LMB: Slow tower",
            "D + LMB: Poison tower",
            "",
            "Merge-upgrade:",
            "Sleep 2 towers van hetzelfde type + level op elkaar",
            f"Max tower level: {MAX_TOWER_LEVEL}",
            "",
            "Selecteer tower + T: target mode (FIRST / STRONG / CLOSEST)",
            f"Sell: selecteer tower + X (refund {int(SELL_REFUND*100)}%)",
            "",
            "ESC: terug"
        ]
        start_y = int(0.28 * HEIGHT)
        for i, line in enumerate(lines):
            txt = FONT.render(line, True, (210, 210, 210))
            screen.blit(txt, (WIDTH//2 - txt.get_width()//2, start_y + i * 30))

        pygame.display.flip()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                viewing = False

def start_screen(levels_unlocked):
    selecting = True
    while selecting:
        screen.fill(BG_COLOR)
        title = BIG_FONT.render("Tower Defence", True, TEXT_COLOR)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, int(0.08 * HEIGHT)))

        mx, my = pygame.mouse.get_pos()
        buttons = []
        entries = ["Level 1", "Level 2", "Level 3", "Instructies"]
        base_y = int(0.30 * HEIGHT)
        step = int(0.12 * HEIGHT)

        for i, name in enumerate(entries):
            unlocked = (name == "Instructies") or levels_unlocked.get(i+1, False)
            color = (255, 255, 0) if unlocked else (120, 120, 120)
            text = FONT.render(name, True, color)
            rect = text.get_rect(center=(WIDTH//2, base_y + i * step))

            if unlocked and rect.collidepoint(mx, my):
                pygame.draw.rect(screen, (255, 255, 150), rect.inflate(30, 16), border_radius=8)

            screen.blit(text, rect)
            buttons.append((rect, name, unlocked))

        hint = SMALL_FONT.render("ESC = quit", True, (180, 180, 180))
        screen.blit(hint, (10, HEIGHT - hint.get_height() - 10))

        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                pygame.quit()
                raise SystemExit
            if e.type == pygame.MOUSEBUTTONDOWN:
                for rect, name, unlocked in buttons:
                    if unlocked and rect.collidepoint(e.pos):
                        if name == "Instructies":
                            instructions_screen()
                        else:
                            return int(name.split()[1])

# ================== HUD ==================
def draw_hud(money, score, base_hp, wave, max_waves):
    # Score eerst
    screen.blit(FONT.render(f"Score: {score}", True, (255, 255, 255)), (10, 10))
    # Base HP tweede
    screen.blit(FONT.render(f"Base HP: {base_hp}", True, (255, 255, 255)), (10, 40))
    # Money derde (groen)
    screen.blit(FONT.render(f"Money: {money}", True, (0, 220, 0)), (10, 70))
    # Wave
    if wave <= max_waves:
        screen.blit(FONT.render(f"Wave: {wave}/{max_waves}", True, (255, 255, 255)), (10, 100))

    # rechts: prijzen
    rx = WIDTH - 330
    screen.blit(FONT.render(f"Normal (LMB): {TOWER_COST}$", True, (200, 200, 200)), (rx, 10))
    screen.blit(FONT.render(f"Sniper (S): {SNIPER_TOWER_COST}$", True, (200, 200, 200)), (rx, 35))
    screen.blit(FONT.render(f"Slow (A): {SLOW_TOWER_COST}$", True, (200, 200, 200)), (rx, 60))
    screen.blit(FONT.render(f"Poison (D): {POISON_TOWER_COST}$", True, (200, 200, 200)), (rx, 85))

    hint = SMALL_FONT.render("Drag=merge | T=target | X=sell | ESC=quit", True, (170, 170, 170))
    screen.blit(hint, (10, HEIGHT - hint.get_height() - 10))

# ================== GAME HELPERS ==================
def tower_at_pos(towers, mx, my):
    for t in reversed(towers):
        rad = max(18, int((26 + t.level) * SCALE))
        if math.hypot(mx - t.x, my - t.y) <= rad:
            return t
    return None

def same_tower_type(a, b):
    return type(a) is type(b)

def tower_type_name(t):
    if isinstance(t, SniperTower):
        return "SNIPER"
    if isinstance(t, SlowTower):
        return "SLOW"
    if isinstance(t, PoisonTower):
        return "POISON"
    return "NORMAL"

# ================== LEVEL RUN ==================
def run_level(level, levels_unlocked):
    paths = level_paths[level]
    base = Base(*level_base[level])

    enemies = []
    towers = []
    bullets = []

    money = 1000000000
    score = 0
    game_over = False

    max_waves = level_wave_map.get(level, 5)
    wave = 1

    # wave pacing
    wave_started = False
    spawn_timer = 0
    spawn_interval = max(18, int(42 * (60 / FPS)))  # stable across FPS
    enemies_spawned = 0
    enemies_per_wave = 6
    inter_wave_pause = int(1.8 * FPS)
    between_waves = 0

    # boss wave: every 5th wave
    def is_boss_wave(w):
        return w % 5 == 0

    boss_spawned = False

    # selection + merge
    selected = None
    mouse_down_tower = None
    dragged = None
    drag_origin = None
    mouse_down_pos = None
    drag_started = False
    DRAG_THRESHOLD = max(7, int(8 * SCALE))

    running = True
    while running:
        clock.tick(FPS)
        screen.fill(BG_COLOR)
        mx, my = pygame.mouse.get_pos()
        keys = pygame.key.get_pressed()

        # ------------------ EVENTS ------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return None

            if event.type == pygame.KEYDOWN and not game_over:
                # Sell
                if event.key == pygame.K_x and selected and selected in towers:
                    money += int(selected.total_value * SELL_REFUND)
                    towers.remove(selected)
                    selected = None

                # Target mode cycle
                if event.key == pygame.K_t and selected and selected in towers:
                    selected.cycle_target_mode()

            if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                if event.button == 1:
                    t = tower_at_pos(towers, mx, my)
                    mouse_down_pos = (mx, my)
                    drag_started = False
                    mouse_down_tower = t

                    if t:
                        selected = t
                    else:
                        selected = None
                        if not is_on_any_path(level, mx, my):
                            # placement keys
                            if keys[pygame.K_s] and money >= SNIPER_TOWER_COST:
                                towers.append(SniperTower(mx, my))
                                money -= SNIPER_TOWER_COST
                            elif keys[pygame.K_a] and money >= SLOW_TOWER_COST:
                                towers.append(SlowTower(mx, my))
                                money -= SLOW_TOWER_COST
                            elif keys[pygame.K_d] and money >= POISON_TOWER_COST:
                                towers.append(PoisonTower(mx, my))
                                money -= POISON_TOWER_COST
                            elif money >= TOWER_COST:
                                towers.append(Tower(mx, my))
                                money -= TOWER_COST

            if event.type == pygame.MOUSEMOTION and not game_over:
                if mouse_down_tower and mouse_down_pos:
                    if (not drag_started) and math.hypot(mx - mouse_down_pos[0], my - mouse_down_pos[1]) >= DRAG_THRESHOLD:
                        drag_started = True
                        dragged = mouse_down_tower
                        drag_origin = (dragged.x, dragged.y)
                        dragged.dragging = True  # exploit fix

            if event.type == pygame.MOUSEBUTTONUP and not game_over:
                if event.button == 1:
                    if dragged:
                        merged = False
                        for t in towers:
                            if t is dragged:
                                continue
                            if same_tower_type(t, dragged) and t.level == dragged.level and t.can_upgrade():
                                if math.hypot(t.x - dragged.x, t.y - dragged.y) <= max(26, int(30 * SCALE)):
                                    if t.upgrade_stats_one_level():
                                        t.total_value += dragged.total_value
                                        towers.remove(dragged)
                                        merged = True
                                    break

                        if not merged and drag_origin:
                            dragged.x, dragged.y = drag_origin  # snap back, no moving

                        if dragged in towers:
                            dragged.dragging = False

                        dragged = None
                        drag_origin = None

                    mouse_down_tower = None
                    mouse_down_pos = None
                    drag_started = False

            if game_over and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return ("RESTART", level)
                if event.key == pygame.K_m:
                    return ("MENU", None)

        # follow mouse while dragging (visual only)
        if dragged and not game_over:
            dragged.x, dragged.y = mx, my

        # ------------------ WAVES / SPAWN ------------------
        if not game_over and wave <= max_waves:
            if between_waves > 0:
                between_waves -= 1
            else:
                if not wave_started:
                    boss_spawned = False
                    start_overlay(f"Wave {wave} starting!", (255, 255, 0), 1.35)
                    wave_started = True

                spawn_timer += 1

                # spawn normal/strong wave mobs
                if enemies_spawned < enemies_per_wave and spawn_timer >= spawn_interval:
                    spawn_timer = 0

                    # choose lane
                    if len(paths) == 1:
                        path_to_use = paths[0]
                    else:
                        path_to_use = paths[(wave + enemies_spawned) % len(paths)]

                    strong = (enemies_spawned % 2 == 0)
                    e = Enemy(path_to_use, strong=strong, boss=False)

                    # scale by wave + level
                    level_boost = (level - 1) * 0.12
                    e.max_hp = int(e.max_hp * (1.0 + 0.22 * (wave - 1) + level_boost))
                    e.hp = e.max_hp
                    e.damage = int(e.damage * (1.0 + 0.12 * (wave - 1) + level_boost))
                    e.base_speed = e.base_speed * (1.0 + 0.03 * (wave - 1))
                    enemies.append(e)

                    enemies_spawned += 1

                # spawn boss after mobs on boss wave
                if is_boss_wave(wave) and (enemies_spawned >= enemies_per_wave) and (not boss_spawned):
                    # spawn boss when no mobs left to spawn (but can still be alive)
                    # small delay: wait a moment
                    if spawn_timer >= int(0.9 * FPS):
                        if len(paths) == 1:
                            path_to_use = paths[0]
                        else:
                            path_to_use = paths[wave % len(paths)]
                        b = Enemy(path_to_use, strong=False, boss=True)

                        level_boost = (level - 1) * 0.25
                        b.max_hp = int(b.max_hp * (1.0 + 0.35 * (wave - 1) + level_boost))
                        b.hp = b.max_hp
                        b.damage = int(b.damage * (1.0 + 0.10 * (wave - 1) + level_boost))
                        b.base_speed = b.base_speed * (1.0 + 0.02 * (wave - 1))
                        enemies.append(b)

                        boss_spawned = True
                        spawn_timer = 0

                # wave complete?
                if enemies_spawned >= enemies_per_wave and len(enemies) == 0 and (not is_boss_wave(wave) or boss_spawned):
                    wave += 1
                    enemies_spawned = 0
                    enemies_per_wave += 2
                    wave_started = False
                    between_waves = inter_wave_pause
                    spawn_timer = 0

                    if wave > max_waves:
                        start_overlay(f"Level {level} Completed!", (0, 255, 0), 2.0)
                        if level < 3:
                            levels_unlocked[level + 1] = True
                        for _ in range(int(1.2 * FPS)):
                            clock.tick(FPS)
                            screen.fill(BG_COLOR)
                            draw_overlay()
                            pygame.display.flip()
                        return ("MENU", None)

        # ------------------ ENEMY UPDATE (end => damage once => remove) ------------------
        for e in enemies[:]:
            reached_end = e.move()
            if reached_end:
                base.take_damage(e.damage)
                enemies.remove(e)
                if base.hp <= 0:
                    game_over = True

        # ------------------ TOWERS SHOOT ------------------
        for t in towers:
            t.shoot(enemies, bullets)

        # ------------------ BULLETS ------------------
        for b in bullets[:]:
            if b.target not in enemies or b.target.hp <= 0:
                bullets.remove(b)
                continue

            b.move()
            if math.hypot(b.x - b.target.x, b.y - b.target.y) < max(10, int(12 * SCALE)):
                # hit
                b.target.hp -= b.damage

                # apply effect
                if b.effect:
                    kind = b.effect[0]
                    if kind == "slow":
                        _, factor, ticks = b.effect
                        b.target.apply_slow(factor, ticks)
                    elif kind == "poison":
                        _, dps, ticks = b.effect
                        b.target.apply_poison(dps, ticks)

                bullets.remove(b)

                if b.target.hp <= 0 and b.target in enemies:
                    enemies.remove(b.target)
                    money += b.target.reward_money
                    score += b.target.reward_score

        # ------------------ DRAW ------------------
        # draw paths
        for p in paths:
            draw_path(screen, p, PATH_WIDTH)

        # base
        base.draw()

        # enemies
        for e in enemies:
            e.draw()

        # towers
        for t in towers:
            t.draw_base()

        # hover/selected info + range circle
        hovered = tower_at_pos(towers, mx, my)
        info_target = hovered if hovered else selected

        if info_target and info_target in towers:
            # range circle
            pygame.draw.circle(screen, (255, 255, 255), (int(info_target.x), int(info_target.y)), int(info_target.range), 1)

            # info box
            ttype = tower_type_name(info_target)
            lvl = f"{info_target.level}/{info_target.max_level}"
            val = info_target.total_value
            sell = int(val * SELL_REFUND)

            lines = [
                f"{ttype}  Lv {lvl}",
                f"Target: {info_target.target_mode}  (T)",
            ]

            # per-type stats
            if isinstance(info_target, SlowTower):
                lines.append(f"DMG: {info_target.damage} | Rate: {info_target.fire_rate}")
                lines.append(f"Slow: {int((1-info_target.slow_factor)*100)}% | Dur: {info_target.slow_duration/FPS:.1f}s")
                lines.append(f"Range: {int(info_target.range)}")
            elif isinstance(info_target, PoisonTower):
                lines.append(f"DMG: {info_target.damage} | Rate: {info_target.fire_rate}")
                lines.append(f"Poison: {info_target.poison_dps:.0f}/s | Dur: {info_target.poison_duration/FPS:.1f}s")
                lines.append(f"Range: {int(info_target.range)}")
            else:
                lines.append(f"DMG: {info_target.damage} | Rate: {info_target.fire_rate}")
                lines.append(f"Range: {int(info_target.range)}")

            lines.append(f"Value: {val}$ | Sell (X): {sell}$")

            renders = [SMALL_FONT.render(s, True, (255, 255, 255)) for s in lines]
            box_w = max(r.get_width() for r in renders)
            pad = 10
            box_h = len(renders) * (SMALL_FONT.get_height() + 4) + pad

            box_x = min(WIDTH - (box_w + 2*pad) - 10, int(info_target.x + 25))
            box_y = max(10, int(info_target.y - box_h - 15))

            pygame.draw.rect(screen, (15, 15, 15), (box_x, box_y, box_w + 2*pad, box_h), border_radius=8)
            pygame.draw.rect(screen, (70, 70, 70), (box_x, box_y, box_w + 2*pad, box_h), 2, border_radius=8)

            yy = box_y + 6
            for r in renders:
                screen.blit(r, (box_x + pad, yy))
                yy += r.get_height() + 4

        # selected marker
        if selected and selected in towers:
            pygame.draw.circle(screen, (255, 255, 255), (int(selected.x), int(selected.y)), max(22, int((26 + selected.level) * SCALE)), 2)

        # bullets
        for b in bullets:
            b.draw()

        # HUD
        draw_hud(money, score, base.hp, wave, max_waves)

        # game over
        if game_over:
            text = BIG_FONT.render("GAME OVER", True, (255, 0, 0))
            sub = FONT.render("R = Restart | M = Menu | ESC = Quit", True, (255, 200, 200))
            screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - text.get_height()))
            screen.blit(sub, (WIDTH//2 - sub.get_width()//2, HEIGHT//2 + 10))

        draw_overlay()
        pygame.display.flip()

    return ("MENU", None)

# ================== MAIN PROGRAM ==================
levels_unlocked = {1: True, 2: True, 3: True}  # als je terug lock wil: zet 2/3 op False

while True:
    level = start_screen(levels_unlocked)
    res = run_level(level, levels_unlocked)

    if res is None:
        break

    action, payload = res
    if action == "RESTART":
        while True:
            r2 = run_level(payload, levels_unlocked)
            if r2 is None:
                pygame.quit()
                raise SystemExit
            if r2[0] == "RESTART":
                continue
            break

pygame.quit()
