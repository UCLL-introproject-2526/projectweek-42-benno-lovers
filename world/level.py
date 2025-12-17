import pygame
import math
import random

# World
from world.maps import level_paths, level_base, level_wave_map, level_backgrounds
from world.base import Base

# Towers
from towers.towers import Tower, SniperTower, SlowTower, PoisonTower

# Enemies
from enemies.enemy_types import Enemy, FastEnemy

# Projectiles
from projectiles.bullet import Bullet  # alleen nodig als je Bullet direct gebruikt

# Utils
from utils.placement import is_on_any_path, too_close_to_tower, tower_at_pos, same_tower_type
from utils.draw import draw_path, draw_enemy_path_preview

# UI
from ui.hud import draw_hud
from ui.overlay import draw_overlay, start_overlay, preview_stats_for_type, tower_type_name


# Settings / Constants
from settings import (
    DEV_INFINITE_MONEY, FPS, BG_COLOR, clock, screen,
    SELL_REFUND, SNIPER_TOWER_COST, SLOW_TOWER_COST, POISON_TOWER_COST,
    TOWER_COST, PATH_WIDTH, SCALE, WIDTH, HEIGHT,
    SMALL_FONT, FONT, BIG_FONT
)

# Settings / Constants
from settings import (
    DEV_INFINITE_MONEY, FPS, BG_COLOR, clock, screen,
    SELL_REFUND, SNIPER_TOWER_COST, SLOW_TOWER_COST, POISON_TOWER_COST,
    TOWER_COST, PATH_WIDTH, SCALE, WIDTH, HEIGHT,
    SMALL_FONT, FONT, BIG_FONT
)
class Level:
    def __init__(self, level_id):
                # Achtergrond instellen via dict
        bg_path = level_backgrounds.get(level_id)
        if bg_path:
            self.bg_image = pygame.image.load(bg_path).convert()
            self.bg_image = pygame.transform.scale(self.bg_image, (WIDTH, HEIGHT))
        else:
            self.bg_image = None
        self.level = level_id

        self.paths = level_paths[level_id]
        self.base = Base(*level_base[level_id])

        self.max_waves = level_wave_map[level_id]
        self.current_wave = 0

        self.enemies = []
        self.towers = []

        self.finished = False
    def update(self, dt):
        for enemy in self.enemies[:]:
            enemy.update(dt)

            if enemy.reached_base:
                self.base.take_damage(enemy.damage)
                self.enemies.remove(enemy)

        if self.base.is_destroyed():
            self.finished = True
    def can_place_tower(self, x, y):
        if is_on_any_path(self.level, x, y, level_paths):
            return False
        if too_close_to_tower(self.towers, x, y):
            return False
        return True
    def draw(self, surface):
        """Tekent het volledige level: achtergrond, paths, towers, enemies en base."""

        # --- Achtergrond ---
        if hasattr(self, "bg_image") and self.bg_image:
            surface.blit(self.bg_image, (0, 0))
        else:
            surface.fill(BG_COLOR)  # fallback kleur

        # --- Paths ---
        for path in self.paths:
            draw_path(surface, path, PATH_WIDTH)

        # --- Towers ---
        for tower in self.towers:
            # Als je je towers een .draw_base(enemies) methode hebt voor firing animatie
            if hasattr(tower, "draw_base"):
                tower.draw_base(self.enemies)
            else:
                tower.draw(surface)

        # --- Enemies ---
        for enemy in self.enemies:
            enemy.draw(surface)

        # --- Base ---
        # self.base.draw(surface)


