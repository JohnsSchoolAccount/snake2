import pygame
import sys
import math  # For potential animations later

# Import the game modes (ensure these files exist and are correct)
try:
    from no_clip_snake import Game as NoClipGame
    from symbiotic_anarchy_snake import Game as SymbioticAnarchyGame
    from ouroboros_paradox_snake import Game as OuroborosParadoxGame
    from bio_mechanical_snake import Game as BioMechanicalGame
except ImportError as e:
    print(f"Error importing game modules: {e}")
    sys.exit()

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60  # Smoother menu animations

# Colors - Theme: Dark Space with Neon/Cyber Accents
COLOR_BACKGROUND = (10, 10, 30)  # Very dark blue
COLOR_TITLE = (0, 220, 255)  # Bright cyan/aqua
COLOR_SUBTITLE = (150, 150, 180)  # Light grey-blue
COLOR_MENU_ITEM_TEXT = (220, 220, 255)  # Light lavender
COLOR_MENU_ITEM_HIGHLIGHT_TEXT = (255, 255, 255)  # White
COLOR_MENU_ITEM_BG = (30, 30, 60)  # Darker blue for button bg
COLOR_MENU_ITEM_HIGHLIGHT_BG = (50, 80, 150)  # Brighter blue on hover
COLOR_MENU_ITEM_BORDER = (80, 80, 120)  # Border for buttons
COLOR_TUTORIAL_TEXT = (230, 230, 240)
COLOR_TUTORIAL_BG = (15, 15, 35)
COLOR_TUTORIAL_BORDER = (60, 60, 90)
COLOR_TUTORIAL_HEADER = (100, 200, 255)

# --- Tutorial Data (from previous response, ensure it's correctly formatted) ---
TUTORIAL_DATA = {
    "No-Clip Nightmare": [
        "[ NO-CLIP NIGHTMARE - 1/3 ]\n\nObjective: Survive & high score!\nClassic Snake, reality-bending twist.\n\nControls:\n  Arrows/WASD: Move\n  SPACE: Toggle No-Clip",
        "[ NO-CLIP NIGHTMARE - 2/3 ]\n\nNo-Clip Mode:\n  - Phase through walls & self!\n  - Consumes [Phase Energy] (green bar).\n  - Recharges when off. No use at 0 energy.\n\nPhasing Sickness:\n  - No-Clip builds [Sickness] (red bar).\n  - High Sickness: Distortions, bad controls.\n  - Max Sickness = Game Over!\n  - Slowly decreases when off.",
        "[ NO-CLIP NIGHTMARE - 3/3 ]\n\nFood:\n  - Yellow: Normal food. Grow & score.\n  - Purple \"Ghost\": High-value! ONLY eatable\n    while No-Clipping.\n\nStrategy: Use No-Clip for escapes or Ghost food.\nBalance use vs. Sickness. Don't break reality!"
    ],
    "Symbiotic Anarchy": [
        "[ SYMBIOTIC ANARCHY - 1/3 ]\n\nObjective: Grow longest, happiest snake!\nEach segment has needs!\n\nControls:\n  - Arrows/WASD: Control Head.",
        "[ SYMBIOTIC ANARCHY - 2/3 ]\n\nSegment Sentience:\n  - Segments (R,G,B) have [Happiness].\n  - Decays over time. Head happiness is CRITICAL!\n\nFood & Happiness:\n  - Red Food: For RED segments.\n  - Blue Food: For BLUE segments.\n  - Green Food: For GREEN segments.\n  - Yellow Universal: Good for ALL.\n  - Preferred food = biggest boost!",
        "[ SYMBIOTIC ANARCHY - 3/3 ]\n\nSegment Abilities (Passive):\n  - Happy RED: Slight speed up.\n  - Happy BLUE (pref. food): Score bonus!\n  - Happy GREEN: Slower happiness decay.\n\nDetachment: Happiness at zero = DETACH!\n(Shortens snake, score penalty).\n\nStrategy: Balance feeding, keep Head happy."
    ],
    "Ouroboros Paradox": [
        "[ OUROBOROS PARADOX - 1/3 ]\n\nObjective: Solve puzzles to reach Red Exit!\nTime loops! Past actions create Echoes.\n\nControls:\n  - Arrows/WASD: Move Snake.",
        "[ OUROBOROS PARADOX - 2/3 ]\n\nTime Loops & Echoes:\n  - Short, repeating loops (see timer).\n  - Snake resets to start on loop end.\n\nSnake Echoes:\n  - Echo of snake from PREVIOUS loop remains.\n  - Default: Obstacles (Game Over on hit).\n  - \"Next Echo\" shows type formed this loop.",
        "[ OUROBOROS PARADOX - 3/3 ]\n\nChrono-Pellets:\n  - Purple \"Solidify\": Next Echo solid & EATABLE.\n  - Cyan \"Phase\": Next Echo intangible.\n  - Orange \"Erase\": Next Echo WON'T form.\n\nStrategy: Use Echoes as tools. Plan across loops.\nUse Chrono-Pellets wisely."
    ],
    "Bio-Mechanical God": [
        "[ BIO-MECHANICAL GOD - 1/4 ]\n\nObjective: Grow colossal! Collect Shards!\nDevour & evolve in space!\n\nControls:\n  Arrows/WASD: Rotate & Thrust (momentum).\n  LSHIFT: Toggle Shield (needs Shield Modules).\n  LCTRL/SPACE: Fire (needs Weapon Modules).",
        "[ BIO-MECHANICAL GOD - 2/4 ]\n\nGrowth & Modules:\n  - Asteroids: Basic growth.\n  - Tech Debris: Adds MODULES!\n      Yellow: THRUSTER | Blue: SHIELD | Red: WEAPON\n  - Comet: Temp speed boost & score! (Pass through).\n  - Shards: Collect to win!\n\nGravitational Pull: Your mass attracts objects.",
        "[ BIO-MECHANICAL GOD - 3/4 ]\n\nHazards & Combat:\n  - Large/Fast Asteroids: Damage segments!\n  - Nebula Clouds: Slow/distort vision.\n  - Singularities: EXTREMELY DANGEROUS!\n  - Enemy Drones: Hostile, will shoot!\n\nCombat & Defense:\n  Shields: Absorb damage. More modules = stronger.\n  Weapons: Destroy Drones. More modules = better.\n  Damage: Strips tail segments. Head loss = Game Over!",
        "[ BIO-MECHANICAL GOD - 4/4 ]\n\nThe Universe:\n  - Space is vast! Wraps around.\n  - Camera follows serpent's head.\n\nStrategy: Get Tech Debris. Use gravity carefully.\nDrones drop loot. Beware Singularities!\n\nBecome the ultimate cosmic entity!"
    ]
}


