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
TOWER_COST = 50
SNIPER_TOWER_COST = 120
SELL_REFUND = 0.75
MAX_TOWER_LEVEL = 6

BG_COLOR = (30, 30, 30)
PATH_COLOR = (100, 100, 100)
ENEMY_COLOR = (200, 50, 50)
STRONG_ENEMY_COLOR = (50, 50, 200)
TOWER_COLOR = (50, 200, 50)
SNIPER_COLOR = (50, 150, 255)
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
    """Scale point (x,y) from 800x600 space to current screen space."""
    x, y = p
    return (int(x * sx), int(y * sy))

def spath(path):
    return [sp(pt) for pt in path]

PATH_WIDTH = max(22, int(40 * SCALE))

# ================== LEVEL MAPS (bron in 800x600) ==================
_level_paths_base = {
    1: [(-50, 550), (50, 550), (50, 200), (200, 150),
        (300, 300), (600, 300), (600, 100), (450, 100), (450, 550)],
    2: [
        # spawn 1
        {'spawn': (-50, 500), 'path': [(-50, 500), (100, 500), (100, 200), (400, 200),
                                       (400, 400), (700, 400), (700, 100), (600, 100), (600, 550)]},
        # spawn 2
        {'spawn': (850, 300), 'path': [(850, 300), (600, 300), (600, 150), (400, 150),
                                       (400, 450), (200, 450), (200, 550), (450, 550)]}
    ]
}

level_paths = {
    1: spath(_level_paths_base[1]),
    2: [
        {'spawn': sp(_level_paths_base[2][0]['spawn']), 'path': spath(_level_paths_base[2][0]['path'])},
        {'spawn': sp(_level_paths_base[2][1]['spawn']), 'path': spath(_level_paths_base[2][1]['path'])},
    ],
    # Level 3: hergebruikt level 2 layout (meer waves/sterker)
    3: [
        {'spawn': sp(_level_paths_base[2][0]['spawn']), 'path': spath(_level_paths_base[2][0]['path'])},
        {'spawn': sp(_level_paths_base[2][1]['spawn']), 'path': spath(_level_paths_base[2][1]['path'])},
    ],
}

level_base = {
    1: sp((450, 550)),
    2: sp((450, 550)),
    3: sp((450, 550)),
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

# ================== GEOMETRIE / PATH HELPERS ==================
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

def is_on_path(x, y, path_to_check):
    for i in range(len(path_to_check) - 1):
        x1, y1 = path_to_check[i]
        x2, y2 = path_to_check[i + 1]
        d = dist_point_to_segment(x, y, x1, y1, x2, y2)
        if d <= PATH_WIDTH // 2 + max(4, int(5 * SCALE)):
            return True
    return False

def is_on_any_path_level(level, x, y):
    if level == 1:
        return is_on_path(x, y, level_paths[1])
    for spawn_info in level_paths[level]:
        if is_on_path(x, y, spawn_info["path"]):
            return True
    return False

def draw_hp_bar_centered(cx, cy, hp, max_hp, w, h, y_offset):
    ratio = 0 if max_hp <= 0 else max(0, min(1, hp / max_hp))
    x = cx - w // 2
    y = cy + y_offset
    pygame.draw.rect(screen, (255, 0, 0), (x, y, w, h))
    pygame.draw.rect(screen, (0, 255, 0), (x, y, int(w * ratio), h))

# ================== UI SCREENS ==================
def instructions_screen():
    viewing = True
    while viewing:
        screen.fill(BG_COLOR)
        title = BIG_FONT.render("Instructies", True, TEXT_COLOR)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, int(0.08 * HEIGHT)))

        lines = [
            "LMB: Tower plaatsen",
            "S + LMB: Sniper plaatsen",
            "",
            "Upgrade (merge):",
            "Sleep 2 towers van hetzelfde type + level op elkaar",
            f"Max tower level: {MAX_TOWER_LEVEL}",
            "",
            f"Sell: selecteer tower + druk X (refund {int(SELL_REFUND*100)}%)",
            "",
            "ESC: terug"
        ]
        start_y = int(0.30 * HEIGHT)
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

        hint = SMALL_FONT.render("ESC = afsluiten", True, (180, 180, 180))
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

