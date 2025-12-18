from enemies.enemy_base import Enemy
import random
def spawn_enemy_for_wave(
    wave,
    path,
    level,
    boss_already_spawned: bool,
    enemies_spawned: int,
    enemies_in_wave: int
):
    if wave < 2:
        return Enemy(path, "fast" if random.random() < 0.12 else "normal"), boss_already_spawned

    elif wave < 3:
        r = random.random()
        if r < 0.18:
            return Enemy(path, "fast"), boss_already_spawned
        elif r < 0.88:
            return Enemy(path, "normal"), boss_already_spawned
        else:
            return Enemy(path, "strong"), boss_already_spawned
    elif (
        wave % 5 == 0
        and not boss_already_spawned
        and enemies_spawned == enemies_in_wave - 1
    ):
        boss_number = min(wave // 5, 4)
        boss_type = f"boss{boss_number}"
        return Enemy(path, boss_type, level), True

    else:
        r = random.random()
        if r < 0.22:
            return Enemy(path, "fast"), boss_already_spawned
        elif r < 0.72:
            return Enemy(path, "normal"), boss_already_spawned
        else:
            return Enemy(path, "strong"), boss_already_spawned
