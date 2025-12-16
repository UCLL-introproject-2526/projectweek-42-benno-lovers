import pygame
import math

pygame.init()

# ================== CONSTANTEN ==================
WIDTH, HEIGHT = 800, 600
FPS = 60

TOWER_COST = 50
SNIPER_TOWER_COST = 120
SELL_REFUND = 0.75
MAX_LEVEL = 6

BG_COLOR = (30, 30, 30)
PATH_COLOR = (100, 100, 100)
ENEMY_COLOR = (200, 50, 50)
TOWER_COLOR = (50, 200, 50)
SNIPER_COLOR = (50, 150, 255)
BASE_COLOR = (200, 50, 50)
BULLET_COLOR = (255, 255, 0)

FONT = pygame.font.SysFont(None, 24)
BIG_FONT = pygame.font.SysFont(None, 52)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tower Defence – Merge Edition")
clock = pygame.time.Clock()

PATH_WIDTH = 40

# ================== LEVEL ==================
path = [(-50, 550), (50, 550), (50, 200), (200, 150),
        (300, 300), (600, 300), (600, 100), (450, 100), (450, 550)]
base_pos = (450, 550)

# ================== HULPFUNCTIES ==================
def draw_path():
    for i in range(len(path)-1):
        pygame.draw.line(screen, PATH_COLOR, path[i], path[i+1], PATH_WIDTH)
        pygame.draw.circle(screen, PATH_COLOR, path[i], PATH_WIDTH//2)
    pygame.draw.circle(screen, PATH_COLOR, path[-1], PATH_WIDTH//2)

def is_on_path(x, y):
    for i in range(len(path)-1):
        x1,y1 = path[i]
        x2,y2 = path[i+1]
        px,py = x2-x1, y2-y1
        norm = px*px+py*py
        u = ((x-x1)*px+(y-y1)*py)/norm if norm else 0
        u = max(0,min(1,u))
        dx,dy = x1+u*px-x, y1+u*py-y
        if math.hypot(dx,dy) <= PATH_WIDTH//2+5:
            return True
    return False

# ================== CLASSES ==================
class Enemy:
    def __init__(self):
        self.x, self.y = path[0]
        self.speed = 2
        self.hp = 100
        self.index = 1

    def move(self):
        if self.index >= len(path):
            return
        tx,ty = path[self.index]
        dx,dy = tx-self.x, ty-self.y
        d = math.hypot(dx,dy)
        if d < self.speed:
            self.index += 1
        else:
            self.x += self.speed*dx/d
            self.y += self.speed*dy/d

    def draw(self):
        pygame.draw.circle(screen, ENEMY_COLOR, (int(self.x),int(self.y)), 14)

class Bullet:
    def __init__(self, x, y, target, dmg):
        self.x,self.y = x,y
        self.target = target
        self.dmg = dmg
        self.speed = 5

    def move(self):
        dx,dy = self.target.x-self.x, self.target.y-self.y
        d = math.hypot(dx,dy)
        if d:
            self.x += self.speed*dx/d
            self.y += self.speed*dy/d

    def draw(self):
        pygame.draw.circle(screen, BULLET_COLOR, (int(self.x),int(self.y)), 4)

class Tower:
    def __init__(self,x,y):
        self.x,self.y = x,y
        self.level = 1
        self.range = 150
        self.fire_rate = 30
        self.damage = 25
        self.cooldown = 0
        self.type = "normal"
        self.color = TOWER_COLOR
        self.base_cost = TOWER_COST
        self.total_value = self.base_cost
        self.dragging = False

    def shoot(self,enemies,bullets):
        if self.cooldown > 0:
            self.cooldown -= 1
            return
        for e in enemies:
            if math.hypot(e.x-self.x,e.y-self.y)<=self.range:
                bullets.append(Bullet(self.x,self.y,e,self.damage))
                self.cooldown = self.fire_rate
                break

    def upgrade(self):
        if self.level >= MAX_LEVEL:
            return
        self.level += 1
        self.damage += 15
        self.range += 20
        self.fire_rate = max(8,self.fire_rate-3)
        self.total_value += self.base_cost

    def draw(self):
        pygame.draw.circle(screen,self.color,(self.x,self.y),14+self.level)
        if self.dragging:
            pygame.draw.circle(screen,(255,255,255),(self.x,self.y),24,2)

class SniperTower(Tower):
    def __init__(self,x,y):
        super().__init__(x,y)
        self.range = 360
        self.fire_rate = 90
        self.damage = 100
        self.type = "sniper"
        self.color = SNIPER_COLOR
        self.base_cost = SNIPER_TOWER_COST
        self.total_value = self.base_cost

    def upgrade(self):
        if self.level >= MAX_LEVEL:
            return
        self.level += 1
        self.damage += 35
        self.range += 35
        self.fire_rate = max(25,self.fire_rate-8)
        self.total_value += self.base_cost

class Base:
    def __init__(self,x,y):
        self.x,self.y = x,y
        self.hp = 200

    def draw(self):
        pygame.draw.rect(screen, BASE_COLOR, (self.x-25,self.y-25,50,50))

# ================== GAME ==================
enemies=[]
towers=[]
bullets=[]
base = Base(*base_pos)

money = 250
dragged = None
drag_origin = None
selected = None

spawn_timer = 0

# ================== LOOP ==================
running=True
while running:
    clock.tick(FPS)
    screen.fill(BG_COLOR)
    mouse = pygame.mouse.get_pos()
    keys = pygame.key.get_pressed()

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running=False

        # ---------- MOUSE DOWN ----------
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            x,y = e.pos
            selected = None

            for t in reversed(towers):
                if math.hypot(x-t.x,y-t.y)<=20:
                    dragged = t
                    drag_origin = (t.x, t.y)
                    t.dragging = True
                    selected = t
                    break
            else:
                if not is_on_path(x,y):
                    if keys[pygame.K_s] and money>=SNIPER_TOWER_COST:
                        towers.append(SniperTower(x,y))
                        money-=SNIPER_TOWER_COST
                    elif money>=TOWER_COST:
                        towers.append(Tower(x,y))
                        money-=TOWER_COST

        # ---------- MOUSE UP ----------
        if e.type == pygame.MOUSEBUTTONUP and e.button == 1 and dragged:
            merged = False
            for t in towers:
                if t is not dragged:
                    if (t.type == dragged.type and
                        t.level == dragged.level and
                        t.level < MAX_LEVEL and
                        math.hypot(t.x-dragged.x,t.y-dragged.y)<=25):
                        t.upgrade()
                        towers.remove(dragged)
                        merged = True
                        break

            if not merged:
                dragged.x, dragged.y = drag_origin

            dragged.dragging = False
            dragged = None
            drag_origin = None

        # ---------- SELL ----------
        if e.type == pygame.KEYDOWN and e.key == pygame.K_x and selected:
            refund = int(selected.total_value * SELL_REFUND)
            money += refund
            towers.remove(selected)
            selected = None

    # ---------- DRAG FOLLOW ----------
    if dragged:
        dragged.x, dragged.y = mouse

    # ---------- SPAWN ----------
    spawn_timer += 1
    if spawn_timer > 120:
        enemies.append(Enemy())
        spawn_timer = 0

    for enemy in enemies[:]:
        enemy.move()
        if enemy.index >= len(path):
            enemies.remove(enemy)

    for t in towers:
        t.shoot(enemies,bullets)

    for b in bullets[:]:
        if b.target not in enemies:
            bullets.remove(b); continue
        b.move()
        if math.hypot(b.x-b.target.x,b.y-b.target.y)<10:
            b.target.hp-=b.dmg
            bullets.remove(b)
            if b.target.hp<=0:
                enemies.remove(b.target)

    # ---------- DRAW ----------
    draw_path()
    base.draw()

    for e in enemies: e.draw()
    for t in towers:
        t.draw()
        if math.hypot(mouse[0]-t.x,mouse[1]-t.y)<=25:
            txt = f"{t.type.upper()} Lv {t.level}/{MAX_LEVEL} | Value {t.total_value}$"
            info = FONT.render(txt,True,(255,255,255))
            screen.blit(info,(t.x-info.get_width()//2,t.y-40))

    for b in bullets: b.draw()

    # ---------- UI ----------
    screen.blit(FONT.render(f"Money: {money}$",True,(255,255,255)),(10,10))

    controls = [
        "LMB: Place Tower",
        "S + LMB: Place Sniper",
        "Drag same type + level: MERGE",
        "X: Sell selected (75%)",
        "Max Level: 6"
    ]
    for i,c in enumerate(controls):
        screen.blit(FONT.render(c,True,(200,200,200)),(WIDTH-300,10+i*20))

    pygame.display.flip()

pygame.quit()
