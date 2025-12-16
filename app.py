import pygame
import math
import random

pygame.init()

# ================== DISPLAY ==================
# Borderless fullscreen (werkt op elke resolutie)
screen = pygame.display.set_mode((0, 0), pygame.NOFRAME)
pygame.display.set_caption("Tower Defence")
clock = pygame.time.Clock()
WIDTH, HEIGHT = screen.get_size()
FPS = 60

# ================== DEV ==================
DEV_INFINITE_MONEY = True  # debug / sandbox mode

# ================== CONSTANTEN ==================
TOWER_COST = 50
SNIPER_TOWER_COST = 120
SLOW_TOWER_COST = 90
POISON_TOWER_COST = 110

SELL_REFUND = 0.75
MAX_TOWER_LEVEL = 6
MIN_TOWER_DISTANCE = 48  # base personal space (wordt geschaald)

# ================== COLORS ==================
BG_COLOR = (30, 30, 30)
PATH_COLOR = (100, 100, 100)

ENEMY_COLOR = (200, 50, 50)
STRONG_ENEMY_COLOR = (50, 50, 200)
FAST_ENEMY_COLOR = (240, 200, 80)
BOSS_COLOR = (160, 60, 220)

TOWER_COLOR = (50, 200, 50)
SNIPER_COLOR = (50, 150, 255)
SLOW_COLOR = (90, 220, 220)
POISON_COLOR = (160, 220, 80)

BASE_COLOR = (200, 50, 50)
BULLET_COLOR = (255, 255, 0)
TEXT_COLOR = (240, 240, 240)

# ================== FONTS ==================
FONT = pygame.font.SysFont(None, 28)
SMALL_FONT = pygame.font.SysFont(None, 22)
BIG_FONT = pygame.font.SysFont(None, 72)

# ================== SCALING (800x600 basis) ==================
BASE_W, BASE_H = 800, 600
sx = WIDTH / BASE_W
sy = HEIGHT / BASE_H
SCALE = min(sx, sy)

def sp(p):
    """Scale position from base resolution"""
    return int(p[0] * sx), int(p[1] * sy)

def spath(path):
    """Scale entire path"""
    return [sp(pt) for pt in path]

PATH_WIDTH = max(22, int(40 * SCALE))
MIN_TOWER_DISTANCE = int(MIN_TOWER_DISTANCE * SCALE)

# ================== MAP DATA (BASE RESOLUTION) ==================
_level_paths_base = {
    # Map 1 — klassiek
    1: [
        (-50, 550), (50, 550), (50, 200), (200, 150),
        (300, 300), (600, 300), (600, 100),
        (450, 100), (450, 550)
    ],

    # Map 2 — slingerpad
    2: [
        (-50, 300), (150, 300), (150, 100),
        (650, 100), (650, 500), (300, 500),
        (300, 250), (550, 250), (550, 550)
    ],

    # Map 3 — multi-lane
    31: [
        (-50, 180), (120, 180), (120, 80),
        (420, 80), (420, 260), (560, 260), (560, 550)
    ],
    32: [
        (850, 420), (680, 420), (680, 520),
        (260, 520), (260, 320), (560, 320), (560, 550)
    ]
}

# ================== SCALED MAPS ==================
level_paths = {
    1: [spath(_level_paths_base[1])],
    2: [spath(_level_paths_base[2])],
    3: [spath(_level_paths_base[31]), spath(_level_paths_base[32])]
}

level_base = {
    1: sp((450, 550)),
    2: sp((550, 550)),
    3: sp((560, 550))
}

level_wave_map = {
    1: 5,
    2: 10,
    3: 15
}
# ================== OVERLAY ==================
overlay = None

def start_overlay(text, color=(255, 255, 0), duration_sec=1.4):
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
    return any(is_on_path(x, y, p) for p in level_paths[level])

def too_close_to_tower(towers, x, y):
    for t in towers:
        if math.hypot(t.x - x, t.y - y) < MIN_TOWER_DISTANCE:
            return True
    return False

