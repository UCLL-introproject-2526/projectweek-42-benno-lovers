import pygame
import math
import random

pygame.init()

# ------------------ CONSTANTEN ------------------
WIDTH, HEIGHT = 800, 600
FPS = 60
TOWER_COST = 50
SNIPER_TOWER_COST = 120

BG_COLOR = (30, 30, 30)
PATH_COLOR = (100, 100, 100)
ENEMY_COLOR = (200, 50, 50)
STRONG_ENEMY_COLOR = (50, 50, 200)
TOWER_COLOR = (50, 200, 50)
BASE_COLOR = (200, 50, 50)
BULLET_COLOR = (255, 255, 0)

FONT = pygame.font.SysFont(None, 36)
BIG_FONT = pygame.font.SysFont(None, 72)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tower Defence")
clock = pygame.time.Clock()

PATH_WIDTH = 40

# ------------------ LEVEL MAPS ------------------
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

level_base = {
    1: (450, 550),
    2: (450, 550)
}

level_wave_map = {1: 5, 2: 10, 3: 15}

# ------------------ FUNCTIES ------------------
def draw_path(surface, path, width):
    for i in range(len(path) - 1):
        pygame.draw.line(surface, PATH_COLOR, path[i], path[i + 1], width)
        pygame.draw.circle(surface, PATH_COLOR, path[i], width // 2)
    pygame.draw.circle(surface, PATH_COLOR, path[-1], width // 2)

def is_on_path(x, y, current_level, current_path=None):
    if current_level == 1:
        path_to_check = level_paths[1]
    elif current_level == 2 and current_path is not None:
        path_to_check = current_path
    else:
        path_to_check = []
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

def show_wave_text(wave):
    text = BIG_FONT.render(f"Wave {wave} starting!", True, (255, 255, 0))
    screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - text.get_height()//2))
    pygame.display.flip()
    pygame.time.delay(2000)

def show_level_completed(level):
    text = BIG_FONT.render(f"Level {level} Completed!", True, (0, 255, 0))
    screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - text.get_height()//2))
    pygame.display.flip()
    pygame.time.delay(2000)

def start_screen(levels_unlocked):
    selecting = True
    while selecting:
        screen.fill(BG_COLOR)
        title = BIG_FONT.render("Tower Defence", True, (255, 255, 255))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))

        mouse_x, mouse_y = pygame.mouse.get_pos()
        level_texts = []

        for i in range(1, 4):
            unlocked = levels_unlocked.get(i, False)
            color = (255, 255, 0) if unlocked else (100, 100, 100)
            text = FONT.render(f"Level {i}", True, color)
            rect = text.get_rect(center=(WIDTH//2, 150 + i*80))

            if unlocked and rect.collidepoint(mouse_x, mouse_y):
                pygame.draw.rect(screen, (255, 255, 150), rect.inflate(20, 10), border_radius=5)
            screen.blit(text, rect)
            level_texts.append((rect, i, unlocked))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                for rect, level_num, unlocked in level_texts:
                    if unlocked and rect.collidepoint(mx, my):
                        return level_num

# ------------------ CLASSES ------------------
class Enemy:
    def __init__(self, path, x=None, y=None, hp=100, damage=10, speed=2):
        self.path = path
        if x is None or y is None:
            self.x, self.y = path[0]
        else:
            self.x, self.y = x, y
        self.speed = speed
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

class StrongEnemy(Enemy):
    def __init__(self, path, x=None, y=None, hp=300, damage=25, speed=1.5):
        super().__init__(path, x, y, hp, damage, speed)
        self.reward_money = 25
        self.reward_score = 30

    def draw(self):
        pygame.draw.circle(screen, STRONG_ENEMY_COLOR, (int(self.x), int(self.y)), 20)

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
        self.range = 150
        self.cooldown = 0
        self.fire_rate = 30
        self.damage = 25
        self.color = TOWER_COLOR

    def shoot(self, enemies, bullets):
        if self.cooldown > 0:
            self.cooldown -= 1
            return
        for enemy in enemies:
            dist = math.hypot(enemy.x - self.x, enemy.y - self.y)
            if dist < self.range and not enemy.attacking:
                bullets.append(Bullet(self.x, self.y, enemy, self.damage))
                self.cooldown = self.fire_rate
                break

    def draw_base(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), 15)

class SniperTower(Tower):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.range = 350
        self.fire_rate = 90
        self.damage = 100
        self.color = (50, 150, 255)

    def draw_base(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), 22)

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
        ratio = self.hp / self.max_hp
        pygame.draw.rect(screen, (255, 0, 0), (self.x - 25, self.y - 40, 50, 8))
        pygame.draw.rect(screen, (0, 255, 0), (self.x - 25, self.y - 40, 50 * ratio, 8))

