import pygame
from pygame.locals import *
import random

pygame.init()

width = 1000
height = 1000

marker_w = 10      
marker_h = 50      

road = (200, 0, 600, height)

left_m  = (190, 0, marker_w, height)
right_m = (790, 0, marker_w, height)

left_line = 300
center_line = 500
right_line = 700
lines = [left_line, center_line, right_line]

y_move = 0


class Vehicle(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        pygame.sprite.Sprite.__init__(self)

        
        image_scale = 150 / image.get_rect().width
        new_width = image.get_rect().width  * image_scale
        new_height = image.get_rect().height * image_scale

        self.image = pygame.transform.scale(image, (new_width, new_height))
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]


class PlayerVehicle(Vehicle):
    def __init__(self, x, y):
    
        image = pygame.image.load(
            'C:/Negr/PP2/PP2-Tasks/Practice10/Racer/image/Topdown_vehicle_sprites_pack/Car.png'
        )
        super().__init__(image, x, y)


class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)

      
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 215, 0), (15, 15), 15)  
        pygame.draw.circle(self.image, (200, 160, 0), (15, 15), 15, 3) 

        self.rect = self.image.get_rect()
        self.rect.center = [x, y]


player_x = 500
player_y = 800

player_group = pygame.sprite.Group()
player = PlayerVehicle(player_x, player_y)
player_group.add(player)

image_filenames = [
    'Mini_truck.png', 'Mini_van.png', 'Police.png', 'truck.png',
    'taxi.png', 'Ambulance.png', 'Audi.png', 'Black_viper.png'
]
transport = []
for image_filename in image_filenames:
    image = pygame.image.load(
        'C:/Negr/PP2/PP2-Tasks/Practice10/Racer/image/Topdown_vehicle_sprites_pack/' + image_filename
    )
    transport.append(image)

vehicle_group = pygame.sprite.Group()

coin_group = pygame.sprite.Group()

crash = pygame.image.load('PP2-Tasks/Practice10/Racer/image/crash.png')
crash_rect = crash.get_rect()

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Racer')
clock = pygame.time.Clock()
fps   = 120

gray = (100, 100, 100)
green = (76,  209,  56)
red = (200,   0,   0)
white = (255, 255, 255)
yellow = (255, 232,   0)
gold = (255, 215,   0)

gameover = False
speed = 2
score = 0
coins_collected = 0  

bg = pygame.mixer.Sound('PP2-Tasks/Practice10/Racer/UNIK - Гонк-Конг.mp3')
bg.play()

haha = pygame.mixer.Sound('PP2-Tasks/Practice10/Racer/mangaletp-funny-laughing-406018.mp3')


running = True
while running:

    clock.tick(fps)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == KEYDOWN:

            if event.key == K_LEFT and player.rect.center[0] > left_line:
                player.rect.x -= 200

            elif event.key == K_RIGHT and player.rect.center[0] < right_line:
                player.rect.x += 200

            for vehicle in vehicle_group:
                if pygame.sprite.collide_rect(player, vehicle):
                    gameover = True

                    if event.key == K_LEFT:
                        player.rect.left = vehicle.rect.right
                        crash_rect.center = [
                            player.rect.left,
                            (player.rect.center[1] + vehicle.rect.center[1]) / 2
                        ]
                    elif event.key == K_RIGHT:
                        player.rect.right = vehicle.rect.left
                        crash_rect.center = [
                            player.rect.right,
                            (player.rect.center[1] + vehicle.rect.center[1]) / 2
                        ]

    screen.fill(green)
    pygame.draw.rect(screen, gray,   road)
    pygame.draw.rect(screen, yellow, right_m)
    pygame.draw.rect(screen, yellow, left_m)

    y_move += speed * 2
    if y_move >= marker_h * 2:
        y_move = 0
    for y in range(marker_h * -2, height, marker_h * 2):
        pygame.draw.rect(screen, white, (left_line   + 90, y + y_move, marker_w, marker_h))
        pygame.draw.rect(screen, white, (center_line + 90, y + y_move, marker_w, marker_h))

    player_group.draw(screen)

    if len(vehicle_group) < 2:
        add_vehicle = True
        for vehicle in vehicle_group:
    
            if vehicle.rect.top < vehicle.rect.height * 1.5:
                add_vehicle = False

        if add_vehicle:
            lane = random.choice(lines)
            image = random.choice(transport)
            vehicle = Vehicle(image, lane, height / -2)
            vehicle_group.add(vehicle)

    for vehicle in vehicle_group:
        vehicle.rect.y += speed

        if vehicle.rect.top >= height:
            vehicle.kill()
            score += 1
            
            if score > 0 and score % 5 == 0:
                speed += 1

    vehicle_group.draw(screen)

    if random.randint(1, 90) == 1:        
        lane = random.choice(lines)
        coin = Coin(lane, -20)            
        coin_group.add(coin)

    for coin in coin_group:
        coin.rect.y += speed
        if coin.rect.top >= height:        
            coin.kill()

    coin_group.draw(screen)

    collected = pygame.sprite.spritecollide(player, coin_group, True)
    coins_collected += len(collected)     
    
    font = pygame.font.Font(pygame.font.get_default_font(), 32)

    text = font.render('Score: ' + str(score), True, white)
    text_rect = text.get_rect()
    text_rect.center = (100, 900)
    screen.blit(text, text_rect)

  
    coin_text = font.render('Coins: ' + str(coins_collected), True, gold)
    coin_text_rect = coin_text.get_rect()
    coin_text_rect.topright = (width - 20, 20)   
    screen.blit(coin_text, coin_text_rect)

    if pygame.sprite.spritecollide(player, vehicle_group, True):
        gameover = True
        crash_rect.center = [player.rect.center[0], player.rect.top]

    if gameover:
        screen.blit(crash, crash_rect)
        pygame.draw.rect(screen, red, (0, 100, width, 200))
        bg.stop()
        haha.play()

        text = font.render("Game Over. Play again? (Enter Y or N)", True, white)
        text_rect = text.get_rect()
        text_rect.center = (width / 2, 200)
        screen.blit(text, text_rect)

    pygame.display.update()

    while gameover:
        clock.tick(fps)

        for event in pygame.event.get():
            if event.type == QUIT:
                gameover = False
                running = False

            if event.type == KEYDOWN:
                if event.key == K_y:
                    
                    running = True
                    gameover = False
                    speed = 2
                    score = 0
                    coins_collected = 0         
                    vehicle_group.empty()
                    coin_group.empty()           
                    player.rect.center = [player_x, player_y]
                    bg.play()
                    haha.stop()

                elif event.key == K_n:
                    
                    running  = False
                    gameover = False

pygame.quit()