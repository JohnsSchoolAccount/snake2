import math

import pygame
import random
import sys
import copy

# Attempt to import ParticleSystem, if not found, define it (for standalone running)
try:
    from particles import Particle, ParticleSystem
except ImportError:
    print("particles.py not found, defining Particle classes locally for ouroboros_paradox_snake.py")


    class Particle:  # Placeholder
        def __init__(self, *args, **kwargs): pass

        def update(self): return False

        def draw(self, *args, **kwargs): pass


    class ParticleSystem:  # Placeholder
        def __init__(self): self.particles = []

        def emit(self, *args, **kwargs): pass

        def update(self): pass

        def draw(self, *args, **kwargs): pass

        def clear(self): pass

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
FPS = 10  # Keep original FPS, loop timing is tied to it

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN_SNAKE = (0, 220, 50)  # Brighter snake
DARK_GREEN_SNAKE = (0, 120, 30)
RED_EXIT = (220, 0, 0)
# Echo Colors
BLUE_ECHO_OBSTACLE = (70, 70, 180)
PURPLE_ECHO_SOLID = (150, 50, 200)
CYAN_ECHO_PHASED_OUTLINE = (0, 200, 200)
# Food Colors
YELLOW_FOOD_NORMAL = (255, 230, 50)
# Chrono-Pellet Colors (make them distinct)
PURPLE_CHRONO_SOLIDIFY = (200, 0, 200)
CYAN_CHRONO_PHASE = (0, 220, 220)
ORANGE_CHRONO_ERASE = (255, 140, 0)
# Particle Colors
TIME_RIPPLE_COLOR = (180, 180, 255)  # For loop reset

# Directions
UP = (0, -1);
DOWN = (0, 1);
LEFT = (-1, 0);
RIGHT = (1, 0)

# Time Loop
LOOP_DURATION_SECONDS = 15
LOOP_DURATION_TICKS = LOOP_DURATION_SECONDS * FPS