# ------------------ LEVEL PROGRESS ------------------
levels_unlocked = {1: True, 2: False, 3: False}
level_chosen = start_screen(levels_unlocked)
max_waves = level_wave_map.get(level_chosen, 5)

# ------------------ GAME OBJECTS ------------------
enemies = []
towers = []
bullets = []
base = Base(*level_base[level_chosen])
money = 100
score = 0
running = True
game_over = False

# ------------------ WAVES ------------------
wave = 1
wave_timer = 0
enemies_spawned_in_wave = 0
enemies_per_wave = 5
wave_cooldown = 120
wave_started = False

# ------------------ GAME LOOP ------------------
while running:
    clock.tick(FPS)
    screen.fill(BG_COLOR)
    mouse_x, mouse_y = pygame.mouse.get_pos()

    # ------------------ EVENT HANDLING ------------------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
            x, y = pygame.mouse.get_pos()
            if level_chosen == 1:
                if not is_on_path(x, y, 1):
                    if event.button == 1 and money >= TOWER_COST:
                        towers.append(Tower(x, y))
                        money -= TOWER_COST
                    if event.button == 3 and money >= SNIPER_TOWER_COST:
                        towers.append(SniperTower(x, y))
                        money -= SNIPER_TOWER_COST
            elif level_chosen == 2:
                for spawn_info in level_paths[2]:
                    if not is_on_path(x, y, 2, spawn_info['path']):
                        if event.button == 1 and money >= TOWER_COST:
                            towers.append(Tower(x, y))
                            money -= TOWER_COST
                        if event.button == 3 and money >= SNIPER_TOWER_COST:
                            towers.append(SniperTower(x, y))
                            money -= SNIPER_TOWER_COST
                        break

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

    # ------------------ ENEMY SPAWN ------------------
    if not game_over and wave <= max_waves:
        if not wave_started:
            show_wave_text(wave)
            wave_started = True

        wave_timer += 1
        if wave_timer > wave_cooldown and enemies_spawned_in_wave < enemies_per_wave:
            if level_chosen == 1:
                spawn_point = level_paths[1][0]
                path_to_use = level_paths[1]
            elif level_chosen == 2:
                spawn_info = level_paths[2][wave % 2]
                spawn_point = spawn_info['spawn']
                path_to_use = spawn_info['path']

            if enemies_spawned_in_wave % 2 == 0:
                enemy = StrongEnemy(path_to_use, *spawn_point)
                enemy.hp += (wave - 1) * 50
                enemy.damage += (wave - 1) * 5
                enemy.speed += (wave - 1) * 0.1
            else:
                enemy = Enemy(path_to_use, *spawn_point)
                enemy.hp += (wave - 1) * 20
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

                # Reset game objecten en terug naar startscherm
                enemies.clear()
                towers.clear()
                bullets.clear()
                base = Base(*level_base[level_chosen])
                score = 0
                money = 100
                wave = 1
                enemies_spawned_in_wave = 0
                enemies_per_wave = 5
                wave_timer = 0
                wave_started = False

                level_chosen = start_screen(levels_unlocked)
                max_waves = level_wave_map.get(level_chosen, 5)
                base = Base(*level_base[level_chosen])

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
                enemies.remove(bullet.target)
                money += bullet.target.reward_money
                score += bullet.target.reward_score

    # ------------------ TEKENING ------------------
    if level_chosen == 1:
        draw_path(screen, level_paths[1], PATH_WIDTH)
    elif level_chosen == 2:
        for spawn_info in level_paths[2]:
            draw_path(screen, spawn_info['path'], PATH_WIDTH)

    base.draw()
    for enemy in enemies:
        enemy.draw()

    for tower in towers:
        tower.draw_base()
        if math.hypot(mouse_x - tower.x, mouse_y - tower.y) <= 25:
            pygame.draw.circle(screen, (*tower.color, 50), (tower.x, tower.y), tower.range, 1)

    for bullet in bullets:
        bullet.draw()

    # ------------------ UI ------------------
    screen.blit(FONT.render(f"Score: {score}", True, (255, 255, 255)), (10, 10))
    screen.blit(FONT.render(f"Base HP: {base.hp}", True, (255, 255, 255)), (10, 40))
    screen.blit(FONT.render(f"Money: {money}", True, (255, 255, 255)), (10, 70))
    if wave <= max_waves:
        screen.blit(FONT.render(f"Wave: {wave}/{max_waves}", True, (255, 255, 255)), (10, 100))
    else:
        screen.blit(FONT.render("Level Completed!", True, (0, 255, 0)), (10, 100))

    if game_over:
        text = FONT.render("GAME OVER - Press R to Restart", True, (255, 0, 0))
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2))

    pygame.display.flip()

pygame.quit()
