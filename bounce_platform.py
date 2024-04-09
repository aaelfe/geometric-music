import math
import pygame
from settings import WHITE, RED

class BouncePlatform:
    def __init__(self, ball, length, width):
        self.angle = 0  # Initial angle
        self.length = length
        self.width = width
        self.x = ball.x
        self.y = ball.y
        self.ball = ball  # A reference to the ball to calculate position

    def draw(self, screen, y_offset):
        # recompute verticies
        self.recompute_verticies(False, y_offset)
        # Draw the platform as a polygon
        pygame.draw.polygon(screen, WHITE, self.vertices)

    def recompute_verticies(self, is_recent, y_offset):
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

        self.vertices = [
            (center_x - dx, center_y + dy),  # Top-left
            (center_x + dx, center_y - dy),  # Top-right
            (end_x + dx, end_y - dy),  # Bottom-right
            (end_x - dx, end_y + dy)   # Bottom-left
        ]

    def check_collision(self, ball_center, ball_radius):
        """
        Check if there is a collision between the ball and the platform.

        :param ball_center: A tuple (x, y) representing the ball's center.
        :param ball_radius: The radius of the ball.
        :return: True if there is a collision, False otherwise.
        """
        closest_point = None
        min_distance = float('inf')

        # Loop through each edge of the platform
        for i in range(len(self.vertices)):
            start_point = self.vertices[i]
            end_point = self.vertices[(i + 1) % len(self.vertices)]

            # Find the closest point on this segment to the center of the ball
            closest_point_on_segment = self.closest_point_on_line(start_point, end_point, ball_center)

            # Calculate the distance from this point to the ball's center
            distance = self.distance_between_points(closest_point_on_segment, ball_center)

            # Check if this is the closest point so far
            if distance < min_distance:
                min_distance = distance
                closest_point = closest_point_on_segment

        # If the closest point is within the ball's radius, there is a collision
        return min_distance <= ball_radius

    def closest_point_on_line(self, start_point, end_point, point):
        """
        Calculate the closest point on a line segment to a given point.

        :param start_point: The starting point of the line segment.
        :param end_point: The ending point of the line segment.
        :param point: The point to find the closest point to.
        :return: The closest point on the line segment to the given point.
        """
        line_vec = (end_point[0] - start_point[0], end_point[1] - start_point[1])
        point_vec = (point[0] - start_point[0], point[1] - start_point[1])

        line_len = line_vec[0]**2 + line_vec[1]**2
        line_unitvec = (line_vec[0] / math.sqrt(line_len), line_vec[1] / math.sqrt(line_len))

        proj_length = point_vec[0] * line_unitvec[0] + point_vec[1] * line_unitvec[1]
        proj_length = max(0, min(proj_length, math.sqrt(line_len)))

        closest_point = (start_point[0] + line_unitvec[0] * proj_length, start_point[1] + line_unitvec[1] * proj_length)
        return closest_point

    def distance_between_points(self, point1, point2):
        """
        Calculate the distance between two points.

        :param point1: The first point.
        :param point2: The second point.
        :return: The distance between the points.
        """
        return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
