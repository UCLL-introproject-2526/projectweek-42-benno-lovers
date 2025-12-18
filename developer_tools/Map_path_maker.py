import pygame

# ============================================================================
# Gw dit bestand runnen en u pad maken, points worden in terminal geprint
# ============================================================================


# ---- Instellingen ----
GAME_WIDTH, GAME_HEIGHT = 800, 600
LINE_COLOR = (200, 180, 50)
LINE_WIDTH = 20
BG_IMAGE_PATH = "./assets/images/BG_Benno's_Hell.png"

# ---- Init Pygame ----
pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
pygame.display.set_caption("Level Path Creator")

# ---- Laad achtergrond ----
bg = pygame.image.load(BG_IMAGE_PATH).convert()
bg = pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))

# ---- Variabelen ----
points = []
running = True
font = pygame.font.SysFont(None, 24)

# Functie om scherm-coördinaten naar game-coördinaten te converteren
def to_game_coords(pos):
    x, y = pos
    gx = int(x / SCREEN_WIDTH * GAME_WIDTH)
    gy = int(y / SCREEN_HEIGHT * GAME_HEIGHT)
    return (gx, gy)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

        # Klik voor punten
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            game_pos = to_game_coords(event.pos)
            points.append(game_pos)
            print(game_pos)  # Print (x, y) zodat je het in level_paths kan plakken

        # Rechtsklik verwijdert laatste punt
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            if points:
                points.pop()

    # ---- Draw ----
    screen.blit(bg, (0, 0))

    if len(points) > 1:
        # Schaal punten terug naar fullscreen voor weergave
        draw_points = [(int(x / GAME_WIDTH * SCREEN_WIDTH), int(y / GAME_HEIGHT * SCREEN_HEIGHT)) for x, y in points]
        pygame.draw.lines(screen, LINE_COLOR, False, draw_points, LINE_WIDTH)

    # Laat aantal punten zien
    txt = font.render(f"Points: {len(points)} (LMB = add, RMB = remove, ESC = quit)", True, (255, 255, 255))
    screen.blit(txt, (10, 10))

    pygame.display.flip()

pygame.quit()
