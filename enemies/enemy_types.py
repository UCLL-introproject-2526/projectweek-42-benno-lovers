from enemies.enemy_base import Enemy
from settings import SCALE, FAST_ENEMY_COLOR

class FastEnemy(Enemy):
    def __init__(self, path):
        super().__init__(path, strong=False, boss=False)
        self.max_hp = 70
        self.hp = self.max_hp
        self.damage = 6
        self.reward_money = 15
        self.reward_score = 8
        self.base_speed = 3.8 * SCALE
        self.speed = self.base_speed
        self.color = FAST_ENEMY_COLOR
        self.radius = max(8, int(10 * SCALE))
        self.mark_bonus = 0.0
        self.mark_ticks = 0

