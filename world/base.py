import pygame
from settings import SCALE, screen
from utils.draw import hp_bar


# ================== SPRITE LOADER ==================
def load_sprite_row(path: str, columns: int):
    """
    Laadt een spritesheet met 1 rij en `columns` frames.
    """
    sheet = pygame.image.load(path).convert_alpha()
    w, h = sheet.get_size()
    frame_w = w // columns

    frames = []
    for i in range(columns):
        rect = pygame.Rect(i * frame_w, 0, frame_w, h)
        frames.append(sheet.subsurface(rect).copy())
    return frames


# ================== SPRITES ==================
PHONE_FRAMES = load_sprite_row("assets/images/Phone.png", 10)


class Base:
    def __init__(self, x, y):
        self.x = x
        self.y = y

        self.max_hp = 100
        self.hp = self.max_hp

        # --- animatie zoals je towers ---
        self.idle_frames = PHONE_FRAMES
        self.anim_index = 0.0
        self.anim_speed = 0.10   # hoger = sneller (probeer 0.12 - 0.30)
        self.sprite_scale = 0.40  # pas aan naar smaak

    def take_damage(self, dmg):
        self.hp -= dmg
        if self.hp < 0:
            self.hp = 0

    def is_destroyed(self):
        return self.hp <= 0

    def draw(self):
        # kies frames (alleen idle in dit geval)
        frames = self.idle_frames

        # animatie “tick” zoals in TowerBase.draw_base()
        self.anim_index = (self.anim_index + self.anim_speed) % len(frames)
        frame = frames[int(self.anim_index)]

        # schalen zoals je towers
        scale = self.sprite_scale * SCALE
        sprite = pygame.transform.scale(
            frame,
            (int(frame.get_width() * scale), int(frame.get_height() * scale))
        )

        rect = sprite.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(sprite, rect)

        # hp bar erboven
        hp_bar(
            int(self.x),
            int(self.y - rect.height / 2 + 15), # Offset nr benede
            self.hp,
            self.max_hp,
            max(70, int(95 * SCALE)),
            h=max(6, int(8 * SCALE))
        )
