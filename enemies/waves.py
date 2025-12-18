from enemies.enemy_base import Enemy
import random

def spawn_enemy_for_wave(wave, path, boss_already_spawned: bool):
    # 1 boss per boss-wave
    if wave % 5 == 0 and not boss_already_spawned:
        return Enemy(path, "boss"), True

    # anders normale logic
    if wave == 1:
        return Enemy(path, "normal"), boss_already_spawned

    elif wave <= 2:
        return Enemy(path, "fast" if random.random() < 0.12 else "normal"), boss_already_spawned

    elif wave <= 4:
        r = random.random()
        if r < 0.18:
            return Enemy(path, "fast"), boss_already_spawned
        elif r < 0.88:
            return Enemy(path, "normal"), boss_already_spawned
        else:
            return Enemy(path, "strong"), boss_already_spawned

    else:
        r = random.random()
        if r < 0.22:
            return Enemy(path, "fast"), boss_already_spawned
        elif r < 0.72:
            return Enemy(path, "normal"), boss_already_spawned
        else:
            return Enemy(path, "strong"), boss_already_spawned
