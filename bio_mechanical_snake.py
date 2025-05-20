import pygame
import random
import sys
import math

# Attempt to import ParticleSystem
try:
    from particles import Particle, ParticleSystem  # Assuming particles.py is in the same directory
except ImportError:
    print("particles.py not found, defining Particle classes locally for bio_mechanical_snake.py")


    # --- PASTE Particle and ParticleSystem classes from particles.py here if running standalone ---
    class Particle:
        def __init__(self, x, y, color, size, lifespan, velocity_x_range=(-1, 1), velocity_y_range=(-1, 1), gravity=0,
                     shrink_rate=0.05, fade_rate=5):
            self.x = x;
            self.y = y;
            self.size = random.uniform(size * 0.7, size * 1.3);
            self.initial_size = self.size
            self.color = list(color);
            if len(self.color) == 3:
                self.color.append(255)
            elif len(self.color) == 4:
                self.color[3] = min(255, max(0, int(self.color[3])))
            self.initial_alpha = self.color[3]
            self.lifespan = random.uniform(lifespan * 0.8, lifespan * 1.2);
            self.initial_lifespan = self.lifespan
            self.vx = random.uniform(velocity_x_range[0], velocity_x_range[1]);
            self.vy = random.uniform(velocity_y_range[0], velocity_y_range[1])
            self.gravity = gravity;
            self.shrink_rate = shrink_rate;
            self.fade_rate = fade_rate

        def update(self):
            self.lifespan -= 1;
            if self.lifespan <= 0: return False
            self.vy += self.gravity;
            self.x += self.vx;
            self.y += self.vy
            self.size -= self.shrink_rate;
            if self.size < 0: self.size = 0
            self.color[3] = max(0, int(self.color[3] - self.fade_rate))
            return True

        def draw(self, surface, camera_offset_x=0, camera_offset_y=0):
            if self.size <= 0 or self.color[3] <= 0: return
            draw_color = tuple(self.color) if len(self.color) == 4 else tuple(list(self.color)[:3] + [255])
            try:
                if draw_color[3] > 0: pygame.draw.circle(surface, draw_color,
                                                         (int(self.x - camera_offset_x), int(self.y - camera_offset_y)),
                                                         int(self.size))
            except (TypeError, ValueError):
                pass


    class ParticleSystem:
        def __init__(self):
            self.particles = []

        def add_particle(self, particle_instance):
            self.particles.append(particle_instance)

        def emit(self, x, y, count, color, base_size, base_lifespan, **kwargs):
            for _ in range(count): self.particles.append(Particle(x, y, color, base_size, base_lifespan, **kwargs))

        def update(self):
            for i in range(len(self.particles) - 1, -1, -1):
                if not self.particles[i].update(): self.particles.pop(i)

        def draw(self, surface, camera_offset_x=0, camera_offset_y=0):
            for p in self.particles: p.draw(surface, camera_offset_x, camera_offset_y)

        def clear(self):
            self.particles.clear()
    # --- END OF PASTED PARTICLE CLASSES ---

# --- Constants ---
SCREEN_WIDTH = 1000;
SCREEN_HEIGHT = 750;
FPS = 30
DEEP_SPACE_BLUE = (5, 0, 25);
STAR_COLORS = [(255, 255, 255), (220, 220, 255), (255, 255, 200), (255, 200, 200)]
WHITE_COLOR = (255, 255, 255);
GREY_COLOR = (128, 128, 128);
DARK_GREY_COLOR = (50, 50, 50);
BLACK_COLOR = (0, 0, 0)
SNAKE_BASE_COLOR = (90, 150, 200);
SNAKE_HEAD_COLOR = (255, 90, 30)
THRUSTER_MODULE_COLOR = (255, 200, 0);
SHIELD_MODULE_COLOR = (60, 180, 255);
WEAPON_MODULE_COLOR = (220, 60, 60)
PROJECTILE_COLOR = (255, 120, 120);
ENEMY_DRONE_COLOR = (180, 80, 220);
ENEMY_PROJECTILE_COLOR = (120, 255, 120)
ASTEROID_COLORS = [(110, 70, 40), (139, 69, 19), (100, 100, 100)]
TECH_DEBRIS_THRUSTER_COLOR = (200, 160, 0);
TECH_DEBRIS_SHIELD_COLOR = (0, 150, 200);
TECH_DEBRIS_WEAPON_COLOR = (180, 30, 30)
CONSTELLATION_SHARD_COLOR = (230, 230, 255);
COMET_CORE_COLOR = (200, 220, 255);
COMET_TAIL_BASE_COLOR = (150, 180, 220)
NEBULA_PARTICLE_COLORS = [(100, 0, 150), (0, 100, 150), (120, 50, 180)]
BLACK_HOLE_CORE_COLOR = (5, 5, 5);
BLACK_HOLE_ACCRETION_COLORS = [(255, 100, 50), (255, 150, 50), (200, 200, 200)]


# --- Helper Functions ---
def normalize_vector(v): l = math.sqrt(v[0] ** 2 + v[1] ** 2);return (0, 0) if l == 0 else (v[0] / l, v[1] / l)


def distance(p1, p2): return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def angle_to_vector(angle_rad): return (math.cos(angle_rad), math.sin(angle_rad))


def vector_to_angle(vx, vy): return math.atan2(vy, vx)


def lerp(a, b, t): return a + (b - a) * t


class Star:
    def __init__(self, x, y, world_w, world_h):
        self.x = x;
        self.y = y;
        self.world_w = world_w;
        self.world_h = world_h;
        self.color = random.choice(STAR_COLORS)
        self.base_size = random.randint(1, 3);
        self.parallax_factor = random.uniform(0.05, 0.4)
        self.twinkle_speed = random.uniform(0.05, 0.2);
        self.twinkle_timer = random.uniform(0, math.pi * 2);
        self.current_size = self.base_size

    def update(self):
        self.twinkle_timer += self.twinkle_speed
        if self.twinkle_timer > math.pi * 2: self.twinkle_timer -= math.pi * 2
        self.current_size = self.base_size + math.sin(self.twinkle_timer) * 0.5

    def draw(self, surface, cam_x, cam_y):
        self.update();
        if self.current_size < 0.5: return
        cam_world_offset_x = (cam_x * self.parallax_factor) // self.world_w;
        cam_world_offset_y = (cam_y * self.parallax_factor) // self.world_h
        for i in range(-1, 2):
            for j in range(-1, 2):
                draw_x_wrapped = self.x - (cam_x - (cam_world_offset_x + i) * self.world_w) * self.parallax_factor
                draw_y_wrapped = self.y - (cam_y - (cam_world_offset_y + j) * self.world_h) * self.parallax_factor
                if 0 <= draw_x_wrapped <= SCREEN_WIDTH and 0 <= draw_y_wrapped <= SCREEN_HEIGHT:
                    pygame.draw.circle(surface, self.color, (int(draw_x_wrapped), int(draw_y_wrapped)),
                                       int(self.current_size))


