import pygame
import json
import os
import sys

from colors  import *
from config  import WIDTH, HEIGHT, CELL, COLS, ROWS, OBSTACLES_FROM_LVL, FOOD_PER_LEVEL, POWERUP_SPAWN_INTERVAL_MS
from game    import (Snake, Food, PoisonFood, PowerUp,
                     generate_obstacles, draw_obstacles, Point)
import db as DB

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake TSIS4")

font_big   = pygame.font.SysFont(None, 52)
font_mid   = pygame.font.SysFont(None, 36)
font_small = pygame.font.SysFont(None, 26)
font_tiny  = pygame.font.SysFont(None, 20)

SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "settings.json")

def load_settings() -> dict:
    defaults = {
        "snake_color": [50, 200, 50],
        "head_color":  [220, 50,  50],
        "grid":        True,
        "sound":       False,
    }
    try:
        with open(SETTINGS_FILE) as f:
            data = json.load(f)
        defaults.update(data)
    except Exception:
        pass
    return defaults

def save_settings(s: dict):
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(s, f, indent=4)
    except Exception as e:
        print(f"[settings] save error: {e}")

def draw_grid(surface):
    for row in range(ROWS):
        for col in range(COLS):
            pygame.draw.rect(surface, colorGRAY,
                             (col * CELL, row * CELL, CELL, CELL), 1)

def draw_text(surface, text, font, color, cx, cy):
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(cx, cy))
    surface.blit(surf, rect)

def draw_button(surface, text, rect, hover=False):
    col = colorLGRAY if hover else (50, 50, 50)
    pygame.draw.rect(surface, col, rect, border_radius=8)
    pygame.draw.rect(surface, colorWHITE, rect, 2, border_radius=8)
    draw_text(surface, text, font_mid, colorWHITE, rect.centerx, rect.centery)

def mouse_over(rect):
    return rect.collidepoint(pygame.mouse.get_pos())