class Snake:
    def __init__(self, start_pos):
        self.body = [start_pos]
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.grow_pending = 0
        # current_path_this_loop removed, Game class will get path from snake.body at loop end

    def move(self):
        head_x, head_y = self.body[0]
        dir_x, dir_y = self.direction
        new_head = ((head_x + dir_x) % GRID_WIDTH, (head_y + dir_y) % GRID_HEIGHT)
        self.body.insert(0, new_head)
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            if len(self.body) > 1: self.body.pop()
        return True

    def grow(self, amount=1):
        self.grow_pending += amount

    def check_collision_self(self):
        return self.body[0] in self.body[1:]

    def draw(self, surface, particle_system_ref=None):  # Added particle_system_ref for potential effects
        for i, segment in enumerate(self.body):
            rect = pygame.Rect(segment[0] * GRID_SIZE, segment[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            color = GREEN_SNAKE if i % 2 == 0 else DARK_GREEN_SNAKE
            if i == 0:  # Head
                head_rect_inner = rect.inflate(-GRID_SIZE * 0.4, -GRID_SIZE * 0.4)
                pygame.draw.rect(surface, (255, 50, 50), rect)  # Outer head color
                pygame.draw.rect(surface, (200, 0, 0), head_rect_inner)  # Inner head dot
            else:
                pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, WHITE, rect, 1)

            # Subtle movement particles (optional)
            if particle_system_ref and i > 0 and random.random() < 0.02:  # Not for head, low chance
                particle_system_ref.emit(
                    rect.centerx, rect.centery, 1, color[:3] + (80,), 2, 5,
                    velocity_x_range=(-0.2, 0.2), velocity_y_range=(-0.2, 0.2), shrink_rate=0.1
                )


class EchoSnake:
    def __init__(self, body_snapshot, echo_type="obstacle", loop_created=0):
        self.body = body_snapshot  # List of (x,y) segment positions
        self.type = echo_type
        self.loop_created = loop_created  # For potential aging effects
        self.base_color_map = {
            "obstacle": BLUE_ECHO_OBSTACLE,
            "solid_edible": PURPLE_ECHO_SOLID,
            "phased": CYAN_ECHO_PHASED_OUTLINE
        }
        self.base_color = self.base_color_map.get(self.type, BLUE_ECHO_OBSTACLE)
        self.pulse_anim = random.uniform(0, math.pi * 2)  # For subtle pulsing
        self.pulse_speed = 0.05

    def update_animation(self):
        self.pulse_anim += self.pulse_speed
        if self.pulse_anim > math.pi * 2: self.pulse_anim -= math.pi * 2

    def draw(self, surface, particle_system_ref=None):
        self.update_animation()
        base_alpha = 100 + int(math.sin(self.pulse_anim) * 20)  # Pulsing alpha

        # Older echoes could be fainter (optional)
        # age_factor = max(0.3, 1.0 - (current_loop - self.loop_created) * 0.1)
        # final_alpha = int(base_alpha * age_factor)

        temp_surface = pygame.Surface((GRID_SIZE, GRID_SIZE), pygame.SRCALPHA)

        for i, segment_pos in enumerate(self.body):
            rect = pygame.Rect(segment_pos[0] * GRID_SIZE, segment_pos[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            current_alpha = base_alpha
            if i == 0 and self.type != "phased":  # Echo head slightly more distinct
                current_alpha = min(200, base_alpha + 50)

            echo_color_with_alpha = self.base_color[:3] + (current_alpha,)

            if self.type == "phased":
                pygame.draw.rect(surface, self.base_color, rect, 2)  # Outline only
            else:
                temp_surface.fill((0, 0, 0, 0))  # Clear for each segment
                pygame.draw.rect(temp_surface, echo_color_with_alpha, (0, 0, GRID_SIZE, GRID_SIZE))
                surface.blit(temp_surface, (rect.x, rect.y))

            pygame.draw.rect(surface, (self.base_color[0] // 2, self.base_color[1] // 2, self.base_color[2] // 2), rect,
                             1)  # Darker outline

            # Echo instability particles
            if particle_system_ref and self.type != "phased" and random.random() < 0.005 * len(
                    self.body):  # More chances for longer echoes
                particle_system_ref.emit(
                    rect.centerx, rect.centery, 1, self.base_color[:3] + (random.randint(50, 100),),
                    random.uniform(1, 3), 10, shrink_rate=0.1, fade_rate=10,
                    velocity_x_range=(-0.3, 0.3), velocity_y_range=(-0.3, 0.3)
                )


class Food:
    def __init__(self, food_type="normal", position=None):
        self.type = food_type
        self.color_map = {
            "normal": YELLOW_FOOD_NORMAL, "chrono_solidify": PURPLE_CHRONO_SOLIDIFY,
            "chrono_phase": CYAN_CHRONO_PHASE, "chrono_erase": ORANGE_CHRONO_ERASE
        }
        self.color = self.color_map.get(self.type, YELLOW_FOOD_NORMAL)
        if position:
            self.position = position
        else:
            self.position = (0, 0); self.spawn_randomly([], [])
        self.pulse_anim = random.uniform(0, math.pi * 2)
        self.pulse_speed = 0.1 if self.type == "normal" else 0.15  # Chrono items pulse faster
        self.base_radius = GRID_SIZE // 2 - 3

    def spawn_randomly(self, snake_body, existing_food_positions_and_exit):
        all_occupied = snake_body + existing_food_positions_and_exit
        while True:
            self.position = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
            if self.position not in all_occupied: break

        rand_val = random.random()
        if rand_val < 0.55:
            self.type = "normal"  # More normal food
        elif rand_val < 0.75:
            self.type = "chrono_solidify"
        elif rand_val < 0.90:
            self.type = "chrono_phase"
        else:
            self.type = "chrono_erase"
        self.color = self.color_map[self.type]
        self.pulse_anim = random.uniform(0, math.pi * 2)

    def update_animation(self):
        self.pulse_anim += self.pulse_speed
        if self.pulse_anim > math.pi * 2: self.pulse_anim -= math.pi * 2

    def draw(self, surface):
        self.update_animation()
        center_x = self.position[0] * GRID_SIZE + GRID_SIZE // 2
        center_y = self.position[1] * GRID_SIZE + GRID_SIZE // 2

        current_radius_offset = math.sin(self.pulse_anim) * (2 if self.type == "normal" else 3)
        current_radius = self.base_radius + current_radius_offset

        # Glow for chrono pellets
        if self.type.startswith("chrono_"):
            glow_radius = current_radius + 5
            glow_alpha = 80 + int(abs(math.sin(self.pulse_anim)) * 40)
            glow_color = self.color[:3] + (glow_alpha,)
            pygame.draw.circle(surface, glow_color, (center_x, center_y), int(glow_radius))

        pygame.draw.circle(surface, self.color, (center_x, center_y), int(current_radius))
        pygame.draw.circle(surface, BLACK, (center_x, center_y), int(current_radius), 1)


class ExitPoint:
    def __init__(self, position):
        self.position = position
        self.color = RED_EXIT
        self.anim_timer = 0
        self.anim_speed = 0.05

    def update(self):
        self.anim_timer += self.anim_speed
        if self.anim_timer > math.pi * 2:
            self.anim_timer -= math.pi * 2

    def draw(self, surface):
        self.update()
        rect = pygame.Rect(self.position[0] * GRID_SIZE, self.position[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(surface, self.color, rect)

        # Pulsing inner design
        inner_size_factor = 0.4 + abs(math.sin(self.anim_timer)) * 0.2
        inner_rect = rect.inflate(-GRID_SIZE * (1 - inner_size_factor), -GRID_SIZE * (1 - inner_size_factor))
        inner_color = (min(255, self.color[0] + 50), min(255, self.color[1] + 50), min(255, self.color[2] + 50))
        pygame.draw.rect(surface, inner_color, inner_rect, border_radius=3)
        pygame.draw.rect(surface, WHITE, rect, 2)


class Game:
    def __init__(self):
        if not pygame.get_init(): pygame.init(); pygame.mixer.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Snake 2: Ouroboros Paradox")
        self.clock = pygame.time.Clock()
        try:
            self.font = pygame.font.SysFont("Consolas", 24)
            self.small_font = pygame.font.SysFont("Consolas", 18)
        except pygame.error:
            self.font = pygame.font.Font(None, 30);
            self.small_font = pygame.font.Font(None, 24)

        self.particle_system = ParticleSystem()
        self.player_start_pos = (GRID_WIDTH // 4, GRID_HEIGHT // 2)
        self.exit_point_pos = (GRID_WIDTH * 3 // 4, GRID_HEIGHT // 2)
        self.reset_level()

    def reset_level(self):
        self.snake = Snake(self.player_start_pos)
        self.echoes = []
        self.foods = []
        self.exit_point = ExitPoint(self.exit_point_pos)
        self.spawn_initial_food()
        self.score = 0;
        self.loop_count = 1;
        self.current_loop_ticks = 0
        self.game_over_flag = False;
        self.paused = False;
        self.level_cleared = False
        self.game_over_reason = "";
        self.next_echo_type = "obstacle"
        self.particle_system.clear()

    def spawn_initial_food(self):
        self.foods = []
        occupied_for_food = [seg for seg in self.snake.body] + [self.exit_point.position]
        for echo in self.echoes: occupied_for_food.extend(echo.body)  # Include echoes too

        # Ensure at least one of each Chrono pellet type if few echoes exist, else more random
        chrono_types_to_spawn = ["chrono_solidify", "chrono_phase", "chrono_erase"]

        num_food_items = 3 + len(self.echoes) // 2  # More food if more echoes exist
        num_food_items = min(num_food_items, 6)  # Cap food items

        for i in range(num_food_items):
            food_type = "normal"
            if i < len(chrono_types_to_spawn) and len(self.echoes) < 2:  # Ensure core chrono types early
                food_type = chrono_types_to_spawn[i]

            food_item = Food(food_type=food_type)  # Food will randomize if type is normal
            if food_type != "normal": food_item.type = food_type  # Force type if specified

            food_item.spawn_randomly(self.snake.body, occupied_for_food + [f.position for f in self.foods])
            self.foods.append(food_item)

    def handle_loop_reset(self):
        # Screen Flash and Particles for Loop Reset
        flash_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        flash_surface.fill(TIME_RIPPLE_COLOR)  # Use a thematic color
        for i in range(5):  # Multiple flashes for intensity
            flash_surface.set_alpha(150 - i * 20)
            self.screen.blit(flash_surface, (0, 0))
            pygame.display.flip()
            pygame.time.wait(20)

        # Emit Particles from screen edges inwards or from center outwards
        for _ in range(60):
            edge = random.choice(["top", "bottom", "left", "right"])
            start_x, start_y = 0, 0
            vel_x_range, vel_y_range = (-1, 1), (-1, 1)  # Default for center emit

            if edge == "top":
                start_x, start_y = random.randint(0, SCREEN_WIDTH), -10; vel_y_range = (1, 3)
            elif edge == "bottom":
                start_x, start_y = random.randint(0, SCREEN_WIDTH), SCREEN_HEIGHT + 10; vel_y_range = (-3, -1)
            elif edge == "left":
                start_x, start_y = -10, random.randint(0, SCREEN_HEIGHT); vel_x_range = (1, 3)
            elif edge == "right":
                start_x, start_y = SCREEN_WIDTH + 10, random.randint(0, SCREEN_HEIGHT); vel_x_range = (-3, -1)

            self.particle_system.emit(start_x, start_y, 1, TIME_RIPPLE_COLOR[:3] + (180,),
                                      random.uniform(2, 5), 30, shrink_rate=0.1, fade_rate=5,
                                      velocity_x_range=vel_x_range, velocity_y_range=vel_y_range)

        if self.next_echo_type != "erased" and self.snake.body:
            echo_body_snapshot = copy.deepcopy(self.snake.body)
            self.echoes.append(EchoSnake(echo_body_snapshot, self.next_echo_type, self.loop_count))

        self.snake = Snake(self.player_start_pos)
        self.current_loop_ticks = 0;
        self.loop_count += 1
        self.next_echo_type = "obstacle"
        self.spawn_initial_food()  # Respawn food strategically

    def display_ui(self):  # Same as before
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        loop_text = self.font.render(f"Loop: {self.loop_count}", True, WHITE)
        self.screen.blit(loop_text, (10, 40))
        time_left = max(0, (LOOP_DURATION_TICKS - self.current_loop_ticks) // FPS)
        time_text = self.font.render(f"Time: {time_left}s", True, WHITE)
        self.screen.blit(time_text, (10, 70))

        next_echo_display_color = WHITE
        if self.next_echo_type == "solid_edible":
            next_echo_display_color = PURPLE_CHRONO_SOLIDIFY
        elif self.next_echo_type == "phased":
            next_echo_display_color = CYAN_CHRONO_PHASE
        elif self.next_echo_type == "erased":
            next_echo_display_color = ORANGE_CHRONO_ERASE

        next_echo_text = self.small_font.render(f"Next Echo: {self.next_echo_type.upper()}", True,
                                                next_echo_display_color)
        self.screen.blit(next_echo_text, (SCREEN_WIDTH - next_echo_text.get_width() - 10, 10))

    def game_over_or_level_clear_screen(self):  # Same, ensure no pygame.quit()
        # ... (game over screen logic) ...
        self.screen.fill(BLACK)
        title_msg = "LEVEL CLEARED!" if self.level_cleared else "PARADOX COLLAPSE!"
        title_color = GREEN_SNAKE if self.level_cleared else RED_EXIT
        title_text = self.font.render(title_msg, True, title_color)
        self.screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 3 - 30))
        if not self.level_cleared:
            reason_text = self.small_font.render(self.game_over_reason, True, WHITE)
            self.screen.blit(reason_text, (SCREEN_WIDTH // 2 - reason_text.get_width() // 2, SCREEN_HEIGHT // 3 + 20))
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        loops_text = self.font.render(f"Loops: {self.loop_count}", True, WHITE)
        restart_text = self.font.render("R: Restart Level | Q: Menu", True, WHITE)
        self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 3 + 70))
        self.screen.blit(loops_text, (SCREEN_WIDTH // 2 - loops_text.get_width() // 2, SCREEN_HEIGHT // 3 + 100))
        self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 3 + 150))
        pygame.display.flip()
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.event.post(pygame.event.Event(pygame.QUIT))  # Repost for main_menu
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q: self.game_over_flag = True; waiting = False  # Signal main loop to exit
                    if event.key == pygame.K_r: self.reset_level(); waiting = False  # Resets game_over_flag
            self.clock.tick(FPS)

    def run(self):
        running = True
        while running:
            if self.game_over_flag or self.level_cleared:
                self.game_over_or_level_clear_screen()
                if self.game_over_flag:  # If Q was pressed or game over is still set
                    running = False  # Exit game loop to return to menu
                # If R was pressed, flags are reset, loop continues
                continue

            for event in pygame.event.get():
                if event.type == pygame.QUIT: running = False
                if event.type == pygame.KEYDOWN:
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
                    elif event.key == pygame.K_ESCAPE:
                        running = False

            if not running: break
            if self.paused:
                pause_text = self.font.render("PAUSED", True, YELLOW_FOOD_NORMAL)
                self.screen.blit(pause_text, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2,
                                              SCREEN_HEIGHT // 2 - pause_text.get_height() // 2))
                pygame.display.flip();
                self.clock.tick(FPS);
                continue

            self.current_loop_ticks += 1
            if self.current_loop_ticks >= LOOP_DURATION_TICKS: self.handle_loop_reset()

            self.snake.move()
            if self.snake.check_collision_self(): self.game_over_flag = True; self.game_over_reason = "Self-collision paradox!"

            for i, echo in reversed(list(enumerate(self.echoes))):
                if echo.type == "phased": continue
                if self.snake.body[0] in echo.body:
                    if echo.type == "solid_edible":
                        self.snake.grow(len(echo.body));
                        self.score += 50 * len(echo.body)
                        # Echo eaten particles
                        for seg_pos in echo.body:  # Particles for each segment of eaten echo
                            self.particle_system.emit(
                                seg_pos[0] * GRID_SIZE + GRID_SIZE // 2, seg_pos[1] * GRID_SIZE + GRID_SIZE // 2,
                                2, echo.base_color[:3] + (180,), 4, 15,
                                velocity_x_range=(-1, 1), velocity_y_range=(-1, 1), shrink_rate=0.2)
                        self.echoes.pop(i)
                    else:
                        self.game_over_flag = True; self.game_over_reason = "Collided with temporal echo!"
                    break
                if self.game_over_flag: break

            food_to_remove_idx = -1
            for idx, food_item in enumerate(self.foods):
                if self.snake.body[0] == food_item.position:
                    food_center_x = food_item.position[0] * GRID_SIZE + GRID_SIZE // 2
                    food_center_y = food_item.position[1] * GRID_SIZE + GRID_SIZE // 2

                    if food_item.type == "normal":
                        self.snake.grow();
                        self.score += 10
                        self.particle_system.emit(food_center_x, food_center_y, 15, food_item.color[:3] + (200,), 4, 15,
                                                  velocity_x_range=(-1.5, 1.5), velocity_y_range=(-1.5, 1.5),
                                                  gravity=0.05)
                    else:  # Chrono pellet
                        self.score += 5
                        if food_item.type == "chrono_solidify":
                            self.next_echo_type = "solid_edible"
                        elif food_item.type == "chrono_phase":
                            self.next_echo_type = "phased"
                        elif food_item.type == "chrono_erase":
                            self.next_echo_type = "erased"
                        self.particle_system.emit(food_center_x, food_center_y, 25, food_item.color[:3] + (220,), 5, 25,
                                                  velocity_x_range=(-2.5, 2.5), velocity_y_range=(-2.5, 2.5),
                                                  shrink_rate=0.15)
                    food_to_remove_idx = idx;
                    break

            if food_to_remove_idx != -1:
                self.foods.pop(food_to_remove_idx)
                if len(self.foods) < (3 + len(self.echoes) // 2) and len(self.foods) < 6:  # Try to maintain food count
                    self.spawn_initial_food()  # This will try to add more food smartly

            if self.snake.body[0] == self.exit_point.position:
                self.level_cleared = True;
                self.score += 100
                # Level clear particles
                self.particle_system.emit(self.exit_point.position[0] * GRID_SIZE + GRID_SIZE // 2,
                                          self.exit_point.position[1] * GRID_SIZE + GRID_SIZE // 2,
                                          50, (255, 255, 100, 200), 6, 40, velocity_x_range=(-3, 3),
                                          velocity_y_range=(-3, 3),
                                          shrink_rate=0.1, fade_rate=5)

            self.particle_system.update()  # Update all particles

            self.screen.fill(BLACK)
            # Draw grid with low alpha for subtlety
            grid_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            for x_g in range(0, SCREEN_WIDTH, GRID_SIZE): pygame.draw.line(grid_surface, (50, 50, 80, 50), (x_g, 0),
                                                                           (x_g, SCREEN_HEIGHT))
            for y_g in range(0, SCREEN_HEIGHT, GRID_SIZE): pygame.draw.line(grid_surface, (50, 50, 80, 50), (0, y_g),
                                                                            (SCREEN_WIDTH, y_g))
            self.screen.blit(grid_surface, (0, 0))

            self.particle_system.draw(self.screen)  # Draw particles underneath everything else

            for echo in self.echoes: echo.draw(self.screen,
                                               self.particle_system)  # Pass particle system for echo effects
            for food_item in self.foods: food_item.draw(self.screen)
            self.exit_point.draw(self.screen);
            self.snake.draw(self.screen, self.particle_system)
            self.display_ui()

            pygame.display.flip();
            self.clock.tick(FPS)