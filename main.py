import asyncio
import pygame
from ui.screens import start_screen
from world.level import Level, run_level


async def main():
    pygame.init()
    pygame.mixer.init()

    running = True
    while running:
        level_number = start_screen()
        if level_number is None:
            running = False
            break

        level = Level(level_number)
        run_level(level)

        # ✔ verplicht asyncio-punt (zonder gameplay te breken)
        await asyncio.sleep(0)

    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main())