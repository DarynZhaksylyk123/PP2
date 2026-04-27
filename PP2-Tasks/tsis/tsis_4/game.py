import pygame
import random

from colors import *
from config import (
    WIDTH, HEIGHT, CELL, COLS, ROWS,
    FOOD_LIFETIME_MS, FOOD_TYPES, FOOD_WEIGHT_POOL,
    POWERUP_FIELD_MS, POWERUP_EFFECT_MS, POWERUP_SPAWN_INTERVAL_MS,
    BASE_FPS, OBSTACLES_FROM_LVL, OBSTACLES_PER_LVL, FOOD_PER_LEVEL,
)

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y


class Snake:
    def __init__(self, settings: dict):
        self.body        = [Point(10, 11), Point(10, 12), Point(10, 13)]
        self.dx          = 1
        self.dy          = 0
        self.score       = 0
        self.level       = 1
        self.alive       = True
        self.foods_eaten = 0

        self.head_color  = tuple(settings.get("head_color",  [220, 50,  50]))
        self.body_color  = tuple(settings.get("snake_color", [50, 200,  50]))

        self.shield_active    = False
        self.shield_used      = False

        self.speed_effect      = None
        self.speed_effect_end  = 0

    def handle_key(self, key):
        if key == pygame.K_RIGHT and self.dx != -1:
            self.dx, self.dy = 1, 0
        elif key == pygame.K_LEFT and self.dx != 1:
            self.dx, self.dy = -1, 0
        elif key == pygame.K_DOWN and self.dy != -1:
            self.dx, self.dy = 0, 1
        elif key == pygame.K_UP and self.dy != 1:
            self.dx, self.dy = 0, -1

    def move(self, obstacles: list):
        for i in range(len(self.body) - 1, 0, -1):
            self.body[i].x = self.body[i - 1].x
            self.body[i].y = self.body[i - 1].y
        self.body[0].x += self.dx
        self.body[0].y += self.dy

        head = self.body[0]

        wall_hit = (
            head.x >= COLS or head.x < 0 or
            head.y >= ROWS or head.y < 0
        )

        self_hit = any(
            head.x == s.x and head.y == s.y
            for s in self.body[1:]
        )

        obs_hit = any(
            head.x == o.x and head.y == o.y
            for o in obstacles
        )

        if wall_hit or self_hit or obs_hit:
            if self.shield_active and not self.shield_used:
                self.shield_used = True
                self.shield_active = False
                head.x = max(0, min(COLS - 1, head.x))
                head.y = max(0, min(ROWS - 1, head.y))
            else:
                self.alive = False

    def grow(self, amount=1):
        tail = self.body[-1]
        for _ in range(amount):
            self.body.append(Point(tail.x, tail.y))

    def shorten(self, amount=2):
        for _ in range(amount):
            if len(self.body) > 1:
                self.body.pop()
        return len(self.body) > 1

    def current_fps(self) -> int:
        now = pygame.time.get_ticks()
        if self.speed_effect and now < self.speed_effect_end:
            if self.speed_effect == "boost":
                return (BASE_FPS + self.level) * 2
            if self.speed_effect == "slow":
                return max(2, (BASE_FPS + self.level) // 2)
        else:
            self.speed_effect = None  
        return BASE_FPS + self.level

    def apply_powerup(self, kind: str):
        now = pygame.time.get_ticks()
        if kind == "boost":
            self.speed_effect     = "boost"
            self.speed_effect_end = now + POWERUP_EFFECT_MS
        elif kind == "slow":
            self.speed_effect     = "slow"
            self.speed_effect_end = now + POWERUP_EFFECT_MS
        elif kind == "shield":
            self.shield_active = True
            self.shield_used   = False

    def draw(self, surface):
        head = self.body[0]
        if self.shield_active:
            pygame.draw.rect(surface, colorCYAN,
                             (head.x * CELL - 2, head.y * CELL - 2,
                              CELL + 4, CELL + 4))
        pygame.draw.rect(surface, self.head_color,
                         (head.x * CELL, head.y * CELL, CELL, CELL))
        for seg in self.body[1:]:
            pygame.draw.rect(surface, self.body_color,
                             (seg.x * CELL, seg.y * CELL, CELL, CELL))


class Food:
    def __init__(self, snake_body, obstacles):
        self.pos        = Point(0, 0)
        self.weight     = 1
        self.color      = colorGREEN
        self.score_val  = 1
        self.spawn_time = 0
        self.respawn(snake_body, obstacles)

    def respawn(self, snake_body, obstacles):
        self.weight     = random.choice(FOOD_WEIGHT_POOL)
        info            = FOOD_TYPES[self.weight]
        self.color      = info["color"]
        self.score_val  = info["score"]
        self.spawn_time = pygame.time.get_ticks()
        self._place(snake_body, obstacles)

    def _place(self, snake_body, obstacles):
        occupied = {(s.x, s.y) for s in snake_body} | {(o.x, o.y) for o in obstacles}
        while True:
            x = random.randint(0, COLS - 1)
            y = random.randint(1, ROWS - 1)
            if (x, y) not in occupied:
                self.pos.x, self.pos.y = x, y
                break

    def is_expired(self):
        return pygame.time.get_ticks() - self.spawn_time >= FOOD_LIFETIME_MS

    def time_left_ratio(self):
        elapsed = pygame.time.get_ticks() - self.spawn_time
        return max(0.0, 1.0 - elapsed / FOOD_LIFETIME_MS)

    def draw(self, surface):
        x, y = self.pos.x * CELL, self.pos.y * CELL
        ratio = self.time_left_ratio()
        r, g, b = self.color
        faded = (int(r * ratio), int(g * ratio), int(b * ratio))
        pygame.draw.rect(surface, faded, (x, y, CELL, CELL))
        lbl = pygame.font.SysFont(None, 20).render(
            str(self.score_val), True, colorWHITE)
        surface.blit(lbl, (x + 4, y + 6))


class PoisonFood:
    LIFETIME_MS = 6000

    def __init__(self, snake_body, obstacles):
        self.pos        = Point(0, 0)
        self.spawn_time = pygame.time.get_ticks()
        self.active     = True
        self._place(snake_body, obstacles)

    def _place(self, snake_body, obstacles):
        occupied = {(s.x, s.y) for s in snake_body} | {(o.x, o.y) for o in obstacles}
        while True:
            x = random.randint(0, COLS - 1)
            y = random.randint(1, ROWS - 1)
            if (x, y) not in occupied:
                self.pos.x, self.pos.y = x, y
                break

    def is_expired(self):
        return pygame.time.get_ticks() - self.spawn_time >= self.LIFETIME_MS

    def draw(self, surface):
        if not self.active:
            return
        x, y = self.pos.x * CELL, self.pos.y * CELL
        pygame.draw.rect(surface, colorDARKRED, (x, y, CELL, CELL))
        lbl = pygame.font.SysFont(None, 20).render("☠", True, colorWHITE)
        surface.blit(lbl, (x + 4, y + 5))


POWERUP_KINDS = ["boost", "slow", "shield"]
POWERUP_COLORS = {
    "boost":  colorGOLD,
    "slow":   colorBLUE,
    "shield": colorCYAN,
}
POWERUP_LABELS = {
    "boost":  "⚡",
    "slow":   "❄",
    "shield": "🛡",
}


class PowerUp:
    def __init__(self, snake_body, obstacles, existing_pos=None):
        self.kind       = random.choice(POWERUP_KINDS)
        self.pos        = Point(0, 0)
        self.spawn_time = pygame.time.get_ticks()
        self.active     = True
        self._place(snake_body, obstacles, existing_pos)

    def _place(self, snake_body, obstacles, existing_pos):
        occupied = (
            {(s.x, s.y) for s in snake_body}
            | {(o.x, o.y) for o in obstacles}
        )
        if existing_pos:
            occupied.add((existing_pos.x, existing_pos.y))
        while True:
            x = random.randint(0, COLS - 1)
            y = random.randint(1, ROWS - 1)
            if (x, y) not in occupied:
                self.pos.x, self.pos.y = x, y
                break

    def is_expired(self):
        return pygame.time.get_ticks() - self.spawn_time >= POWERUP_FIELD_MS

    def time_left_ratio(self):
        elapsed = pygame.time.get_ticks() - self.spawn_time
        return max(0.0, 1.0 - elapsed / POWERUP_FIELD_MS)

    def draw(self, surface):
        if not self.active:
            return
        x, y = self.pos.x * CELL, self.pos.y * CELL
        ratio = self.time_left_ratio()
        r, g, b = POWERUP_COLORS[self.kind]
        faded = (int(r * ratio + 30), int(g * ratio + 30), int(b * ratio + 30))
        pygame.draw.rect(surface, faded, (x, y, CELL, CELL))
        lbl = pygame.font.SysFont(None, 22).render(
            POWERUP_LABELS[self.kind], True, colorWHITE)
        surface.blit(lbl, (x + 3, y + 5))


def generate_obstacles(level: int, snake_body: list, existing: list) -> list:
    occupied = (
        {(s.x, s.y) for s in snake_body}
        | {(o.x, o.y) for o in existing}
    )
    head = snake_body[0]
    safe = {(head.x + dx, head.y + dy)
            for dx in range(-3, 4)
            for dy in range(-3, 4)}
    occupied |= safe

    new_blocks = []
    attempts   = 0
    while len(new_blocks) < OBSTACLES_PER_LVL and attempts < 500:
        attempts += 1
        x = random.randint(1, COLS - 2)
        y = random.randint(2, ROWS - 2)
        if (x, y) not in occupied:
            occupied.add((x, y))
            new_blocks.append(Point(x, y))

    return existing + new_blocks


def draw_obstacles(surface, obstacles: list):
    for o in obstacles:
        pygame.draw.rect(surface, colorLGRAY,
                         (o.x * CELL, o.y * CELL, CELL, CELL))
        pygame.draw.rect(surface, colorDARK,
                         (o.x * CELL, o.y * CELL, CELL, CELL), 2)