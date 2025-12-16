import pygame
import math
import random

pygame.init()

# ================== CONSTANTEN ==================
WIDTH, HEIGHT = 800, 600
FPS = 60

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

FONT = pygame.font.SysFont(None, 28)
BIG_FONT = pygame.font.SysFont(None, 72)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tower Defence")
clock = pygame.time.Clock()

PATH_WIDTH = 40

# ================== LEVEL MAPS ==================
level_paths = {
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

level_base = {1: (450, 550), 2: (450, 550)}
level_wave_map = {1: 5, 2: 10, 3: 15}

# ================== OVERLAY (NIET-BLOKKEREND) ==================
overlay = None

def start_overlay(text, color=(255, 255, 0), duration_sec=2):
    global overlay
    overlay = {"text": text, "color": color, "frames_left": int(duration_sec * FPS)}

def draw_overlay():
    global overlay
    if not overlay:
        return
    fade_frames = int(0.5 * FPS)
    alpha = 255 if overlay["frames_left"] > fade_frames else max(0, int(255 * (overlay["frames_left"] / fade_frames)))
    surf = BIG_FONT.render(overlay["text"], True, overlay["color"]).convert_alpha()
    surf.set_alpha(alpha)
    screen.blit(surf, (WIDTH//2 - surf.get_width()//2, HEIGHT//2 - surf.get_height()//2))
    overlay["frames_left"] -= 1
    if overlay["frames_left"] <= 0:
        overlay = None

# ================== FUNCTIES ==================
def draw_path(surface, path, width):
    for i in range(len(path) - 1):
        pygame.draw.line(surface, PATH_COLOR, path[i], path[i + 1], width)
        pygame.draw.circle(surface, PATH_COLOR, path[i], width // 2)
    pygame.draw.circle(surface, PATH_COLOR, path[-1], width // 2)

def is_on_path(x, y, path_to_check):
    for i in range(len(path_to_check) - 1):
        x1, y1 = path_to_check[i]
        x2, y2 = path_to_check[i + 1]
        px = x2 - x1
        py = y2 - y1
        norm = px*px + py*py
        u = ((x - x1) * px + (y - y1) * py) / float(norm) if norm != 0 else 0
        u = max(0, min(1, u))
        dx = x1 + u * px - x
        dy = y1 + u * py - y
        dist = math.hypot(dx, dy)
        if dist <= PATH_WIDTH // 2 + 5:
            return True
    return False

def is_on_any_path_level2(x, y):
    for spawn_info in level_paths[2]:
        if is_on_path(x, y, spawn_info["path"]):
            return True
    return False

def draw_hp_bar_centered(cx, cy, hp, max_hp, w=34, h=6, y_offset=-28):
    ratio = 0 if max_hp <= 0 else max(0, min(1, hp / max_hp))
    x = cx - w // 2
    y = cy + y_offset
    pygame.draw.rect(screen, (255, 0, 0), (x, y, w, h))
    pygame.draw.rect(screen, (0, 255, 0), (x, y, int(w * ratio), h))

def show_level_completed(level):
    start_overlay(f"Level {level} Completed!", (0, 255, 0), 2)

def instructions_screen():
    viewing = True
    while viewing:
        screen.fill(BG_COLOR)
        title = BIG_FONT.render("Instructies", True, (255, 255, 255))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))

        lines = [
            "Plaats Tower: Linkermuisknop",
            "Plaats Sniper: S + Linkermuisknop",
            "",
            "Upgrade (merge):",
            "Sleep 2 towers van hetzelfde type + level op elkaar",
            f"Max level: {MAX_TOWER_LEVEL}",
            "",
            f"Sell: hover tower + druk X (refund {int(SELL_REFUND*100)}%)",
            "",
            "ESC: terug"
        ]
        for i, line in enumerate(lines):
            txt = FONT.render(line, True, (200, 200, 200))
            screen.blit(txt, (WIDTH//2 - txt.get_width()//2, 170 + i * 28))

        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                viewing = False

def start_screen(levels_unlocked):
    selecting = True
    while selecting:
        screen.fill(BG_COLOR)
        title = BIG_FONT.render("Tower Defence", True, (255, 255, 255))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))

        mouse_x, mouse_y = pygame.mouse.get_pos()
        buttons = []

        entries = ["Level 1", "Level 2", "Level 3", "Instructies"]
        for i, name in enumerate(entries):
            unlocked = (name == "Instructies") or levels_unlocked.get(i+1, False)
            color = (255, 255, 0) if unlocked else (120, 120, 120)
            text = FONT.render(name, True, color)
            rect = text.get_rect(center=(WIDTH//2, 170 + i*75))

            if unlocked and rect.collidepoint(mouse_x, mouse_y):
                pygame.draw.rect(screen, (255, 255, 150), rect.inflate(20, 10), border_radius=6)

            screen.blit(text, rect)
            buttons.append((rect, name, unlocked))

        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                exit()
            if e.type == pygame.MOUSEBUTTONDOWN:
                mx, my = e.pos
                for rect, name, unlocked in buttons:
                    if unlocked and rect.collidepoint(mx, my):
                        if name == "Instructies":
                            instructions_screen()
                        else:
                            return int(name.split()[1])

# ================== CLASSES ==================
class Enemy:
    def __init__(self, path, x=None, y=None, hp=100, damage=10, speed=2):
        self.path = path
        if x is None or y is None:
            self.x, self.y = path[0]
        else:
            self.x, self.y = x, y
        self.speed = speed
        self.max_hp = hp
        self.hp = hp
        self.damage = damage
        self.attack_timer = 60
        self.target_index = 1
        self.attacking = False
        self.reward_money = 10
        self.reward_score = 10

    def move(self):
        if self.attacking:
            return False
        if self.target_index >= len(self.path):
            self.attacking = True
            return True
        tx, ty = self.path[self.target_index]
        dx = tx - self.x
        dy = ty - self.y
        dist = math.hypot(dx, dy)
        if dist < self.speed:
            self.target_index += 1
        else:
            self.x += self.speed * dx / dist
            self.y += self.speed * dy / dist
        return False

    def attack(self, base):
        self.attack_timer -= 1
        if self.attack_timer <= 0:
            base.take_damage(self.damage)
            self.attack_timer = 60
            return True
        return False

    def draw(self):
        pygame.draw.circle(screen, ENEMY_COLOR, (int(self.x), int(self.y)), 15)
        draw_hp_bar_centered(self.x, self.y, self.hp, self.max_hp, w=34)

class StrongEnemy(Enemy):
    def __init__(self, path, x=None, y=None, hp=300, damage=25, speed=1.5):
        super().__init__(path, x, y, hp, damage, speed)
        self.reward_money = 25
        self.reward_score = 30

    def draw(self):
        pygame.draw.circle(screen, STRONG_ENEMY_COLOR, (int(self.x), int(self.y)), 20)
        draw_hp_bar_centered(self.x, self.y, self.hp, self.max_hp, w=40)

class Bullet:
    def __init__(self, x, y, target, damage):
        self.x = x
        self.y = y
        self.target = target
        self.speed = 5
        self.damage = damage

    def move(self):
        dx = self.target.x - self.x
        dy = self.target.y - self.y
        dist = math.hypot(dx, dy)
        if dist != 0:
            self.x += self.speed * dx / dist
            self.y += self.speed * dy / dist

    def draw(self):
        pygame.draw.circle(screen, BULLET_COLOR, (int(self.x), int(self.y)), 5)

class Tower:
    def __init__(self, x, y):
        self.x = x
        self.y = y

        self.level = 1
        self.max_level = MAX_TOWER_LEVEL

        self.range = 150
        self.cooldown = 0
        self.fire_rate = 30
        self.damage = 25
        self.color = TOWER_COLOR

        self.base_cost = TOWER_COST
        self.total_value = self.base_cost

        self.dragging = False  # IMPORTANT: exploit fix

    def shoot(self, enemies, bullets):
        # EXPLOIT FIX: tijdens drag/merge niet schieten
        if self.dragging:
            return
        if self.cooldown > 0:
            self.cooldown -= 1
            return
        for enemy in enemies:
            dist = math.hypot(enemy.x - self.x, enemy.y - self.y)
            if dist < self.range and not enemy.attacking:
                bullets.append(Bullet(self.x, self.y, enemy, self.damage))
                self.cooldown = self.fire_rate
                break

    def can_upgrade(self):
        return self.level < self.max_level

    def upgrade_one_level(self):
        if not self.can_upgrade():
            return False
        self.level += 1
        self.damage += 15
        self.range += 20
        self.fire_rate = max(8, self.fire_rate - 3)
        self.total_value += self.base_cost
        return True

    def draw_base(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), 15 + self.level)

class SniperTower(Tower):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.range = 350
        self.fire_rate = 90
        self.damage = 100
        self.color = SNIPER_COLOR

        self.base_cost = SNIPER_TOWER_COST
        self.total_value = self.base_cost

    def upgrade_one_level(self):
        if not self.can_upgrade():
            return False
        self.level += 1
        self.damage += 35
        self.range += 35
        self.fire_rate = max(25, self.fire_rate - 8)
        self.total_value += self.base_cost
        return True

    def draw_base(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), 22 + self.level)

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
        pygame.draw.rect(screen, BASE_COLOR, (self.x - 25, self.y - 25, 50, 50))
        ratio = self.hp / self.max_hp if self.max_hp else 0
        pygame.draw.rect(screen, (255, 0, 0), (self.x - 25, self.y - 40, 50, 8))
        pygame.draw.rect(screen, (0, 255, 0), (self.x - 25, self.y - 40, 50 * ratio, 8))

# ================== GAME SETUP ==================
levels_unlocked = {1: True, 2: False, 3: False}
level_chosen = start_screen(levels_unlocked)
max_waves = level_wave_map.get(level_chosen, 5)

enemies = []
towers = []
bullets = []
base = Base(*level_base.get(level_chosen, (450, 550)))

money = 100
score = 0
game_over = False

# WAVES
wave = 1
wave_timer = 0
enemies_spawned_in_wave = 0
enemies_per_wave = 5
wave_cooldown = 120
wave_started = False

# merge/select state
selected_tower = None
mouse_down_tower = None
dragged_tower = None
drag_origin = None
mouse_down_pos = None
drag_started = False
DRAG_THRESHOLD = 6

def tower_at_pos(mx, my):
    for t in reversed(towers):
        radius = 26 + t.level
        if math.hypot(mx - t.x, my - t.y) <= radius:
            return t
    return None

def same_tower_type(a, b):
    return type(a) is type(b)

def draw_hud():
    # CLEAN HUD: alleen stats + kosten
    screen.blit(FONT.render(f"Score: {score}", True, (255, 255, 255)), (10, 10))
    screen.blit(FONT.render(f"Base HP: {base.hp}", True, (255, 255, 255)), (10, 40))
    screen.blit(FONT.render(f"Money: {money}", True, (255, 255, 255)), (10, 70))
    if wave <= max_waves:
        screen.blit(FONT.render(f"Wave: {wave}/{max_waves}", True, (255, 255, 255)), (10, 100))
    else:
        screen.blit(FONT.render("Level Completed!", True, (0, 255, 0)), (10, 100))

    # costs rechtsboven
    screen.blit(FONT.render(f"Tower: {TOWER_COST}$", True, (200, 200, 200)), (WIDTH - 170, 10))
    screen.blit(FONT.render(f"Sniper: {SNIPER_TOWER_COST}$", True, (200, 200, 200)), (WIDTH - 170, 40))

# ================== MAIN LOOP ==================
running = True
while running:
    clock.tick(FPS)
    screen.fill(BG_COLOR)
    mouse_x, mouse_y = pygame.mouse.get_pos()
    keys = pygame.key.get_pressed()

    # ------------------ EVENTS ------------------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Sell selected (X) — contextueel: je moet hoveren/selection hebben
        if event.type == pygame.KEYDOWN and not game_over:
            if event.key == pygame.K_x and selected_tower and selected_tower in towers:
                refund = int(selected_tower.total_value * SELL_REFUND)
                money += refund
                towers.remove(selected_tower)
                selected_tower = None

        if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
            mx, my = event.pos

            if event.button == 1:
                t = tower_at_pos(mx, my)
                mouse_down_pos = (mx, my)
                drag_started = False
                mouse_down_tower = t

                if t:
                    selected_tower = t
                else:
                    blocked = is_on_path(mx, my, level_paths[1]) if level_chosen == 1 else is_on_any_path_level2(mx, my)
                    if not blocked:
                        if keys[pygame.K_s] and money >= SNIPER_TOWER_COST:
                            towers.append(SniperTower(mx, my))
                            money -= SNIPER_TOWER_COST
                        elif money >= TOWER_COST:
                            towers.append(Tower(mx, my))
                            money -= TOWER_COST

        if event.type == pygame.MOUSEMOTION and not game_over:
            if mouse_down_tower and mouse_down_pos:
                mx, my = event.pos
                if not drag_started and math.hypot(mx - mouse_down_pos[0], my - mouse_down_pos[1]) >= DRAG_THRESHOLD:
                    drag_started = True
                    dragged_tower = mouse_down_tower
                    drag_origin = (dragged_tower.x, dragged_tower.y)
                    dragged_tower.dragging = True  # <<<< exploit fix active

        if event.type == pygame.MOUSEBUTTONUP and not game_over:
            if event.button == 1:
                if dragged_tower:
                    merged = False
                    for t in towers:
                        if t is dragged_tower:
                            continue
                        if same_tower_type(t, dragged_tower) and t.level == dragged_tower.level and t.can_upgrade():
                            if math.hypot(t.x - dragged_tower.x, t.y - dragged_tower.y) <= 28:
                                t.upgrade_one_level()
                                towers.remove(dragged_tower)
                                merged = True
                                break

                    if not merged and drag_origin:
                        dragged_tower.x, dragged_tower.y = drag_origin

                    # einde drag: weer mogen schieten (als tower nog bestaat)
                    if dragged_tower in towers:
                        dragged_tower.dragging = False

                    dragged_tower = None
                    drag_origin = None

                mouse_down_tower = None
                mouse_down_pos = None
                drag_started = False

        # Restart
        if game_over and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                enemies.clear()
                towers.clear()
                bullets.clear()
                base.hp = base.max_hp
                score = 0
                money = 100
                wave = 1
                enemies_spawned_in_wave = 0
                enemies_per_wave = 5
                wave_started = False
                game_over = False
                selected_tower = None
                mouse_down_tower = None
                dragged_tower = None
                drag_origin = None
                mouse_down_pos = None
                drag_started = False

    # follow mouse during drag (temporary visual)
    if dragged_tower and not game_over:
        dragged_tower.x, dragged_tower.y = mouse_x, mouse_y

    # ------------------ SPAWN / WAVES ------------------
    if not game_over and wave <= max_waves:
        if not wave_started:
            start_overlay(f"Wave {wave} starting!", (255, 255, 0), 2)
            wave_started = True

        wave_timer += 1
        if wave_timer > wave_cooldown and enemies_spawned_in_wave < enemies_per_wave:
            if level_chosen == 1:
                spawn_point = level_paths[1][0]
                path_to_use = level_paths[1]
            else:
                spawn_info = level_paths[2][wave % 2]
                spawn_point = spawn_info['spawn']
                path_to_use = spawn_info['path']

            if enemies_spawned_in_wave % 2 == 0:
                enemy = StrongEnemy(path_to_use, *spawn_point)
                enemy.max_hp += (wave - 1) * 50
                enemy.hp = enemy.max_hp
                enemy.damage += (wave - 1) * 5
                enemy.speed += (wave - 1) * 0.1
            else:
                enemy = Enemy(path_to_use, *spawn_point)
                enemy.max_hp += (wave - 1) * 20
                enemy.hp = enemy.max_hp
                enemy.damage += (wave - 1) * 2
                enemy.speed += (wave - 1) * 0.05

            enemies.append(enemy)
            enemies_spawned_in_wave += 1
            wave_timer = 0

        if enemies_spawned_in_wave >= enemies_per_wave and len(enemies) == 0:
            wave += 1
            enemies_spawned_in_wave = 0
            enemies_per_wave += 2
            wave_timer = -60
            wave_started = False

            if wave > max_waves:
                if level_chosen < 3:
                    levels_unlocked[level_chosen + 1] = True
                show_level_completed(level_chosen)

                # reset + terug naar start screen (zoals eerder)
                enemies.clear()
                towers.clear()
                bullets.clear()
                base = Base(*level_base.get(level_chosen, (450, 550)))
                score = 0
                money = 100
                wave = 1
                enemies_spawned_in_wave = 0
                enemies_per_wave = 5
                wave_timer = 0
                wave_started = False

                selected_tower = None
                mouse_down_tower = None
                dragged_tower = None
                drag_origin = None
                mouse_down_pos = None
                drag_started = False

                level_chosen = start_screen(levels_unlocked)
                max_waves = level_wave_map.get(level_chosen, 5)
                base = Base(*level_base.get(level_chosen, (450, 550)))

    # ------------------ ENEMY UPDATE ------------------
    for enemy in enemies[:]:
        enemy.move()
        if enemy.attacking and enemy.attack(base):
            if base.hp <= 0:
                game_over = True

    # ------------------ TOWER SHOOT ------------------
    for tower in towers:
        tower.shoot(enemies, bullets)

    # ------------------ BULLETS ------------------
    for bullet in bullets[:]:
        if bullet.target not in enemies or bullet.target.hp <= 0:
            bullets.remove(bullet)
            continue
        bullet.move()
        if math.hypot(bullet.x - bullet.target.x, bullet.y - bullet.target.y) < 10:
            bullet.target.hp -= bullet.damage
            bullets.remove(bullet)
            if bullet.target.hp <= 0:
                if bullet.target in enemies:
                    enemies.remove(bullet.target)
                money += bullet.target.reward_money
                score += bullet.target.reward_score

    # ------------------ DRAW ------------------
    if level_chosen == 1:
        draw_path(screen, level_paths[1], PATH_WIDTH)
    else:
        for spawn_info in level_paths[2]:
            draw_path(screen, spawn_info['path'], PATH_WIDTH)

    base.draw()

    for enemy in enemies:
        enemy.draw()

    # Towers + contextueel info (hover)
    for tower in towers:
        tower.draw_base()

        if selected_tower is tower:
            pygame.draw.circle(screen, (255, 255, 255), (tower.x, tower.y), 26 + tower.level, 2)

        if math.hypot(mouse_x - tower.x, mouse_y - tower.y) <= 30 + tower.level:
            pygame.draw.circle(screen, (255, 255, 255), (tower.x, tower.y), tower.range, 1)

            ttype = "SNIPER" if isinstance(tower, SniperTower) else "TOWER"
            lvl = f"{tower.level}/{tower.max_level}"
            val = tower.total_value
            sell = int(val * SELL_REFUND)

            info1 = FONT.render(f"{ttype} Lv {lvl}", True, (255, 255, 255))
            info2 = FONT.render(f"Value: {val}$ | Sell(X): {sell}$", True, (255, 255, 255))
            screen.blit(info1, (tower.x - info1.get_width()//2, tower.y - 62))
            screen.blit(info2, (tower.x - info2.get_width()//2, tower.y - 38))

    for bullet in bullets:
        bullet.draw()

    draw_hud()

    if game_over:
        text = FONT.render("GAME OVER - Press R to Restart", True, (255, 0, 0))
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2))

    draw_overlay()
    pygame.display.flip()

pygame.quit()
