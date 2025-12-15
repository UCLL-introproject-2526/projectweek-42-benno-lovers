import pygame

# ------------------------------
# State class
# ------------------------------
class State:
    def __init__(self, screen_size):
        self.screen_size = screen_size
        self.circle_x = screen_size[0] // 2  # Start in het midden X
        self.circle_y = screen_size[1] // 2  # Start in het midden Y
        self.circle_radius = 80
        self.circle_color = (255, 100, 100)
        self.font = pygame.font.Font(None, 50)
        self.last_key = None
        self.background_color = (0, 0, 0)
        self.speed = 5  # pixels per frame

# ------------------------------
# Key input processing
# ------------------------------
def process_key_input(state, keys_pressed):
    # Beweeg de cirkel op basis van ingedrukte toetsen
    if keys_pressed[pygame.K_LEFT]:
        state.circle_x -= state.speed
    if keys_pressed[pygame.K_RIGHT]:
        state.circle_x += state.speed
    if keys_pressed[pygame.K_UP]:
        state.circle_y -= state.speed
    if keys_pressed[pygame.K_DOWN]:
        state.circle_y += state.speed

    # Optioneel: houd de cirkel binnen het scherm
    state.circle_x = max(state.circle_radius, min(state.circle_x, state.screen_size[0] - state.circle_radius))
    state.circle_y = max(state.circle_radius, min(state.circle_y, state.screen_size[1] - state.circle_radius))

# ------------------------------
# Rendering
# ------------------------------
def create_main_surface(screen_size):
    display = pygame.display.set_mode(screen_size)
    surface = pygame.Surface(screen_size)
    return surface, display

def render_state(surface, state):
    surface.fill(state.background_color)
    pygame.draw.circle(surface, state.circle_color, (state.circle_x, state.circle_y), state.circle_radius)
    if state.last_key:
        text = state.font.render(f"Last key: {state.last_key}", True, (255, 255, 255))
        surface.blit(text, (50, 50))

# ------------------------------
# Main loop
# ------------------------------
def main():
    pygame.init()
    screen_size = (1024, 768)
    surface, screen = create_main_surface(screen_size)
    pygame.display.set_caption("Move the Circle")

    state = State(screen_size)

    clock = pygame.time.Clock()
    running = True

    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                state.last_key = pygame.key.name(event.key)
                if event.key == pygame.K_ESCAPE:
                    running = False

        # Key pressed state
        keys_pressed = pygame.key.get_pressed()
        process_key_input(state, keys_pressed)

        # Render everything
        render_state(surface, state)
        screen.blit(surface, (0, 0))
        pygame.display.flip()

        clock.tick(60)

    pygame.quit()
main()

