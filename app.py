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
        {'spawn': (-50, 500), 'path': [(-50, 500), (100, 500), (100, 200), (400, 200),
                                       (400, 400), (700, 400), (700, 100), (600, 100), (600, 550)]},
        {'spawn': (850, 300), 'path': [(850, 300), (600, 300), (600, 150), (400, 150),
                                       (400, 450), (200, 450), (200, 550), (450, 550)]}
    ]
}

level_base = {1: (450, 550), 2: (450, 550)}
level_wave_map = {1: 5, 2: 10, 3: 15}

# ------------------ OVERLAY ANIMATIE ------------------
overlay = None

def start_overlay(text, color=(255, 255, 0), duration=2):
    global overlay
    overlay = {
        "text": text,
        "color": color,
        "frames": int(duration * FPS)
    }

def draw_overlay():
    global overlay
    if not overlay:
        return

    fade_time = int(0.5 * FPS)
    alpha = 255
    if overlay["frames"] < fade_time:
        alpha = int(255 * overlay["frames"] / fade_time)

    surf = BIG_FONT.render(overlay["text"], True, overlay["color"]).convert_alpha()
    surf.set_alpha(alpha)
    screen.blit(surf, (WIDTH//2 - surf.get_width()//2,
                       HEIGHT//2 - surf.get_height()//2))

    overlay["frames"] -= 1
    if overlay["frames"] <= 0:
        overlay = None

# ------------------ FUNCTIES ------------------
def draw_path(surface, path, width):
    for i in range(len(path) - 1):
        pygame.draw.line(surface, PATH_COLOR, path[i], path[i + 1], width)
        pygame.draw.circle(surface, PATH_COLOR, path[i], width // 2)
    pygame.draw.circle(surface, PATH_COLOR, path[-1], width // 2)

def is_on_path(x, y, path):
    for i in range(len(path) - 1):
        x1, y1 = path[i]
        x2, y2 = path[i + 1]
        px, py = x2 - x1, y2 - y1
        norm = px*px + py*py
        u = ((x-x1)*px + (y-y1)*py) / norm if norm else 0
        u = max(0, min(1, u))
        dx, dy = x1 + u*px - x, y1 + u*py - y
        if math.hypot(dx, dy) <= PATH_WIDTH//2 + 5:
            return True
    return False

def start_screen(levels_unlocked):
    while True:
        screen.fill(BG_COLOR)
        title = BIG_FONT.render("Tower Defence", True, (255,255,255))
        screen.blit(title, (WIDTH//2-title.get_width()//2, 50))

        mouse = pygame.mouse.get_pos()
        buttons = []

        for i in range(1,4):
            unlocked = levels_unlocked.get(i, False)
            color = (255,255,0) if unlocked else (100,100,100)
            txt = FONT.render(f"Level {i}", True, color)
            rect = txt.get_rect(center=(WIDTH//2, 150+i*80))
            if unlocked and rect.collidepoint(mouse):
                pygame.draw.rect(screen, (255,255,150), rect.inflate(20,10), border_radius=5)
            screen.blit(txt, rect)
            buttons.append((rect,i,unlocked))

        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); exit()
            if e.type == pygame.MOUSEBUTTONDOWN:
                for rect, lvl, ok in buttons:
                    if ok and rect.collidepoint(e.pos):
                        return lvl

# ------------------ CLASSES ------------------
class Enemy:
    def __init__(self, path, x, y, hp=100, dmg=10, speed=2):
        self.path = path
        self.x, self.y = x, y
        self.hp, self.damage, self.speed = hp, dmg, speed
        self.index = 1
        self.attacking = False
        self.timer = 60
        self.reward_money = 10
        self.reward_score = 10

    def move(self):
        if self.attacking: return
        if self.index >= len(self.path):
            self.attacking = True
            return
        tx, ty = self.path[self.index]
        dx, dy = tx-self.x, ty-self.y
        d = math.hypot(dx, dy)
        if d < self.speed:
            self.index += 1
        else:
            self.x += self.speed*dx/d
            self.y += self.speed*dy/d

    def attack(self, base):
        self.timer -= 1
        if self.timer <= 0:
            base.hp -= self.damage
            self.timer = 60

    def draw(self):
        pygame.draw.circle(screen, ENEMY_COLOR, (int(self.x), int(self.y)), 15)

class StrongEnemy(Enemy):
    def __init__(self, path, x, y):
        super().__init__(path, x, y, 300, 25, 1.5)
        self.reward_money = 25
        self.reward_score = 30

    def draw(self):
        pygame.draw.circle(screen, STRONG_ENEMY_COLOR, (int(self.x), int(self.y)), 20)

class Bullet:
    def __init__(self, x, y, target, dmg):
        self.x, self.y, self.target, self.dmg = x, y, target, dmg
        self.speed = 5

    def move(self):
        dx, dy = self.target.x-self.x, self.target.y-self.y
        d = math.hypot(dx, dy)
        if d:
            self.x += self.speed*dx/d
            self.y += self.speed*dy/d

    def draw(self):
        pygame.draw.circle(screen, BULLET_COLOR, (int(self.x), int(self.y)), 5)

class Tower:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.range, self.cool, self.rate, self.dmg = 150, 0, 30, 25
        self.color = TOWER_COLOR

    def shoot(self, enemies, bullets):
        if self.cool: self.cool -= 1; return
        for e in enemies:
            if math.hypot(e.x-self.x, e.y-self.y) < self.range and not e.attacking:
                bullets.append(Bullet(self.x, self.y, e, self.dmg))
                self.cool = self.rate
                break

    def draw(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), 15)

class SniperTower(Tower):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.range, self.rate, self.dmg = 350, 90, 100
        self.color = (50,150,255)

    def draw(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), 22)

class Base:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.max_hp = 200
        self.hp = self.max_hp

    def draw(self):
        pygame.draw.rect(screen, BASE_COLOR, (self.x-25, self.y-25, 50, 50))
        pygame.draw.rect(screen, (255,0,0), (self.x-25, self.y-40, 50, 8))
        pygame.draw.rect(screen, (0,255,0), (self.x-25, self.y-40, 50*self.hp/self.max_hp, 8))

# ------------------ START ------------------
levels_unlocked = {1: True, 2: False, 3: False}
level = start_screen(levels_unlocked)

while True:
    max_waves = level_wave_map[level]
    enemies, towers, bullets = [], [], []
    base = Base(*level_base[level])
    money, score = 100, 0
    wave, spawned, per_wave = 1, 0, 5
    timer, started, game_over = 0, False, False

    while True:
        clock.tick(FPS)
        screen.fill(BG_COLOR)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); exit()
            if e.type == pygame.MOUSEBUTTONDOWN and not game_over:
                x,y = e.pos
                paths = [level_paths[level]] if level == 1 else [p['path'] for p in level_paths[2]]
                if not any(is_on_path(x,y,p) for p in paths):
                    if e.button == 1 and money >= 50:
                        towers.append(Tower(x,y)); money -= 50
                    if e.button == 3 and money >= 120:
                        towers.append(SniperTower(x,y)); money -= 120

        if not started:
            start_overlay(f"Wave {wave} starting!")
            started = True

        timer += 1
        if timer > 120 and spawned < per_wave:
            if level == 1:
                path = level_paths[1]; spawn = path[0]
            else:
                info = level_paths[2][wave % 2]
                path, spawn = info['path'], info['spawn']
            enemy = StrongEnemy(path,*spawn) if spawned%2==0 else Enemy(path,*spawn)
            enemies.append(enemy)
            spawned += 1; timer = 0

        for enemy in enemies[:]:
            enemy.move()
            if enemy.attacking:
                enemy.attack(base)
                if base.hp <= 0: game_over = True

        for t in towers:
            t.shoot(enemies, bullets)

        for b in bullets[:]:
            if b.target not in enemies:
                bullets.remove(b); continue
            b.move()
            if math.hypot(b.x-b.target.x, b.y-b.target.y) < 10:
                b.target.hp -= b.dmg
                bullets.remove(b)
                if b.target.hp <= 0:
                    enemies.remove(b.target)
                    money += b.target.reward_money
                    score += b.target.reward_score

        if spawned >= per_wave and not enemies:
            wave += 1; spawned = 0; per_wave += 2; started = False
            if wave > max_waves:
                levels_unlocked[level+1] = True
                start_overlay(f"Level {level} Completed!", (0,255,0), 3)
                pygame.time.wait(2000)
                level = start_screen(levels_unlocked)
                break

        if level == 1:
            draw_path(screen, level_paths[1], PATH_WIDTH)
        else:
            for p in level_paths[2]:
                draw_path(screen, p['path'], PATH_WIDTH)

        base.draw()
        for e in enemies: e.draw()
        for t in towers: t.draw()
        for b in bullets: b.draw()

        screen.blit(FONT.render(f"Money: {money}", True, (255,255,255)), (10,10))
        screen.blit(FONT.render(f"Base HP: {base.hp}", True, (255,255,255)), (10,40))
        screen.blit(FONT.render(f"Wave {wave}/{max_waves}", True, (255,255,255)), (10,70))

        draw_overlay()
        pygame.display.flip()
