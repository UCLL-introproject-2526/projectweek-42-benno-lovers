# settings.py
import pygame

pygame.init()

# DISPLAY
screen = pygame.display.set_mode((0, 0), pygame.NOFRAME)
WIDTH, HEIGHT = screen.get_size()
FPS = 60
clock = pygame.time.Clock()

# DEV
DEV_INFINITE_MONEY = False
# ---------------- DEV / TEST ----------------
START_WAVE = 1  # zet bv. 1, 5, 10, 20 ...


# CONSTANTEN
TOWER_COST = 70
SNIPER_TOWER_COST = 120
SLOW_TOWER_COST = 90
POISON_TOWER_COST = 110

SELL_REFUND = 0.75
MAX_TOWER_LEVEL = 6
MIN_TOWER_DISTANCE = 48  # base personal space (wordt geschaald)

# COLORS
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

# FONTS
FONT = pygame.font.SysFont(None, 28)
SMALL_FONT = pygame.font.SysFont(None, 22)
BIG_FONT = pygame.font.SysFont(None, 72)

# SCALING
BASE_W, BASE_H = 800, 600
sx = WIDTH / BASE_W
sy = HEIGHT / BASE_H
SCALE = min(sx, sy)

PATH_WIDTH = max(22, int(30 * SCALE))

# ================== TARGETING ==================
TARGET_FIRST = "FIRST"
TARGET_STRONG = "STRONG"
TARGET_CLOSEST = "CLOSEST"
TARGET_MODES = [TARGET_FIRST, TARGET_STRONG, TARGET_CLOSEST]

# ================= ENEMIES ======================
HP_SCALE = 0.22
DMG_SCALE = 0.12
SPD_SCALE = 0.03
LEVEL_BOOST_FACTOR = 0.12