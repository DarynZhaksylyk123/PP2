import pygame
import math
from pygame.locals import *
from collections import deque
from datetime import datetime

pygame.init()

clock = pygame.time.Clock()
screen = pygame.display.set_mode((1000, 700))
pygame.display.set_caption("Enhanced Paint")

tools = ['Brush', 'Pencil', 'Line', 'Rect', 'Circle', 'Square',
         'RightTri', 'EquiTri', 'Rhombus', 'Fill', 'Eraser', 'Text']
current_tool = "Brush"

canvas = pygame.Surface((1000, 640))
canvas.fill((255, 255, 255))

start_pos = None
last_pos  = None          

colors = [(0, 0, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255),
          (255, 255, 0), (255, 0, 255), (0, 255, 255), (255, 165, 0),
          (128, 0, 128), (255, 255, 255)]
current_color = (0, 0, 0)

brush_sizes = {1: 2, 2: 5, 3: 10}
current_size_key = 1

text_active = False
text_pos    = (0, 0)
text_buffer = ""
font_text   = pygame.font.SysFont("monospace", 20)

status_msg   = ""
status_timer = 0

def flood_fill(surface, pos, new_color):
    x0, y0 = pos
    w, h = surface.get_size()
    if not (0 <= x0 < w and 0 <= y0 < h):
        return
    old_color = surface.get_at((x0, y0))[:3]
    new_color3 = new_color[:3]
    if old_color == new_color3:
        return
    surface.lock()
    queue   = deque([(x0, y0)])
    visited = {(x0, y0)}
    while queue:
        x, y = queue.popleft()
        if surface.get_at((x, y))[:3] != old_color:
            continue
        surface.set_at((x, y), new_color)
        for nx, ny in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in visited:
                visited.add((nx, ny))
                queue.append((nx, ny))
    surface.unlock()

def save_canvas():
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"canvas_{ts}.png"
    pygame.image.save(canvas, filename)
    return filename

