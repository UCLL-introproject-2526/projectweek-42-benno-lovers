from settings import LEVEL_BOOST_FACTOR, HP_SCALE, DMG_SCALE, SPD_SCALE

def scale_enemy(e, wave, level):
    ramp = max(0, wave - 4)

    ramp_hp  = 0.015 * ramp
    ramp_dmg = 0.010 * ramp
    ramp_spd = 0.003 * ramp

    level_boost = (level.level - 1) * LEVEL_BOOST_FACTOR

    e.max_hp = int(e.max_hp * (1.0 + (HP_SCALE + ramp_hp) * (wave - 1) + level_boost))
    e.hp = e.max_hp

    e.damage = int(e.damage * (1.0 + (DMG_SCALE + ramp_dmg) * (wave - 1) + level_boost))
    e.base_speed *= (1.0 + (SPD_SCALE + ramp_spd) * (wave - 1))


def scale_boss(b, wave, level):
    ramp = max(0, wave - 4)
    level_boost = (level.level - 1) * (LEVEL_BOOST_FACTOR + 0.05)

    b.max_hp = int(b.max_hp * (1.0 + (HP_SCALE + 0.12 + 0.02 * ramp) * (wave - 1) + level_boost))
    b.hp = b.max_hp

    b.damage = int(b.damage * (1.0 + (DMG_SCALE + 0.05 + 0.015 * ramp) * (wave - 1) + level_boost))
    b.base_speed *= (1.0 + (SPD_SCALE + 0.006 + 0.002 * ramp) * (wave - 1))
