
from settings import sx, sy

def sp(p):
    return int(p[0] * sx), int(p[1] * sy)

def spath(path):
    return [sp(pt) for pt in path]


_level_paths_base = {
    # Map 1 — klassiek
    1: [
    (401, 599), #BEGIN
    (401, 514), #eeste hoek
    (514, 514), #tweede hoek
    (516, 401),
    (510, 391),
    (293, 391),
    (293, 283),
    (293, 277),
    (72, 277),
    (72, 162),
    (399, 154),
    (399, 206),
    (393, 206)
    ],

    # Map 2 — slingerpad
    2: [
    (-50, 320),      # start links buiten beeld
    (80, 320),      # gang 1 in
    (80, 210),      # omhoog tussen banken
    (750, 210),      # lange horizontale gang rechts
    (750, 380),      # omlaag langs banken
    (400, 380),      # terug naar links
    (400, 150)        # einde bij desk
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
    # Map 3 — multi-lane
    41: [
        (-50, 180), (120, 180), (120, 80),
        (420, 80), (420, 260), (560, 260), (560, 550)
    ],
    42: [
        (850, 420), (680, 420), (680, 520),
        (260, 520), (260, 320), (560, 320), (560, 550)
    ],



}

level_paths = {
    1: [spath(_level_paths_base[1])],
    2: [spath(_level_paths_base[2])],
    3: [spath(_level_paths_base[3])],
    4: [spath(_level_paths_base[41]), spath(_level_paths_base[42])],

}

level_base = {
    1: sp((393, 206)),
    2: sp((400, 150)),
    3: sp((710, 133)),
    4: sp((560, 550)),
    

}

level_wave_map = {
    1: 5,
    2: 10,
    3: 15,
    4: 20,
}

level_backgrounds = {
    1: "assets/images/BG_Restaurant.png",
    2: "assets/images/BG_Aula.png",
    3: "assets/images/BG_Classroom.png"
}