def hp_bar(x, y, hp, max_hp, w, h=6):
    ratio = 0 if max_hp <= 0 else max(0, min(1, hp / max_hp))
    pygame.draw.rect(screen, (255, 0, 0), (x - w//2, y, w, h))
    pygame.draw.rect(screen, (0, 255, 0), (x - w//2, y, int(w * ratio), h))

# ================== PATH PREVIEW (cirkels volgen exact enemy route) ==================
# Dit tekent een "ghost train" van cirkels die het pad volgen.
# Gebruik dit in placement preview zodat je ziet hoe enemies lopen.
def draw_enemy_path_preview(paths, tick, spacing_px=None):
    if spacing_px is None:
        spacing_px = max(26, int(34 * SCALE))  # afstand tussen preview-cirkels

    # helper: lineair interpoleren
    def lerp(a, b, t):
        return a + (b - a) * t

    for path in paths:
        # loop segments en leg ghost-cirkels op vaste afstanden
        for i in range(len(path) - 1):
            x1, y1 = path[i]
            x2, y2 = path[i + 1]
            dx, dy = x2 - x1, y2 - y1
            seg_len = math.hypot(dx, dy)
            if seg_len <= 0:
                continue

            # verschuiving zodat de cirkels "bewegen" langs het pad
            # tick bepaalt offset in pixels
            offset = (-tick * max(1.0, 2.2 * SCALE)) % spacing_px

            # plaats meerdere cirkels op dit segment
            # start bij -offset zodat het mooi doorloopt over segmenten
            s = -offset
            while s < seg_len:
                t = max(0.0, min(1.0, s / seg_len))
                px = lerp(x1, x2, t)
                py = lerp(y1, y2, t)

                # subtiele ghost (ring)
                pygame.draw.circle(
                    screen,
                    (160, 160, 160),
                    (int(px), int(py)),
                    max(6, int(8 * SCALE)),
                    1
                )
                s += spacing_px

# ================== TARGETING ==================
TARGET_FIRST = "FIRST"
TARGET_STRONG = "STRONG"
TARGET_CLOSEST = "CLOSEST"
TARGET_MODES = [TARGET_FIRST, TARGET_STRONG, TARGET_CLOSEST]

# ================== ENEMIES ==================
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

class FastEnemy(Enemy):
    def __init__(self, path):
        super().__init__(path, strong=False, boss=False)
        self.max_hp = 45
        self.hp = self.max_hp
        self.damage = 6
        self.reward_money = 8
        self.reward_score = 8
        self.base_speed = 3.8 * SCALE
        self.speed = self.base_speed
        self.color = FAST_ENEMY_COLOR
        self.radius = max(8, int(10 * SCALE))

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
        # merge moet hard voelen
        self.damage += 22
        self.range += int(26 * SCALE)
        self.fire_rate = max(7, self.fire_rate - 4)
        return True

class SniperTower(TowerBase):
    def __init__(self, x, y):
        super().__init__(x, y, SNIPER_TOWER_COST, SNIPER_COLOR)
        self.range = int(350 * SCALE)
        self.fire_rate = 90
        self.damage = 100

    def draw_base(self):
        r = max(14, int((22 + self.level) * SCALE))
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), r)
        txt = SMALL_FONT.render(str(self.level), True, (0, 0, 0))
        screen.blit(txt, (int(self.x - txt.get_width()/2), int(self.y - txt.get_height()/2)))

    def upgrade_stats_one_level(self):
        if not self.can_upgrade():
            return False
        self.level += 1
        self.damage += 55
        self.range += int(40 * SCALE)
        self.fire_rate = max(20, self.fire_rate - 10)
        return True

class SlowTower(TowerBase):
    def __init__(self, x, y):
        super().__init__(x, y, SLOW_TOWER_COST, SLOW_COLOR)
        self.range = int(170 * SCALE)
        self.fire_rate = 45
        self.damage = 8
        self.slow_factor = 0.55
        self.slow_duration = int(2.2 * FPS)

    def upgrade_stats_one_level(self):
        if not self.can_upgrade():
            return False
        self.level += 1
        self.damage += 7
        self.range += int(22 * SCALE)
        self.fire_rate = max(14, self.fire_rate - 4)
        self.slow_factor = max(0.25, self.slow_factor - 0.06)
        self.slow_duration = int(min(6.0 * FPS, self.slow_duration + 0.8 * FPS))
        return True

    def shoot(self, enemies, bullets):
        if self.dragging:
            return
        if self.cooldown > 0:
            self.cooldown -= 1
            return

        target = self.choose_target(enemies)
        if not target:
            return

        bullets.append(Bullet(self.x, self.y, target, self.damage, ("slow", self.slow_factor, self.slow_duration)))
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
        self.damage += 8 + self.level * 2
        self.range += int(22 * SCALE)
        self.fire_rate = max(10, self.fire_rate - 5)
        # poison moet echt hard gaan op lvl 5-6
        self.poison_dps = self.poison_dps * 1.45 + 10
        self.poison_duration = int(min(7.0 * FPS, self.poison_duration + 0.9 * FPS))
        return True

    def shoot(self, enemies, bullets):
        if self.dragging:
            return
        if self.cooldown > 0:
            self.cooldown -= 1
            return

        target = self.choose_target(enemies)
        if not target:
            return

        bullets.append(Bullet(self.x, self.y, target, self.damage, ("poison", self.poison_dps, self.poison_duration)))
        self.cooldown = self.fire_rate

# ================== HELPERS (selection/merge) ==================
def tower_at_pos(towers, mx, my):
    for t in reversed(towers):
        rad = max(18, int((26 + t.level) * SCALE))
        if math.hypot(mx - t.x, my - t.y) <= rad:
            return t
    return None

def same_tower_type(a, b):
    return type(a) is type(b)

def tower_type_name(t):
    if isinstance(t, SniperTower): return "SNIPER"
    if isinstance(t, SlowTower): return "SLOW"
    if isinstance(t, PoisonTower): return "POISON"
    return "NORMAL"

def preview_stats_for_type(ttype):
    if ttype == "SNIPER":
        return SNIPER_COLOR, int(350 * SCALE)
    if ttype == "SLOW":
        return SLOW_COLOR, int(170 * SCALE)
    if ttype == "POISON":
        return POISON_COLOR, int(160 * SCALE)
    return TOWER_COLOR, int(150 * SCALE)

# ================== BASE ==================
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

# ================== UI SCREENS ==================
def instructions_screen():
    viewing = True
    while viewing:
        screen.fill(BG_COLOR)
        title = BIG_FONT.render("Instructies", True, TEXT_COLOR)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, int(0.08 * HEIGHT)))

        lines = [
            "Plaatsen (klik INHOUDEN):",
            "LMB = Normal",
            "S + LMB = Sniper",
            "A + LMB = Slow",
            "D + LMB = Poison",
            "",
            "Loslaten = plaatsen | loslaten op pad = annuleren",
            "",
            "Merge-upgrade:",
            "Sleep 2 towers van hetzelfde type + level op elkaar",
            f"Max tower level: {MAX_TOWER_LEVEL}",
            "",
            "Selecteer tower + T: target mode",
            f"Sell: selecteer tower + X (refund {int(SELL_REFUND*100)}%)",
            "",
            "ESC: terug"
        ]

        y0 = int(0.24 * HEIGHT)
        for i, line in enumerate(lines):
            txt = FONT.render(line, True, (210, 210, 210))
            screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, y0 + i * 30))

        pygame.display.flip()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                viewing = False


