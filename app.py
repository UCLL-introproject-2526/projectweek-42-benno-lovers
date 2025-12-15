def main():
    import pygame


    # Initialize Pygame
    pygame.init()

    # Tuple representing width and height in pixels
    screen_size = (1024, 768)

    # Create window with given size
    pygame.display.set_mode(screen_size)


    def create_main_surface():
        pygame.display.set_mode(screen_size)
        return pygame.Surface(screen_size)

    while True:
        pass
main()