# Helper to create nice looking text surfaces
def create_text_surface(text, font, color, antialias=True):
    return font.render(text, antialias, color)


class MenuItem:
    def __init__(self, text, action, center_pos, font,
                 text_color=COLOR_MENU_ITEM_TEXT,
                 highlight_text_color=COLOR_MENU_ITEM_HIGHLIGHT_TEXT,
                 bg_color=COLOR_MENU_ITEM_BG,
                 highlight_bg_color=COLOR_MENU_ITEM_HIGHLIGHT_BG,
                 border_color=COLOR_MENU_ITEM_BORDER,
                 width=350, height=50, border_radius=5):
        self.text = text
        self.action = action
        self.font = font
        self.center_pos = center_pos

        self.text_color = text_color
        self.highlight_text_color = highlight_text_color
        self.bg_color = bg_color
        self.highlight_bg_color = highlight_bg_color
        self.border_color = border_color

        self.width = width
        self.height = height
        self.border_radius = border_radius

        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = self.center_pos

        self.is_highlighted = False
        self.hover_progress = 0.0  # For smooth animation
        self.hover_speed = 0.1

    def update(self):
        if self.is_highlighted:
            self.hover_progress = min(1.0, self.hover_progress + self.hover_speed)
        else:
            self.hover_progress = max(0.0, self.hover_progress - self.hover_speed)

    def draw(self, surface):
        self.update()

        current_bg_color = (
            int(self.bg_color[0] + (self.highlight_bg_color[0] - self.bg_color[0]) * self.hover_progress),
            int(self.bg_color[1] + (self.highlight_bg_color[1] - self.bg_color[1]) * self.hover_progress),
            int(self.bg_color[2] + (self.highlight_bg_color[2] - self.bg_color[2]) * self.hover_progress)
        )
        current_text_color = (
            int(self.text_color[0] + (self.highlight_text_color[0] - self.text_color[0]) * self.hover_progress),
            int(self.text_color[1] + (self.highlight_text_color[1] - self.text_color[1]) * self.hover_progress),
            int(self.text_color[2] + (self.highlight_text_color[2] - self.text_color[2]) * self.hover_progress)
        )

        pygame.draw.rect(surface, current_bg_color, self.rect, border_radius=self.border_radius)
        pygame.draw.rect(surface, self.border_color, self.rect, 2, border_radius=self.border_radius)

        text_surf = create_text_surface(self.text, self.font, current_text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, mouse_pos):
        self.is_highlighted = self.rect.collidepoint(mouse_pos)

    def perform_action(self):
        if self.action:
            # Optional: add a small click animation or sound
            self.hover_progress = 0.5  # Quick visual feedback for click
            self.action()


