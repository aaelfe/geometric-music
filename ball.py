import pygame
import pygame.gfxdraw
import math

from settings import FPS

class Ball:
    def __init__(self, x, y, radius, color, outline_color, velocity, gravity, restitution):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.outline_color = outline_color
        self.velocity = velocity
        self.gravity = gravity
        self.restitution = restitution

        self.paused = False
        self.prev_velocity = (0, 0)
        self.projected_path = []

    def draw(self, screen, y_offset):
        adjusted_y = int(self.y - y_offset)

        # Draw the outline
        pygame.gfxdraw.aacircle(screen, int(self.x), adjusted_y, self.radius, self.outline_color)
        pygame.gfxdraw.filled_circle(screen, int(self.x), adjusted_y, self.radius, self.outline_color)
        
        # Draw the inner ball
        pygame.gfxdraw.aacircle(screen, int(self.x), adjusted_y, self.radius - 1, self.color)
        pygame.gfxdraw.filled_circle(screen, int(self.x), adjusted_y, self.radius - 1, self.color)

    def update(self):
        # If paused - nothing to be done
        if self.paused:
            return

        # Else update the ball's position
        self.x += self.velocity[0]
        self.y += self.velocity[1]

        self.velocity = (self.velocity[0], self.velocity[1] - self.gravity)
    
    def pause(self):
        self.prev_velocity = self.velocity
        self.velocity = (0, 0)
        self.paused = True

    def resume(self):
        self.velocity = self.prev_velocity
        self.paused = False

    def bounce_off_platform(self, platform):
        # Calculate the incoming angle
        velocity_angle_rad = math.atan2(-self.velocity[1], self.velocity[0])
        platform_angle_rad = math.radians(platform.angle)
        
        # Calculate the reflection angle
        reflection_angle_rad = 2*platform_angle_rad - velocity_angle_rad
        
        # Calculate the speed (magnitude of the velocity vector)
        speed = math.sqrt(self.velocity[0] ** 2 + self.velocity[1] ** 2)
        
        # Apply restitution (assuming the ball's restitution attribute represents this)
        speed *= self.restitution
        
        # Update the velocity based on the reflection angle
        self.velocity = (
            -speed * math.cos(reflection_angle_rad), 
            speed * math.sin(reflection_angle_rad)  # Negate y-component to account for Pygame's coordinate system
        )
    
    def project_bounce_path(self, platform_angle, total_time=2, time_per_step=0.1):
        projected_path = []
        # Starting from the ball's current position
        sim_position = [self.x, self.y]

        # Initial velocity considering the bounce off the platform, using ball's prev_velocity
        velocity_angle_rad = math.atan2(-self.prev_velocity[1], self.prev_velocity[0])
        platform_angle_rad = math.radians(platform_angle)
        reflection_angle_rad = 2*platform_angle_rad - velocity_angle_rad
        
        # Calculate the speed (magnitude of the velocity vector)
        speed = math.sqrt(self.prev_velocity[0] ** 2 + self.prev_velocity[1] ** 2)
        
        # Apply restitution
        speed *= self.restitution

        # Update the velocity based on the reflection angle
        sim_velocity = [
            -speed * math.cos(reflection_angle_rad), 
            speed * math.sin(reflection_angle_rad)  # Negate y-component for Pygame's coordinate system
        ]

        steps = int((total_time * FPS) / time_per_step)

        for _ in range(steps):
            # Apply gravity to the y-component of the velocity
            sim_velocity[1] -= self.gravity * time_per_step

            # Simulate the ball's movement
            sim_position[0] += sim_velocity[0] * time_per_step
            sim_position[1] += sim_velocity[1] * time_per_step

            # Update the projected path with the new position
            projected_path.append(tuple(sim_position))
     
        # # print every parameter and every self variable used in this function
        # print("platform_angle",platform_angle)
        # print("total_time",total_time)
        # print("time_per_step",time_per_step)
        # print("self.prev_velocity",self.prev_velocity)
        # print("self.restitution",self.restitution)
        # print("self.gravity",self.gravity)
        # print("self.x",self.x)
        # print("self.y",self.y)
        # print("self.radius",self.radius)

        self.projected_path = projected_path