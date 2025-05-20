import math

import pygame
import random
import sys

# Attempt to import ParticleSystem
try:
    from particles import Particle, ParticleSystem
except ImportError:
    print("particles.py not found, defining Particle classes locally for symbiotic_anarchy_snake.py")


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
FPS = 8  # Original FPS

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
# Segment Colors
COLOR_RED_SEG_BASE = (200, 0, 0)
COLOR_BLUE_SEG_BASE = (0, 0, 200)
COLOR_GREEN_SEG_BASE = (0, 150, 0)
COLOR_HEAD = (255, 100, 0)
# Food Colors
COLOR_RED_FOOD = (255, 50, 50)
COLOR_BLUE_FOOD = (50, 50, 255)
COLOR_GREEN_FOOD = (50, 200, 50)
COLOR_UNIVERSAL_FOOD = (220, 220, 0)  # Brighter Universal
# Particle Colors
UNHAPPY_SMOKE_COLOR = (80, 80, 80, 120)
DETACH_POOF_BASE_COLOR = (150, 150, 150)  # Mixed with segment color

UP = (0, -1);
DOWN = (0, 1);
LEFT = (-1, 0);
RIGHT = (1, 0)
SEGMENT_TYPES = ["RED", "BLUE", "GREEN"]
FOOD_TYPES = ["RED_FOOD", "BLUE_FOOD", "GREEN_FOOD", "UNIVERSAL_FOOD"]


class Segment:
    def __init__(self, position, seg_type, is_head=False):
        self.position = position
        self.type = seg_type
        self.is_head = is_head
        self.happiness_max = 100
        self.happiness = self.happiness_max * 0.75  # Start a bit happier
        self.preferred_food_map = {"RED": "RED_FOOD", "BLUE": "BLUE_FOOD", "GREEN": "GREEN_FOOD"}
        self.pulse_anim = random.uniform(0, math.pi * 2)  # For subtle pulsing based on happiness
        self.pulse_speed = 0.1

    def update_happiness(self, food_eaten=None, food_type_eaten=None):
        decay_rate = 0.4  # Slightly less decay
        if self.type == "GREEN" and self.happiness > self.happiness_max * 0.6: decay_rate = 0.2
        self.happiness -= decay_rate
        bonus_score_signal = False

        if food_eaten and food_type_eaten:
            gain = 0
            if food_type_eaten == "UNIVERSAL_FOOD":
                gain = 20  # Universal is good but not best
            elif food_type_eaten == self.preferred_food_map.get(self.type):
                gain = 45
                if self.type == "BLUE" and self.happiness > self.happiness_max * 0.5:
                    bonus_score_signal = True
            else:
                gain = 3  # Small gain even for non-preferred
            self.happiness += gain
        self.happiness = max(0, min(self.happiness, self.happiness_max))
        return bonus_score_signal

    def update_animation(self):
        self.pulse_anim += self.pulse_speed * (self.happiness / self.happiness_max + 0.5)  # Pulse faster when happier
        if self.pulse_anim > math.pi * 2: self.pulse_anim -= math.pi * 2

    def get_color(self):
        if self.is_head: return COLOR_HEAD

        base_color_map = {
            "RED": COLOR_RED_SEG_BASE, "BLUE": COLOR_BLUE_SEG_BASE, "GREEN": COLOR_GREEN_SEG_BASE
        }
        base_color = list(base_color_map.get(self.type, (100, 100, 100)))

        # Intensity based on happiness
        intensity_factor = 0.4 + 0.6 * (self.happiness / self.happiness_max)
        # Pulsing brightness based on animation
        pulse_factor = 0.9 + abs(math.sin(self.pulse_anim)) * 0.1  # Subtle pulse

        final_intensity = intensity_factor * pulse_factor
        return tuple(int(c * final_intensity) for c in base_color)