def start_screen():
    selecting = True
    while selecting:
        screen.fill(BG_COLOR)
        title = BIG_FONT.render("Tower Defence", True, TEXT_COLOR)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, int(0.10 * HEIGHT)))

        mx, my = pygame.mouse.get_pos()
        entries = ["Level 1", "Level 2", "Level 3", "Instructies"]
        rects = []
        y0 = int(0.36 * HEIGHT)
        step = int(0.11 * HEIGHT)

        for i, name in enumerate(entries):
            text = FONT.render(name, True, (255, 255, 0))
            rect = text.get_rect(center=(WIDTH // 2, y0 + i * step))
            if rect.collidepoint(mx, my):
                pygame.draw.rect(screen, (255, 255, 150), rect.inflate(30, 16), border_radius=8)
            screen.blit(text, rect)
            rects.append((rect, name))

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
                for rect, name in rects:
                    if rect.collidepoint(e.pos):
                        if name == "Instructies":
                            instructions_screen()
                        else:
                            return int(name.split()[1])

# ================== HUD ==================
def draw_hud(money, score, base_hp, wave, max_waves):
    screen.blit(FONT.render(f"Score: {score}", True, (255, 255, 255)), (10, 10))
    screen.blit(FONT.render(f"Base HP: {base_hp}", True, (255, 255, 255)), (10, 40))
    screen.blit(FONT.render(f"Money: {money}", True, (0, 220, 0)), (10, 70))
    screen.blit(FONT.render(f"Wave: {wave}/{max_waves}", True, (255, 255, 255)), (10, 100))

    rx = WIDTH - 380
    screen.blit(FONT.render(f"LMB = Normal ({TOWER_COST}$)", True, (200, 200, 200)), (rx, 10))
    screen.blit(FONT.render(f"S + LMB = Sniper ({SNIPER_TOWER_COST}$)", True, (200, 200, 200)), (rx, 35))
    screen.blit(FONT.render(f"A + LMB = Slow ({SLOW_TOWER_COST}$)", True, (200, 200, 200)), (rx, 60))
    screen.blit(FONT.render(f"D + LMB = Poison ({POISON_TOWER_COST}$)", True, (200, 200, 200)), (rx, 85))

    hint = SMALL_FONT.render(
        "Hold+Release to place | Drag=merge | T=target | X=sell | ESC=menu",
        True,
        (170, 170, 170)
    )
    screen.blit(hint, (10, HEIGHT - hint.get_height() - 10))

# ================== LEVEL LOOP ==================
def run_level(level):
    paths = level_paths[level]
    base = Base(*level_base[level])

    enemies = []
    towers = []
    bullets = []

    money = 99999999 if DEV_INFINITE_MONEY else 140
    score = 0
    game_over = False

    max_waves = level_wave_map.get(level, 5)
    wave = 1

    wave_started = False
    spawn_timer = 0
    spawn_interval = max(18, int(42 * (60 / FPS)))
    enemies_spawned = 0
    enemies_per_wave = 6
    inter_wave_pause = int(1.8 * FPS)
    between_waves = 0

    def is_boss_wave(w):
        return w % 5 == 0

    boss_spawned = False

    # selection + merge
    selected = None
    dragged = None
    drag_origin = None

    # placement preview state (CLICK-HOLD)
    placing_preview = False
    placing_type = None
    placing_cost = 0

    tick = 0  # voor moving path preview

    running = True
    while running:
        clock.tick(FPS)
        screen.fill(BG_COLOR)
        mx, my = pygame.mouse.get_pos()
        keys = pygame.key.get_pressed()
        tick += 1

        # ------------------ EVENTS ------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return None

            if event.type == pygame.KEYDOWN and not game_over:
                # sell
                if event.key == pygame.K_x and selected and selected in towers:
                    if not DEV_INFINITE_MONEY:
                        money += int(selected.total_value * SELL_REFUND)
                    towers.remove(selected)
                    selected = None

                # targeting
                if event.key == pygame.K_t and selected and selected in towers:
                    selected.cycle_target_mode()

            if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                if event.button == 1:
                    # klik op tower = drag voor merge
                    t = tower_at_pos(towers, mx, my)
                    if t:
                        selected = t
                        dragged = t
                        drag_origin = (t.x, t.y)
                        t.dragging = True
                        placing_preview = False
                        placing_type = None
                        placing_cost = 0
                    else:
                        # placement preview start
                        selected = None

                        if keys[pygame.K_s]:
                            placing_type = "SNIPER"
                            placing_cost = SNIPER_TOWER_COST
                        elif keys[pygame.K_a]:
                            placing_type = "SLOW"
                            placing_cost = SLOW_TOWER_COST
                        elif keys[pygame.K_d]:
                            placing_type = "POISON"
                            placing_cost = POISON_TOWER_COST
                        else:
                            placing_type = "NORMAL"
                            placing_cost = TOWER_COST

                        if DEV_INFINITE_MONEY or money >= placing_cost:
                            placing_preview = True
                        else:
                            placing_preview = False
                            placing_type = None
                            placing_cost = 0

            if event.type == pygame.MOUSEBUTTONUP and not game_over:
                if event.button == 1:
                    # ------------------ PLACE ON RELEASE ------------------
                    if placing_preview:
                        valid = (
                            not is_on_any_path(level, mx, my)
                            and not too_close_to_tower(towers, mx, my)
                        )

                        if valid:
                            if placing_type == "SNIPER":
                                towers.append(SniperTower(mx, my))
                            elif placing_type == "SLOW":
                                towers.append(SlowTower(mx, my))
                            elif placing_type == "POISON":
                                towers.append(PoisonTower(mx, my))
                            else:
                                towers.append(Tower(mx, my))

                            if not DEV_INFINITE_MONEY:
                                money -= placing_cost

                        # reset placement state
                        placing_preview = False
                        placing_type = None
                        placing_cost = 0

                    # ------------------ MERGE ON RELEASE ------------------
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
                            dragged.x, dragged.y = drag_origin  # snap back

                        if dragged in towers:
                            dragged.dragging = False

                        dragged = None
                        drag_origin = None

        # drag follow mouse (visual only) — snaps back if not merged
        if dragged and not game_over:
            dragged.x, dragged.y = mx, my

        # ------------------ WAVES / SPAWN ------------------
        if not game_over and wave <= max_waves:
            if between_waves > 0:
                between_waves -= 1
            else:
                if not wave_started:
                    boss_spawned = False
                    start_overlay(f"Wave {wave} starting!", (255, 255, 0), 1.2)
                    wave_started = True

                spawn_timer += 1

                if enemies_spawned < enemies_per_wave and spawn_timer >= spawn_interval:
                    spawn_timer = 0
                    path_to_use = paths[(wave + enemies_spawned) % len(paths)]

                    r = random.random()
                    if r < 0.25:
                        e = FastEnemy(path_to_use)
                    elif r < 0.65:
                        e = Enemy(path_to_use, strong=False)
                    else:
                        e = Enemy(path_to_use, strong=True)

                    # scale by wave + level
                    level_boost = (level - 1) * 0.12
                    e.max_hp = int(e.max_hp * (1.0 + 0.22 * (wave - 1) + level_boost))
                    e.hp = e.max_hp
                    e.damage = int(e.damage * (1.0 + 0.12 * (wave - 1) + level_boost))
                    e.base_speed = e.base_speed * (1.0 + 0.03 * (wave - 1))
                    enemies.append(e)

                    enemies_spawned += 1

                # boss wave
                if is_boss_wave(wave) and enemies_spawned >= enemies_per_wave and not boss_spawned:
                    if spawn_timer >= int(0.9 * FPS):
                        path_to_use = paths[wave % len(paths)]
                        b = Enemy(path_to_use, boss=True)

                        level_boost = (level - 1) * 0.25
                        b.max_hp = int(b.max_hp * (1.0 + 0.35 * (wave - 1) + level_boost))
                        b.hp = b.max_hp
                        b.damage = int(b.damage * (1.0 + 0.10 * (wave - 1) + level_boost))
                        b.base_speed = b.base_speed * (1.0 + 0.02 * (wave - 1))
                        enemies.append(b)

                        boss_spawned = True
                        spawn_timer = 0

                # wave complete
                if enemies_spawned >= enemies_per_wave and len(enemies) == 0 and (not is_boss_wave(wave) or boss_spawned):
                    wave += 1
                    enemies_spawned = 0
                    enemies_per_wave += 2
                    wave_started = False
                    between_waves = inter_wave_pause
                    spawn_timer = 0

                    if wave > max_waves:
                        start_overlay(f"Level {level} Completed!", (0, 255, 0), 2.0)
                        for _ in range(int(1.0 * FPS)):
                            clock.tick(FPS)
                            screen.fill(BG_COLOR)
                            draw_overlay()
                            pygame.display.flip()
                        return ("MENU", None)

        # ------------------ ENEMIES UPDATE ------------------
        # Belangrijk: Enemy.move() kan "DEAD" teruggeven door poison (DEEL 2 fix).
        for e in enemies[:]:
            res = e.move()

            if res == "DEAD":
                enemies.remove(e)
                continue

            if res is True:  # reached end
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
                b.target.hp -= b.damage

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
                    if not DEV_INFINITE_MONEY:
                        money += b.target.reward_money
                    score += b.target.reward_score

        # ------------------ DRAW ------------------
        for p in paths:
            draw_path(screen, p, PATH_WIDTH)

        base.draw()

        for e in enemies:
            e.draw()

        for t in towers:
            t.draw_base()

        # ------------------ PLACEMENT PREVIEW ------------------
        if placing_preview and placing_type:
            # bewegende path preview (cirkels volgen pad)
            draw_enemy_path_preview(paths, tick)

            color, rng = preview_stats_for_type(placing_type)
            valid = (not is_on_any_path(level, mx, my)) and (not too_close_to_tower(towers, mx, my))
            ghost_col = color if valid else (220, 80, 80)

            pygame.draw.circle(screen, ghost_col, (mx, my), max(12, int(18 * SCALE)), 2)
            pygame.draw.circle(screen, (255, 255, 255), (mx, my), rng, 1)

            tip = SMALL_FONT.render("Hold LMB... release to place", True, (230, 230, 230))
            screen.blit(tip, (mx + 18, my + 18))

        # ------------------ HOVER/SELECT INFO ------------------
        hovered = tower_at_pos(towers, mx, my)
        info_target = hovered if hovered else selected
        if info_target and info_target in towers:
            pygame.draw.circle(
                screen,
                (255, 255, 255),
                (int(info_target.x), int(info_target.y)),
                int(info_target.range),
                1
            )

            ttype = tower_type_name(info_target)
            lvl = f"{info_target.level}/{info_target.max_level}"
            val = info_target.total_value
            sell = int(val * SELL_REFUND)

            lines = [
                f"{ttype}  Lv {lvl}",
                f"Target: {info_target.target_mode} (T)",
                f"DMG: {getattr(info_target, 'damage', 0)} | Rate: {getattr(info_target, 'fire_rate', 0)}",
                f"Range: {int(getattr(info_target, 'range', 0))}",
                f"Value: {val}$ | Sell (X): {sell}$"
            ]

            renders = [SMALL_FONT.render(s, True, (255, 255, 255)) for s in lines]
            box_w = max(r.get_width() for r in renders)
            pad = 10
            box_h = len(renders) * (SMALL_FONT.get_height() + 4) + pad

            box_x = min(WIDTH - (box_w + 2 * pad) - 10, int(info_target.x + 25))
            box_y = max(10, int(info_target.y - box_h - 15))

            pygame.draw.rect(screen, (15, 15, 15), (box_x, box_y, box_w + 2 * pad, box_h), border_radius=8)
            pygame.draw.rect(screen, (70, 70, 70), (box_x, box_y, box_w + 2 * pad, box_h), 2, border_radius=8)

            yy = box_y + 6
            for r in renders:
                screen.blit(r, (box_x + pad, yy))
                yy += r.get_height() + 4

        if selected and selected in towers:
            pygame.draw.circle(
                screen,
                (255, 255, 255),
                (int(selected.x), int(selected.y)),
                max(22, int((26 + selected.level) * SCALE)),
                2
            )

        for b in bullets:
            b.draw()

        draw_hud(money, score, base.hp, wave, max_waves)
        draw_overlay()

        if game_over:
            text = BIG_FONT.render("GAME OVER", True, (255, 0, 0))
            sub = FONT.render("ESC = Menu", True, (255, 200, 200))
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height()))
            screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, HEIGHT // 2 + 10))

        pygame.display.flip()

# ================== MAIN ==================
while True:
    level = start_screen()
    run_level(level)

pygame.quit()
