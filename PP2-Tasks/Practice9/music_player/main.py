import pygame
from player import Player
import os

pygame.init()
pygame.mixer.init()
player = Player()
player.load("C:/Negr/PP2/PP2-Tasks/Practice9/music_player/music")

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption('Music Player')

clock = pygame.time.Clock()
font = pygame.font.Font("C:/Negr/VsCode/Python/game/fonts/MinecraftItalic-R8Mo.otf", 30)

play = font.render("P-play", False, 'White')
next = font.render("N-next", False, 'White')
stop = font.render("S-stop", False, 'White')
pre = font.render("P-previous", False, 'White')
quit = font.render("Q-quit", False, 'White')

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
                running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                player.play()
            if event.key == pygame.K_n:
                player.next()
            if event.key == pygame.K_b:
                player.pre()
            if event.key == pygame.K_s:
                player.stop()
            if event.key == pygame.K_q:
                running = False    
    
    
            
    
    
    screen.fill((30, 30, 30))
    screen.blit(play, (30,170))
    screen.blit(stop, (30,200))
    screen.blit(next, (30,230))
    screen.blit(pre, (30,260))
    screen.blit(quit, (30, 290))
    track_name = os.path.basename(player.tracks[player.cur])
    text = font.render(track_name, False, (255,255,255))
    screen.blit(text, (50, 50))
    status = "Playing" if player.playing else "Stopped"
    status_text = font.render(status, False, (0,255,0))
    screen.blit(status_text, (50, 100))
    pygame.display.flip()
    clock.tick(60)