# ================== LEVEL LOOP ==================
def run_level(level: Level):
        # --- LEVEL MUZIEK ---
    pygame.mixer.music.load("assets\\music\\SpotiDown.App - Mother North - Satyricon.mp3")
    pygame.mixer.music.set_volume(1)
    pygame.mixer.music.play(-1)

    paths = level_paths[level.level]
    base = Base(*level_base[level.level])

    enemies = []
    towers = []
    bullets = []

    money = 99999999 if DEV_INFINITE_MONEY else 140
    score = 0
    game_over = False

    max_waves = level_wave_map.get(level.level, 5)
    wave = 1

    wave_started = False
    spawn_timer = 0
    spawn_interval = max(18, int(42 * (60 / FPS)))
    enemies_spawned = 0
    enemies_per_wave = 6
    inter_wave_pause = int(1.8 * FPS)
    between_waves = 0

    def is_boss_wave(w):
        return w % 5 == 0

    boss_spawned = False

    # selection + merge
    selected = None
    dragged = None
    drag_origin = None

    # placement preview state (CLICK-HOLD)
    placing_preview = False
    placing_type = None
    placing_cost = 0

    tick = 0  # voor moving path preview

    running = True
    while running:
        clock.tick(FPS)
        screen.fill(BG_COLOR)
        mx, my = pygame.mouse.get_pos()
        keys = pygame.key.get_pressed()
        tick += 1
        level.draw(screen)
        # ------------------ EVENTS ------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.mixer.music.stop()
                return None
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.mixer.music.stop()
                return None

            if event.type == pygame.KEYDOWN and not game_over:
                # sell
                if event.key == pygame.K_x and selected and selected in towers:
                    if not DEV_INFINITE_MONEY:
                        money += int(selected.total_value * SELL_REFUND)
                    towers.remove(selected)
                    selected = None

                # targeting
                if event.key == pygame.K_t and selected and selected in towers:
                    selected.cycle_target_mode()

            if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                if event.button == 1:
                    # klik op tower = drag voor merge
                    t = tower_at_pos(towers, mx, my)
                    if t:
                        selected = t
                        dragged = t
                        drag_origin = (t.x, t.y)
                        t.dragging = True
                        placing_preview = False
                        placing_type = None
                        placing_cost = 0
                    else:
                        # placement preview start
                        selected = None

                        placing_type = selected

                        if placing_type == "SNIPER":
                         placing_cost = SNIPER_TOWER_COST
                        elif placing_type == "SLOW":
                         placing_cost = SLOW_TOWER_COST
                        elif placing_type == "POISON":
                         placing_cost = POISON_TOWER_COST
                        else:
                         placing_cost = TOWER_COST

                        if DEV_INFINITE_MONEY or money >= placing_cost:
                            placing_preview = True
                        else:
                            placing_preview = False
                            placing_type = None
                            placing_cost = 0

            if event.type == pygame.MOUSEBUTTONUP and not game_over:
                if event.button == 1:
                    # ------------------ PLACE ON RELEASE ------------------
                    if placing_preview:
                        valid = (
                            not is_on_any_path(level, mx, my)
                            and not too_close_to_tower(towers, mx, my)
                        )

                        if valid:
                            if placing_type == "SNIPER":
                                towers.append(SniperTower(mx, my))
                            elif placing_type == "SLOW":
                                towers.append(SlowTower(mx, my))
                            elif placing_type == "POISON":
                                towers.append(PoisonTower(mx, my))
                            else:
                                towers.append(Tower(mx, my))

                            if not DEV_INFINITE_MONEY:
                                money -= placing_cost

                        # reset placement state
                        placing_preview = False
                        placing_type = None
                        placing_cost = 0

                    # ------------------ MERGE ON RELEASE ------------------
                    if dragged:
                        merged = False
                        for t in towers:
                            if t is dragged:
                                continue
                            if same_tower_type(t, dragged) and t.level == dragged.level and t.can_upgrade():
                                if math.hypot(t.x - dragged.x, t.y - dragged.y) <= max(26, int(30 * SCALE)):
                                    if t.upgrade_stats_one_level():
                                        t.total_value += dragged.total_value
                                        towers.remove(dragged)
                                        merged = True
                                    break

                        if not merged and drag_origin:
                            dragged.x, dragged.y = drag_origin  # snap back

                        if dragged in towers:
                            dragged.dragging = False

                        dragged = None
                        drag_origin = None

        # drag follow mouse (visual only) — snaps back if not merged
        if dragged and not game_over:
            dragged.x, dragged.y = mx, my

        # ------------------ WAVES / SPAWN ------------------
        if not game_over and wave <= max_waves:
            if between_waves > 0:
                between_waves -= 1
            else:
                if not wave_started:
                    boss_spawned = False
                    start_overlay(f"Wave {wave} starting!", (255, 255, 0), 1.2)
                    wave_started = True

                spawn_timer += 1

                if enemies_spawned < enemies_per_wave and spawn_timer >= spawn_interval:
                    spawn_timer = 0
                    path_to_use = paths[(wave + enemies_spawned) % len(paths)]

                    r = random.random()
                    if r < 0.25:
                        e = FastEnemy(path_to_use)
                    elif r < 0.65:
                        e = Enemy(path_to_use, strong=False)
                    else:
                        e = Enemy(path_to_use, strong=True)

                    # scale by wave + level
                    level_boost = (level.level - 1) * 0.12
                    e.max_hp = int(e.max_hp * (1.0 + 0.22 * (wave - 1) + level_boost))
                    e.hp = e.max_hp
                    e.damage = int(e.damage * (1.0 + 0.12 * (wave - 1) + level_boost))
                    e.base_speed = e.base_speed * (1.0 + 0.03 * (wave - 1))
                    enemies.append(e)

                    enemies_spawned += 1

                # boss wave
                if is_boss_wave(wave) and enemies_spawned >= enemies_per_wave and not boss_spawned:
                    if spawn_timer >= int(0.9 * FPS):
                        path_to_use = paths[wave % len(paths)]
                        b = Enemy(path_to_use, boss=True)

                        level_boost = (level.level - 1) * 0.25
                        b.max_hp = int(b.max_hp * (1.0 + 0.35 * (wave - 1) + level_boost))
                        b.hp = b.max_hp
                        b.damage = int(b.damage * (1.0 + 0.10 * (wave - 1) + level_boost))
                        b.base_speed = b.base_speed * (1.0 + 0.02 * (wave - 1))
                        enemies.append(b)

                        boss_spawned = True
                        spawn_timer = 0

                # wave complete
                if enemies_spawned >= enemies_per_wave and len(enemies) == 0 and (not is_boss_wave(wave) or boss_spawned):
                    wave += 1
                    enemies_spawned = 0
                    enemies_per_wave += 2
                    wave_started = False
                    between_waves = inter_wave_pause
                    spawn_timer = 0

                    if wave > max_waves:
                        start_overlay(f"Level {level} Completed!", (0, 255, 0), 2.0)
                        for _ in range(int(1.0 * FPS)):
                            clock.tick(FPS)
                            screen.fill(BG_COLOR)
                            draw_overlay()
                            pygame.display.flip()
                        pygame.mixer.music.stop()
                        return ("MENU", None)

        # ------------------ ENEMIES UPDATE ------------------
        # Belangrijk: Enemy.move() kan "DEAD" teruggeven door poison (DEEL 2 fix).
        for e in enemies[:]:
            res = e.move()

            if res == "DEAD":
                enemies.remove(e)
                continue

            if res is True:  # reached end
                base.take_damage(e.damage)
                enemies.remove(e)
                if base.hp <= 0:
                    game_over = True

        # ------------------ TOWERS SHOOT ------------------
        for t in towers:
            t.shoot(enemies, bullets)

        # ------------------ BULLETS ------------------
        for b in bullets[:]:
            if b.target not in enemies or b.target.hp <= 0:
                bullets.remove(b)
                continue

            b.move()
            if math.hypot(b.x - b.target.x, b.y - b.target.y) < max(10, int(12 * SCALE)):
                b.target.hp -= b.damage

                if b.effect:
                    kind = b.effect[0]
                    if kind == "slow":
                        _, factor, ticks = b.effect
                        b.target.apply_slow(factor, ticks)
                    elif kind == "poison":
                        _, dps, ticks = b.effect
                        b.target.apply_poison(dps, ticks)

                bullets.remove(b)

                if b.target.hp <= 0 and b.target in enemies:
                    enemies.remove(b.target)
                    if not DEV_INFINITE_MONEY:
                        money += b.target.reward_money
                    score += b.target.reward_score

        # ------------------ DRAW ------------------
        for p in paths:
            draw_path(screen, p, PATH_WIDTH)

        base.draw()

        for e in enemies:
            e.draw()

        for t in towers:
            t.draw_base(enemies)

        # ------------------ PLACEMENT PREVIEW ------------------
        if placing_preview and placing_type:
            # bewegende path preview (cirkels volgen pad)
            draw_enemy_path_preview(paths, tick)

            color, rng = preview_stats_for_type(placing_type)
            valid = (not is_on_any_path(level, mx, my)) and (not too_close_to_tower(towers, mx, my))
            ghost_col = color if valid else (220, 80, 80)

            pygame.draw.circle(screen, ghost_col, (mx, my), max(12, int(18 * SCALE)), 2)
            pygame.draw.circle(screen, (255, 255, 255), (mx, my), rng, 1)

            tip = SMALL_FONT.render("Hold LMB... release to place", True, (230, 230, 230))
            screen.blit(tip, (mx + 18, my + 18))

        # ------------------ HOVER/SELECT INFO ------------------
        hovered = tower_at_pos(towers, mx, my)
        info_target = hovered if hovered else selected
        if info_target and info_target in towers:
            pygame.draw.circle(
                screen,
                (255, 255, 255),
                (int(info_target.x), int(info_target.y)),
                int(info_target.range),
                1
            )

            ttype = tower_type_name(info_target)
            lvl = f"{info_target.level}/{info_target.max_level}"
            val = info_target.total_value
            sell = int(val * SELL_REFUND)

            lines = [
                f"{ttype}  Lv {lvl}",
                f"Target: {info_target.target_mode} (T)",
                f"DMG: {getattr(info_target, 'damage', 0)} | Rate: {getattr(info_target, 'fire_rate', 0)}",
                f"Range: {int(getattr(info_target, 'range', 0))}",
                f"Value: {val}$ | Sell (X): {sell}$"
            ]

            renders = [SMALL_FONT.render(s, True, (255, 255, 255)) for s in lines]
            box_w = max(r.get_width() for r in renders)
            pad = 10
            box_h = len(renders) * (SMALL_FONT.get_height() + 4) + pad

            box_x = min(WIDTH - (box_w + 2 * pad) - 10, int(info_target.x + 25))
            box_y = max(10, int(info_target.y - box_h - 15))

            pygame.draw.rect(screen, (15, 15, 15), (box_x, box_y, box_w + 2 * pad, box_h), border_radius=8)
            pygame.draw.rect(screen, (70, 70, 70), (box_x, box_y, box_w + 2 * pad, box_h), 2, border_radius=8)

            yy = box_y + 6
            for r in renders:
                screen.blit(r, (box_x + pad, yy))
                yy += r.get_height() + 4

        if selected and selected in towers:
            pygame.draw.circle(
                screen,
                (255, 255, 255),
                (int(selected.x), int(selected.y)),
                max(22, int((26 + selected.level) * SCALE)),
                2
            )

        for b in bullets:
            b.draw()

        draw_hud(money, score, base.hp, wave, max_waves)
        draw_overlay()

        if game_over:
            text = BIG_FONT.render("GAME OVER", True, (255, 0, 0))
            sub = FONT.render("ESC = Menu", True, (255, 200, 200))
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height()))
            screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, HEIGHT // 2 + 10))

        pygame.display.flip()