import math
import pygame
import random
import sys

# Attempt to import ParticleSystem, if not found, define it (for standalone running)
try:
    from particles import Particle, ParticleSystem
except ImportError:
    print("particles.py not found, defining Particle classes locally for no_clip_snake.py")


    # --- Paste Particle and ParticleSystem classes from particles.py here ---
    # (For brevity, I'm assuming particles.py is present. If running this file standalone,
    # you MUST paste the Particle and ParticleSystem class code here)
    class Particle:  # Placeholder if not imported
        def __init__(self, *args, **kwargs): pass

        def update(self): return False

        def draw(self, *args, **kwargs): pass


    class ParticleSystem:  # Placeholder
        def __init__(self): self.particles = []

        def emit(self, *args, **kwargs): pass

        def update(self): pass

        def draw(self, *args, **kwargs): pass

        def clear(self): pass
    # --- End of pasted Particle classes ---

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
FPS = 12  # Slightly increased FPS for smoother particles

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
DARK_GREEN = (0, 100, 0)
RED = (200, 0, 0)  # Head color
BLUE = (0, 0, 200)  # Darker phasing segment color
LIGHT_BLUE_PHASE = (100, 150, 255)  # Brighter phasing segment color / particles
YELLOW_FOOD = (255, 255, 0)
PURPLE_GHOST_FOOD = (180, 0, 255)

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)


