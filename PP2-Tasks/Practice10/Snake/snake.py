import pygame
from pygame.locals import *
from colors import *
import random

pygame.init()

width = 600
height = 600

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Snakeiooooo")

cell = 30

def grid():
    for i in range (height // cell):
        for j in range (width // cell):
            pygame.draw.rect(screen, colorWHITE, (i * cell, j * cell, cell,cell), 1)
    
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __str__(self):
        return f"{self.x}, {self.y}"  

class Snake:
    def __init__(self):
        self.body = [Point(10, 11), Point(10, 12), Point(10, 13)]
        self.dx = 1
        self.dy = 0
    def move(self):
        for i in range(len(self.body) - 1, 0, -1):
            self.body[i].x = self.body[i - 1].x
            self.body[i].y = self.body[i - 1].y
        
        self.body[0].x += self.dx
        self.body[0].y += self.dy
        
        if self.body[0].x > width // cell - 1:
            self.body[0].x = 0
        
        if self.body[0].x < 0:
            self.body[0].x = width // cell - 1

        if self.body[0].y > height // cell - 1:
            self.body[0].y = 0

        if self.body[0].y < 0:
            self.body[0].y = height // cell - 1\
                
    def draw(self):
        head = self.body[0]
        pygame.draw.rect(screen, colorBLUE, (head.x * cell, head.y * cell, cell, cell))
        for segment in self.body[1:]:
            pygame.draw.rect(screen, colorGREEN, (segment.x * cell, segment.y * cell, cell, cell))

    def check_collision(self, food):
        head = self.body[0]
        if head.x == food.pos.x and head.y == food.pos.y:
            print("Got food!")
            self.body.append(Point(head.x, head.y))
            food.generate_random_pos()
            
class Food:
    def __init__(self):
        self.pos = Point(9, 9)

    def draw(self):
        pygame.draw.rect(screen, colorYELLOW, (self.pos.x * cell, self.pos.y * cell, cell, cell))

    def generate_random_pos(self):
        self.pos.x = random.randint(0, width // cell - 1)
        self.pos.y = random.randint(0, height // cell - 1)


FPS = 5
clock = pygame.time.Clock()

food = Food()
snake = Snake()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                snake.dx = 1
                snake.dy = 0
            elif event.key == pygame.K_LEFT:
                snake.dx = -1
                snake.dy = 0
            elif event.key == pygame.K_DOWN:
                snake.dx = 0
                snake.dy = 1
            elif event.key == pygame.K_UP:
                snake.dx = 0
                snake.dy = -1

    screen.fill(colorBLACK)

    grid()

    snake.move()
    snake.check_collision(food)

    snake.draw()
    food.draw()

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()