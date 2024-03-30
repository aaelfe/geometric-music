import pygame
import pygame.gfxdraw
class Ball:
    def __init__(self, x, y, radius, color, outline_color, velocity):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.outline_color = outline_color
        self.velocity = velocity

    def draw(self, screen):
        # Draw the outline
        pygame.gfxdraw.aacircle(screen, int(self.x), int(self.y), self.radius, self.outline_color)
        pygame.gfxdraw.filled_circle(screen, int(self.x), int(self.y), self.radius, self.outline_color)
        
        # Draw the inner ball
        pygame.gfxdraw.aacircle(screen, int(self.x), int(self.y), self.radius - 1, self.color)
        pygame.gfxdraw.filled_circle(screen, int(self.x), int(self.y), self.radius - 1, self.color)

    def update(self):
        # Update the ball's position
        self.x += self.velocity[0]
        self.y += self.velocity[1]