def render_multiline_text_enhanced(surface, text, start_pos, font, color, header_font, header_color, max_width,
                                   line_spacing=7, bg_color=None, padding=20, border_color=None, border_width=2,
                                   border_radius=8):
    """Renders multiline text with header, word wrapping, and styled background."""
    lines = text.splitlines()
    x, y = start_pos[0] + padding, start_pos[1] + padding

    rendered_lines = []
    total_text_height = 0
    actual_text_block_width = 0

    # First line as header
    if lines:
        header_surf = create_text_surface(lines[0], header_font, header_color)
        rendered_lines.append({'surf': header_surf, 'x': x, 'is_header': True})
        total_text_height += header_surf.get_height() + line_spacing * 1.5  # More space after header
        actual_text_block_width = max(actual_text_block_width, header_surf.get_width())

        # Process remaining lines
        for line_text in lines[1:]:
            if not line_text.strip():  # Handle empty lines for spacing
                total_text_height += font.get_height() // 2  # Smaller space for empty visual line
                rendered_lines.append({'surf': None, 'x': x, 'is_header': False})  # Placeholder for spacing
                continue

            words = line_text.split(' ')
            current_line = ""
            current_line_width = 0
            space_width = font.size(' ')[0]

            for word in words:
                word_surf = font.render(word, True, color)
                word_w = word_surf.get_width()
                if current_line_width + word_w < max_width - padding * 2:
                    current_line += word + " "
                    current_line_width += word_w + space_width
                else:
                    if current_line:
                        line_surf = create_text_surface(current_line.strip(), font, color)
                        rendered_lines.append({'surf': line_surf, 'x': x, 'is_header': False})
                        total_text_height += line_surf.get_height() + line_spacing
                        actual_text_block_width = max(actual_text_block_width, line_surf.get_width())
                    current_line = word + " "
                    current_line_width = word_w + space_width

            if current_line:  # Add the last part of the line
                line_surf = create_text_surface(current_line.strip(), font, color)
                rendered_lines.append({'surf': line_surf, 'x': x, 'is_header': False})
                total_text_height += line_surf.get_height() + line_spacing
                actual_text_block_width = max(actual_text_block_width, line_surf.get_width())

    total_text_height -= line_spacing  # Remove extra spacing after last line

    if bg_color:
        bg_rect_width = actual_text_block_width + padding * 2
        bg_rect_height = total_text_height + padding * 2
        # Center the background block if it's narrower than max_width
        bg_x = start_pos[0] + (max_width - bg_rect_width) / 2 if bg_rect_width < max_width else start_pos[0]
        bg_rect = pygame.Rect(bg_x, start_pos[1], bg_rect_width, bg_rect_height)
        pygame.draw.rect(surface, bg_color, bg_rect, border_radius=border_radius)
        if border_color:
            pygame.draw.rect(surface, border_color, bg_rect, border_width, border_radius=border_radius)

    current_y = start_pos[1] + padding
    for item_data in rendered_lines:
        line_surface = item_data['surf']
        if line_surface:
            line_x_offset = item_data['x']
            # Center header text if it's a header
            if item_data['is_header']:
                line_x_offset = bg_x + padding + (actual_text_block_width - line_surface.get_width()) / 2

            surface.blit(line_surface, (line_x_offset, current_y))
            current_y += line_surface.get_height() + (line_spacing * 1.5 if item_data['is_header'] else line_spacing)
        else:  # Empty line for spacing
            current_y += font.get_height() // 2 + line_spacing


