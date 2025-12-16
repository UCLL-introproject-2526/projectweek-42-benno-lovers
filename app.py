import pygame
import enum
from dataclasses import dataclass, field

# =========================================================
# CONSTANTS
# =========================================================

WIDTH, HEIGHT = 800, 600
DESIRED_FPS = 60
BG_COLOR = (40, 40, 40)
WHITE = (255, 255, 255)

# =========================================================
# GAME STATES
# =========================================================

class GameState(enum.Enum):
    initializing = 0
    main_menu = 1
    playing = 2
    quitting = 3

# =========================================================
# GAME LOOP BASE CLASS
# =========================================================

@dataclass
class GameLoop:
    game: "TowerGame"

    def handle_events(self):
        """
        Default OS-level event processing.
        MUST be called to avoid freezing.
        """
        for event in pygame.event.get():
            if (
                event.type == pygame.QUIT
                or (
                    event.type == pygame.KEYDOWN
                    and event.key == pygame.K_ESCAPE
                )
            ):
                self.set_state(GameState.quitting)

            # Delegate to subclass
            self.handle_event(event)

    def handle_event(self, event):
        """
        Override in subclass if needed.
        """
        pass

    def loop(self):
        """
        Override in subclass.
        """
        while self.state != GameState.quitting:
            self.handle_events()

    # ---- shortcuts ----

    def set_state(self, new_state: GameState):
        self.game.set_state(new_state)

    @property
    def screen(self):
        return self.game.screen

    @property
    def state(self):
        return self.game.state


# =========================================================
# MAIN MENU SCREEN
# =========================================================

@dataclass
class GameMenu(GameLoop):

    def loop(self):
        clock = pygame.time.Clock()

        while self.state == GameState.main_menu:
            self.handle_events()

            self.screen.fill(BG_COLOR)
            self.draw_text("TOWER DEFENCE", 64, HEIGHT // 2 - 80)
            self.draw_text("Click to Start", 32, HEIGHT // 2 + 20)

            pygame.display.flip()
            pygame.display.set_caption(f"FPS: {round(clock.get_fps())}")
            clock.tick(DESIRED_FPS)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.set_state(GameState.playing)

    def draw_text(self, text, size, y):
        font = pygame.font.SysFont(None, size)
        surface = font.render(text, True, WHITE)
        self.screen.blit(
            surface,
            (WIDTH // 2 - surface.get_width() // 2, y),
        )


# =========================================================
# GAMEPLAY SCREEN (placeholder gameplay loop)
# =========================================================

@dataclass
class GamePlaying(GameLoop):

    def loop(self):
        clock = pygame.time.Clock()

        while self.state == GameState.playing:
            self.handle_events()
            self.update()
            self.draw()

            pygame.display.flip()
            pygame.display.set_caption(f"FPS: {round(clock.get_fps())}")
            clock.tick(DESIRED_FPS)

    def update(self):
        # Gameplay logic would go here
        pass

    def draw(self):
        self.screen.fill((20, 60, 20))
        self.draw_text("GAME RUNNING", 48, HEIGHT // 2 - 30)
        self.draw_text("ESC to quit", 24, HEIGHT // 2 + 40)

    def draw_text(self, text, size, y):
        font = pygame.font.SysFont(None, size)
        surface = font.render(text, True, WHITE)
        self.screen.blit(
            surface,
            (WIDTH // 2 - surface.get_width() // 2, y),
        )


# =========================================================
# MAIN CONTROLLER
# =========================================================

@dataclass
class TowerGame:
    screen: pygame.Surface = field(init=False)
    state: GameState = field(init=False, default=GameState.initializing)

    game_menu: GameMenu = field(init=False)
    game_playing: GamePlaying = field(init=False)

    def init(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Tower Defence")

        # Initialize screens
        self.game_menu = GameMenu(game=self)
        self.game_playing = GamePlaying(game=self)

        self.set_state(GameState.main_menu)

    def set_state(self, new_state: GameState):
        self.state = new_state

    def loop(self):
        """
        Central controller loop.
        Delegates control to GameLoop subclasses.
        """
        while self.state != GameState.quitting:
            if self.state == GameState.main_menu:
                self.game_menu.loop()

            elif self.state == GameState.playing:
                self.game_playing.loop()

        pygame.quit()


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":
    game = TowerGame()
    game.init()
    game.loop()
