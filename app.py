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
STRONG_ENEMY_COLOR = (50, 100, 220)
TOWER_COLOR = (50, 200, 50)
SNIPER_COLOR = (50, 150, 255)
BASE_COLOR = (200, 50, 50)
BULLET_COLOR = (255, 255, 0)

FONT = pygame.font.SysFont(None, 26)
BIG_FONT = pygame.font.SysFont(None, 64)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tower Defence")
clock = pygame.time.Clock()

PATH_WIDTH = 40

# ================== LEVEL DATA ==================
level_paths = {
    1: [(-50, 550), (50, 550), (50, 200), (200, 150),
        (300, 300), (600, 300), (600, 100), (450, 100), (450, 550)],
    2: [
        {'spawn': (-50, 500), 'path': [(-50, 500), (100, 500), (100, 200),
                                       (400, 200), (400, 400), (700, 400),
                                       (700, 100), (600, 100), (600, 550)]},
        {'spawn': (850, 300), 'path': [(850, 300), (600, 300), (600, 150),
                                       (400, 150), (400, 450), (200, 450),
                                       (200, 550), (450, 550)]}
    ]
}

level_base = {1: (450, 550), 2: (450, 550)}
level_wave_map = {1: 5, 2: 10, 3: 15}

# ================== OVERLAY ==================
overlay = None

def start_overlay(text, color=(255,255,0), duration=2):
    global overlay
    overlay = {"text": text, "color": color, "frames": int(duration * FPS)}

