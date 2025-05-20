# particles.py
import pygame
import random
import math


class Particle:
    def __init__(self, x, y, color, size, lifespan, velocity_x_range=(-1, 1), velocity_y_range=(-1, 1), gravity=0,
                 shrink_rate=0.05, fade_rate=5):
        self.x = x
        self.y = y
        self.size = random.uniform(size * 0.7, size * 1.3)
        self.initial_size = self.size

        # Ensure color is a list and has an alpha component
        self.color = list(color)
        if len(self.color) == 3:
            self.color.append(255)  # Default to full alpha if not provided
        elif len(self.color) == 4:
            self.color[3] = min(255, max(0, int(self.color[3])))  # Clamp provided alpha

        self.initial_alpha = self.color[3]

        self.lifespan = random.uniform(lifespan * 0.8, lifespan * 1.2)
        self.initial_lifespan = self.lifespan

        self.vx = random.uniform(velocity_x_range[0], velocity_x_range[1])
        self.vy = random.uniform(velocity_y_range[0], velocity_y_range[1])
        self.gravity = gravity
        self.shrink_rate = shrink_rate
        self.fade_rate = fade_rate

    def update(self):
        self.lifespan -= 1
        if self.lifespan <= 0:
            return False

        self.vy += self.gravity
        self.x += self.vx
        self.y += self.vy

        self.size -= self.shrink_rate
        if self.size < 0: self.size = 0

        self.color[3] = max(0, int(self.color[3] - self.fade_rate))  # Ensure alpha is int

        return True

    def draw(self, surface, camera_offset_x=0, camera_offset_y=0):
        if self.size <= 0 or self.color[3] <= 0:
            return

        # Create a temporary surface for drawing the particle with alpha
        # This ensures correct alpha blending if the main surface doesn't handle it per-draw
        # For simple circles, pygame.draw.circle handles RGBA colors correctly on surfaces
        # that support alpha (like the main screen surface if SRCALPHA is used, or temp surfaces).

        # Optimized: directly draw if color has alpha
        # Make sure color is a tuple of 4 for pygame.draw.circle with alpha
        draw_color = tuple(self.color) if len(self.color) == 4 else tuple(list(self.color)[:3] + [255])

        try:
            if draw_color[3] > 0:  # Only draw if visible
                pygame.draw.circle(surface, draw_color,
                                   (int(self.x - camera_offset_x), int(self.y - camera_offset_y)),
                                   int(self.size))
        except (TypeError, ValueError) as e:
            # print(f"Particle draw error: {e}, Color: {draw_color}, Size: {self.size}")
            pass  # Catch potential errors with color format or negative size


class ParticleSystem:
    def __init__(self):
        self.particles = []

    def add_particle(self, particle_instance):
        self.particles.append(particle_instance)

    def emit(self, x, y, count, color, base_size, base_lifespan, **kwargs):
        for _ in range(count):
            self.particles.append(Particle(x, y, color, base_size, base_lifespan, **kwargs))

    def update(self):
        # Iterate backwards for safe removal
        for i in range(len(self.particles) - 1, -1, -1):
            if not self.particles[i].update():
                self.particles.pop(i)
        # self.particles = [p for p in self.particles if p.update()] # Alternative list comprehension

    def draw(self, surface, camera_offset_x=0, camera_offset_y=0):
        # For better alpha blending performance, especially with many particles,
        # one could draw all particles of similar type onto a temporary transparent surface,
        # then blit that surface once. But for now, individual draws are fine.
        for p in self.particles:
            p.draw(surface, camera_offset_x, camera_offset_y)

    def clear(self):
        self.particles.clear()