import pygame
import random
from colors import *

pygame.init()

WIDTH  = 600
HEIGHT = 600
CELL   = 30

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake")

font       = pygame.font.SysFont(None, 36)
font_small = pygame.font.SysFont(None, 26)


# FOOD WEIGHT TABLE

FOOD_TYPES = {
    1: {"score": 1, "color": colorGREEN},
    3: {"score": 3, "color": colorORANGE},
    5: {"score": 5, "color": colorPURPLE},
}

FOOD_WEIGHT_POOL = [1, 1, 1, 1, 3, 3, 5]


# GRID

def draw_grid():
    for i in range(HEIGHT // CELL):
        for j in range(WIDTH // CELL):
            if j != 0:
                pygame.draw.rect(screen, colorGRAY, (i * CELL, j * CELL, CELL, CELL), 1)



# POINT

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

# SNAKE

class Snake:
    def __init__(self):
        self.body  = [Point(10, 11), Point(10, 12), Point(10, 13)]
        self.dx    = 1
        self.dy    = 0
        self.score = 0
        self.level = 1
        self.alive = True

    def move(self):
        for i in range(len(self.body) - 1, 0, -1):
            self.body[i].x = self.body[i - 1].x
            self.body[i].y = self.body[i - 1].y
        self.body[0].x += self.dx
        self.body[0].y += self.dy

        if self.body[0].x > WIDTH  // CELL - 1: self.alive = False
        if self.body[0].x < 0:                  self.alive = False
        if self.body[0].y > HEIGHT // CELL - 1: self.alive = False
        if self.body[0].y == 0:                 self.alive = False

        head = self.body[0]
        for segment in self.body[1:]:
            if head.x == segment.x and head.y == segment.y:
                self.alive = False

    def grow(self, amount=1):
        tail = self.body[-1]
        for _ in range(amount):
            self.body.append(Point(tail.x, tail.y))

    def draw(self):
        head = self.body[0]
        pygame.draw.rect(screen, colorRED,
                         (head.x * CELL, head.y * CELL, CELL, CELL))
        for segment in self.body[1:]:
            pygame.draw.rect(screen, colorYELLOW,
                             (segment.x * CELL, segment.y * CELL, CELL, CELL))

    def check_collision(self, food):
        head = self.body[0]
        return head.x == food.pos.x and head.y == food.pos.y



# FOOD

class Food:
    LIFETIME_MS = 5000  # 5 seconds

    def __init__(self, snake_body):
        self.pos        = Point(0, 0)
        self.weight     = random.choice(FOOD_WEIGHT_POOL)
        self.color      = FOOD_TYPES[self.weight]["color"]
        self.score_val  = FOOD_TYPES[self.weight]["score"]
        self.spawn_time = pygame.time.get_ticks()
        self.generate_random_pos(snake_body)

    def respawn(self, snake_body):
        """Move to a new random spot and reset the 5-second timer."""
        self.weight     = random.choice(FOOD_WEIGHT_POOL)
        self.color      = FOOD_TYPES[self.weight]["color"]
        self.score_val  = FOOD_TYPES[self.weight]["score"]
        self.spawn_time = pygame.time.get_ticks()
        self.generate_random_pos(snake_body)

    def is_expired(self):
        return pygame.time.get_ticks() - self.spawn_time >= self.LIFETIME_MS

    def time_left_ratio(self):
        elapsed = pygame.time.get_ticks() - self.spawn_time
        return max(0.0, 1.0 - elapsed / self.LIFETIME_MS)

    def draw(self):
        x = self.pos.x * CELL
        y = self.pos.y * CELL
        
        pygame.draw.rect(screen, self.color, (x, y, CELL, CELL))

    def generate_random_pos(self, snake_body):
        while True:
            self.pos.x = random.randint(0, WIDTH  // CELL - 1)
            self.pos.y = random.randint(1, HEIGHT // CELL - 1)
            if not any(self.pos.x == s.x and self.pos.y == s.y for s in snake_body):
                break



# GAME-OVER SCREEN

def show_game_over(score, level):
    """Show score, offer R to restart or Q to quit. Returns True = restart."""
    go_surf   = font.render("GAME OVER", True, colorRED)
    go_rect   = go_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40))
    stat_surf = font.render(f"Score: {score}   Level: {level}", True, colorWHITE)
    stat_rect = stat_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 10))
    hint_surf = font_small.render("R — restart        Q — quit", True, colorGRAY)
    hint_rect = hint_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 55))

    while True:
        screen.fill(colorBLACK)
        screen.blit(go_surf,   go_rect)
        screen.blit(stat_surf, stat_rect)
        screen.blit(hint_surf, hint_rect)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return True
                if event.key == pygame.K_q:
                    return False



# ONE GAME SESSION

def run_game():
    FPS   = 5
    clock = pygame.time.Clock()
    snake = Snake()
    food  = Food(snake.body)   # single food cube

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT and snake.dx != -1:
                    snake.dx, snake.dy = 1, 0
                elif event.key == pygame.K_LEFT and snake.dx != 1:
                    snake.dx, snake.dy = -1, 0
                elif event.key == pygame.K_DOWN and snake.dy != -1:
                    snake.dx, snake.dy = 0, 1
                elif event.key == pygame.K_UP and snake.dy != 1:
                    snake.dx, snake.dy = 0, -1

        snake.move()

        if not snake.alive:
            return show_game_over(snake.score, snake.level)

        if snake.check_collision(food):
            # Snake ate the food
            snake.score += food.score_val
            snake.grow(food.score_val)
            snake.level = 1 + snake.score // 3
            food.respawn(snake.body)
        elif food.is_expired():
            # Time ran out — move food elsewhere
            food.respawn(snake.body)

        screen.fill(colorBLACK)
        draw_grid()
        snake.draw()
        food.draw()

        screen.blit(font.render(f'Score: {snake.score}', True, colorWHITE), (2,   0))
        screen.blit(font.render(f'Level: {snake.level}', True, colorWHITE), (160, 0))

        pygame.display.flip()
        clock.tick(FPS + snake.level)



# ENTRY POINT

while True:
    if not run_game():
        break

pygame.quit()