def draw_overlay():
    global overlay
    if not overlay:
        return
    fade = int(0.5 * FPS)
    alpha = 255 if overlay["frames"] > fade else int(255 * overlay["frames"] / fade)
    surf = BIG_FONT.render(overlay["text"], True, overlay["color"]).convert_alpha()
    surf.set_alpha(alpha)
    screen.blit(surf, (WIDTH//2 - surf.get_width()//2,
                       HEIGHT//2 - surf.get_height()//2))
    overlay["frames"] -= 1
    if overlay["frames"] <= 0:
        overlay = None

# ================== HULPFUNCTIES ==================
def draw_path(path):
    for i in range(len(path)-1):
        pygame.draw.line(screen, PATH_COLOR, path[i], path[i+1], PATH_WIDTH)
        pygame.draw.circle(screen, PATH_COLOR, path[i], PATH_WIDTH//2)
    pygame.draw.circle(screen, PATH_COLOR, path[-1], PATH_WIDTH//2)

def draw_hp_bar(x, y, hp, max_hp, w=32):
    ratio = max(0, hp / max_hp)
    pygame.draw.rect(screen, (255,0,0), (x-w//2, y-28, w, 5))
    pygame.draw.rect(screen, (0,255,0), (x-w//2, y-28, int(w*ratio), 5))

def on_path(x, y, level):
    paths = [level_paths[1]] if level == 1 else [p["path"] for p in level_paths[2]]
    for path in paths:
        for i in range(len(path)-1):
            x1,y1 = path[i]
            x2,y2 = path[i+1]
            px,py = x2-x1, y2-y1
            norm = px*px + py*py
            if norm == 0: continue
            u = ((x-x1)*px + (y-y1)*py) / norm
            u = max(0, min(1, u))
            dx,dy = x1+u*px-x, y1+u*py-y
            if math.hypot(dx,dy) <= PATH_WIDTH//2:
                return True
    return False

# ================== CLASSES ==================
class Enemy:
    def __init__(self, path):
        self.path = path
        self.x, self.y = path[0]
        self.index = 1
        self.speed = 2
        self.max_hp = 100
        self.hp = self.max_hp
        self.damage = 10
        self.reward = 10

    def move(self):
        if self.index >= len(self.path):
            return True
        tx,ty = self.path[self.index]
        dx,dy = tx-self.x, ty-self.y
        d = math.hypot(dx,dy)
        if d < self.speed:
            self.index += 1
        else:
            self.x += self.speed*dx/d
            self.y += self.speed*dy/d
        return False

    def draw(self):
        pygame.draw.circle(screen, ENEMY_COLOR, (int(self.x),int(self.y)), 14)
        draw_hp_bar(self.x, self.y, self.hp, self.max_hp)

class StrongEnemy(Enemy):
    def __init__(self, path):
        super().__init__(path)
        self.max_hp = 300
        self.hp = self.max_hp
        self.speed = 1.5
        self.damage = 25
        self.reward = 25

    def draw(self):
        pygame.draw.circle(screen, STRONG_ENEMY_COLOR, (int(self.x),int(self.y)), 18)
        draw_hp_bar(self.x, self.y, self.hp, self.max_hp, 40)

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
        self.base_cost = TOWER_COST
        self.total_value = self.base_cost

    def shoot(self,enemies,bullets):
        if self.cooldown>0:
            self.cooldown-=1
            return
        for e in enemies:
            if math.hypot(e.x-self.x,e.y-self.y)<=self.range:
                bullets.append(Bullet(self.x,self.y,e,self.damage))
                self.cooldown=self.fire_rate
                break

    def upgrade(self):
        if self.level>=MAX_TOWER_LEVEL:
            return
        self.level+=1
        self.damage+=15
        self.range+=20
        self.fire_rate=max(8,self.fire_rate-3)
        self.total_value+=self.base_cost

    def draw(self):
        pygame.draw.circle(screen, TOWER_COLOR, (self.x,self.y), 14+self.level)

class SniperTower(Tower):
    def __init__(self,x,y):
        super().__init__(x,y)
        self.range = 350
        self.fire_rate = 90
        self.damage = 100
        self.base_cost = SNIPER_TOWER_COST
        self.total_value = self.base_cost

    def upgrade(self):
        if self.level>=MAX_TOWER_LEVEL:
            return
        self.level+=1
        self.damage+=35
        self.range+=35
        self.fire_rate=max(25,self.fire_rate-8)
        self.total_value+=self.base_cost

    def draw(self):
        pygame.draw.circle(screen, SNIPER_COLOR, (self.x,self.y), 18+self.level)

class Base:
    def __init__(self,x,y):
        self.x,self.y=x,y
        self.max_hp=200
        self.hp=200

    def draw(self):
        pygame.draw.rect(screen, BASE_COLOR, (self.x-25,self.y-25,50,50))
        draw_hp_bar(self.x, self.y+20, self.hp, self.max_hp, 50)

# ================== START MENU ==================
def instructions_screen():
    while True:
        screen.fill(BG_COLOR)
        title = BIG_FONT.render("Instructies", True, (255,255,255))
        screen.blit(title, (WIDTH//2-title.get_width()//2,40))

        lines = [
            "Plaats tower: Linkermuisknop",
            "Plaats sniper: S + Linkermuisknop",
            "",
            "Upgrade:",
            "Sleep twee towers van hetzelfde",
            "type en level op elkaar",
            "",
            "Verkoop:",
            "Selecteer tower en druk X",
            "",
            "ESC = terug"
        ]

        for i,l in enumerate(lines):
            t=FONT.render(l,True,(200,200,200))
            screen.blit(t,(WIDTH//2-t.get_width()//2,140+i*26))

        pygame.display.flip()
        for e in pygame.event.get():
            if e.type==pygame.QUIT:
                pygame.quit();exit()
            if e.type==pygame.KEYDOWN and e.key==pygame.K_ESCAPE:
                return

def start_screen(unlocked):
    while True:
        screen.fill(BG_COLOR)
        title = BIG_FONT.render("Tower Defence",True,(255,255,255))
        screen.blit(title,(WIDTH//2-title.get_width()//2,40))

        options=["Level 1","Level 2","Level 3","Instructies"]
        mouse=pygame.mouse.get_pos()
        rects=[]

        for i,opt in enumerate(options):
            ok = opt=="Instructies" or unlocked.get(i+1,False)
            col=(255,255,0) if ok else (120,120,120)
            txt=FONT.render(opt,True,col)
            r=txt.get_rect(center=(WIDTH//2,160+i*70))
            if ok and r.collidepoint(mouse):
                pygame.draw.rect(screen,(255,255,150),r.inflate(20,10),border_radius=6)
            screen.blit(txt,r)
            rects.append((r,opt,ok))

        pygame.display.flip()
        for e in pygame.event.get():
            if e.type==pygame.QUIT:
                pygame.quit();exit()
            if e.type==pygame.MOUSEBUTTONDOWN:
                for r,opt,ok in rects:
                    if ok and r.collidepoint(e.pos):
                        if opt=="Instructies":
                            instructions_screen()
                        else:
                            return int(opt.split()[1])

# ================== GAME ==================
levels_unlocked={1:True,2:False,3:False}
level=start_screen(levels_unlocked)

enemies=[]
towers=[]
bullets=[]
base=Base(*level_base[level])

money=150
score=0
wave=1
spawned=0
per_wave=5
timer=0

drag=None
origin=None

# ================== LOOP ==================
running=True
while running:
    clock.tick(FPS)
    screen.fill(BG_COLOR)
    mx,my=pygame.mouse.get_pos()
    keys=pygame.key.get_pressed()

    for e in pygame.event.get():
        if e.type==pygame.QUIT:
            running=False

        if e.type==pygame.MOUSEBUTTONDOWN and e.button==1:
            for t in towers:
                if math.hypot(mx-t.x,my-t.y)<=22:
                    drag=t
                    origin=(t.x,t.y)
                    break
            else:
                if not on_path(mx,my,level):
                    if keys[pygame.K_s] and money>=SNIPER_TOWER_COST:
                        towers.append(SniperTower(mx,my)); money-=SNIPER_TOWER_COST
                    elif money>=TOWER_COST:
                        towers.append(Tower(mx,my)); money-=TOWER_COST

        if e.type==pygame.MOUSEBUTTONUP and e.button==1 and drag:
            merged=False
            for t in towers:
                if t!=drag and type(t)==type(drag) and t.level==drag.level and t.level<MAX_TOWER_LEVEL:
                    if math.hypot(t.x-drag.x,t.y-drag.y)<=24:
                        t.upgrade()
                        towers.remove(drag)
                        merged=True
                        break
            if not merged:
                drag.x,drag.y=origin
            drag=None

        if e.type==pygame.KEYDOWN and e.key==pygame.K_x:
            for t in towers:
                if math.hypot(mx-t.x,my-t.y)<=22:
                    money+=int(t.total_value*SELL_REFUND)
                    towers.remove(t)
                    break

    if drag:
        drag.x,drag.y=mx,my

    timer+=1
    if timer>120 and spawned<per_wave:
        path = level_paths[level] if level==1 else level_paths[2][wave%2]["path"]
        enemy = StrongEnemy(path) if spawned%2==0 else Enemy(path)
        enemies.append(enemy)
        spawned+=1
        timer=0

    for en in enemies[:]:
        if en.move():
            base.hp-=en.damage
            enemies.remove(en)

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
                money+=b.target.reward
                score+=b.target.reward
                enemies.remove(b.target)

    if spawned>=per_wave and not enemies:
        wave+=1
        spawned=0
        per_wave+=2
        start_overlay(f"Wave {wave}")

    if level==1:
        draw_path(level_paths[1])
    else:
        for p in level_paths[2]:
            draw_path(p["path"])

    base.draw()
    for en in enemies: en.draw()
    for t in towers:
        t.draw()
        if math.hypot(mx-t.x,my-t.y)<=28:
            pygame.draw.circle(screen,(255,255,255),(t.x,t.y),t.range,1)
            txt1=FONT.render(f"Lv {t.level}/{MAX_TOWER_LEVEL}",True,(255,255,255))
            txt2=FONT.render(f"Value {t.total_value}$ | Sell {int(t.total_value*SELL_REFUND)}$",True,(255,255,255))
            screen.blit(txt1,(t.x-txt1.get_width()//2,t.y-55))
            screen.blit(txt2,(t.x-txt2.get_width()//2,t.y-30))

    for b in bullets: b.draw()

    # ---------- HUD ----------
    screen.blit(FONT.render(f"Money: {money}$",True,(255,255,255)),(10,10))
    screen.blit(FONT.render(f"Score: {score}",True,(255,255,255)),(10,35))
    screen.blit(FONT.render(f"Base HP: {base.hp}",True,(255,255,255)),(10,60))
    screen.blit(FONT.render(f"Wave: {wave}",True,(255,255,255)),(10,85))
    screen.blit(FONT.render(f"Tower: {TOWER_COST}$",True,(200,200,200)),(WIDTH-160,10))
    screen.blit(FONT.render(f"Sniper: {SNIPER_TOWER_COST}$",True,(200,200,200)),(WIDTH-160,35))

    draw_overlay()
    pygame.display.flip()

pygame.quit()