def draw_hud(surface, snake, personal_best, powerup):
    pygame.draw.rect(surface, colorDARK, (0, 0, WIDTH, CELL))
    surface.blit(font_small.render(f"Score:{snake.score}", True, colorWHITE), (4, 4))
    surface.blit(font_small.render(f"Lvl:{snake.level}", True, colorWHITE), (130, 4))
    surface.blit(font_small.render(f"Best:{personal_best}", True, colorGOLD), (210, 4))

    effect_str = ""
    if snake.speed_effect:
        remain = max(0, (snake.speed_effect_end - pygame.time.get_ticks()) // 1000)
        icon   = "⚡" if snake.speed_effect == "boost" else "❄"
        effect_str = f"{icon}{remain}s"
    if snake.shield_active:
        effect_str += "🛡"
    if effect_str:
        surface.blit(font_small.render(effect_str, True, colorCYAN), (340, 4))

    if powerup:
        remain = max(0, (powerup.spawn_time + 8000 - pygame.time.get_ticks()) // 1000)
        surface.blit(font_tiny.render(f"PU:{remain}s", True, colorGOLD), (450, 6))

def screen_main_menu() -> tuple:
    username     = ""
    input_active = True
    clock        = pygame.time.Clock()

    btn_play  = pygame.Rect(WIDTH//2 - 110, 280, 220, 50)
    btn_lb    = pygame.Rect(WIDTH//2 - 110, 345, 220, 50)
    btn_sett  = pygame.Rect(WIDTH//2 - 110, 410, 220, 50)
    btn_quit  = pygame.Rect(WIDTH//2 - 110, 475, 220, 50)

    while True:
        clock.tick(30)
        screen.fill(colorBLACK)

        draw_text(screen, "🐍 SNAKE", font_big, colorGREEN, WIDTH//2, 80)
        draw_text(screen, "TSIS 4", font_mid, colorLGRAY, WIDTH//2, 130)

        draw_text(screen, "Enter username:", font_small, colorWHITE, WIDTH//2, 190)
        inp_rect = pygame.Rect(WIDTH//2 - 120, 208, 240, 38)
        pygame.draw.rect(screen, (30, 30, 30), inp_rect)
        border_col = colorCYAN if input_active else colorLGRAY
        pygame.draw.rect(screen, border_col, inp_rect, 2, border_radius=4)
        uname_surf = font_mid.render(username + ("|" if input_active else ""), True, colorWHITE)
        screen.blit(uname_surf, (inp_rect.x + 8, inp_rect.y + 5))

        for btn, label in [(btn_play, "▶  Play"),
                           (btn_lb,   "🏆  Leaderboard"),
                           (btn_sett, "⚙  Settings"),
                           (btn_quit, "✕  Quit")]:
            draw_button(screen, label, btn, mouse_over(btn))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return ("quit", username)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_play.collidepoint(event.pos):
                    if username.strip():
                        return ("play", username.strip())
                elif btn_lb.collidepoint(event.pos):
                    return ("leaderboard", username.strip())
                elif btn_sett.collidepoint(event.pos):
                    return ("settings", username.strip())
                elif btn_quit.collidepoint(event.pos):
                    return ("quit", username.strip())
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                elif event.key == pygame.K_RETURN:
                    if username.strip():
                        return ("play", username.strip())
                else:
                    if len(username) < 20:
                        username += event.unicode

def screen_game(username: str, settings: dict, personal_best: int) -> dict:
    clock     = pygame.time.Clock()
    snake     = Snake(settings)
    obstacles = []
    food      = Food(snake.body, obstacles)

    poison    = None
    powerup   = None
    next_powerup_time = pygame.time.get_ticks() + POWERUP_SPAWN_INTERVAL_MS

    prev_level = snake.level

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return {"score": snake.score, "level": snake.level, "action": "quit"}
            if event.type == pygame.KEYDOWN:
                snake.handle_key(event.key)

        snake.move(obstacles)

        if not snake.alive:
            return {"score": snake.score, "level": snake.level, "action": "dead"}

        if food.pos == snake.body[0]:
            snake.score       += food.score_val
            snake.foods_eaten += 1
            snake.grow(food.score_val)
            new_level = 1 + snake.foods_eaten // FOOD_PER_LEVEL
            if new_level > snake.level:
                snake.level = new_level
            food.respawn(snake.body, obstacles)

            if poison is None and __import__("random").random() < 0.3:
                poison = PoisonFood(snake.body, obstacles)
        elif food.is_expired():
            food.respawn(snake.body, obstacles)

        if poison and poison.active:
            if poison.pos == snake.body[0]:
                if not snake.shorten(2):
                    snake.alive = False
                    return {"score": snake.score, "level": snake.level, "action": "dead"}
                poison = None
            elif poison.is_expired():
                poison = None

        now = pygame.time.get_ticks()
        if powerup is None and now >= next_powerup_time:
            powerup           = PowerUp(snake.body, obstacles,
                                        existing_pos=food.pos)
            next_powerup_time = now + POWERUP_SPAWN_INTERVAL_MS

        if powerup and powerup.active:
            if powerup.pos == snake.body[0]:
                snake.apply_powerup(powerup.kind)
                powerup           = None
                next_powerup_time = pygame.time.get_ticks() + POWERUP_SPAWN_INTERVAL_MS
            elif powerup.is_expired():
                powerup           = None
                next_powerup_time = pygame.time.get_ticks() + POWERUP_SPAWN_INTERVAL_MS

        if snake.level != prev_level:
            prev_level = snake.level
            if snake.level >= OBSTACLES_FROM_LVL:
                obstacles = generate_obstacles(snake.level, snake.body, obstacles)

        screen.fill(colorBLACK)
        if settings.get("grid", True):
            draw_grid(screen)

        draw_obstacles(screen, obstacles)
        food.draw(screen)
        if poison and poison.active:
            poison.draw(screen)
        if powerup and powerup.active:
            powerup.draw(screen)
        snake.draw(screen)
        draw_hud(screen, snake, personal_best, powerup)

        pygame.display.flip()
        clock.tick(snake.current_fps())

def screen_game_over(score: int, level: int, personal_best: int) -> str:
    clock    = pygame.time.Clock()
    btn_retry = pygame.Rect(WIDTH//2 - 110, 370, 210, 50)
    btn_menu  = pygame.Rect(WIDTH//2 - 110, 435, 210, 50)

    while True:
        clock.tick(30)
        screen.fill(colorBLACK)

        draw_text(screen, "GAME OVER", font_big, colorRED, WIDTH//2, 160)
        draw_text(screen, f"Score: {score}", font_mid, colorWHITE, WIDTH//2, 240)
        draw_text(screen, f"Level: {level}", font_mid, colorWHITE, WIDTH//2, 285)
        draw_text(screen, f"Personal Best: {personal_best}", font_mid, colorGOLD, WIDTH//2, 330)

        draw_button(screen, "↺  Retry",     btn_retry, mouse_over(btn_retry))
        draw_button(screen, "⌂  Main Menu", btn_menu,  mouse_over(btn_menu))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_retry.collidepoint(event.pos):
                    return "retry"
                if btn_menu.collidepoint(event.pos):
                    return "menu"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return "retry"
                if event.key == pygame.K_m:
                    return "menu"
                if event.key == pygame.K_q:
                    return "quit"

def screen_leaderboard():
    clock    = pygame.time.Clock()
    btn_back = pygame.Rect(WIDTH//2 - 80, HEIGHT - 70, 160, 45)
    rows     = DB.get_top10()

    while True:
        clock.tick(30)
        screen.fill(colorBLACK)

        draw_text(screen, "🏆 LEADERBOARD", font_big, colorGOLD, WIDTH//2, 45)

        if not rows:
            draw_text(screen, "No data (DB not connected)", font_mid, colorLGRAY, WIDTH//2, HEIGHT//2)
        else:
            headers = ["#", "Player", "Score", "Lvl", "Date"]
            col_x   = [30, 80, 310, 390, 450]
            col_w   = 60
            for hdr, cx in zip(headers, col_x):
                surf = font_small.render(hdr, True, colorGOLD)
                screen.blit(surf, (cx, 90))
            pygame.draw.line(screen, colorLGRAY, (20, 112), (WIDTH - 20, 112), 1)

            for i, row in enumerate(rows):
                y   = 118 + i * 26
                date_str = str(row.get("played_at", ""))[:10]
                values = [
                    str(i + 1),
                    row.get("username", "?")[:14],
                    str(row.get("score", 0)),
                    str(row.get("level_reached", 0)),
                    date_str,
                ]
                color = colorGOLD if i == 0 else colorWHITE
                for val, cx in zip(values, col_x):
                    surf = font_small.render(val, True, color)
                    screen.blit(surf, (cx, y))

        draw_button(screen, "← Back", btn_back, mouse_over(btn_back))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_back.collidepoint(event.pos):
                    return
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                    return

SNAKE_COLOR_OPTIONS = [
    ("Green",  [50,  200, 50]),
    ("Blue",   [50,  100, 220]),
    ("Cyan",   [0,   200, 220]),
    ("Purple", [160, 50,  220]),
    ("White",  [220, 220, 220]),
]

def screen_settings(settings: dict) -> dict:
    clock    = pygame.time.Clock()
    btn_save = pygame.Rect(WIDTH//2 - 100, HEIGHT - 80, 200, 50)

    color_idx = 0
    for i, (name, rgb) in enumerate(SNAKE_COLOR_OPTIONS):
        if rgb == list(settings.get("snake_color", [50, 200, 50])):
            color_idx = i
            break

    while True:
        clock.tick(30)
        screen.fill(colorBLACK)

        draw_text(screen, "⚙ SETTINGS", font_big, colorWHITE, WIDTH//2, 50)

        draw_text(screen, "Grid overlay:", font_mid, colorWHITE, WIDTH//2 - 80, 160)
        grid_btn = pygame.Rect(WIDTH//2 + 70, 143, 110, 36)
        grid_on  = settings.get("grid", True)
        draw_button(screen, "ON" if grid_on else "OFF", grid_btn, mouse_over(grid_btn))

        draw_text(screen, "Sound:", font_mid, colorWHITE, WIDTH//2 - 110, 220)
        snd_btn = pygame.Rect(WIDTH//2 + 70, 203, 110, 36)
        snd_on  = settings.get("sound", False)
        draw_button(screen, "ON" if snd_on else "OFF", snd_btn, mouse_over(snd_btn))

        draw_text(screen, "Snake color:", font_mid, colorWHITE, WIDTH//2 - 80, 290)
        name, rgb = SNAKE_COLOR_OPTIONS[color_idx]
        prev_btn = pygame.Rect(WIDTH//2 - 10, 273, 36, 36)
        next_btn = pygame.Rect(WIDTH//2 + 170, 273, 36, 36)
        draw_button(screen, "<", prev_btn, mouse_over(prev_btn))
        draw_button(screen, ">", next_btn, mouse_over(next_btn))
        pygame.draw.rect(screen, tuple(rgb), (WIDTH//2 + 28, 273, 140, 36), border_radius=6)
        draw_text(screen, name, font_small, colorBLACK, WIDTH//2 + 98, 291)

        draw_button(screen, "💾  Save & Back", btn_save, mouse_over(btn_save))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return settings
            if event.type == pygame.MOUSEBUTTONDOWN:
                if grid_btn.collidepoint(event.pos):
                    settings["grid"] = not settings.get("grid", True)
                elif snd_btn.collidepoint(event.pos):
                    settings["sound"] = not settings.get("sound", False)
                elif prev_btn.collidepoint(event.pos):
                    color_idx = (color_idx - 1) % len(SNAKE_COLOR_OPTIONS)
                    settings["snake_color"] = SNAKE_COLOR_OPTIONS[color_idx][1]
                elif next_btn.collidepoint(event.pos):
                    color_idx = (color_idx + 1) % len(SNAKE_COLOR_OPTIONS)
                    settings["snake_color"] = SNAKE_COLOR_OPTIONS[color_idx][1]
                elif btn_save.collidepoint(event.pos):
                    save_settings(settings)
                    return settings
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    save_settings(settings)
                    return settings

def main():
    DB.init_db()
    settings = load_settings()

    username      = ""
    personal_best = 0

    while True:
        action, username = screen_main_menu()

        if action == "quit":
            break
        if action == "leaderboard":
            screen_leaderboard()
            continue
        if action == "settings":
            settings = screen_settings(settings)
            continue

        personal_best = DB.get_personal_best(username)

        while True:
            result = screen_game(username, settings, personal_best)

            score = result["score"]
            level = result["level"]

            DB.save_session(username, score, level)

            if score > personal_best:
                personal_best = score

            if result["action"] == "quit":
                pygame.quit()
                sys.exit()

            go_action = screen_game_over(score, level, personal_best)

            if go_action == "retry":
                continue
            elif go_action == "menu":
                break
            else:
                pygame.quit()
                sys.exit()

if __name__ == "__main__":
    main()
    pygame.quit()