class MainMenu:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Snake 2: The Unhinged Collection")
        self.clock = pygame.time.Clock()

        self.title_font = pygame.font.SysFont("Bahnschrift", 72, bold=True)  # Changed font
        self.subtitle_font = pygame.font.SysFont("Bahnschrift Light", 24)
        self.menu_item_font = pygame.font.SysFont("Segoe UI Semibold", 28)
        self.tutorial_header_font = pygame.font.SysFont("Segoe UI Bold", 24)
        self.tutorial_body_font = pygame.font.SysFont("Segoe UI", 18)
        self.tutorial_nav_font = pygame.font.SysFont("Segoe UI Semibold", 20)

        self.current_menu_state = "main"
        self.menu_items = []
        self.running_game_instance = None
        self.current_tutorial_key = None
        self.current_tutorial_page = 0

        # Starfield background for menu
        self.stars = []
        for _ in range(100):
            self.stars.append({
                'x': random.randint(0, SCREEN_WIDTH),
                'y': random.randint(0, SCREEN_HEIGHT),
                'size': random.randint(1, 2),
                'speed': random.uniform(0.1, 0.5),
                'color': random.choice([(100, 100, 120), (150, 150, 180), (200, 200, 220)])
            })
        self.setup_main_menu()

    def _create_menu(self, items_data, start_y, item_spacing, font, item_width=400, item_height=55):
        temp_items = []
        for i, (text, action) in enumerate(items_data):
            pos = (SCREEN_WIDTH // 2, start_y + i * item_spacing)
            temp_items.append(MenuItem(text, action, pos, font, width=item_width, height=item_height))
        return temp_items

    def setup_main_menu(self):
        self.current_menu_state = "main"
        title_area_height = SCREEN_HEIGHT * 0.35
        menu_start_y = title_area_height + 50  # Start menu below title area
        available_menu_height = SCREEN_HEIGHT - menu_start_y - 50  # Space for menu items + bottom padding

        items_data = [
            ("No-Clip Nightmare", self.start_no_clip_nightmare),
            ("Symbiotic Anarchy", self.start_symbiotic_anarchy),
            ("Ouroboros Paradox", self.start_ouroboros_paradox),
            ("Bio-Mechanical God", self.start_bio_mechanical_god),
            ("How to Play", self.show_tutorial_selection_menu),
            ("Quit", self.quit_game)
        ]
        num_items = len(items_data)
        item_height_with_spacing = 65  # Desired height + spacing
        total_menu_block_height = num_items * item_height_with_spacing - 10  # No spacing after last

        # Adjust start_y to center the block of menu items
        menu_block_start_y = menu_start_y + (available_menu_height - total_menu_block_height) / 2

        self.menu_items = self._create_menu(items_data, menu_block_start_y, item_height_with_spacing,
                                            self.menu_item_font)

    def setup_tutorial_selection_menu(self):
        self.current_menu_state = "tutorial_selection"
        title_area_height = SCREEN_HEIGHT * 0.25
        menu_start_y = title_area_height + 40

        items_data = []
        for game_name in TUTORIAL_DATA.keys():
            items_data.append((game_name, lambda name=game_name: self.prepare_display_tutorial(name)))
        items_data.append(("Back to Main Menu", self.setup_main_menu))

        item_height_with_spacing = 60
        num_items = len(items_data)
        available_menu_height = SCREEN_HEIGHT - menu_start_y - 50
        total_menu_block_height = num_items * item_height_with_spacing - 10
        menu_block_start_y = menu_start_y + (available_menu_height - total_menu_block_height) / 2

        self.menu_items = self._create_menu(items_data, menu_block_start_y, item_height_with_spacing,
                                            self.menu_item_font, item_width=450)

    def prepare_display_tutorial(self, game_name_key):
        self.current_menu_state = "tutorial_display"
        self.current_tutorial_key = game_name_key
        self.current_tutorial_page = 0

    def show_tutorial_selection_menu(self):
        self.setup_tutorial_selection_menu()

    def _run_game(self, GameClass):
        self.running_game_instance = GameClass()
        self.running_game_instance.run()
        self.running_game_instance = None
        if pygame.display.get_init():
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            pygame.display.set_caption("Snake 2: The Unhinged Collection")
        else:
            pygame.init();
            pygame.mixer.init()
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            pygame.display.set_caption("Snake 2: The Unhinged Collection")
        self.setup_main_menu()

    def start_no_clip_nightmare(self):
        self._run_game(NoClipGame)

    def start_symbiotic_anarchy(self):
        self._run_game(SymbioticAnarchyGame)

    def start_ouroboros_paradox(self):
        self._run_game(OuroborosParadoxGame)

    def start_bio_mechanical_god(self):
        self._run_game(BioMechanicalGame)

    def quit_game(self):
        pygame.quit(); sys.exit()

    def display_tutorial_content(self):
        self.screen.fill(COLOR_BACKGROUND)  # Consistent background
        self.draw_starfield()  # Draw stars behind tutorial too

        if not self.current_tutorial_key or self.current_tutorial_key not in TUTORIAL_DATA:
            self.setup_tutorial_selection_menu();
            return

        tutorial_pages = TUTORIAL_DATA[self.current_tutorial_key]
        page_text = tutorial_pages[self.current_tutorial_page]

        text_x_start = 60
        text_y_start = 60
        max_text_width = SCREEN_WIDTH - 2 * text_x_start

        render_multiline_text_enhanced(self.screen, page_text, (text_x_start, text_y_start),
                                       self.tutorial_body_font, COLOR_TUTORIAL_TEXT,
                                       self.tutorial_header_font, COLOR_TUTORIAL_HEADER,
                                       max_text_width, line_spacing=8,
                                       bg_color=COLOR_TUTORIAL_BG, padding=25,
                                       border_color=COLOR_TUTORIAL_BORDER, border_radius=10)

        self.menu_items = []
        button_y = SCREEN_HEIGHT - 50
        nav_button_width = 150
        nav_button_height = 40

        if self.current_tutorial_page > 0:
            prev_button = MenuItem("< Prev",
                                   lambda: setattr(self, 'current_tutorial_page', self.current_tutorial_page - 1),
                                   (SCREEN_WIDTH // 4, button_y), self.tutorial_nav_font, width=nav_button_width,
                                   height=nav_button_height)
            self.menu_items.append(prev_button)

        if self.current_tutorial_page < len(tutorial_pages) - 1:
            next_button = MenuItem("Next >",
                                   lambda: setattr(self, 'current_tutorial_page', self.current_tutorial_page + 1),
                                   (SCREEN_WIDTH * 3 // 4, button_y), self.tutorial_nav_font, width=nav_button_width,
                                   height=nav_button_height)
            self.menu_items.append(next_button)

        back_button_width = 220
        back_button = MenuItem("Back to Tutorials", self.setup_tutorial_selection_menu,
                               (SCREEN_WIDTH // 2, button_y + (
                                   0 if self.current_tutorial_page > 0 or self.current_tutorial_page < len(
                                       tutorial_pages) - 1 else -12)),  # Center if only button
                               self.tutorial_nav_font, width=back_button_width, height=nav_button_height)
        self.menu_items.append(back_button)

        for item in self.menu_items: item.draw(self.screen)

    def draw_starfield(self):
        for star in self.stars:
            star['y'] += star['speed']
            if star['y'] > SCREEN_HEIGHT:
                star['y'] = 0
                star['x'] = random.randint(0, SCREEN_WIDTH)
            pygame.draw.circle(self.screen, star['color'], (star['x'], star['y']), star['size'])

    def run(self):
        menu_running = True
        while menu_running:
            mouse_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT: menu_running = False
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for item in self.menu_items:
                        if item.is_highlighted: item.perform_action(); break
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.current_menu_state == "tutorial_display":
                            self.setup_tutorial_selection_menu()
                        elif self.current_menu_state == "tutorial_selection":
                            self.setup_main_menu()
                        else:
                            menu_running = False
                    if self.current_menu_state == "tutorial_display":
                        tutorial_pages = TUTORIAL_DATA.get(self.current_tutorial_key, [])
                        if event.key == pygame.K_LEFT and self.current_tutorial_page > 0:
                            self.current_tutorial_page -= 1
                        elif event.key == pygame.K_RIGHT and self.current_tutorial_page < len(tutorial_pages) - 1:
                            self.current_tutorial_page += 1

            for item in self.menu_items: item.check_hover(mouse_pos)

            self.screen.fill(COLOR_BACKGROUND)
            self.draw_starfield()

            if self.current_menu_state == "main" or self.current_menu_state == "tutorial_selection":
                title_y_pos = SCREEN_HEIGHT * 0.20  # Moved title higher
                title_text_str = "SELECT TUTORIAL" if self.current_menu_state == "tutorial_selection" else "SNAKE II"
                title_rendered = create_text_surface(title_text_str, self.title_font, COLOR_TITLE)
                self.screen.blit(title_rendered, title_rendered.get_rect(center=(SCREEN_WIDTH // 2, title_y_pos)))

                if self.current_menu_state == "main":
                    subtitle_rendered = create_text_surface("The Unhinged Collection", self.subtitle_font,
                                                            COLOR_SUBTITLE)
                    self.screen.blit(subtitle_rendered,
                                     subtitle_rendered.get_rect(center=(SCREEN_WIDTH // 2, title_y_pos + 60)))

                for item in self.menu_items: item.draw(self.screen)

            elif self.current_menu_state == "tutorial_display":
                self.display_tutorial_content()

            pygame.display.flip()
            self.clock.tick(FPS)
        self.quit_game()


if __name__ == "__main__":
    main_menu = MainMenu()
    main_menu.run()