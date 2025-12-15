import pygame

def main():
    pygame.init()

    screen_size = (1024, 768)

    surface, screen = create_main_surface(screen_size)

    render_frame(surface, screen)


def create_main_surface(screen_size):
    display = pygame.display.set_mode(screen_size)
    surface = pygame.Surface(screen_size)
    return surface, display


def render_frame(surface, screen):
    pygame.draw.circle(surface, (255, 100, 100), (512, 384), 80)
    screen.blit(surface, (0, 0))
    pygame.display.flip()


main()
while True:
    pass
