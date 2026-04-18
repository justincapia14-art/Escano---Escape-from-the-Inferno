import pygame
import random

class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = random.randint(2, 5)
        self.color = (255, 140, 0)  # light gray for dust
        self.vel_x = random.uniform(-1, 1)
        self.vel_y = random.uniform(-1, -0.5)
        self.lifetime = 15  # frames

    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.lifetime -= 1
        self.size = max(0, self.size - 0.1)  # slowly shrink

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.size))