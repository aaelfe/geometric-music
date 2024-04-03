import pygame
import pygame.gfxdraw
import math

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
    
    def project_bounce_path(self, platform_angle, steps=50, step_distance=10):
        projected_path = []
        sim_ball_pos = [self.x, self.y]
        sim_velocity = list(self.prev_velocity) # when this is called actual velocity will be 0 (paused)
        gravity = self.gravity

        for _ in range(steps):
            # Update the simulated ball's position
            sim_ball_pos[0] += sim_velocity[0]
            sim_ball_pos[1] += sim_velocity[1]

            # Apply gravity
            sim_velocity[1] -= gravity

            # Add the current position to the path
            projected_path.append(tuple(sim_ball_pos))

            # Check for bounce - this is simplified, you might want to check based on platform's position
            if len(projected_path) == steps // 2:  # Assuming bounce occurs halfway through the projection
                # Reflect the velocity based on the platform angle
                angle_rad = math.radians(platform_angle)
                sim_velocity[0] = -sim_velocity[0] * math.cos(2 * angle_rad) - sim_velocity[1] * math.sin(2 * angle_rad)
                sim_velocity[1] = -sim_velocity[1] * math.cos(2 * angle_rad) + sim_velocity[0] * math.sin(2 * angle_rad)
        
        return projected_path