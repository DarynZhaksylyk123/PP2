import pygame
import os

class Player:
    def __init__(self):
        self.tracks = []
        self.cur = 0
        self.playing = False
        
    def load(self, folder):
        files = os.listdir(folder)
        for file in files:
            self.tracks.append(folder + "/" + file)

    def play(self):
        pygame.mixer.music.load(self.tracks[self.cur])
        pygame.mixer.music.play()
        self.playing = True
        
    def stop(self):
        pygame.mixer.music.stop()
        self.playing = False
        
    def next(self):
        self.cur = (self.cur + 1) % len(self.tracks)
        self.play()
        
    def pre(self):
        self.cur = (self.cur - 1) % len(self.tracks)
        self.play()
        
        
        