import pygame
from ball import Ball
pygame.init()
clock = pygame.time.Clock()
ball = Ball()

screen = pygame.display.set_mode((800, 600))

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
    
    press = pygame.key.get_pressed()
    ball.move(press)

    screen.fill((255,255,255))
    
    ball.draw(screen)
    
    clock.tick(60)
    
    pygame.display.flip()