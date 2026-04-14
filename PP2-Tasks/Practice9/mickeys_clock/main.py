import pygame
import datetime

pygame.init()

screen = pygame.display.set_mode((1200, 700))
pygame.display.set_caption("Mickey's clock")
clock = pygame.time.Clock()

clc_image = pygame.image.load('C:/Negr/PP2/PP2-Tasks/Practice9/mickeys_clock/images/clock.png')
clc_image = pygame.transform.scale(clc_image, (1100, 700))

mick_img = pygame.image.load('C:/Negr/PP2/PP2-Tasks/Practice9/mickeys_clock/images/mickey.png')
mick_img = pygame.transform.scale(mick_img, (400, 400))

right = pygame.image.load('C:/Negr/PP2/PP2-Tasks/Practice9/mickeys_clock/images/hand_right.png')
right = pygame.transform.scale(right, (180, 180))

left = pygame.image.load('C:/Negr/PP2/PP2-Tasks/Practice9/mickeys_clock/images/hand_left.png')
left = pygame.transform.scale(left, (180, 180))

def rotate(image, angle, x, y):
    rotated_image = pygame.transform.rotate(image, -angle)
    new_rect = rotated_image.get_rect(center=(x, y))
    return rotated_image, new_rect

center_x = 1200 // 2
center_y = 700 // 2

clock_x = (1200 - 1100) // 2
clock_y = (700 - 700) // 2

mickey_x = center_x - (400 // 2)
mickey_y = center_y - (400 // 2)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    now = datetime.datetime.now()
    minutes = now.minute
    seconds = now.second
    
    m_angle = minutes * 6
    s_angle = seconds * 6
    
    rotated_right, right_rect = rotate(right, m_angle, center_x, center_y)
    rotated_left, left_rect = rotate(left, s_angle, center_x, center_y)
    
    screen.fill((255, 255, 255))
    screen.blit(clc_image, (clock_x, clock_y))
    screen.blit(mick_img, (mickey_x, mickey_y))
    screen.blit(rotated_right, right_rect.topleft)
    screen.blit(rotated_left, left_rect.topleft)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()