import pygame

def create_main_surface(screen_size):
    display = pygame.display.set_mode(screen_size)
    surface = pygame.Surface(screen_size)
    return surface, display

def main():
    pygame.init()
    screen_size = (1024, 768)
    surface, screen = create_main_surface(screen_size)
    pygame.display.set_caption("Key Press Test")

    running = True
    last_key = None

    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # ESC om te stoppen
                    running = False
                last_key = pygame.key.name(event.key)
                print(f"Key pressed: {last_key}")

        # Clear screen
        surface.fill((0, 0, 0))  # zwart achtergrond

        # Draw circle
        pygame.draw.circle(surface, (255, 100, 100), (512, 384), 80)

        # Optional: display last key pressed
        if last_key:
            font = pygame.font.Font(None, 50)
            text = font.render(f"Last key: {last_key}", True, (255, 255, 255))
            surface.blit(text, (50, 50))

        # Update the display
        screen.blit(surface, (0, 0))
        pygame.display.flip()
main()