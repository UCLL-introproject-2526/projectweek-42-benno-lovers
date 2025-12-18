from enemies.enemy_base import Enemy, BennoBoss
import random


def spawn_enemy_for_wave(wave, path, level, boss_already_spawned: bool):
    # ✅ Benno ONLY: level 4, wave 20 (1x)
    if level == 4 and wave == 20 and not boss_already_spawned:
        return BennoBoss(path, level_id=level), True

    # ❌ oude boss-wave logic uitzetten (anders krijg je bosses op wave 5,10,15,...)
    # if wave % 5 == 0 and not boss_already_spawned:
    #     return Enemy(path, "boss", level), True

    # ---- normale enemies ----
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
