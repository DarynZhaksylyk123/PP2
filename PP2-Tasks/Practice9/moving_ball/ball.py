import pygame

class Ball:
    def __init__(self):
        self.x = 400
        self.y = 300
        self.speed = 10
        self.radius = 25
    def move(self, keys):
        
        if keys[pygame.K_UP]:
            self.y -= 10
        if keys[pygame.K_DOWN]:
            self.y += 10
        if keys[pygame.K_RIGHT]:
            self.x += 10
        if keys[pygame.K_LEFT]:
            self.x -= 10
                
        if self.x < 25:
            self.x = 25
        if self.x > 775:
            self.x = 775
        if self.y < 25:
            self.y = 25
        if self.y > 575:
            self.y = 575
            
    def draw(self, screen):
        pygame.draw.circle(screen, (195, 96, 200), (self.x, self.y), self.radius)
        