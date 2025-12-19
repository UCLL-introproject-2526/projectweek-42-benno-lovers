from enemies.enemy_base import Enemy, BennoBoss
import random


def spawn_enemy_for_wave(
    wave,
    path,
    level,
    boss_already_spawned: bool,
    enemies_spawned: int,
    enemies_in_wave: int
):
    # -------------------------
    # ✅ BENNO OVERRIDE
    # Level 4, Wave 20: Benno komt als "boss" op de laatste spawn van de wave
    # -------------------------
    if (
        level == 4
        and wave == 20
        and not boss_already_spawned
        and enemies_spawned == enemies_in_wave - 1
    ):
        return BennoBoss(path, level_id=level), True

    # -------------------------
    # Normale waves logic
    # -------------------------
    if wave < 2:
        return Enemy(path, "fast" if random.random() < 0.20 else "normal"), boss_already_spawned

    elif wave < 3:
        r = random.random()
        if r < 0.18:
            return Enemy(path, "fast"), boss_already_spawned
        elif r < 0.75:
            return Enemy(path, "normal"), boss_already_spawned
        else:
            return Enemy(path, "strong"), boss_already_spawned

    # -------------------------
    # Boss waves (elke 5e wave)
    # -------------------------
    elif (
        wave % 5 == 0
        and not boss_already_spawned
        and enemies_spawned == enemies_in_wave - 1
    ):
        boss_number = min(wave // 5, 4)
        boss_type = f"boss{boss_number}"
        return Enemy(path, boss_type, level), True

    # -------------------------
    # Default enemies
    # -------------------------
    else:
        r = random.random()
        if r < 0.22:
            return Enemy(path, "fast"), boss_already_spawned
        elif r < 0.72:
            return Enemy(path, "normal"), boss_already_spawned
        else:
            return Enemy(path, "strong"), boss_already_spawned
