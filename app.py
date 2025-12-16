import pygame
import math
import random

pygame.init()

# ================== BORDERLESS FULLSCREEN ==================
screen = pygame.display.set_mode((0, 0), pygame.NOFRAME)
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

FONT = pygame.font.SysFont(None, 28)
SMALL_FONT = pygame.font.SysFont(None, 22)
BIG_FONT = pygame.font.SysFont(None, 72)

# ================== SCHALING ==================
BASE_W, BASE_H = 800, 600
sx = WIDTH / BASE_W
sy = HEIGHT / BASE_H
SCALE = min(sx, sy)
PATH_WIDTH = int(40 * SCALE)

# ================== LEVEL DATA ==================
def scale(p):
    return int(p[0] * sx), int(p[1] * sy)

def scale_path(path):
    return [scale(p) for p in path]

base_paths = {
    1: [(-50, 550), (50, 550), (50, 200), (200, 150),
        (300, 300), (600, 300), (600, 100), (450, 100), (450, 550)]
}

level_paths = {1: scale_path(base_paths[1])}
level_base = {1: scale((450, 550))}
level_wave_map = {1: 10}

# ================== HELPERS ==================
def draw_path(path):
    for i in range(len(path)-1):
        pygame.draw.line(screen, PATH_COLOR, path[i], path[i+1], PATH_WIDTH)
        pygame.draw.circle(screen, PATH_COLOR, path[i], PATH_WIDTH//2)
    pygame.draw.circle(screen, PATH_COLOR, path[-1], PATH_WIDTH//2)

def is_on_path(x, y, path):
    for i in range(len(path)-1):
        x1,y1 = path[i]
        x2,y2 = path[i+1]
        px,py = x2-x1, y2-y1
        norm = px*px + py*py
        if norm == 0: continue
        u = ((x-x1)*px + (y-y1)*py)/norm
        u = max(0, min(1, u))
        dx = x1 + u*px - x
        dy = y1 + u*py - y
        if math.hypot(dx,dy) <= PATH_WIDTH//2 + 4:
            return True
    return False

def hp_bar(x,y,hp,max_hp,w):
    ratio = max(0, hp/max_hp)
    pygame.draw.rect(screen,(255,0,0),(x-w//2,y,w,6))
    pygame.draw.rect(screen,(0,255,0),(x-w//2,y,int(w*ratio),6))

# ================== CLASSES ==================
class Enemy:
    def __init__(self,path,strong=False):
        self.path = path
        self.x,self.y = path[0]
        self.i = 1
        self.speed = 1.5*SCALE if strong else 2.2*SCALE
        self.max_hp = 300 if strong else 100
        self.hp = self.max_hp
        self.damage = 25 if strong else 10
        self.reward = 25 if strong else 10
        self.color = STRONG_ENEMY_COLOR if strong else ENEMY_COLOR
        self.r = int(20*SCALE if strong else 14*SCALE)

    def move(self):
        if self.i >= len(self.path):
            return True
        tx,ty = self.path[self.i]
        dx,dy = tx-self.x, ty-self.y
        d = math.hypot(dx,dy)
        if d < self.speed:
            self.i += 1
        else:
            self.x += self.speed*dx/d
            self.y += self.speed*dy/d
        return False

    def draw(self):
        pygame.draw.circle(screen,self.color,(int(self.x),int(self.y)),self.r)
        hp_bar(self.x,self.y-int(30*SCALE),self.hp,self.max_hp,int(50*SCALE))

class Bullet:
    def __init__(self,x,y,t,d):
        self.x,self.y=x,y
        self.t=t
        self.d=d
        self.s=6*SCALE

    def move(self):
        dx,dy=self.t.x-self.x,self.t.y-self.y
        dist=math.hypot(dx,dy)
        if dist:
            self.x+=self.s*dx/dist
            self.y+=self.s*dy/dist

    def draw(self):
        pygame.draw.circle(screen,BULLET_COLOR,(int(self.x),int(self.y)),int(4*SCALE))

class Tower:
    def __init__(self,x,y,sniper=False):
        self.x,self.y=x,y
        self.sniper=sniper
        self.level=1
        self.range=int((350 if sniper else 150)*SCALE)
        self.damage=100 if sniper else 25
        self.rate=90 if sniper else 30
        self.cd=0
        self.drag=False
        self.value=SNIPER_TOWER_COST if sniper else TOWER_COST
        self.color=SNIPER_COLOR if sniper else TOWER_COLOR

    def shoot(self,enemies,bullets):
        if self.drag: return
        if self.cd>0:
            self.cd-=1; return
        for e in enemies:
            if math.hypot(e.x-self.x,e.y-self.y)<=self.range:
                bullets.append(Bullet(self.x,self.y,e,self.damage))
                self.cd=self.rate
                break

    def upgrade(self):
        if self.level>=MAX_TOWER_LEVEL: return
        self.level+=1
        self.damage+=20
        self.range+=int(20*SCALE)
        self.rate=max(10,self.rate-4)

    def draw(self):
        r=int((14+self.level)*SCALE)
        pygame.draw.circle(screen,self.color,(int(self.x),int(self.y)),r)
        txt=SMALL_FONT.render(str(self.level),True,(0,0,0))
        screen.blit(txt,(self.x-txt.get_width()//2,self.y-txt.get_height()//2))

class Base:
    def __init__(self,x,y):
        self.x,self.y=x,y
        self.max_hp=200
        self.hp=200

    def draw(self):
        s=int(50*SCALE)
        pygame.draw.rect(screen,BASE_COLOR,(self.x-s//2,self.y-s//2,s,s))
        hp_bar(self.x,self.y-s//2-10,self.hp,self.max_hp,int(80*SCALE))

# ================== GAME STATE ==================
path=level_paths[1]
base=Base(*level_base[1])
enemies=[]
towers=[]
bullets=[]
money=150
wave=1
spawned=0
timer=0
per_wave=6
game_over=False
selected=None
dragged=None
origin=None

# ================== MAIN LOOP ==================
running=True
while running:
    clock.tick(FPS)
    screen.fill(BG_COLOR)
    mx,my=pygame.mouse.get_pos()

    for e in pygame.event.get():
        if e.type==pygame.QUIT:
            running=False
        if e.type==pygame.KEYDOWN and e.key==pygame.K_ESCAPE:
            running=False
        if e.type==pygame.KEYDOWN and e.key==pygame.K_x and selected in towers:
            money+=int(selected.value*SELL_REFUND)
            towers.remove(selected)
            selected=None

        if e.type==pygame.MOUSEBUTTONDOWN and not game_over:
            if e.button==1:
                selected=None
                for t in towers:
                    if math.hypot(mx-t.x,my-t.y)<=20*SCALE:
                        selected=t
                        dragged=t
                        origin=(t.x,t.y)
                        t.drag=True
                        break
                else:
                    if not is_on_path(mx,my,path):
                        if pygame.key.get_pressed()[pygame.K_s] and money>=SNIPER_TOWER_COST:
                            towers.append(Tower(mx,my,True)); money-=SNIPER_TOWER_COST
                        elif money>=TOWER_COST:
                            towers.append(Tower(mx,my)); money-=TOWER_COST

        if e.type==pygame.MOUSEBUTTONUP and dragged:
            merged=False
            for t in towers:
                if t is not dragged and t.level==dragged.level and t.sniper==dragged.sniper:
                    if math.hypot(t.x-dragged.x,t.y-dragged.y)<=25*SCALE:
                        t.upgrade()
                        towers.remove(dragged)
                        merged=True
                        break
            if not merged:
                dragged.x,dragged.y=origin
            dragged.drag=False
            dragged=None

    if dragged:
        dragged.x,dragged.y=mx,my

    timer+=1
    if timer>90 and spawned<per_wave:
        enemies.append(Enemy(path,spawned%2==0))
        spawned+=1
        timer=0

    for en in enemies[:]:
        if en.move():
            base.hp-=en.damage
            enemies.remove(en)
            if base.hp<=0:
                game_over=True

    for t in towers:
        t.shoot(enemies,bullets)

    for b in bullets[:]:
        if b.t not in enemies:
            bullets.remove(b); continue
        b.move()
        if math.hypot(b.x-b.t.x,b.y-b.t.y)<10*SCALE:
            b.t.hp-=b.d
            bullets.remove(b)
            if b.t.hp<=0:
                enemies.remove(b.t)
                money+=b.t.reward

    draw_path(path)
    base.draw()
    for en in enemies: en.draw()
    for t in towers:
        t.draw()
        if t==selected:
            pygame.draw.circle(screen,(255,255,255),(t.x,t.y),t.range,1)
    for b in bullets: b.draw()

    screen.blit(FONT.render(f"Money: {money}",True,(255,255,255)),(10,10))
    screen.blit(FONT.render(f"Base HP: {base.hp}",True,(255,255,255)),(10,40))

    if game_over:
        txt=BIG_FONT.render("GAME OVER",True,(255,0,0))
        screen.blit(txt,(WIDTH//2-txt.get_width()//2,HEIGHT//2))

    pygame.display.flip()

pygame.quit()
