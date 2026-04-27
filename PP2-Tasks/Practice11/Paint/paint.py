import pygame
import math
from pygame.locals import *

pygame.init()

clock = pygame.time.Clock()
screen = pygame.display.set_mode((1000, 700)) # Экранды сәл үлкейттік (құралдар сыю үшін)
pygame.display.set_caption("Enhanced Paint")

tools = ['Brush', 'Rect', 'Circle', 'Square', 'RightTri', 'EquiTri', 'Rhombus', 'Eraser']
current_tool = "Brush"

canvas = pygame.Surface((1000, 640))
canvas.fill((255, 255, 255))
start_pos = None
colors = [(0, 0, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255)]
current_color = (0, 0, 0)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == MOUSEBUTTONDOWN:
            mx, my = event.pos
      
            for i, tool in enumerate(tools):
                x = 10 + i * 110
                if x < mx < x + 100 and 10 < my < 50:
                    current_tool = tool
            
           
            for i, color in enumerate(colors):
                x = 10 + i * 45
                if x < mx < x + 40 and 60 < my < 90:
                    current_color = color
            
            
            if my > 100:
                start_pos = (mx, my - 100)

        elif event.type == MOUSEMOTION:
            mx, my = event.pos
            if pygame.mouse.get_pressed()[0] and my > 100:
                if current_tool == "Brush":
                    pygame.draw.circle(canvas, current_color, (mx, my - 100), 5)
                elif current_tool == "Eraser":
                    pygame.draw.circle(canvas, (255, 255, 255), (mx, my - 100), 50)

        elif event.type == MOUSEBUTTONUP:
            mx, my = event.pos
            if start_pos and my > 100:
                end_pos = (mx, my - 100)
                dx = end_pos[0] - start_pos[0]
                dy = end_pos[1] - start_pos[1]

                # 1. Rectangle 
                if current_tool == "Rect":
                    pygame.draw.rect(canvas, current_color, (start_pos[0], start_pos[1], dx, dy), 2)
                
                # 2. Circle 
                elif current_tool == "Circle":
                    radius = int(math.hypot(dx, dy))
                    pygame.draw.circle(canvas, current_color, start_pos, radius, 2)
                
                # 3. Square 
                elif current_tool == "Square":
                    side = max(abs(dx), abs(dy))
                    s_x = start_pos[0] if dx > 0 else start_pos[0] - side
                    s_y = start_pos[1] if dy > 0 else start_pos[1] - side
                    pygame.draw.rect(canvas, current_color, (s_x, s_y, side, side), 2)

                # 4. Right Triangle 
                elif current_tool == "RightTri":
                    points = [start_pos, (start_pos[0], end_pos[1]), end_pos]
                    pygame.draw.polygon(canvas, current_color, points, 2)

                # 5. Equilateral Triangle 
                elif current_tool == "EquiTri":
                    side = dx
                    height = side * math.sqrt(3) / 2
                    points = [
                        start_pos, 
                        (start_pos[0] + side, start_pos[1]), 
                        (start_pos[0] + side // 2, start_pos[1] - height)
                    ]
                    pygame.draw.polygon(canvas, current_color, points, 2)

                # 6. Rhombus 
                elif current_tool == "Rhombus":
                    points = [
                        (start_pos[0] + dx // 2, start_pos[1]), # жоғарғы нүкте
                        (start_pos[0] + dx, start_pos[1] + dy // 2), # оң жақ
                        (start_pos[0] + dx // 2, start_pos[1] + dy), # төменгі
                        (start_pos[0], start_pos[1] + dy // 2)  # сол жақ
                    ]
                    pygame.draw.polygon(canvas, current_color, points, 2)

                start_pos = None


    screen.fill((240, 240, 240))
    

    pygame.draw.rect(screen, (100, 100, 100), (0, 0, 1000, 100))
    screen.blit(canvas, (0, 100))

    for i, tool in enumerate(tools):
        x = 10 + i * 120
        color = (255, 255, 0) if current_tool == tool else (180, 180, 180)
        pygame.draw.rect(screen, color, (x, 10, 110, 40))
        font = pygame.font.Font(None, 24)
        text = font.render(tool, True, (0, 0, 0))
        screen.blit(text, (x + 10, 22))
        

    for i, color in enumerate(colors):
        x = 10 + i * 45
        pygame.draw.rect(screen, color, (x, 60, 40, 30))
        if current_color == color:
            pygame.draw.rect(screen, (255, 255, 255), (x, 60, 40, 30), 3)

    clock.tick(120)
    pygame.display.update()

pygame.quit()