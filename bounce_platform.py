import math
import pygame
from settings import WHITE

class BouncePlatform:
    def __init__(self, ball, length, width):
        self.angle = 0  # Initial angle
        self.length = length
        self.width = width
        self.x = ball.x
        self.y = ball.y
        self.ball = ball  # A reference to the ball to calculate position

    def draw(self, screen, y_offset, is_recent=False):
        if is_recent:
            # Calculate center for the most recent platform using the ball's current position
            center_x = self.ball.x + math.cos(math.radians(self.angle)) * self.ball.radius
            center_y = (self.ball.y - math.sin(math.radians(self.angle)) * self.ball.radius) - y_offset
        else:
            # Use the stored initial offset for static platforms
            center_x = self.x + math.cos(math.radians(self.angle)) * self.ball.radius
            center_y = (self.y - math.sin(math.radians(self.angle)) * self.ball.radius) - y_offset

        # Calculate the centerline of the platform
        # center_x = self.ball.x + math.cos(math.radians(self.angle)) * self.ball.radius
        # center_y = self.ball.y - math.sin(math.radians(self.angle)) * self.ball.radius
        end_x = center_x + math.cos(math.radians(self.angle)) * self.width
        end_y = center_y - math.sin(math.radians(self.angle)) * self.width

        # Calculate the four corners of the platform
        dx = math.cos(math.radians(self.angle + 90)) * (self.length / 2)
        dy = math.sin(math.radians(self.angle + 90)) * (self.length / 2)

        vertices = [
            (center_x - dx, center_y + dy),  # Top-left
            (center_x + dx, center_y - dy),  # Top-right
            (end_x + dx, end_y - dy),  # Bottom-right
            (end_x - dx, end_y + dy)   # Bottom-left
        ]

        adjusted_vertices = [(x, y) for x, y in vertices]

        # Draw the platform as a polygon
        pygame.draw.polygon(screen, WHITE, adjusted_vertices)

    def update_angle(self, angle_change):
        self.angle += angle_change
        self.angle %= 360  # Keep the angle within 0-359 degrees