# ================== CLASSES ==================
class Enemy:
    def __init__(self, path, x=None, y=None, hp=100, damage=10, speed=2.0):
        self.path = path
        self.x, self.y = (path[0] if (x is None or y is None) else (x, y))
        self.speed = speed
        self.max_hp = hp
        self.hp = hp
        self.damage = damage
        self.target_index = 1
        self.reward_money = 10
        self.reward_score = 10

    def move(self):
        # ✅ Einde bereikt => True (wordt dan verwijderd in game loop)
        if self.target_index >= len(self.path):
            return True

        tx, ty = self.path[self.target_index]
        dx, dy = tx - self.x, ty - self.y
        dist = math.hypot(dx, dy)
        if dist < self.speed:
            self.target_index += 1
        else:
            self.x += self.speed * dx / dist
            self.y += self.speed * dy / dist
        return False

    def draw(self):
        r = max(10, int(15 * SCALE))
        pygame.draw.circle(screen, ENEMY_COLOR, (int(self.x), int(self.y)), r)
        draw_hp_bar_centered(int(self.x), int(self.y), self.hp, self.max_hp,
                             w=max(40, int(55 * SCALE)), h=max(6, int(8 * SCALE)), y_offset=-int(30 * SCALE))

class StrongEnemy(Enemy):
    def __init__(self, path, x=None, y=None, hp=300, damage=25, speed=1.5):
        super().__init__(path, x, y, hp, damage, speed)
        self.reward_money = 25
        self.reward_score = 30

    def draw(self):
        r = max(14, int(20 * SCALE))
        pygame.draw.circle(screen, STRONG_ENEMY_COLOR, (int(self.x), int(self.y)), r)
        draw_hp_bar_centered(int(self.x), int(self.y), self.hp, self.max_hp,
                             w=max(44, int(65 * SCALE)), h=max(6, int(8 * SCALE)), y_offset=-int(34 * SCALE))

class Bullet:
    def __init__(self, x, y, target, damage):
        self.x = x
        self.y = y
        self.target = target
        self.speed = max(5, int(7 * SCALE))
        self.damage = damage

    def move(self):
        dx = self.target.x - self.x
        dy = self.target.y - self.y
        dist = math.hypot(dx, dy)
        if dist:
            self.x += self.speed * dx / dist
            self.y += self.speed * dy / dist

    def draw(self):
        pygame.draw.circle(screen, BULLET_COLOR, (int(self.x), int(self.y)), max(3, int(5 * SCALE)))

class Tower:
    def __init__(self, x, y):
        self.x = x
        self.y = y

        self.level = 1
        self.max_level = MAX_TOWER_LEVEL

        self.range = int(150 * SCALE)
        self.cooldown = 0
        self.fire_rate = 30
        self.damage = 25
        self.color = TOWER_COLOR

        self.base_cost = TOWER_COST
        self.total_value = self.base_cost  # som van investeringen via merges

        self.dragging = False  # exploit fix

    def shoot(self, enemies, bullets):
        if self.dragging:
            return
        if self.cooldown > 0:
            self.cooldown -= 1
            return
        for enemy in enemies:
            if math.hypot(enemy.x - self.x, enemy.y - self.y) < self.range:
                bullets.append(Bullet(self.x, self.y, enemy, self.damage))
                self.cooldown = self.fire_rate
                break

    def can_upgrade(self):
        return self.level < self.max_level

    def upgrade_stats_one_level(self):
        if not self.can_upgrade():
            return False
        self.level += 1
        self.damage += 15
        self.range += int(20 * SCALE)
        self.fire_rate = max(8, self.fire_rate - 3)
        return True

    def draw_base(self):
        r = max(10, int((15 + self.level) * SCALE))
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), r)
        txt = SMALL_FONT.render(str(self.level), True, (0, 0, 0))
        screen.blit(txt, (int(self.x - txt.get_width()/2), int(self.y - txt.get_height()/2)))

