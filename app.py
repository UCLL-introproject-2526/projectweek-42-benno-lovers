import pygame
import enum
import math
from dataclasses import dataclass, field

# =========================================================
# CONSTANTS
# =========================================================

WIDTH, HEIGHT = 800, 600
FPS = 60
BG_COLOR = (40, 40, 40)
WHITE = (255, 255, 255)
PATH_COLOR = (120, 80, 40)
TOWER_COLOR = (200, 200, 50)
BASE_COLOR = (150, 50, 50)
PATH_WIDTH = 40

# =========================================================
# GAME STATES
# =========================================================

class GameState(enum.Enum):
    initializing = 0
    main_menu = 1
    playing = 2
    quitting = 3

# =========================================================
# LEVEL DATA
# =========================================================

level_paths = {
    1: [(-50, 550), (50, 550), (50, 200), (200, 150),
        (300, 300), (600, 300), (600, 100), (450, 100), (450, 550)],
}

level_base = {1: (450, 550)}
level_wave_map = {1: 5}

# =========================================================
# GAME LOOP BASE CLASS
# =========================================================

@dataclass
class GameLoop:
    game: "TowerGame"

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.set_state(GameState.quitting)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.set_state(GameState.main_menu)
            self.handle_event(event)

    def handle_event(self, event):
        pass

    def loop(self):
        while self.game.state != GameState.quitting:
            self.handle_events()

    def set_state(self, state):
        self.game.state = state

    @property
    def screen(self):
        return self.game.screen

# =========================================================
# MENU (LEVEL SELECT)
# =========================================================

@dataclass
class GameMenu(GameLoop):

    def loop(self):
        clock = pygame.time.Clock()
        while self.game.state == GameState.main_menu:
            self.handle_events()
            self.screen.fill(BG_COLOR)
            self.draw_text("TOWER DEFENCE", 64, 100)
            self.draw_text("Click to start", 32, 250)
            pygame.display.flip()
            clock.tick(FPS)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.set_state(GameState.playing)

    def draw_text(self, txt, size, y):
        font = pygame.font.SysFont(None, size)
        surf = font.render(txt, True, WHITE)
        self.screen.blit(surf, (WIDTH//2 - surf.get_width()//2, y))

# =========================================================
# GAME OBJECTS
# =========================================================

class Enemy:
    def __init__(self, path):
        self.path = path
        self.x, self.y = path[0]
        self.index = 1
        self.hp = 100
        self.speed = 2

    def move(self):
        if self.index >= len(self.path): return
        tx, ty = self.path[self.index]
        dx, dy = tx - self.x, ty - self.y
        d = math.hypot(dx, dy)
        if d < self.speed:
            self.index += 1
        else:
            self.x += self.speed * dx / d
            self.y += self.speed * dy / d

    def draw(self, screen):
        pygame.draw.circle(screen, (255, 0, 0), (int(self.x), int(self.y)), 10)

class Tower:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.range = 150
        self.cooldown = 0

    def shoot(self, enemies):
        if self.cooldown > 0:
            self.cooldown -= 1
            return
        for e in enemies:
            if math.hypot(e.x - self.x, e.y - self.y) < self.range:
                e.hp -= 10
                self.cooldown = 30
                break

    def draw(self, screen):
        pygame.draw.circle(screen, TOWER_COLOR, (self.x, self.y), 15)

class Base:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.hp = 200
        self.max_hp = 200

    def draw(self, screen):
        pygame.draw.rect(screen, BASE_COLOR, (self.x-20, self.y-20, 40, 40))
        pygame.draw.rect(screen, (255,0,0), (10, 40, 200, 10))
        pygame.draw.rect(screen, (0,255,0), (10, 40, 200*self.hp/self.max_hp, 10))

# =========================================================
# GAMEPLAY LOOP
# =========================================================

@dataclass
class GamePlaying(GameLoop):

    def loop(self):
        clock = pygame.time.Clock()
        enemies = []
        towers = []
        base = Base(*level_base[1])
        path = level_paths[1]

        while self.game.state == GameState.playing:
            self.handle_events()
            self.screen.fill(BG_COLOR)

            for e in pygame.event.get():
                if e.type == pygame.MOUSEBUTTONDOWN:
                    x, y = e.pos
                    towers.append(Tower(x, y))

            if len(enemies) < 5:
                enemies.append(Enemy(path))

            for e in enemies[:]:
                e.move()
                if e.hp <= 0:
                    enemies.remove(e)

            for t in towers:
                t.shoot(enemies)

            self.draw_path(path)
            base.draw(self.screen)
            for e in enemies: e.draw(self.screen)
            for t in towers: t.draw(self.screen)

            pygame.display.flip()
            clock.tick(FPS)

    def draw_path(self, path):
        for i in range(len(path)-1):
            pygame.draw.line(self.screen, PATH_COLOR, path[i], path[i+1], PATH_WIDTH)

# =========================================================
# CONTROLLER
# =========================================================

@dataclass
class TowerGame:
    screen: pygame.Surface = field(init=False)
    state: GameState = field(default=GameState.initializing)

    def init(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.menu = GameMenu(self)
        self.playing = GamePlaying(self)
        self.state = GameState.main_menu

    def loop(self):
        while self.state != GameState.quitting:
            if self.state == GameState.main_menu:
                self.menu.loop()
            elif self.state == GameState.playing:
                self.playing.loop()
        pygame.quit()

# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":
    game = TowerGame()
    game.init()
    game.loop()
