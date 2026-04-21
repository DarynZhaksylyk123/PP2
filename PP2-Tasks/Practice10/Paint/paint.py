import pygame
import math
from pygame.locals import *
pygame.init()

clock = pygame.time.Clock()
screen = pygame.display.set_mode((800,600))
pygame.display.set_caption("Paint")


tools = ['Brush', 'Rect', 'Circle', 'Eraser']
current_tool = "Brush"

canvas = pygame.Surface((800,540))
canvas.fill((255,255,255))
start_pos = None
colors = [(0,0,0), (255,0,0), (0,255,0), (0,0,255), (255,255,0)]
current_color = (0,0,0)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == MOUSEBUTTONDOWN:
            
            for i, tool in enumerate(tools):
                x = 10 + i * 110
                mx, my = event.pos
                if x < mx < x + 100 and 10 < my < 50:
                    current_tool = tool
                    print(current_tool + " selected")
                for i, color in enumerate(colors):
                    x = 470 + i * 45
                    if x < mx < x + 40 and 10 < my < 50:
                        current_color = color
                
            if current_tool == "Rect" and my > 60:
                start_pos = (mx, my - 60)
            if current_tool == "Circle" and my > 60:
                start_pos = (mx, my - 60)
        elif event.type == MOUSEMOTION:
            mx, my = event.pos
            if pygame.mouse.get_pressed()[0] and my > 60:
                if current_tool == "Brush":
                    pygame.draw.circle(canvas, (current_color), (mx, my - 60), 5)
                elif current_tool == "Eraser":
                    pygame.draw.circle(canvas, (255,255,255), (mx, my - 60), 50)
            
        elif event.type == MOUSEBUTTONUP:
            mx, my = event.pos
            if current_tool == "Rect" and start_pos:
                end_pos = (mx, my-60)
                w = end_pos[0] - start_pos[0]
                h = end_pos[1] - start_pos[1]
                pygame.draw.rect(canvas, (current_color), (start_pos[0], start_pos[1], w, h), 2)
                start_pos = None
                
            if current_tool == "Circle" and start_pos:
                end_pos = (mx, my-60)
                dx = end_pos[0] - start_pos[0]
                dy = end_pos[1] - start_pos[1]
                radius = int(math.hypot(dx,dy))
                pygame.draw.circle(canvas, (current_color), start_pos, radius, 2)
                start_pos = None
                
                    
            
    screen.fill((255,255,255))  
    pygame.draw.rect(screen, (100,100,100), (0,0,800,60))
    
    
    screen.blit(canvas, (0,60))
    
    for i, tool in enumerate(tools):
        x = 10 + i * 110
        pygame.draw.rect(screen, (180,180,180), (x, 10, 100, 40))
        font = pygame.font.Font(pygame.font.get_default_font(), 28)
        text = font.render(tool, True, (0,0,0))
        screen.blit(text, (x + 10,20))
        
    for i, color in enumerate(colors):
        x = 470 + i * 45
        pygame.draw.rect(screen, color, (x, 10, 40, 40))
    
    clock.tick(120)
    pygame.display.update()
pygame.quit()