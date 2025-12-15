import pygame

def create_main_surface(screen_size):
    display = pygame.display.set_mode(screen_size)
    surface = pygame.Surface(screen_size)
    return surface, display


def render_frame(surface, screen, x):
    # teken de cirkel op positie x
    pygame.draw.circle(surface, (255, 100, 100), (x, 384), 80)
    screen.blit(surface, (0, 0))
    pygame.display.flip()


def main():
    pygame.init()
    screen_size = (1024, 768)
    surface, screen = create_main_surface(screen_size)
    pygame.display.set_caption("Naive Animation")

    running = True
    x = 0  # startpositie van de cirkel

    while running:
        # events afhandelen
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # render frame (nu elke loop)
        render_frame(surface, screen, x)

        # cirkel verplaatsen
        x += 1


main()