class SniperTower(Tower):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.range = int(350 * SCALE)
        self.fire_rate = 90
        self.damage = 100
        self.color = SNIPER_COLOR

        self.base_cost = SNIPER_TOWER_COST
        self.total_value = self.base_cost

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
        txt = SMALL_FONT.render(str(self.level), True, (0, 0, 0))
        screen.blit(txt, (int(self.x - txt.get_width()/2), int(self.y - txt.get_height()/2)))

class Base:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.max_hp = 200
        self.hp = self.max_hp

    def take_damage(self, dmg):
        self.hp -= dmg
        if self.hp < 0:
            self.hp = 0

    def draw(self):
        size = max(40, int(55 * SCALE))
        pygame.draw.rect(screen, BASE_COLOR, (int(self.x - size/2), int(self.y - size/2), size, size))

        # ✅ correcte HP bar
        bar_w = max(60, int(90 * SCALE))
        bar_h = max(6, int(8 * SCALE))
        ratio = self.hp / self.max_hp if self.max_hp else 0
        x = int(self.x - bar_w/2)
        y = int(self.y - size/2 - (bar_h + 8))
        pygame.draw.rect(screen, (255, 0, 0), (x, y, bar_w, bar_h))
        pygame.draw.rect(screen, (0, 255, 0), (x, y, int(bar_w * ratio), bar_h))

# ================== GAME HELPERS ==================
def tower_at_pos(towers, mx, my):
    for t in reversed(towers):
        rad = max(18, int((26 + t.level) * SCALE))
        if math.hypot(mx - t.x, my - t.y) <= rad:
            return t
    return None

def same_tower_type(a, b):
    return type(a) is type(b)

def draw_hud(money, score, base_hp, wave, max_waves):
    # links: stats
    screen.blit(FONT.render(f"Money: {money}", True, TEXT_COLOR), (10, 10))
    screen.blit(FONT.render(f"Base HP: {base_hp}", True, TEXT_COLOR), (10, 40))
    screen.blit(FONT.render(f"Score: {score}", True, TEXT_COLOR), (10, 70))
    if wave <= max_waves:
        screen.blit(FONT.render(f"Wave: {wave}/{max_waves}", True, TEXT_COLOR), (10, 100))

    # rechts: prijzen
    right_x = WIDTH - 260
    screen.blit(FONT.render(f"Tower (LMB): {TOWER_COST}$", True, (200, 200, 200)), (right_x, 10))
    screen.blit(FONT.render(f"Sniper (S+LMB): {SNIPER_TOWER_COST}$", True, (200, 200, 200)), (right_x, 40))

    # mini controls hint (klein, niet “helft van scherm”)
    hint = SMALL_FONT.render("Drag=merge | X=sell | ESC=quit", True, (170, 170, 170))
    screen.blit(hint, (10, HEIGHT - hint.get_height() - 10))

