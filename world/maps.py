
from settings import sx, sy

def sp(p):
    return int(p[0] * sx), int(p[1] * sy)

def spath(path):
    return [sp(pt) for pt in path]


_level_paths_base = {
    # Map 1 — klassiek
    1: [
        (-50, 550), (50, 550), (50, 200), (200, 150),
        (300, 300), (600, 300), (600, 100),
        (450, 100), (450, 550)
    ],

    # Map 2 — slingerpad
    2: [
        (-50, 300), (150, 300), (150, 100),
        (650, 100), (650, 500), (300, 500),
        (300, 250), (550, 250), (550, 550)
    ],

    # Map 3 — multi-lane
    31: [
        (-50, 180), (120, 180), (120, 80),
        (420, 80), (420, 260), (560, 260), (560, 550)
    ],
    32: [
        (850, 420), (680, 420), (680, 520),
        (260, 520), (260, 320), (560, 320), (560, 550)
    ],
        # Map 4 — slingerpad
    3: [
        (-50, 400),
        (204, 405),
        (195, 271),
        (402, 267),
        (396, 564),
        (593, 564),
        (588, 134),
        (710, 133)
    ],

}

level_paths = {
    1: [spath(_level_paths_base[1])],
    2: [spath(_level_paths_base[2])],
    3: [spath(_level_paths_base[31]), spath(_level_paths_base[32])],
    4: [spath(_level_paths_base[3])],
}

level_base = {
    1: sp((450, 550)),
    2: sp((550, 550)),
    3: sp((560, 550)),
    4: sp((710, 133))
}

level_wave_map = {
    1: 5,
    2: 10,
    3: 14,
    4: 5
}

level_backgrounds = {
    4: "assets/images/BG_Classroom.png",
}