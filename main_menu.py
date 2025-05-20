import pygame
import sys

# Import the game modes
try:
    from no_clip_snake import Game as NoClipGame
    from symbiotic_anarchy_snake import Game as SymbioticAnarchyGame
    from ouroboros_paradox_snake import Game as OuroborosParadoxGame
    from bio_mechanical_snake import Game as BioMechanicalGame
    # from sentient_tail_snake import Game as SentientTailGame # Placeholder for the future
except ImportError as e:
    print(f"Error importing game modules: {e}")
    print("Make sure all game mode .py files (e.g., no_clip_snake.py) are in the same directory as main_menu.py.")
    print("And ensure their Game classes are available for import.")
    sys.exit()

# --- Constants ---
SCREEN_WIDTH = 800  # Default, individual games might override
SCREEN_HEIGHT = 600  # Default
FPS = 30

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (100, 100, 100)
LIGHT_BLUE = (173, 216, 230)
HIGHLIGHT_COLOR = (255, 255, 0)  # Yellow for highlight


class MenuItem:
    def __init__(self, text, action, position, font, base_color=WHITE, highlight_color=HIGHLIGHT_COLOR):
        self.text = text
        self.action = action
        self.font = font
        self.base_color = base_color
        self.highlight_color = highlight_color
        self.is_highlighted = False

        self.rendered_text_normal = self.font.render(self.text, True, self.base_color)
        self.rendered_text_highlighted = self.font.render(self.text, True, self.highlight_color)

        self.rect = self.rendered_text_normal.get_rect(center=position)

    def draw(self, surface):
        if self.is_highlighted:
            surface.blit(self.rendered_text_highlighted, self.rect)
        else:
            surface.blit(self.rendered_text_normal, self.rect)

    def check_hover(self, mouse_pos):
        self.is_highlighted = self.rect.collidepoint(mouse_pos)

    def perform_action(self):
        if self.action:
            self.action()


class MainMenu:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()  # Initialize mixer once
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Snake 2: The Unhinged Collection - Main Menu")
        self.clock = pygame.time.Clock()

        self.title_font = pygame.font.SysFont("Consolas", 60, bold=True)  # Adjusted size
        self.menu_font = pygame.font.SysFont("Consolas", 40)  # Adjusted size
        self.small_font = pygame.font.SysFont("Consolas", 20)  # Adjusted size

        self.menu_items = []
        self.running_game_instance = None  # To hold the instance of the currently running game

        self.setup_menu_items()

    def setup_menu_items(self):
        self.menu_items = []
        menu_start_y = SCREEN_HEIGHT // 2 - 80  # Adjusted start
        item_spacing = 60  # Adjusted spacing

        items_data = [
            ("No-Clip Nightmare", self.start_no_clip_nightmare),
            ("Symbiotic Anarchy", self.start_symbiotic_anarchy),
            ("Ouroboros Paradox", self.start_ouroboros_paradox),
            ("Bio-Mechanical God", self.start_bio_mechanical_god),
            # ("Sentient Tail", self.start_sentient_tail), # Placeholder
            ("Quit", self.quit_game)
        ]

        for i, (text, action) in enumerate(items_data):
            pos = (SCREEN_WIDTH // 2, menu_start_y + i * item_spacing)
            self.menu_items.append(MenuItem(text, action, pos, self.menu_font))

    def _run_game(self, GameClass):
        """Helper to instantiate and run a game, then reset screen."""
        self.running_game_instance = GameClass()
        self.running_game_instance.run()  # This should block until the game is over/exited
        self.running_game_instance = None  # Clear the game instance

        # Re-assert menu's control over the display IF the game didn't quit pygame
        if pygame.display.get_init():  # Check if display module is still initialized
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))  # Reset to menu dimensions
            pygame.display.set_caption("Snake 2: The Unhinged Collection - Main Menu")
        else:  # If a game called pygame.quit(), we need to reinit for the menu
            pygame.init()
            pygame.mixer.init()  # Re-init mixer too
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            pygame.display.set_caption("Snake 2: The Unhinged Collection - Main Menu")

    def start_no_clip_nightmare(self):
        print("Starting No-Clip Nightmare...")
        self._run_game(NoClipGame)

    def start_symbiotic_anarchy(self):
        print("Starting Symbiotic Anarchy...")
        self._run_game(SymbioticAnarchyGame)

    def start_ouroboros_paradox(self):
        print("Starting Ouroboros Paradox...")
        self._run_game(OuroborosParadoxGame)

    def start_bio_mechanical_god(self):
        print("Starting Bio-Mechanical God Serpent...")
        self._run_game(BioMechanicalGame)

    # def start_sentient_tail(self): # Placeholder
    #     print("Sentient Tail - Not Implemented Yet")
    #     # self._run_game(SentientTailGame)

    def quit_game(self):
        pygame.quit()
        sys.exit()

    def run(self):
        menu_running = True
        while menu_running:
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    menu_running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        for item in self.menu_items:
                            if item.is_highlighted:
                                item.perform_action()
                                break
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        menu_running = False

            for item in self.menu_items:
                item.check_hover(mouse_pos)

            self.screen.fill(BLACK)

            title_text = self.title_font.render("SNAKE II", True, LIGHT_BLUE)  # Changed text slightly
            subtitle_text = self.small_font.render("The Unhinged Collection", True, GREY)
            self.screen.blit(title_text, title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)))
            self.screen.blit(subtitle_text, subtitle_text.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4 + 55)))  # Adjusted pos

            for item in self.menu_items:
                item.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(FPS)

        self.quit_game()


if __name__ == "__main__":
    main_menu = MainMenu()
    main_menu.run()