from settings import SCALE
from settings import (
    ENEMY_COLOR,
    STRONG_ENEMY_COLOR,
    FAST_ENEMY_COLOR,
    BOSS_COLOR
)

ENEMY_TYPES = {
    "normal": {
        "hp": 155,
        "damage": 10,
        "speed": 2.2,
        "radius": 14,
        "color": ENEMY_COLOR,
        "reward_money": 25,
        "reward_score": 10
    },
    "strong": {
        "hp": 500,
        "damage": 25,
        "speed": 1.5,
        "radius": 20,
        "color": STRONG_ENEMY_COLOR,
        "reward_money": 35,
        "reward_score": 30
    },
    "fast": {
        "hp": 70,
        "damage": 6,
        "speed": 3.8,
        "radius": 10,
        "color": FAST_ENEMY_COLOR,
        "reward_money": 15,
        "reward_score": 8
    },
    "boss": {
        "hp": 4000,
        "damage": 2999,
        "speed": 0.66,
        "radius": 26,
        "color": BOSS_COLOR,
        "reward_money": 250,
        "reward_score": 250
    }
}