class Snake:
    def __init__(self):
        self.body = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.grow_pending = 0
        self.is_phasing = False
        self.phase_energy_max = 100
        self.phase_energy = self.phase_energy_max
        self.phasing_sickness = 0
        self.phasing_sickness_max = 100
        self.phasing_cost_per_tick = 4  # Adjusted
        self.sickness_increase_per_tick = 1.5  # Adjusted
        self.sickness_decrease_per_tick = 0.3  # Adjusted
        self.phase_recharge_per_tick = 0.8  # Adjusted

    def move(self):
        head_x, head_y = self.body[0]
        dir_x, dir_y = self.direction
        new_head = ((head_x + dir_x) % GRID_WIDTH, (head_y + dir_y) % GRID_HEIGHT)
        self.body.insert(0, new_head)

        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.body.pop()
        return True

    def grow(self, amount=1):
        self.grow_pending += amount

    def check_collision_self(self):
        if self.is_phasing:
            return False
        return self.body[0] in self.body[1:]

    def toggle_phase(self):
        if self.phase_energy > self.phasing_cost_per_tick or self.is_phasing:
            self.is_phasing = not self.is_phasing
            if self.is_phasing and self.phase_energy <= 0:
                self.is_phasing = False

    def update_phase_mechanics(self):
        if self.is_phasing:
            self.phase_energy -= self.phasing_cost_per_tick
            self.phasing_sickness += self.sickness_increase_per_tick
            if self.phase_energy <= 0:
                self.phase_energy = 0
                self.is_phasing = False
        else:
            self.phase_energy += self.phase_recharge_per_tick
            if self.phase_energy > self.phase_energy_max:
                self.phase_energy = self.phase_energy_max

        self.phasing_sickness -= self.sickness_decrease_per_tick
        if self.phasing_sickness < 0:
            self.phasing_sickness = 0
        if self.phasing_sickness >= self.phasing_sickness_max:  # Use >= for safety
            self.phasing_sickness = self.phasing_sickness_max
            return True  # Reality Fracture
        return False

    def draw(self, surface):
        color = LIGHT_BLUE_PHASE if self.is_phasing else GREEN
        dark_color = BLUE if self.is_phasing else DARK_GREEN

        for i, segment in enumerate(self.body):
            rect = pygame.Rect(segment[0] * GRID_SIZE, segment[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            current_color = color if i % 2 == 0 else dark_color
            if i == 0:
                pygame.draw.rect(surface, RED, rect)
            else:
                pygame.draw.rect(surface, current_color, rect)

            # Segment outline
            outline_color = WHITE if not self.is_phasing else (200, 220, 255)
            pygame.draw.rect(surface, outline_color, rect, 1)


class Food:
    def __init__(self):  # Removed food_type argument, will be set in spawn
        self.position = (0, 0)
        self.type = "normal"
        self.color = YELLOW_FOOD
        self.radius_anim = 0  # For pulsing effect
        self.pulse_speed = 0.2
        self.max_pulse_offset = 2
        self.spawn_randomly([])

    def spawn_randomly(self, snake_body):
        while True:
            self.position = (random.randint(0, GRID_WIDTH - 1),
                             random.randint(0, GRID_HEIGHT - 1))
            if self.position not in snake_body:
                break
        self.type = "ghost" if random.random() < 0.35 else "normal"  # Slightly more ghost food
        self.color = PURPLE_GHOST_FOOD if self.type == "ghost" else YELLOW_FOOD
        self.radius_anim = 0

    def update(self):
        self.radius_anim += self.pulse_speed
        if self.radius_anim > math.pi * 2:
            self.radius_anim -= math.pi * 2

    def draw(self, surface):
        self.update()  # Update animation state

        center_x = self.position[0] * GRID_SIZE + GRID_SIZE // 2
        center_y = self.position[1] * GRID_SIZE + GRID_SIZE // 2
        base_radius = GRID_SIZE // 2 - 2

        current_radius_offset = math.sin(self.radius_anim) * self.max_pulse_offset
        current_radius = base_radius + current_radius_offset

        # Glow effect for ghost food
        if self.type == "ghost":
            glow_radius = current_radius + 4
            glow_color = list(self.color)
            glow_color.append(80)  # Alpha for glow
            pygame.draw.circle(surface, tuple(glow_color), (center_x, center_y), int(glow_radius))

        pygame.draw.circle(surface, self.color, (center_x, center_y), int(current_radius))
        pygame.draw.circle(surface, BLACK, (center_x, center_y), int(current_radius), 1)


class Game:
    def __init__(self):
        if not pygame.get_init():
            pygame.init()
            if not pygame.mixer.get_init():  # Only init mixer if not already
                pygame.mixer.init()

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Snake 2: No-Clip Nightmare")
        self.clock = pygame.time.Clock()

        try:
            self.font = pygame.font.SysFont("Consolas", 24)
            self.small_font = pygame.font.SysFont("Consolas", 18)
        except pygame.error:
            self.font = pygame.font.Font(None, 30)
            self.small_font = pygame.font.Font(None, 24)

        self.particle_system = ParticleSystem()
        self.reset_game()

    def reset_game(self):
        self.snake = Snake()
        self.food = Food()
        # self.food.spawn_randomly(self.snake.body) # Already called in Food.__init__
        self.score = 0
        self.game_over_flag = False
        self.paused = False
        self.game_over_reason = ""
        self.particle_system.clear()

    def display_ui(self):
        # ... (UI drawing code remains largely the same)
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))

        phase_bar_width = 150;
        phase_bar_height = 20
        current_phase_width = (self.snake.phase_energy / self.snake.phase_energy_max) * phase_bar_width
        pygame.draw.rect(self.screen, DARK_GREEN, (10, 40, phase_bar_width, phase_bar_height))
        pygame.draw.rect(self.screen, GREEN, (10, 40, current_phase_width, phase_bar_height))
        phase_text = self.small_font.render("Phase Energy", True, WHITE)
        self.screen.blit(phase_text, (10 + phase_bar_width + 5, 40))

        sickness_bar_width = 150;
        sickness_bar_height = 20
        current_sickness_width = (self.snake.phasing_sickness / self.snake.phasing_sickness_max) * sickness_bar_width
        pygame.draw.rect(self.screen, DARK_GREEN, (10, 70, sickness_bar_width, sickness_bar_height))
        pygame.draw.rect(self.screen, RED, (10, 70, current_sickness_width, sickness_bar_height))
        sickness_text = self.small_font.render("Sickness", True, WHITE)
        self.screen.blit(sickness_text, (10 + sickness_bar_width + 5, 70))

        if self.snake.is_phasing:
            phasing_indicator = self.small_font.render("PHASING ACTIVE", True, LIGHT_BLUE_PHASE)
            self.screen.blit(phasing_indicator, (SCREEN_WIDTH - phasing_indicator.get_width() - 10, 10))

    def apply_sickness_effects(self):
        if self.snake.phasing_sickness > self.snake.phasing_sickness_max * 0.2:
            sickness_alpha_tint = int((self.snake.phasing_sickness / self.snake.phasing_sickness_max) * 70)
            sickness_overlay_tint = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            sickness_overlay_tint.fill((200, 0, 50, sickness_alpha_tint))  # More purplish red
            self.screen.blit(sickness_overlay_tint, (0, 0))

            if self.snake.phasing_sickness > self.snake.phasing_sickness_max * 0.55 and random.random() < 0.25:
                num_glitches = int((self.snake.phasing_sickness / self.snake.phasing_sickness_max) * 8) + 1
                for _ in range(num_glitches):
                    gx = random.randint(0, SCREEN_WIDTH - 30)
                    gy = random.randint(0, SCREEN_HEIGHT - 10)
                    gw = random.randint(10, 30)
                    gh = random.randint(3, 10)

                    if random.random() < 0.6:  # Shift block
                        shift_x = random.randint(-8, 8)
                        shift_y = random.randint(-5, 5)
                        try:
                            glitch_area_rect = pygame.Rect(gx, gy, gw, gh)
                            glitch_area_rect.clamp_ip(self.screen.get_rect())  # Ensure it's within screen bounds
                            if glitch_area_rect.width > 0 and glitch_area_rect.height > 0:
                                glitch_area = self.screen.subsurface(glitch_area_rect).copy()
                                self.screen.blit(glitch_area,
                                                 (glitch_area_rect.x + shift_x, glitch_area_rect.y + shift_y))
                        except ValueError:
                            pass
                    else:  # Color glitch block
                        g_color = (random.randint(50, 200), random.randint(0, 50), random.randint(50, 200),
                                   100)  # Glitchy purple/reds with alpha
                        temp_surface = pygame.Surface((gw, gh), pygame.SRCALPHA)
                        temp_surface.fill(g_color)
                        self.screen.blit(temp_surface, (gx, gy))

    def game_over_screen(self):  # Same as before, just ensure it doesn't quit pygame
        # ... (game over screen logic) ...
        self.screen.fill(BLACK)
        title_text = self.font.render("GAME OVER", True, RED)
        reason_text = self.small_font.render(self.game_over_reason, True, YELLOW_FOOD)
        score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
        restart_text = self.font.render("Press 'R' to Restart or 'Q' to Menu", True, WHITE)

        self.screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 3))
        self.screen.blit(reason_text, (SCREEN_WIDTH // 2 - reason_text.get_width() // 2, SCREEN_HEIGHT // 3 + 50))
        self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 3 + 80))
        self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 3 + 120))
        pygame.display.flip()

        waiting_for_input = True
        while waiting_for_input:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # Instead of pygame.quit(), signal main menu to handle full exit
                    self.game_over_flag = True  # Keep it set
                    pygame.event.post(pygame.event.Event(pygame.QUIT))  # Re-post QUIT for main_menu
                    return  # Exit this screen, main game loop will see game_over_flag and QUIT
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        self.game_over_flag = True  # Ensure it stays game over for main loop to exit
                        waiting_for_input = False  # This will cause game_over_screen to return
                    if event.key == pygame.K_r:
                        self.reset_game()  # This sets self.game_over_flag to False
                        waiting_for_input = False
            self.clock.tick(FPS)
        # If 'R' was pressed, self.game_over_flag is now False.
        # If 'Q' was pressed, self.game_over_flag is True.

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if self.game_over_flag:
                        if event.key == pygame.K_r:
                            self.reset_game()
                        elif event.key == pygame.K_q:
                            running = False
                        continue

                    if event.key == pygame.K_p: self.paused = not self.paused
                    if self.paused: continue

                    if event.key == pygame.K_UP and self.snake.direction != DOWN:
                        self.snake.direction = UP
                    elif event.key == pygame.K_DOWN and self.snake.direction != UP:
                        self.snake.direction = DOWN
                    elif event.key == pygame.K_LEFT and self.snake.direction != RIGHT:
                        self.snake.direction = LEFT
                    elif event.key == pygame.K_RIGHT and self.snake.direction != LEFT:
                        self.snake.direction = RIGHT
                    elif event.key == pygame.K_SPACE:
                        self.snake.toggle_phase()
                    elif event.key == pygame.K_ESCAPE:
                        running = False

            if not running: break

            if self.game_over_flag:
                self.game_over_screen()
                # After game_over_screen, if self.game_over_flag is still true, it means Q was pressed
                # or the screen was exited without pressing R.
                if self.game_over_flag:
                    running = False  # Exit to menu
                # If R was pressed, game_over_flag is false, and loop continues
                continue

            if self.paused:
                pause_text = self.font.render("PAUSED", True, YELLOW_FOOD)
                self.screen.blit(pause_text, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2,
                                              SCREEN_HEIGHT // 2 - pause_text.get_height() // 2))
                pygame.display.flip();
                self.clock.tick(FPS);
                continue

            # --- Game Logic Update ---
            self.snake.move()

            if self.snake.update_phase_mechanics():
                self.game_over_flag = True
                self.game_over_reason = "Reality Fracture: Sickness Overload!"

            # Phasing particles
            if self.snake.is_phasing and random.random() < 0.6:
                for seg_idx, seg_pos in enumerate(self.snake.body):
                    if random.random() < (0.05 + seg_idx * 0.005):  # More particles towards tail
                        self.particle_system.emit(
                            seg_pos[0] * GRID_SIZE + GRID_SIZE // 2 + random.uniform(-3, 3),
                            seg_pos[1] * GRID_SIZE + GRID_SIZE // 2 + random.uniform(-3, 3),
                            count=1, color=LIGHT_BLUE_PHASE[:3] + (random.randint(100, 180),),
                            base_size=random.uniform(1.5, 3.5), base_lifespan=8,
                            velocity_x_range=(-0.3, 0.3), velocity_y_range=(-0.3, 0.3),
                            shrink_rate=0.25, fade_rate=20
                        )

            # Food collision
            if self.snake.body[0] == self.food.position:
                can_eat_food = (self.food.type == "normal") or \
                               (self.food.type == "ghost" and self.snake.is_phasing)
                if can_eat_food:
                    self.snake.grow()
                    self.score += 10 if self.food.type == "normal" else 25

                    # Food eat particles
                    food_center_x = self.food.position[0] * GRID_SIZE + GRID_SIZE // 2
                    food_center_y = self.food.position[1] * GRID_SIZE + GRID_SIZE // 2
                    particle_color = list(self.food.color)
                    if len(particle_color) == 3:
                        particle_color.append(220)
                    else:
                        particle_color[3] = 220

                    self.particle_system.emit(
                        food_center_x, food_center_y, count=20, color=particle_color,
                        base_size=5, base_lifespan=20, velocity_x_range=(-2.5, 2.5),
                        velocity_y_range=(-2.5, 2.5), gravity=0.08, shrink_rate=0.15, fade_rate=12
                    )
                    self.food.spawn_randomly(self.snake.body)

            if self.snake.check_collision_self():
                self.game_over_flag = True;
                self.game_over_reason = "Crashed into yourself!"

            self.particle_system.update()

            # --- Drawing ---
            self.screen.fill(BLACK)
            # Draw grid (optional, can be distracting with particles)
            # for x_g in range(0, SCREEN_WIDTH, GRID_SIZE): pygame.draw.line(self.screen, (30,30,30), (x_g,0), (x_g, SCREEN_HEIGHT))
            # for y_g in range(0, SCREEN_HEIGHT, GRID_SIZE): pygame.draw.line(self.screen, (30,30,30), (0,y_g), (SCREEN_WIDTH,y_g))

            self.particle_system.draw(self.screen)  # Draw particles BEHIND food/snake
            self.food.draw(self.screen)
            self.snake.draw(self.screen)
            self.apply_sickness_effects()  # Apply OVER everything else
            self.display_ui()  # UI on top of everything

            pygame.display.flip()
            self.clock.tick(FPS)

        # print(f"No Clip Snake run loop ended. Game over: {self.game_over_flag}")