# ================== MAIN GAME LOOP FUNCTION ==================
def run_level(level_chosen, levels_unlocked):
    max_waves = level_wave_map.get(level_chosen, 5)

    enemies = []
    towers = []
    bullets = []
    base = Base(*level_base[level_chosen])

    money = 100
    score = 0
    game_over = False

    # waves
    wave = 1
    wave_timer = 0
    enemies_spawned = 0
    enemies_per_wave = 6
    spawn_interval = int(45 * (60 / FPS))  # frames tussen spawns (stabiel)
    inter_wave_pause = int(2.0 * FPS)      # pauze na wave
    between_waves = 0
    wave_started = False

    # merge / select state
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

        # -------------- EVENTS --------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None  # exit
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return None  # exit

            if event.type == pygame.KEYDOWN and not game_over:
                # Sell (X)
                if event.key == pygame.K_x and selected and selected in towers:
                    refund = int(selected.total_value * SELL_REFUND)
                    money += refund
                    towers.remove(selected)
                    selected = None

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
                        if not is_on_any_path_level(level_chosen, mx, my):
                            if keys[pygame.K_s] and money >= SNIPER_TOWER_COST:
                                towers.append(SniperTower(mx, my))
                                money -= SNIPER_TOWER_COST
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
                                    # merge => upgrade target, value = sum
                                    if t.upgrade_stats_one_level():
                                        t.total_value += dragged.total_value
                                        towers.remove(dragged)
                                        merged = True
                                    break

                        if not merged and drag_origin:
                            # snap back => niet verplaatsen
                            dragged.x, dragged.y = drag_origin

                        if dragged in towers:
                            dragged.dragging = False

                        dragged = None
                        drag_origin = None

                    mouse_down_tower = None
                    mouse_down_pos = None
                    drag_started = False

            if game_over and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    # restart current level
                    return ("RESTART", level_chosen)
                if event.key == pygame.K_m:
                    # back to menu
                    return ("MENU", None)

        # drag visuals (alleen zolang je vasthoudt)
        if dragged and not game_over:
            dragged.x, dragged.y = mx, my

        # -------------- WAVES / SPAWN --------------
        if not game_over and wave <= max_waves:
            if between_waves > 0:
                between_waves -= 1
            else:
                if not wave_started:
                    start_overlay(f"Wave {wave} starting!", (255, 255, 0), 1.4)
                    wave_started = True

                wave_timer += 1
                if wave_timer >= spawn_interval and enemies_spawned < enemies_per_wave:
                    # kies pad
                    if level_chosen == 1:
                        spawn_point = level_paths[1][0]
                        path_to_use = level_paths[1]
                    else:
                        spawn_info = level_paths[level_chosen][wave % 2]
                        spawn_point = spawn_info["spawn"]
                        path_to_use = spawn_info["path"]

                    # spawn type
                    if enemies_spawned % 2 == 0:
                        enemy = StrongEnemy(path_to_use, *spawn_point)
                        enemy.max_hp += (wave - 1) * 60
                        enemy.hp = enemy.max_hp
                        enemy.damage += (wave - 1) * 6
                        enemy.speed += (wave - 1) * 0.12
                    else:
                        enemy = Enemy(path_to_use, *spawn_point)
                        enemy.max_hp += (wave - 1) * 25
                        enemy.hp = enemy.max_hp
                        enemy.damage += (wave - 1) * 2
                        enemy.speed += (wave - 1) * 0.06

                    enemies.append(enemy)
                    enemies_spawned += 1
                    wave_timer = 0

                # wave klaar?
                if enemies_spawned >= enemies_per_wave and len(enemies) == 0:
                    wave += 1
                    enemies_spawned = 0
                    enemies_per_wave += 2
                    wave_timer = 0
                    wave_started = False
                    between_waves = inter_wave_pause

                    if wave > max_waves:
                        # level complete
                        start_overlay(f"Level {level_chosen} Completed!", (0, 255, 0), 2.0)
                        if level_chosen < 3:
                            levels_unlocked[level_chosen + 1] = True
                        # even overlay laten zien en dan terug menu
                        for _ in range(int(1.2 * FPS)):
                            clock.tick(FPS)
                            screen.fill(BG_COLOR)
                            draw_overlay()
                            pygame.display.flip()
                        return ("MENU", None)

        # -------------- ENEMIES UPDATE (FIX: 1x damage -> remove) --------------
        for e in enemies[:]:
            reached_end = e.move()
            if reached_end:
                base.take_damage(e.damage)
                enemies.remove(e)  # ✅ verdwijnen gegarandeerd
                if base.hp <= 0:
                    game_over = True

        # -------------- TOWERS SHOOT --------------
        for t in towers:
            t.shoot(enemies, bullets)

        # -------------- BULLETS UPDATE --------------
        for b in bullets[:]:
            if b.target not in enemies or b.target.hp <= 0:
                bullets.remove(b)
                continue
            b.move()
            if math.hypot(b.x - b.target.x, b.y - b.target.y) < max(10, int(12 * SCALE)):
                b.target.hp -= b.damage
                bullets.remove(b)
                if b.target.hp <= 0:
                    if b.target in enemies:
                        enemies.remove(b.target)
                    money += b.target.reward_money
                    score += b.target.reward_score

        # -------------- DRAW --------------
        if level_chosen == 1:
            draw_path(screen, level_paths[1], PATH_WIDTH)
        else:
            for spawn_info in level_paths[level_chosen]:
                draw_path(screen, spawn_info["path"], PATH_WIDTH)

        base.draw()

        for e in enemies:
            e.draw()

        # towers draw + hover/selected info + range
        for t in towers:
            t.draw_base()

        # hover info (contextueel) + range ring
        hovered = tower_at_pos(towers, mx, my)
        info_target = hovered if hovered else selected

        if info_target and info_target in towers:
            pygame.draw.circle(screen, (255, 255, 255), (int(info_target.x), int(info_target.y)), int(info_target.range), 1)

            ttype = "SNIPER" if isinstance(info_target, SniperTower) else "TOWER"
            lvl = f"{info_target.level}/{info_target.max_level}"
            val = info_target.total_value
            sell = int(val * SELL_REFUND)

            info_lines = [
                f"{ttype}  Lv {lvl}",
                f"DMG: {info_target.damage} | Rate: {info_target.fire_rate}",
                f"Range: {int(info_target.range)}",
                f"Value: {val}$ | Sell (X): {sell}$"
            ]

            box_w = 0
            renders = []
            for line in info_lines:
                r = SMALL_FONT.render(line, True, (255, 255, 255))
                renders.append(r)
                box_w = max(box_w, r.get_width())

            pad = 10
            box_h = len(renders) * (SMALL_FONT.get_height() + 4) + pad
            box_x = min(WIDTH - (box_w + 2 * pad) - 10, int(info_target.x + 25))
            box_y = max(10, int(info_target.y - box_h - 15))

            pygame.draw.rect(screen, (15, 15, 15), (box_x, box_y, box_w + 2*pad, box_h), border_radius=8)
            pygame.draw.rect(screen, (70, 70, 70), (box_x, box_y, box_w + 2*pad, box_h), 2, border_radius=8)

            y = box_y + 6
            for r in renders:
                screen.blit(r, (box_x + pad, y))
                y += r.get_height() + 4

        # selected marker
        if selected and selected in towers:
            pygame.draw.circle(screen, (255, 255, 255), (int(selected.x), int(selected.y)), max(22, int((26 + selected.level) * SCALE)), 2)

        for b in bullets:
            b.draw()

        draw_hud(money, score, base.hp, wave, max_waves)

        if game_over:
            text = BIG_FONT.render("GAME OVER", True, (255, 0, 0))
            sub = FONT.render("R = Restart | M = Menu | ESC = Quit", True, (255, 200, 200))
            screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - text.get_height()))
            screen.blit(sub, (WIDTH//2 - sub.get_width()//2, HEIGHT//2 + 10))

        draw_overlay()
        pygame.display.flip()

    return ("MENU", None)

# ================== MAIN PROGRAM ==================
levels_unlocked = {1: True, 2: False, 3: False}

while True:
    level = start_screen(levels_unlocked)
    res = run_level(level, levels_unlocked)

    if res is None:
        break
    action, payload = res
    if action == "RESTART":
        # restart selected level
        while True:
            res2 = run_level(payload, levels_unlocked)
            if res2 is None:
                pygame.quit()
                raise SystemExit
            if res2[0] == "RESTART":
                continue
            break
    # MENU -> gewoon terug naar start_screen loop

pygame.quit()