class Projectile:
    def __init__(self, x, y, angle_rad, speed, color, damage, owner_type="player", p_system_ref=None):
        self.x = x;
        self.y = y;
        self.radius = 3 if owner_type == "player" else 4;
        self.color = color;
        self.speed = speed
        self.vx, self.vy = angle_to_vector(angle_rad);
        self.vx *= speed;
        self.vy *= speed;
        self.lifespan = 1.2 * FPS;
        self.damage = damage
        self.owner_type = owner_type;
        self.p_system_ref = p_system_ref;
        self.trail_emit_cooldown = 1;
        self.trail_cooldown_counter = 0

    def update(self):
        self.x += self.vx;
        self.y += self.vy;
        self.lifespan -= 1;
        self.trail_cooldown_counter -= 1
        if self.p_system_ref and self.trail_cooldown_counter <= 0:
            self.p_system_ref.emit(self.x, self.y, 1, self.color[:3] + (random.randint(80, 150),), self.radius * 0.6, 8,
                                   velocity_x_range=(-0.1, 0.1), velocity_y_range=(-0.1, 0.1), shrink_rate=0.15,
                                   fade_rate=15)
            self.trail_cooldown_counter = self.trail_emit_cooldown
        return self.lifespan > 0

    def draw(self, surface, cam_x, cam_y):
        pygame.draw.circle(surface, self.color, (int(self.x - cam_x), int(self.y - cam_y)), self.radius)
        core_color = (min(255, self.color[0] + 50), min(255, self.color[1] + 50), min(255, self.color[2] + 50))
        pygame.draw.circle(surface, core_color, (int(self.x - cam_x), int(self.y - cam_y)), self.radius // 2)


class CelestialBody:
    def __init__(self, x, y, r, c, type="asteroid", val=1, custom_vel=None):
        self.x = x;
        self.y = y;
        self.radius = r;
        self.base_radius = r;
        self.color = c;
        self.type = type;
        self.value = val
        self.velocity = list(custom_vel) if custom_vel else [random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5)]
        self.mass = r;
        self.rotation_angle = random.uniform(0, math.pi * 2);
        self.rotation_speed = random.uniform(-0.02, 0.02) if type == "asteroid" else 0
        self.affected_by_nebula = False;
        self.pulse_anim = random.uniform(0, math.pi * 2)

    def update(self, gravity_sources=[], p_system_ref=None):
        self.affected_by_nebula = False;
        original_max_speed = 2 if self.type != "comet" else 7
        for gx, gy, gmass, gtype in gravity_sources:
            dist_val = distance((self.x, self.y), (gx, gy));
            if dist_val < 1: dist_val = 1
            pull_str_f = 0.05;
            if gtype == "black_hole": pull_str_f = 0.6;
            if dist_val < gmass * 0.1: pull_str_f *= 4
            force_mag = (gmass / (dist_val * dist_val)) * pull_str_f
            direction = normalize_vector((gx - self.x, gy - self.y))
            self.velocity[0] += direction[0] * force_mag;
            self.velocity[1] += direction[1] * force_mag
        current_max_speed = original_max_speed
        speed = math.sqrt(self.velocity[0] ** 2 + self.velocity[1] ** 2)
        if speed > current_max_speed: self.velocity = [(v / speed) * current_max_speed for v in self.velocity]
        self.x += self.velocity[0];
        self.y += self.velocity[1];
        self.rotation_angle += self.rotation_speed
        self.pulse_anim = (self.pulse_anim + 0.1) % (math.pi * 2)
        self.radius = self.base_radius + math.sin(
            self.pulse_anim) * 1 if self.type == "constellation_shard" else self.base_radius
        if self.type == "comet" and p_system_ref and random.random() < 0.8:
            tail_angle = vector_to_angle(-self.velocity[0], -self.velocity[1])
            p_system_ref.emit(self.x, self.y, 2, COMET_TAIL_BASE_COLOR[:3] + (random.randint(50, 120),),
                              self.radius * random.uniform(0.4, 0.8), random.randint(20, 40),
                              velocity_x_range=(math.cos(tail_angle) * 0.5 - 0.3, math.cos(tail_angle) * 0.5 + 0.3),
                              velocity_y_range=(math.sin(tail_angle) * 0.5 - 0.3, math.sin(tail_angle) * 0.5 + 0.3),
                              shrink_rate=0.1, fade_rate=3 + random.randint(0, 3))
        self.x %= Game.WORLD_WIDTH;
        self.y %= Game.WORLD_HEIGHT

    def draw(self, surface, cam_x, cam_y):
        dx = int(self.x - cam_x);
        dy = int(self.y - cam_y)
        if self.type == "asteroid":
            points = [];
            num_sides = random.choice([5, 6, 7])
            for i in range(num_sides):
                angle = self.rotation_angle + (math.pi * 2 / num_sides * i)
                r_offset = self.radius * random.uniform(0.75, 1.25)
                px = dx + r_offset * math.cos(angle);
                py = dy + r_offset * math.sin(angle)
                points.append((px, py))
            pygame.draw.polygon(surface, self.color, points)
            pygame.draw.polygon(surface, tuple(int(c // 1.5) for c in self.color), points, 2)  # Ensure int
        else:
            pygame.draw.circle(surface, self.color, (dx, dy), int(self.radius))
        if self.type.startswith("tech_debris") or self.type == "constellation_shard":
            pygame.draw.circle(surface, WHITE_COLOR, (dx, dy), int(self.radius), 2)
            if random.random() < 0.05:
                glint_angle = random.uniform(0, math.pi * 2);
                glint_len = self.radius * 1.5
                gx_s = dx + self.radius * 0.5 * math.cos(glint_angle);
                gy_s = dy + self.radius * 0.5 * math.sin(glint_angle)
                gx_e = dx + glint_len * math.cos(glint_angle);
                gy_e = dy + glint_len * math.sin(glint_angle)
                pygame.draw.line(surface, WHITE_COLOR, (int(gx_s), int(gy_s)), (int(gx_e), int(gy_e)), 1)


class NebulaCloud:
    def __init__(self, x, y, radius, density_factor=0.0005):
        self.x = x;
        self.y = y;
        self.radius = radius;
        self.particles = ParticleSystem()
        num_particles = int(math.pi * radius ** 2 * density_factor)
        for _ in range(num_particles):
            px_offset = random.uniform(-radius, radius);
            py_offset = random.uniform(-radius, radius)
            if distance((0, 0), (px_offset, py_offset)) < radius:
                particle_color = random.choice(NEBULA_PARTICLE_COLORS)
                self.particles.add_particle(
                    Particle(x + px_offset, y + py_offset, particle_color[:3] + (random.randint(10, 40),),
                             random.uniform(15, 45), float('inf'), velocity_x_range=(-0.03, 0.03),
                             velocity_y_range=(-0.03, 0.03), gravity=0, shrink_rate=0, fade_rate=0))

    def is_inside(self, px, py):
        return distance((self.x, self.y), (px, py)) < self.radius

    def update(self):
        self.particles.update()

    def draw(self, surface, cam_x, cam_y):
        self.particles.draw(surface, cam_x, cam_y)


class Singularity:
    def __init__(self, x, y, radius, event_horizon_radius):
        self.x = x;
        self.y = y;
        self.radius = radius;
        self.event_horizon_radius = event_horizon_radius
        self.color = BLACK_HOLE_CORE_COLOR;
        self.gravity_mass = 2500
        self.accretion_particles = []
        for _ in range(120):
            self.accretion_particles.append(
                [random.uniform(0, math.pi * 2), random.uniform(radius * 1.2, event_horizon_radius * 1.6),
                 random.uniform(0.005, 0.025), random.randint(0, len(BLACK_HOLE_ACCRETION_COLORS) - 1)])

    def update(self, p_system_ref):
        for p_data in self.accretion_particles:
            p_data[0] += p_data[2];
            p_data[1] -= 0.025
            if p_data[1] < self.radius * 1.05: p_data[1] = random.uniform(self.event_horizon_radius * 1.3,
                                                                          self.event_horizon_radius * 1.6);p_data[
                0] = random.uniform(0, math.pi * 2)
        if p_system_ref and random.random() < 0.25:
            angle_to_center = random.uniform(0, math.pi * 2);
            dist_from_edge = self.event_horizon_radius * random.uniform(1.6, 2.8)
            s_x = self.x + math.cos(angle_to_center) * dist_from_edge;
            s_y = self.y + math.sin(angle_to_center) * dist_from_edge
            suck_vel_mag = random.uniform(0.5, 1.0);
            suck_dir = normalize_vector((self.x - s_x, self.y - s_y))
            p_system_ref.emit(s_x, s_y, 1, random.choice(BLACK_HOLE_ACCRETION_COLORS)[:3] + (random.randint(80, 150),),
                              random.uniform(1, 4), random.randint(15, 25), shrink_rate=0.15, fade_rate=8,
                              velocity_x_range=(suck_dir[0] * suck_vel_mag - 0.1, suck_dir[0] * suck_vel_mag + 0.1),
                              velocity_y_range=(suck_dir[1] * suck_vel_mag - 0.1, suck_dir[1] * suck_vel_mag + 0.1))

    def draw(self, surface, cam_x, cam_y):
        dx = int(self.x - cam_x);
        dy = int(self.y - cam_y)
        for angle, dist, speed, color_idx in self.accretion_particles:
            px = dx + dist * math.cos(angle);
            py = dy + dist * math.sin(angle)
            p_size = max(1, int(3.5 * (self.event_horizon_radius / (dist + 0.1))))
            p_color = BLACK_HOLE_ACCRETION_COLORS[color_idx]
            pygame.draw.circle(surface, p_color, (int(px), int(py)), p_size)
        pygame.draw.circle(surface, self.color, (dx, dy), self.radius)


class EnemyDrone:
    def __init__(self, x, y):
        self.x = x;
        self.y = y;
        self.radius = 9;
        self.color = ENEMY_DRONE_COLOR;
        self.speed = random.uniform(1.2, 1.8)
        self.health = 40;
        self.shoot_cooldown_max = random.uniform(1.2, 2.0) * FPS;
        self.shoot_cooldown = random.randint(0, int(self.shoot_cooldown_max))
        self.target_angle = 0;
        self.current_angle = random.uniform(0, math.pi * 2);
        self.turn_speed = 0.04
        self.dodge_timer = 0;
        self.dodge_direction = 0

    def update(self, player_head_pos, projectiles_list_ref, p_system_ref):
        dx = player_head_pos[0] - self.x;
        dy = player_head_pos[1] - self.y;
        dist_to_player = math.sqrt(dx ** 2 + dy ** 2)
        if dist_to_player < 0.1: dist_to_player = 0.1
        self.target_angle = vector_to_angle(dx, dy)
        angle_diff = (self.target_angle - self.current_angle + math.pi) % (2 * math.pi) - math.pi
        if angle_diff > self.turn_speed:
            self.current_angle += self.turn_speed
        elif angle_diff < -self.turn_speed:
            self.current_angle -= self.turn_speed
        else:
            self.current_angle = self.target_angle
        if self.dodge_timer > 0:
            self.dodge_timer -= 1;
            perp_angle = self.current_angle + self.dodge_direction * (math.pi / 2)
            self.x += math.cos(perp_angle) * self.speed * 0.7;
            self.y += math.sin(perp_angle) * self.speed * 0.7
        else:
            desired_distance = random.uniform(180, 250)
            if dist_to_player > desired_distance:
                self.x += math.cos(self.current_angle) * self.speed;
                self.y += math.sin(self.current_angle) * self.speed
            elif dist_to_player < desired_distance - 30:
                self.x -= math.cos(self.current_angle) * self.speed * 0.5;
                self.y -= math.sin(
                    self.current_angle) * self.speed * 0.5
            if random.random() < 0.01: self.dodge_timer = int(0.5 * FPS);self.dodge_direction = random.choice([-1, 1])
        self.x %= Game.WORLD_WIDTH;
        self.y %= Game.WORLD_HEIGHT
        self.shoot_cooldown -= 1
        if self.shoot_cooldown <= 0 and dist_to_player < 350:
            projectiles_list_ref.append(
                Projectile(self.x, self.y, self.current_angle, 5, ENEMY_PROJECTILE_COLOR, 8, "enemy", p_system_ref))
            self.shoot_cooldown = self.shoot_cooldown_max
        return self.health > 0

    def take_damage(self, amount, p_system_ref):
        self.health -= amount
        if p_system_ref: p_system_ref.emit(self.x, self.y, random.randint(4, 7), (200, 200, 100, 200),
                                           random.uniform(2, 4), 10, velocity_x_range=(-1.2, 1.2),
                                           velocity_y_range=(-1.2, 1.2), shrink_rate=0.25)

    def draw(self, surface, cam_x, cam_y):
        points = [];
        num_points = 5
        for i in range(num_points):
            angle_offset = (2 * math.pi / num_points) * i;
            px = self.x + self.radius * math.cos(self.current_angle + angle_offset);
            py = self.y + self.radius * math.sin(self.current_angle + angle_offset)
            points.append((int(px - cam_x), int(py - cam_y)))
        pygame.draw.polygon(surface, self.color, points)
        pygame.draw.polygon(surface, WHITE_COLOR, points, 1)
        engine_x = self.x - math.cos(self.current_angle) * self.radius * 0.8;
        engine_y = self.y - math.sin(self.current_angle) * self.radius * 0.8
        engine_glow_color = (255, random.randint(80, 120), random.randint(80, 120), 150 + random.randint(0, 50))
        pygame.draw.circle(surface, engine_glow_color, (int(engine_x - cam_x), int(engine_y - cam_y)),
                           self.radius // 2.5)


class Segment:
    def __init__(self, x, y, r, type="generic"):
        self.x = x;
        self.y = y;
        self.radius = r;
        self.type = type
        self.color_map = {"generic": SNAKE_BASE_COLOR, "thruster": THRUSTER_MODULE_COLOR, "shield": SHIELD_MODULE_COLOR,
                          "weapon": WEAPON_MODULE_COLOR}
        self.color = self.color_map.get(type, SNAKE_BASE_COLOR);
        self.is_shield_active = False;
        self.shield_health = 0
        self.pulse_anim = random.uniform(0, math.pi * 2);
        self.pulse_speed = 0.05

    def update_animation(self):
        self.pulse_anim += self.pulse_speed;
        if self.pulse_anim > math.pi * 2: self.pulse_anim -= math.pi * 2

    def draw(self, surface, cam_x, cam_y, is_head=False, head_angle=0):
        self.update_animation();
        dx = int(self.x - cam_x);
        dy = int(self.y - cam_y)
        current_radius = self.radius * (0.95 + abs(math.sin(self.pulse_anim)) * 0.05) if not is_head else self.radius
        if is_head:
            pygame.draw.circle(surface, SNAKE_HEAD_COLOR, (dx, dy), int(current_radius))
            indicator_len = current_radius * 1.3;
            end_x = dx + indicator_len * math.cos(head_angle);
            end_y = dy + indicator_len * math.sin(head_angle)
            pygame.draw.line(surface, WHITE_COLOR, (dx, dy), (int(end_x), int(end_y)), 3)
            eye_angle_offset = math.pi / 6;
            eye_dist = current_radius * 0.5;
            eye_r = current_radius * 0.2
            for sign in [-1, 1]:
                eye_x = dx + eye_dist * math.cos(head_angle + sign * eye_angle_offset);
                eye_y = dy + eye_dist * math.sin(head_angle + sign * eye_angle_offset)
                pygame.draw.circle(surface, pygame.Color("black"), (int(eye_x), int(eye_y)), int(eye_r))
                pygame.draw.circle(surface, pygame.Color("white"), (int(eye_x) + 1, int(eye_y) - 1), int(eye_r * 0.5))
        else:
            pygame.draw.circle(surface, self.color, (dx, dy), int(current_radius))
        outline_c = tuple(int(c // 1.5) for c in (SNAKE_HEAD_COLOR if is_head else self.color))
        pygame.draw.circle(surface, outline_c, (dx, dy), int(current_radius), 2)
        if self.type == "shield" and self.is_shield_active and self.shield_health > 0:
            shield_cap_factor = 1.0
            if GodSerpent.instance and GodSerpent.instance.shield_module_count > 0:
                shield_cap_factor = GodSerpent.SHIELD_MAX_HEALTH_PER_MODULE * GodSerpent.instance.shield_module_count
            else:
                shield_cap_factor = GodSerpent.SHIELD_MAX_HEALTH_PER_MODULE
            if shield_cap_factor == 0: shield_cap_factor = GodSerpent.SHIELD_MAX_HEALTH_PER_MODULE

            alpha = 80 + int(120 * (self.shield_health / shield_cap_factor))
            shield_c = (SHIELD_MODULE_COLOR[0], SHIELD_MODULE_COLOR[1], SHIELD_MODULE_COLOR[2], max(0, min(255, alpha)))
            shield_radius_factor = 1.3 + abs(math.sin(pygame.time.get_ticks() * 0.01 + self.pulse_anim)) * 0.1
            pygame.draw.circle(surface, shield_c, (dx, dy), int(current_radius * shield_radius_factor))
        elif self.type == "weapon":
            pygame.draw.circle(surface, WHITE_COLOR, (dx, dy), int(current_radius // 3.5))
        elif self.type == "thruster":
            t_color_base = THRUSTER_MODULE_COLOR
            pulse_val = abs(math.sin(pygame.time.get_ticks() * 0.01 + self.pulse_anim * 2))
            t_color_final = (min(255, t_color_base[0] + int(pulse_val * 50)),
                             min(255, t_color_base[1] + int(pulse_val * 30)), t_color_base[2],
                             180 + int(pulse_val * 50))
            pygame.draw.circle(surface, self.color, (dx, dy), int(current_radius))
            pygame.draw.circle(surface, t_color_final, (dx, dy), int(current_radius * 0.65))


class GodSerpent:
    SHIELD_MAX_HEALTH_PER_MODULE = 100;
    instance = None

    def __init__(self, x, y):
        GodSerpent.instance = self;
        self.base_radius = 12
        self.segments = [Segment(x, y, self.base_radius)];
        self.angle = random.uniform(0, math.pi * 2);
        self.speed = 0
        self.max_speed_base = 2.8;
        self.acceleration_base = 0.09;
        self.turn_speed = 0.055;
        self.segment_spacing_factor = 0.75
        self.length_score = 1;
        self.gravity_mass_factor = 18;
        self.thruster_module_count = 0;
        self.shield_module_count = 0
        self.weapon_module_count = 0;
        self.shield_active = False;
        self.current_shield_health = 0
        self.weapon_cooldown_max_base = 0.6 * FPS;
        self.weapon_cooldown = 0;
        self.in_nebula_slow = False;
        self.comet_speed_boost_timer = 0

    @property
    def head(self):
        return self.segments[0]

    @property
    def mass(self):
        return len(self.segments) * self.gravity_mass_factor

    @property
    def max_speed(self):
        boost = 2.5 if self.comet_speed_boost_timer > 0 else 1.0;
        nebula_factor = 0.5 if self.in_nebula_slow else 1.0;
        return (
                self.max_speed_base + self.thruster_module_count * 0.35) * nebula_factor * boost

    @property
    def acceleration(self):
        boost = 1.8 if self.comet_speed_boost_timer > 0 else 1.0;
        nebula_factor = 0.5 if self.in_nebula_slow else 1.0;
        return (
                self.acceleration_base + self.thruster_module_count * 0.02) * nebula_factor * boost

    @property
    def weapon_cooldown_max(self):
        return self.weapon_cooldown_max_base / (1 + self.weapon_module_count * 0.3)

    def grow(self, seg_type="generic"):
        last_seg = self.segments[-1];
        new_seg = Segment(last_seg.x, last_seg.y, self.base_radius, seg_type)
        self.segments.append(new_seg);
        self.length_score += 1
        if seg_type == "thruster":
            self.thruster_module_count += 1
        elif seg_type == "shield":
            self.shield_module_count += 1
        elif seg_type == "weapon":
            self.weapon_module_count += 1

    def update(self, keys, projectiles_list_ref, p_system_ref):
        self.in_nebula_slow = False
        if self.comet_speed_boost_timer > 0: self.comet_speed_boost_timer -= 1
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: self.angle -= self.turn_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: self.angle += self.turn_speed
        is_thrusting = False
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.speed += self.acceleration;
            is_thrusting = True
        else:
            self.speed *= 0.975
        if abs(self.speed) < 0.05: self.speed = 0
        self.speed = max(-self.max_speed / 3, min(self.speed, self.max_speed))
        self.head.x += math.cos(self.angle) * self.speed;
        self.head.y += math.sin(self.angle) * self.speed
        self.head.x %= Game.WORLD_WIDTH;
        self.head.y %= Game.WORLD_HEIGHT
        if is_thrusting and p_system_ref:
            num_thruster_particles = 1 + self.thruster_module_count // 2
            for _ in range(num_thruster_particles):
                if len(self.segments) > 0:
                    last_seg = self.segments[-1];
                    offset_dist = last_seg.radius
                    emit_x = last_seg.x - math.cos(self.angle) * offset_dist;
                    emit_y = last_seg.y - math.sin(self.angle) * offset_dist
                    thrust_angle_visual = self.angle + math.pi + random.uniform(-0.2, 0.2);
                    particle_speed = abs(self.speed) * 0.5 + random.uniform(1, 3)
                    p_system_ref.emit(emit_x, emit_y, 1,
                                      random.choice([(255, 150, 0), (255, 200, 50)])[:3] + (random.randint(150, 220),),
                                      random.uniform(3, 6), random.randint(10, 20), shrink_rate=0.25, fade_rate=10,
                                      velocity_x_range=(math.cos(thrust_angle_visual) * particle_speed - 0.5,
                                                        math.cos(thrust_angle_visual) * particle_speed + 0.5),
                                      velocity_y_range=(math.sin(thrust_angle_visual) * particle_speed - 0.5,
                                                        math.sin(thrust_angle_visual) * particle_speed + 0.5))
        for i in range(1, len(self.segments)):
            leader = self.segments[i - 1];
            follower = self.segments[i];
            target_d = (leader.radius + follower.radius) * self.segment_spacing_factor
            dx_direct = leader.x - follower.x;
            dy_direct = leader.y - follower.y;
            dx_wrap = dx_direct;
            dy_wrap = dy_direct
            if abs(dx_direct) > Game.WORLD_WIDTH / 2: dx_wrap = dx_direct - math.copysign(Game.WORLD_WIDTH, dx_direct)
            if abs(dy_direct) > Game.WORLD_HEIGHT / 2: dy_wrap = dy_direct - math.copysign(Game.WORLD_HEIGHT, dy_direct)
            current_d = math.sqrt(dx_wrap ** 2 + dy_wrap ** 2)
            if current_d > target_d and current_d > 0.1:
                move_f = min(((current_d - target_d) / current_d) * 0.6, 1.0)
                follower.x += dx_wrap * move_f;
                follower.y += dy_wrap * move_f
                follower.x %= Game.WORLD_WIDTH;
                follower.y %= Game.WORLD_HEIGHT
        if self.weapon_cooldown > 0: self.weapon_cooldown -= 1
        if keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL] or keys[pygame.K_SPACE]:
            if self.weapon_module_count > 0 and self.weapon_cooldown <= 0:
                num_shots = 1 + self.weapon_module_count // 2
                for i_shot in range(num_shots):
                    shot_angle = self.angle + (i_shot - (num_shots - 1) / 2) * 0.05
                    projectiles_list_ref.append(
                        Projectile(self.head.x, self.head.y, shot_angle, abs(self.speed) + 6, PROJECTILE_COLOR,
                                   15 + self.weapon_module_count * 2, "player", p_system_ref))
                self.weapon_cooldown = self.weapon_cooldown_max
        if self.shield_active and self.shield_module_count > 0:
            if self.current_shield_health <= 0: self.shield_active = False
        for seg in self.segments:
            if seg.type == "shield": seg.is_shield_active = self.shield_active;seg.shield_health = self.current_shield_health

    def toggle_shield(self):
        if self.shield_module_count > 0 and not self.shield_active:
            self.shield_active = True;
            self.current_shield_health = GodSerpent.SHIELD_MAX_HEALTH_PER_MODULE * self.shield_module_count
        elif self.shield_active:
            self.shield_active = False

    def take_damage(self, amount, p_system_ref=None):
        hit_pos = (self.head.x, self.head.y)
        if self.shield_active and self.current_shield_health > 0:
            self.current_shield_health -= amount
            if p_system_ref: p_system_ref.emit(hit_pos[0], hit_pos[1], 15, SHIELD_MODULE_COLOR[:3] + (220,), 5, 12,
                                               velocity_x_range=(-1.5, 1.5), velocity_y_range=(-1.5, 1.5),
                                               shrink_rate=0.4)
            if self.current_shield_health < 0: self.current_shield_health = 0
            return False
        else:
            actual_hit_segment = self.segments[-1] if len(self.segments) > 1 else self.head
            if p_system_ref: p_system_ref.emit(actual_hit_segment.x, actual_hit_segment.y, 20, (220, 220, 100, 230), 4,
                                               20, velocity_x_range=(-2.5, 2.5), velocity_y_range=(-2.5, 2.5),
                                               gravity=0.03, shrink_rate=0.2)
            if len(self.segments) > 1:
                lost = self.segments.pop();
                self.length_score -= 1
                if lost.type == "thruster":
                    self.thruster_module_count = max(0, self.thruster_module_count - 1)
                elif lost.type == "shield":
                    self.shield_module_count = max(0, self.shield_module_count - 1)
                elif lost.type == "weapon":
                    self.weapon_module_count = max(0, self.weapon_module_count - 1)
                return False
            else:
                if p_system_ref:
                    p_system_ref.emit(hit_pos[0], hit_pos[1], 70, (255, 120, 0, 250), 8, 50, velocity_x_range=(-4, 4),
                                      velocity_y_range=(-4, 4), gravity=0.01, shrink_rate=0.1, fade_rate=4)
                    p_system_ref.emit(hit_pos[0], hit_pos[1], 50, (150, 150, 150, 200), 10, 70,
                                      velocity_x_range=(-2, 2), velocity_y_range=(-2, 2), shrink_rate=0.05, fade_rate=2)
                return True

    def draw(self, surface, cam_x, cam_y):
        for i in range(len(self.segments) - 1, -1, -1): self.segments[i].draw(surface, cam_x, cam_y, is_head=(i == 0),
                                                                              head_angle=self.angle)


class Game:
    WORLD_WIDTH = SCREEN_WIDTH * 3;
    WORLD_HEIGHT = SCREEN_HEIGHT * 3

    def __init__(self):
        if not pygame.get_init(): pygame.init();pygame.mixer.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Snake 2: Bio-Mechanical God Serpent")
        self.clock = pygame.time.Clock()
        try:
            self.font = pygame.font.SysFont("Consolas", 24);
            self.small_font = pygame.font.SysFont("Consolas", 18)
        except pygame.error:
            self.font = pygame.font.Font(None, 30);
            self.small_font = pygame.font.Font(None, 24)
        self.camera_x = 0;
        self.camera_y = 0
        self.stars = [Star(random.randint(0, Game.WORLD_WIDTH), random.randint(0, Game.WORLD_HEIGHT), Game.WORLD_WIDTH,
                           Game.WORLD_HEIGHT) for _ in range(200)]
        self.particle_system = ParticleSystem()
        self.reset_game()

    def reset_game(self):
        self.player = GodSerpent(Game.WORLD_WIDTH // 2, Game.WORLD_HEIGHT // 2)
        self.celestial_bodies = [];
        self.nebula_clouds = [];
        self.singularities = [];
        self.enemy_drones = [];
        self.projectiles = []
        self.num_const_shards_win = 5;
        self.const_shards_collected = 0;
        self.initial_spawn()
        self.score = 0;
        self.game_over_flag = False;
        self.paused = False;
        self.win_flag = False;
        self.game_over_reason = ""
        self.particle_system.clear()

    def initial_spawn(self):
        min_dist = SCREEN_WIDTH / 2.5
        for _ in range(45): self.spawn_celestial_body("asteroid", min_dist_from_player=min_dist)
        for _ in range(7): self.spawn_celestial_body(
            random.choice(["tech_debris_thruster", "tech_debris_shield", "tech_debris_weapon"]),
            min_dist_from_player=min_dist)
        for _ in range(self.num_const_shards_win): self.spawn_celestial_body("constellation_shard",
                                                                             min_dist_from_player=min_dist)
        for _ in range(4): self.spawn_celestial_body("comet", min_dist_from_player=min_dist)
        for _ in range(random.randint(3, 4)): self.nebula_clouds.append(
            NebulaCloud(random.uniform(0, Game.WORLD_WIDTH), random.uniform(0, Game.WORLD_HEIGHT),
                        random.uniform(200, 350)))
        for _ in range(random.randint(2, 3)): self.singularities.append(
            Singularity(random.uniform(0, Game.WORLD_WIDTH), random.uniform(0, Game.WORLD_HEIGHT),
                        random.randint(10, 15), random.randint(70, 100)))
        for _ in range(random.randint(3, 5)): self.enemy_drones.append(
            EnemyDrone(random.uniform(0, Game.WORLD_WIDTH), random.uniform(0, Game.WORLD_HEIGHT)))

    def spawn_celestial_body(self, item_type, position=None, min_dist_from_player=0):
        r_map = {"asteroid": random.randint(10, 25), "tech_debris_thruster": 10, "tech_debris_shield": 10,
                 "tech_debris_weapon": 10, "constellation_shard": 12, "comet": 8}
        c_map = {"asteroid": random.choice(ASTEROID_COLORS), "tech_debris_thruster": TECH_DEBRIS_THRUSTER_COLOR,
                 "tech_debris_shield": TECH_DEBRIS_SHIELD_COLOR,
                 "tech_debris_weapon": TECH_DEBRIS_WEAPON_COLOR, "constellation_shard": CONSTELLATION_SHARD_COLOR,
                 "comet": COMET_CORE_COLOR}
        v_map = {"asteroid": 1, "tech_debris_thruster": 5, "tech_debris_shield": 5, "tech_debris_weapon": 5,
                 "constellation_shard": 20, "comet": 15}
        custom_vel = None
        if item_type == "comet": angle = random.uniform(0, 2 * math.pi);speed = random.uniform(4, 8);custom_vel = (
            math.cos(angle) * speed, math.sin(angle) * speed)
        if position is None:
            spawn_attempts = 0
            while spawn_attempts < 50:
                x = random.uniform(0, Game.WORLD_WIDTH);
                y = random.uniform(0, Game.WORLD_HEIGHT)
                if distance((x, y), (self.player.head.x, self.player.head.y)) > min_dist_from_player: break
                spawn_attempts += 1
            if spawn_attempts == 50: x = random.uniform(0, Game.WORLD_WIDTH);y = random.uniform(0, Game.WORLD_HEIGHT)
        else:
            x, y = position
        new_body = CelestialBody(x, y, r_map[item_type], c_map[item_type], item_type, v_map[item_type], custom_vel)
        self.celestial_bodies.append(new_body)

    def update_camera(self):
        tx = self.player.head.x - SCREEN_WIDTH / 2;
        ty = self.player.head.y - SCREEN_HEIGHT / 2;
        self.camera_x = lerp(
            self.camera_x, tx, 0.08);
        self.camera_y = lerp(self.camera_y, ty, 0.08)

    def display_ui(self):
        score_t = self.font.render(f"Mass: {self.player.length_score}", True, WHITE_COLOR);
        self.screen.blit(score_t, (10, 10))
        shards_t = self.font.render(f"Shards: {self.const_shards_collected}/{self.num_const_shards_win}", True,
                                    CONSTELLATION_SHARD_COLOR);
        self.screen.blit(shards_t, (10, 40))
        mod_y = 70
        thrust_t = self.small_font.render(f"Thrusters: {self.player.thruster_module_count}", True,
                                          THRUSTER_MODULE_COLOR);
        self.screen.blit(thrust_t, (10, mod_y));
        mod_y += 25
        shield_t = self.small_font.render(f"Shields: {self.player.shield_module_count}", True, SHIELD_MODULE_COLOR);
        self.screen.blit(shield_t, (10, mod_y));
        mod_y += 25
        weapon_t = self.small_font.render(f"Weapons: {self.player.weapon_module_count}", True, WEAPON_MODULE_COLOR);
        self.screen.blit(weapon_t, (10, mod_y))
        if self.player.shield_active:
            sh_stat_t = self.small_font.render(f"Shield HP: {int(self.player.current_shield_health)}", True,
                                               WHITE_COLOR)
        elif self.player.shield_module_count > 0:
            sh_stat_t = self.small_font.render("Shield (LSHIFT)", True, GREY_COLOR)
        else:
            sh_stat_t = None
        if sh_stat_t: self.screen.blit(sh_stat_t, (SCREEN_WIDTH - sh_stat_t.get_width() - 10, 10))
        if self.player.weapon_module_count > 0:
            wp_cd_text = "Ready" if self.player.weapon_cooldown <= 0 else f"{(self.player.weapon_cooldown / FPS):.1f}s"
            wp_cd = self.small_font.render(f"Weapon: {wp_cd_text} (LCTRL/SPACE)", True, WHITE_COLOR);
            self.screen.blit(wp_cd, (SCREEN_WIDTH - wp_cd.get_width() - 10, 35))
        if self.player.comet_speed_boost_timer > 0:
            boost_t = self.small_font.render(f"BOOST: {(self.player.comet_speed_boost_timer / FPS):.1f}s", True,
                                             COMET_CORE_COLOR)
            self.screen.blit(boost_t, (SCREEN_WIDTH // 2 - boost_t.get_width() // 2, 10))

    def game_over_or_win_screen(self):
        self.screen.fill(BLACK_COLOR);
        title_msg = "CONSTELLATION FORMED!" if self.win_flag else "SERPENT DESTROYED!"
        title_c = CONSTELLATION_SHARD_COLOR if self.win_flag else SNAKE_HEAD_COLOR;
        title_t = self.font.render(title_msg, True, title_c)
        self.screen.blit(title_t, (SCREEN_WIDTH // 2 - title_t.get_width() // 2, SCREEN_HEIGHT // 3 - 30))
        if not self.win_flag:
            reason_t = self.small_font.render(self.game_over_reason, True, WHITE_COLOR);
            self.screen.blit(reason_t, (SCREEN_WIDTH // 2 - reason_t.get_width() // 2, SCREEN_HEIGHT // 3 + 20))
        score_t = self.font.render(f"Final Mass: {self.player.length_score}", True, WHITE_COLOR);
        self.screen.blit(score_t, (SCREEN_WIDTH // 2 - score_t.get_width() // 2, SCREEN_HEIGHT // 3 + 70))
        restart_t = self.font.render("R: Restart | Q: Menu", True, WHITE_COLOR);
        self.screen.blit(restart_t, (SCREEN_WIDTH // 2 - restart_t.get_width() // 2, SCREEN_HEIGHT // 3 + 120))
        pygame.display.flip();
        waiting = True
        while waiting:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT: pygame.event.post(pygame.event.Event(pygame.QUIT));return
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_q: self.game_over_flag = True;waiting = False
                    if ev.key == pygame.K_r: self.reset_game();waiting = False
            self.clock.tick(FPS)

    def run(self):
        running = True
        while running:
            if self.game_over_flag or self.win_flag:
                self.game_over_or_win_screen()
                if self.game_over_flag or self.win_flag:  # Re-check because R might have been pressed
                    return  # Exit run() method, back to main menu

            keys = pygame.key.get_pressed()
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT: running = False
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_p: self.paused = not self.paused
                    if self.paused: continue
                    if ev.key == pygame.K_LSHIFT: self.player.toggle_shield()
                    if ev.key == pygame.K_ESCAPE: running = False

            if not running: break

            if self.paused:
                pause_text = self.font.render("PAUSED", True, WHITE_COLOR);
                self.screen.blit(pause_text, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2,
                                              SCREEN_HEIGHT // 2 - pause_text.get_height() // 2))
                pygame.display.flip();
                self.clock.tick(FPS);
                continue

            self.player.update(keys, self.projectiles, self.particle_system)
            self.update_camera();
            self.particle_system.update()
            self.player.in_nebula_slow = any(
                n.is_inside(self.player.head.x, self.player.head.y) for n in self.nebula_clouds)
            visual_distortion_in_nebula = self.player.in_nebula_slow  # Define it here

            gravity_sources = [(self.player.head.x, self.player.head.y, self.player.mass, "player")]
            for s_obj in self.singularities: gravity_sources.append(
                (s_obj.x, s_obj.y, s_obj.gravity_mass, "black_hole"));s_obj.update(self.particle_system)

            for body in self.celestial_bodies:
                body.update(gravity_sources, self.particle_system);
                body.affected_by_nebula = any(n.is_inside(body.x, body.y) for n in self.nebula_clouds)
                if body.affected_by_nebula: body.velocity = [v * 0.96 for v in body.velocity]

            drones_to_remove = [];
            for drone in self.enemy_drones:
                if not drone.update((self.player.head.x, self.player.head.y), self.projectiles, self.particle_system):
                    self.particle_system.emit(drone.x, drone.y, 30, (200, 100, 220, 200), 5, 30,
                                              velocity_x_range=(-2, 2), velocity_y_range=(-2, 2), shrink_rate=0.15)
                    self.particle_system.emit(drone.x, drone.y, 20, (100, 100, 100, 150), 7, 40,
                                              velocity_x_range=(-1, 1), velocity_y_range=(-1, 1), shrink_rate=0.05)
                    self.spawn_celestial_body(
                        random.choice(["asteroid", "tech_debris_thruster", "tech_debris_shield", "tech_debris_weapon"]),
                        (drone.x, drone.y))
                    drones_to_remove.append(drone)
            for d in drones_to_remove: self.enemy_drones.remove(d)

            active_projectiles = []
            for p in self.projectiles:
                if p.update():
                    collided = False
                    if p.owner_type == "player":
                        for drone_idx, drone in enumerate(self.enemy_drones):
                            if distance((p.x, p.y), (drone.x, drone.y)) < p.radius + drone.radius: drone.take_damage(
                                p.damage, self.particle_system);collided = True;break
                    elif p.owner_type == "enemy":
                        for seg_idx, segment in enumerate(self.player.segments):
                            if distance((p.x, p.y), (segment.x, segment.y)) < p.radius + segment.radius:
                                if self.player.take_damage(p.damage,
                                                           self.particle_system): self.game_over_flag = True;self.game_over_reason = "Killed by enemy drone!"
                                collided = True;
                                break
                    if not collided: active_projectiles.append(p)
            self.projectiles = active_projectiles

            if self.game_over_flag: continue  # Skip to top of loop if game over by projectile

            bodies_to_remove_indices = []
            for i, body in enumerate(self.celestial_bodies):
                if distance((self.player.head.x, self.player.head.y),
                            (body.x, body.y)) < self.player.head.radius + body.radius:
                    ate_comet = False  # Initialize for each collision check
                    if body.type == "asteroid":
                        self.player.grow("generic")
                    elif body.type == "tech_debris_thruster":
                        self.player.grow("thruster")
                    elif body.type == "tech_debris_shield":
                        self.player.grow("shield")
                    elif body.type == "tech_debris_weapon":
                        self.player.grow("weapon")
                    elif body.type == "comet":
                        self.player.comet_speed_boost_timer = 5 * FPS;
                        self.score += body.value;  # Comets also give score
                        ate_comet = True;  # Mark as comet so it's not added to removal list below
                        self.particle_system.emit(
                            body.x, body.y, 30, COMET_CORE_COLOR[:3] + (200,), 5, 25, velocity_x_range=(-2, 2),
                            velocity_y_range=(-2, 2))
                    elif body.type == "constellation_shard":
                        self.const_shards_collected += 1;
                        # Score for shard is added below if not ate_comet
                        if self.const_shards_collected >= self.num_const_shards_win: self.win_flag = True

                    if not ate_comet:  # All non-comet consumables
                        self.score += body.value;
                        bodies_to_remove_indices.append(i)
                        self.particle_system.emit(body.x, body.y, 10, body.color[:3] + (180,), body.radius * 0.3, 15,
                                                  velocity_x_range=(-1, 1), velocity_y_range=(-1, 1))
                        if random.random() < 0.65 and not self.win_flag:
                            nt_ch = ["asteroid"] * 6 + ["tech_debris_thruster", "tech_debris_shield",
                                                        "tech_debris_weapon"]
                            nt = "asteroid" if random.random() > 0.25 else random.choice(nt_ch)
                            if random.random() < 0.08: nt = "comet"
                            self.spawn_celestial_body(nt, min_dist_from_player=SCREEN_WIDTH / 4)

            for i in sorted(bodies_to_remove_indices, reverse=True):
                if i < len(self.celestial_bodies):
                    del self.celestial_bodies[i]

            for s_obj in self.singularities:
                if distance((self.player.head.x, self.player.head.y),
                            (s_obj.x, s_obj.y)) < s_obj.event_horizon_radius + self.player.head.radius:
                    self.game_over_flag = True
                    self.game_over_reason = "Consumed by a singularity!"
                    break  # Exit this loop, game_over_flag is set

            # ---- Conditional Drawing and End-of-Loop Operations ----
            if not self.game_over_flag and not self.win_flag:
                self.screen.fill(DEEP_SPACE_BLUE)
                for star in self.stars: star.draw(self.screen, self.camera_x, self.camera_y)
                for nebula in self.nebula_clouds: nebula.update(); nebula.draw(self.screen, self.camera_x,
                                                                               self.camera_y)
                for body in self.celestial_bodies: body.draw(self.screen, self.camera_x, self.camera_y)
                for s_obj_draw in self.singularities: s_obj_draw.draw(self.screen, self.camera_x, self.camera_y)

                self.particle_system.draw(self.screen, self.camera_x, self.camera_y)

                for drone in self.enemy_drones: drone.draw(self.screen, self.camera_x, self.camera_y)
                for p in self.projectiles: p.draw(self.screen, self.camera_x, self.camera_y)
                self.player.draw(self.screen, self.camera_x, self.camera_y)

                if visual_distortion_in_nebula:
                    distort_surface = self.screen.copy();
                    distort_surface.set_alpha(20)
                    for i_distort in range(0, SCREEN_HEIGHT, 20):
                        offset_distort = int(math.sin(pygame.time.get_ticks() * 0.0025 + i_distort * 0.07) * 6)
                        try:
                            self.screen.blit(distort_surface, (offset_distort, i_distort),
                                             (0, i_distort, SCREEN_WIDTH, 20))
                        except pygame.error:
                            pass

                self.display_ui()
                pygame.display.flip()

            self.clock.tick(FPS)