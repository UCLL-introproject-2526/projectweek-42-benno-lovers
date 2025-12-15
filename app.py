import pygame

import pygame

class State:
    def __init__(self, screen_size):
        self.screen_size = screen_size
        self.circle_x = 0  # Public field for the circle's X-coordinate
        self.circle_y = screen_size[1] // 2  # Center Y
        self.circle_radius = 80
        self.circle_color = (255, 100, 100)
        self.font = pygame.font.Font(None, 50)
        self.last_key = None
        self.background_color = (0, 0, 0)

    # Update the state
    def update(self):
        self.circle_x += 1  # Move circle to the right
        if self.circle_x > self.screen_size[0]:  # Wrap around
            self.circle_x = 0

    # Render the state
    def render(self, surface):
        surface.fill(self.background_color)
        pygame.draw.circle(surface, self.circle_color, (self.circle_x, self.circle_y), self.circle_radius)
        if self.last_key:
            text = self.font.render(f"Last key: {self.last_key}", True, (255, 255, 255))
            surface.blit(text, (50, 50))


def create_main_surface(screen_size):
    display = pygame.display.set_mode(screen_size)
    surface = pygame.Surface(screen_size)
    return surface, display

def main():
    pygame.init()
    screen_size = (1024, 768)
    surface, screen = create_main_surface(screen_size)
    pygame.display.set_caption("State Example")

    state = State(screen_size)  # Create State object

    running = True
    clock = pygame.time.Clock()

    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                state.last_key = pygame.key.name(event.key)

        # Update state
        state.update()

        # Render state
        state.render(surface)
        screen.blit(surface, (0, 0))
        pygame.display.flip()

        clock.tick(60)  # Limit to 60 FPS

main()