class Snake:
    def __init__(self):
        self.initial_pos = (GRID_WIDTH // 2, GRID_HEIGHT // 2)
        first_seg_type = random.choice(SEGMENT_TYPES)
        self.body = [Segment(self.initial_pos, first_seg_type, is_head=True)]
        # Add a couple more starting segments for immediate visual
        for i in range(1, 3):
            self.body.append(Segment(self.initial_pos, random.choice(SEGMENT_TYPES)))

        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.grow_food_type_buffer = None

    def move_and_update(self, food_eaten_this_tick=None, food_type_eaten=None):
        events = []  # For particle effects like detachment
        old_positions = [seg.position for seg in self.body]

        head = self.body[0]
        head_x, head_y = head.position
        dir_x, dir_y = self.direction
        new_head_pos = ((head_x + dir_x) % GRID_WIDTH, (head_y + dir_y) % GRID_HEIGHT)
        head.position = new_head_pos

        total_bonus_score_signal = head.update_happiness(food_eaten_this_tick, food_type_eaten)
        head.update_animation()

        for i in range(1, len(self.body)):
            segment = self.body[i]
            segment.position = old_positions[i - 1]
            if segment.update_happiness(food_eaten_this_tick, food_type_eaten):
                total_bonus_score_signal = True
            segment.update_animation()

        if self.grow_food_type_buffer:
            new_seg_type = "RED"
            if self.grow_food_type_buffer == "RED_FOOD":
                new_seg_type = "RED"
            elif self.grow_food_type_buffer == "BLUE_FOOD":
                new_seg_type = "BLUE"
            elif self.grow_food_type_buffer == "GREEN_FOOD":
                new_seg_type = "GREEN"
            elif self.grow_food_type_buffer == "UNIVERSAL_FOOD":
                new_seg_type = random.choice(SEGMENT_TYPES)

            pos_for_new_segment = old_positions[
                -1] if old_positions else self.initial_pos  # old_positions might be empty if snake is just head
            self.body.append(Segment(pos_for_new_segment, new_seg_type))
            self.grow_food_type_buffer = None

        detached_count = 0
        for i in range(len(self.body) - 1, 0, -1):  # Iterate backwards, exclude head
            if self.body[i].happiness <= 0:
                seg_pos_pixels = (self.body[i].position[0] * GRID_SIZE + GRID_SIZE // 2,
                                  self.body[i].position[1] * GRID_SIZE + GRID_SIZE // 2)
                events.append({"type": "detach_poof", "pos": seg_pos_pixels, "color": self.body[i].get_color()})
                self.body.pop(i)
                detached_count += 1

        if head.happiness <= 0: return False, total_bonus_score_signal, detached_count, events
        return True, total_bonus_score_signal, detached_count, events

    def set_grow_flag(self, food_type):
        self.grow_food_type_buffer = food_type

    def check_collision_self(self):
        return self.body[0].position in [s.position for s in self.body[1:]]

    def get_passive_speed_modifier(self):  # Speed modifier based on happy RED segments
        modifier = 1.0
        happy_red_count = sum(1 for seg in self.body if seg.type == "RED" and seg.happiness > seg.happiness_max * 0.75)
        if happy_red_count > 0: modifier += happy_red_count * 0.06  # Slightly more boost
        # Unhappy segments could also slow down the snake
        unhappy_any_count = sum(
            1 for seg in self.body[1:] if seg.happiness < seg.happiness_max * 0.25)  # Exclude head for this
        modifier -= unhappy_any_count * 0.03
        return max(0.5, modifier)  # Ensure snake doesn't stop or reverse speed

    def draw(self, surface):
        for segment_obj in self.body:
            rect = pygame.Rect(segment_obj.position[0] * GRID_SIZE, segment_obj.position[1] * GRID_SIZE, GRID_SIZE,
                               GRID_SIZE)
            pygame.draw.rect(surface, segment_obj.get_color(), rect, border_radius=3)  # Rounded rects
            pygame.draw.rect(surface, tuple(c // 2 for c in segment_obj.get_color()[:3]), rect, 1,
                             border_radius=3)  # Darker outline


class Food:
    def __init__(self):
        self.position = (0, 0)
        self.type = random.choice(FOOD_TYPES)
        self.color_map = {"RED_FOOD": COLOR_RED_FOOD, "BLUE_FOOD": COLOR_BLUE_FOOD,
                          "GREEN_FOOD": COLOR_GREEN_FOOD, "UNIVERSAL_FOOD": COLOR_UNIVERSAL_FOOD}
        self.color = self.color_map[self.type]
        self.pulse_anim = random.uniform(0, math.pi * 2)
        self.pulse_speed = 0.12
        self.base_radius = GRID_SIZE // 2 - 2
        self.spawn_randomly([])

    def spawn_randomly(self, snake_body_positions):
        while True:
            self.position = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
            if self.position not in snake_body_positions: break
        self.type = random.choice(FOOD_TYPES)
        self.color = self.color_map[self.type]
        self.pulse_anim = random.uniform(0, math.pi * 2)

    def update_animation(self):
        self.pulse_anim += self.pulse_speed
        if self.pulse_anim > math.pi * 2: self.pulse_anim -= math.pi * 2

    def draw(self, surface):
        self.update_animation()
        center_x = self.position[0] * GRID_SIZE + GRID_SIZE // 2
        center_y = self.position[1] * GRID_SIZE + GRID_SIZE // 2
        current_radius_offset = math.sin(self.pulse_anim) * 2.5
        current_radius = self.base_radius + current_radius_offset

        # Glow effect
        glow_radius = current_radius + 4
        glow_alpha = 70 + int(abs(math.sin(self.pulse_anim)) * 30)
        glow_color = self.color[:3] + (glow_alpha,)
        pygame.draw.circle(surface, glow_color, (center_x, center_y), int(glow_radius))

        pygame.draw.circle(surface, self.color, (center_x, center_y), int(current_radius))
        pygame.draw.circle(surface, BLACK, (center_x, center_y), int(current_radius), 1)


class Game:
    def __init__(self):
        if not pygame.get_init(): pygame.init(); pygame.mixer.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Snake 2: Symbiotic Anarchy")
        self.clock = pygame.time.Clock()
        try:
            self.font = pygame.font.SysFont("Consolas", 24)
            self.small_font = pygame.font.SysFont("Consolas", 18)
        except pygame.error:
            self.font = pygame.font.Font(None, 30);
            self.small_font = pygame.font.Font(None, 24)

        self.particle_system = ParticleSystem()
        self.reset_game()

    def reset_game(self):
        self.snake = Snake()
        self.food = Food()
        self.food.spawn_randomly([seg.position for seg in self.snake.body])
        self.score = 0
        self.game_over_flag = False;
        self.paused = False;
        self.game_over_reason = ""
        self.particle_system.clear()

    def display_ui(self):  # Same as before
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        if self.snake.body:
            avg_happiness = sum(s.happiness for s in self.snake.body) / len(self.snake.body)
            avg_happy_text = self.small_font.render(f"Avg Happiness: {avg_happiness:.1f}%", True, WHITE)
            self.screen.blit(avg_happy_text, (10, 40))
            head_happy_text = self.small_font.render(f"Head Happiness: {self.snake.body[0].happiness:.1f}%", True,
                                                     WHITE)
            self.screen.blit(head_happy_text, (10, 70))
        # Display current speed modifier
        speed_mod_text = self.small_font.render(f"Speed Mod: {self.snake.get_passive_speed_modifier():.2f}x", True,
                                                WHITE)
        self.screen.blit(speed_mod_text, (10, 100))

    def game_over_screen(self):  # Same, ensure no pygame.quit()
        self.screen.fill(BLACK)
        title_text = self.font.render("GAME OVER", True, COLOR_RED_SEG_BASE)
        reason_text = self.small_font.render(self.game_over_reason, True, WHITE)
        score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
        restart_text = self.font.render("R: Restart | Q: Menu", True, WHITE)
        self.screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 3 - 30))
        self.screen.blit(reason_text, (SCREEN_WIDTH // 2 - reason_text.get_width() // 2, SCREEN_HEIGHT // 3 + 20))
        self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 3 + 70))
        self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 3 + 120))
        pygame.display.flip()
        waiting = True
        while waiting:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT: pygame.event.post(pygame.event.Event(pygame.QUIT)); return
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_q: self.game_over_flag = True; waiting = False
                    if ev.key == pygame.K_r: self.reset_game(); waiting = False
            self.clock.tick(FPS)

    def run(self):
        running = True
        while running:
            food_eaten_this_tick = False
            food_type_eaten_this_tick = None
            for event in pygame.event.get():
                if event.type == pygame.QUIT: running = False
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
                    elif event.key == pygame.K_ESCAPE:
                        running = False

            if not running: break
            if self.game_over_flag:
                self.game_over_screen()
                if self.game_over_flag: running = False; break  # If Q pressed in game_over
                continue  # If R pressed, loop continues

            if self.paused:
                pause_text = self.font.render("PAUSED", True, COLOR_UNIVERSAL_FOOD)
                self.screen.blit(pause_text, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2,
                                              SCREEN_HEIGHT // 2 - pause_text.get_height() // 2))
                pygame.display.flip();
                self.clock.tick(FPS);
                continue

            # Food eaten check
            if self.snake.body and self.snake.body[0].position == self.food.position:  # Check if snake body exists
                food_eaten_this_tick = True
                food_type_eaten_this_tick = self.food.type
                self.snake.set_grow_flag(self.food.type)
                self.score += 10
                # Food eat particles
                food_center_x = self.food.position[0] * GRID_SIZE + GRID_SIZE // 2
                food_center_y = self.food.position[1] * GRID_SIZE + GRID_SIZE // 2
                p_color = list(self.food.color)
                if len(p_color) == 3:
                    p_color.append(200)
                else:
                    p_color[3] = 200
                self.particle_system.emit(food_center_x, food_center_y, 15, p_color, 4, 15,
                                          velocity_x_range=(-1.5, 1.5), velocity_y_range=(-1.5, 1.5), gravity=0.05)
                self.food.spawn_randomly([seg.position for seg in self.snake.body])

            if not self.snake.body:  # If snake somehow became empty (shouldn't happen if head death is game over)
                self.game_over_flag = True;
                self.game_over_reason = "Snake vanished entirely!";
                continue

            snake_alive, bonus_score_signal, detached_segments, snake_events = self.snake.move_and_update(
                food_eaten_this_tick, food_type_eaten_this_tick)
            if bonus_score_signal: self.score += 20
            if detached_segments > 0: self.score = max(0, self.score - detached_segments * 5)

            # Process snake events for particles
            for event_data in snake_events:
                if event_data["type"] == "detach_poof":
                    base_poof_color = event_data["color"][:3]  # Get RGB from segment
                    mixed_color = tuple((base_poof_color[i] + DETACH_POOF_BASE_COLOR[i]) // 2 for i in range(3))
                    self.particle_system.emit(
                        event_data["pos"][0], event_data["pos"][1],
                        count=25, color=mixed_color + (180,), base_size=5, base_lifespan=25,
                        velocity_x_range=(-2, 2), velocity_y_range=(-2, 2), gravity=0.02,
                        shrink_rate=0.2, fade_rate=8
                    )

            # Happiness/Unhappiness particles for segments
            for seg in self.snake.body:
                if seg.is_head: continue
                center_x = seg.position[0] * GRID_SIZE + GRID_SIZE // 2
                center_y = seg.position[1] * GRID_SIZE + GRID_SIZE // 2

                if seg.happiness > seg.happiness_max * 0.85 and random.random() < 0.15:  # Very happy, more particles
                    self.particle_system.emit(center_x, center_y, 1, seg.get_color()[:3] + (80,),
                                              random.uniform(1.5, 2.5), 8, velocity_y_range=(-0.6, -0.2),
                                              shrink_rate=0.15, fade_rate=12)
                elif seg.happiness < seg.happiness_max * 0.15 and random.random() < 0.2:  # Very unhappy, smoky
                    self.particle_system.emit(center_x, center_y, 1, UNHAPPY_SMOKE_COLOR,
                                              random.uniform(2, 4), 20, velocity_y_range=(0.05, 0.2),
                                              shrink_rate=0.05, fade_rate=5)

            if not snake_alive: self.game_over_flag = True; self.game_over_reason = "Head segment perished from unhappiness!"
            if self.snake.check_collision_self(): self.game_over_flag = True; self.game_over_reason = "Snake collided with itself!"
            if not self.snake.body and not self.game_over_flag:  # Should be caught by head death first
                self.game_over_flag = True;
                self.game_over_reason = "Snake completely disbanded!"

            self.particle_system.update()

            self.screen.fill(BLACK)
            # Optional subtle background pattern
            bg_pattern_surf = pygame.Surface((GRID_SIZE * 2, GRID_SIZE * 2), pygame.SRCALPHA)
            pygame.draw.line(bg_pattern_surf, (20, 20, 20, 100), (0, GRID_SIZE), (GRID_SIZE * 2, GRID_SIZE))
            pygame.draw.line(bg_pattern_surf, (20, 20, 20, 100), (GRID_SIZE, 0), (GRID_SIZE, GRID_SIZE * 2))
            for x_bg in range(-GRID_SIZE, SCREEN_WIDTH, GRID_SIZE * 2):
                for y_bg in range(-GRID_SIZE, SCREEN_HEIGHT, GRID_SIZE * 2):
                    self.screen.blit(bg_pattern_surf, (x_bg, y_bg))

            self.particle_system.draw(self.screen)
            self.food.draw(self.screen)
            if self.snake.body: self.snake.draw(self.screen)  # Check if snake body exists before drawing

            self.display_ui()
            pygame.display.flip()

            current_fps = FPS * self.snake.get_passive_speed_modifier()
            self.clock.tick(current_fps)