running = True
while running:
    dt = clock.tick(120)

    brush_size = brush_sizes[current_size_key]

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == KEYDOWN:

            if text_active:
                if event.key == K_RETURN:
                    img = font_text.render(text_buffer, True, current_color)
                    canvas.blit(img, text_pos)
                    text_active = False
                    text_buffer = ""
                elif event.key == K_ESCAPE:
                    text_active = False
                    text_buffer = ""
                elif event.key == K_BACKSPACE:
                    text_buffer = text_buffer[:-1]
                elif event.unicode and event.unicode.isprintable():
                    text_buffer += event.unicode
                continue

            mods = pygame.key.get_mods()
            if event.key == K_s and (mods & KMOD_CTRL):
                fn = save_canvas()
                status_msg   = f"Saved: {fn}"
                status_timer = 3000
                continue

            if event.key == K_1:
                current_size_key = 1
            elif event.key == K_2:
                current_size_key = 2
            elif event.key == K_3:
                current_size_key = 3

            if event.key == K_ESCAPE:
                start_pos = None

        if event.type == MOUSEBUTTONDOWN:
            mx, my = event.pos

            for i, tool in enumerate(tools):
                x = 10 + i * 83
                if x < mx < x + 78 and 5 < my < 35:
                    current_tool = tool
                    text_active  = False
                    text_buffer  = ""

            for i, color in enumerate(colors):
                x = 10 + i * 45
                if x < mx < x + 40 and 40 < my < 70:
                    current_color = color

            for key in brush_sizes:
                bx = 470 + (key - 1) * 55
                if bx < mx < bx + 50 and 40 < my < 70:
                    current_size_key = key

            if my > 100:
                cp = (mx, my - 100)

                if current_tool == "Text":
                    text_active = True
                    text_pos    = cp
                    text_buffer = ""

                elif current_tool == "Fill":
                    flood_fill(canvas, cp, current_color)

                else:
                    start_pos = cp
                    last_pos  = cp

        elif event.type == MOUSEMOTION:
            mx, my = event.pos
            if pygame.mouse.get_pressed()[0] and my > 100:
                cp = (mx, my - 100)

                if current_tool == "Brush":
                    if last_pos:
                        pygame.draw.line(canvas, current_color, last_pos, cp, brush_size)
                    last_pos = cp

                elif current_tool == "Pencil":
                    if last_pos:
                        pygame.draw.line(canvas, current_color, last_pos, cp, brush_size)
                    last_pos = cp

                elif current_tool == "Eraser":
                    if last_pos:
                        pygame.draw.line(canvas, (255, 255, 255), last_pos, cp, brush_size * 4)
                    last_pos = cp

        elif event.type == MOUSEBUTTONUP:
            mx, my = event.pos
            if start_pos and my > 100:
                end_pos = (mx, my - 100)
                dx = end_pos[0] - start_pos[0]
                dy = end_pos[1] - start_pos[1]

                if current_tool == "Line":
                    pygame.draw.line(canvas, current_color, start_pos, end_pos, brush_size)

                elif current_tool == "Rect":
                    rect = (min(start_pos[0], end_pos[0]),
                            min(start_pos[1], end_pos[1]),
                            abs(dx), abs(dy))
                    pygame.draw.rect(canvas, current_color, rect, brush_size)

                elif current_tool == "Circle":
                    radius = int(math.hypot(dx, dy))
                    pygame.draw.circle(canvas, current_color, start_pos, radius, brush_size)

                elif current_tool == "Square":
                    side = max(abs(dx), abs(dy))
                    s_x = start_pos[0] if dx > 0 else start_pos[0] - side
                    s_y = start_pos[1] if dy > 0 else start_pos[1] - side
                    pygame.draw.rect(canvas, current_color, (s_x, s_y, side, side), brush_size)

                elif current_tool == "RightTri":
                    points = [start_pos, (start_pos[0], end_pos[1]), end_pos]
                    pygame.draw.polygon(canvas, current_color, points, brush_size)

                elif current_tool == "EquiTri":
                    side   = dx
                    height = side * math.sqrt(3) / 2
                    points = [
                        start_pos,
                        (start_pos[0] + side, start_pos[1]),
                        (start_pos[0] + side // 2, int(start_pos[1] - height))
                    ]
                    pygame.draw.polygon(canvas, current_color, points, brush_size)

                elif current_tool == "Rhombus":
                    points = [
                        (start_pos[0] + dx // 2, start_pos[1]),
                        (start_pos[0] + dx,      start_pos[1] + dy // 2),
                        (start_pos[0] + dx // 2, start_pos[1] + dy),
                        (start_pos[0],            start_pos[1] + dy // 2),
                    ]
                    pygame.draw.polygon(canvas, current_color, points, brush_size)

            start_pos = None
            last_pos  = None

    if status_timer > 0:
        status_timer -= dt

    screen.fill((240, 240, 240))
    pygame.draw.rect(screen, (100, 100, 100), (0, 0, 1000, 100))
    screen.blit(canvas, (0, 100))

    if start_pos and current_tool in ("Line", "Rect", "Circle", "Square",
                                       "RightTri", "EquiTri", "Rhombus"):
        mx, my = pygame.mouse.get_pos()
        if my > 100:
            ep  = (mx, my - 100)
            dx_ = ep[0] - start_pos[0]
            dy_ = ep[1] - start_pos[1]
            ox, oy = 0, 100

            if current_tool == "Line":
                pygame.draw.line(screen, current_color,
                                 (start_pos[0]+ox, start_pos[1]+oy),
                                 (ep[0]+ox, ep[1]+oy), brush_size)

            elif current_tool == "Rect":
                r = (min(start_pos[0], ep[0])+ox,
                     min(start_pos[1], ep[1])+oy,
                     abs(dx_), abs(dy_))
                pygame.draw.rect(screen, current_color, r, brush_size)

            elif current_tool == "Circle":
                rad = int(math.hypot(dx_, dy_))
                pygame.draw.circle(screen, current_color,
                                   (start_pos[0]+ox, start_pos[1]+oy),
                                   rad, brush_size)

            elif current_tool == "Square":
                side = max(abs(dx_), abs(dy_))
                sx = start_pos[0] if dx_ > 0 else start_pos[0] - side
                sy = start_pos[1] if dy_ > 0 else start_pos[1] - side
                pygame.draw.rect(screen, current_color,
                                 (sx+ox, sy+oy, side, side), brush_size)

            elif current_tool == "RightTri":
                pts = [(start_pos[0]+ox, start_pos[1]+oy),
                       (start_pos[0]+ox, ep[1]+oy),
                       (ep[0]+ox, ep[1]+oy)]
                pygame.draw.polygon(screen, current_color, pts, brush_size)

            elif current_tool == "EquiTri":
                side = dx_
                h    = int(side * math.sqrt(3) / 2)
                pts  = [(start_pos[0]+ox, start_pos[1]+oy),
                        (start_pos[0]+dx_+ox, start_pos[1]+oy),
                        (start_pos[0]+dx_//2+ox, start_pos[1]-h+oy)]
                pygame.draw.polygon(screen, current_color, pts, brush_size)

            elif current_tool == "Rhombus":
                pts = [(start_pos[0]+dx_//2+ox, start_pos[1]+oy),
                       (start_pos[0]+dx_+ox,    start_pos[1]+dy_//2+oy),
                       (start_pos[0]+dx_//2+ox, start_pos[1]+dy_+oy),
                       (start_pos[0]+ox,         start_pos[1]+dy_//2+oy)]
                pygame.draw.polygon(screen, current_color, pts, brush_size)

    if text_active:
        preview = font_text.render(text_buffer + "|", True, current_color)
        screen.blit(preview, (text_pos[0], text_pos[1] + 100))

    font_btn = pygame.font.Font(None, 22)
    for i, tool in enumerate(tools):
        x     = 10 + i * 83
        color = (255, 255, 0) if current_tool == tool else (180, 180, 180)
        pygame.draw.rect(screen, color, (x, 5, 78, 28), border_radius=4)
        txt = font_btn.render(tool, True, (0, 0, 0))
        screen.blit(txt, (x + 4, 13))

    for i, color in enumerate(colors):
        x = 10 + i * 45
        pygame.draw.rect(screen, color, (x, 40, 40, 28))
        if current_color == color:
            pygame.draw.rect(screen, (255, 255, 255), (x, 40, 40, 28), 3)

    font_sz = pygame.font.Font(None, 20)
    size_labels = {1: "S(1)", 2: "M(2)", 3: "L(3)"}
    for key in brush_sizes:
        bx    = 470 + (key - 1) * 55
        color = (255, 200, 0) if current_size_key == key else (180, 180, 180)
        pygame.draw.rect(screen, color, (bx, 40, 50, 28), border_radius=4)
        t = font_sz.render(size_labels[key], True, (0, 0, 0))
        screen.blit(t, (bx + 6, 50))

    pygame.draw.rect(screen, current_color, (940, 40, 50, 28))
    pygame.draw.rect(screen, (255,255,255), (940, 40, 50, 28), 2)

    if status_timer > 0:
        font_st = pygame.font.Font(None, 22)
        st = font_st.render(status_msg, True, (0, 180, 0))
        screen.blit(st, (10, 78))

    pygame.display.update()

pygame.quit()