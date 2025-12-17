import pygame
from ui.screens import start_screen
from world.level import Level, run_level
pygame.init()

while True:
    level_number = start_screen()
    current_level = Level(level_number)
    run_level(current_level)
pygame.quit()