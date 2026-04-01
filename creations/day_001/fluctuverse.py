import random
import math
import pygame
from pygame.locals import *

# Initialize the Pygame library
pygame.init()

# Define the dimensions of the window
width, height = 800, 600
screen = pygame.display.set_mode((width, height))

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]

# Define the entity class
class Fluctuon:
    def __init__(self):
        self.x = random.uniform(0, width)
        self.y = random.uniform(0, height)
        self.size = random.uniform(5, 15)
        self.color = random.choice(COLORS)
        self.angle = random.uniform(0, 2 * math.pi)
        self.speed = random.uniform(1, 3)

    def update(self):
        # Update position based on speed and angle
        self.x += self.speed * math.cos(self.angle)
        self.y += self.speed * math.sin(self.angle)

        # Reflect off walls to create a closed universe effect
        if self.x <= 0 or self.x >= width:
            self.angle = math.pi - self.angle
        if self.y <= 0 or self.y >= height:
            self.angle = -self.angle

        # Randomly change speed and direction
        if random.random() < 0.05:
            self.speed = random.uniform(1, 3)
            self.angle += random.uniform(-0.5, 0.5)

    def display(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.size))

# Create a list of entities
fluctuons = [Fluctuon() for _ in range(100)]

# Main loop
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

    # Update the universe
    for fluctuon in fluctuons:
        fluctuon.update()

    # Draw everything
    screen.fill(BLACK)
    for fluctuon in fluctuons:
        fluctuon.display(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()