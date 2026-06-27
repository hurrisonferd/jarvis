"""
Game Engine Core - Game Class
Handles main game loop, state machine, and clock management.
"""

import pygame
from enum import Enum, auto
from engine.renderer import Renderer
from engine.input import InputHandler


class GameState(Enum):
    """Game state enumeration for the state machine."""
    MENU = auto()
    PLAYING = auto()
    GAME_OVER = auto()


class Game:
    """
    Main game class that manages the game loop, state machine, and clock.
    
    Attributes:
        screen_width: Width of the game window in pixels.
        screen_height: Height of the game window in pixels.
        target_fps: Target frames per second for the game loop.
        state: Current game state (menu/playing/gameover).
        clock: Pygame clock for frame rate management.
        renderer: Renderer instance for drawing.
        input_handler: Input handler for player controls.
    """
    
    def __init__(self, screen_width: int = 800, screen_height: int = 600, target_fps: int = 60):
        """
        Initialize the game with screen dimensions and target FPS.
        
        Args:
            screen_width: Width of the game window.
            screen_height: Height of the game window.
            target_fps: Target frames per second.
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.target_fps = target_fps
        
        # Initialize state machine
        self.state = GameState.MENU
        
        # Initialize Pygame clock for frame rate management
        self.clock = pygame.time.Clock()
        self.delta_time = 0.0
        self.frame_count = 0
        self.running = True
        
        # Create display surface
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("Space Invaders")
        
        # Initialize subsystems
        self.renderer = Renderer(self.screen, screen_width, screen_height)
        self.input_handler = InputHandler()
        
        # Game statistics
        self.score = 0
        self.lives = 3
    
    def run(self):
        """
        Main game loop - runs until quit.
        Implements the game loop pattern: process input -> update -> render.
        """
        while self.running:
            # Calculate delta time
            self.delta_time = self.clock.tick(self.target_fps) / 1000.0
            self.frame_count += 1
            
            # Process input
            self._process_events()
            
            # Update game state based on current state
            self._update()
            
            # Render current frame
            self._render()
            
            # Update display
            pygame.display.flip()
    
    def _process_events(self):
        """
        Process all pending Pygame events.
        Handles quit events and passes input to input handler.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self.input_handler.on_key_down(event.key)
            elif event.type == pygame.KEYUP:
                self.input_handler.on_key_up(event.key)
    
    def _update(self):
        """
        Update game state based on current state.
        Handles state transitions and per-state updates.
        """
        if self.state == GameState.MENU:
            self._update_menu()
        elif self.state == GameState.PLAYING:
            self._update_playing()
        elif self.state == GameState.GAME_OVER:
            self._update_game_over()
    
    def _update_menu(self):
        """Update logic for menu state."""
        if self.input_handler.is_key_pressed(pygame.K_SPACE):
            self._start_game()
    
    def _update_playing(self):
        """Update logic for playing state."""
        # Placeholder for actual game update logic
        # This will be extended with player, enemies, bullets, etc.
        pass
    
    def _update_game_over(self):
        """Update logic for game over state."""
        if self.input_handler.is_key_pressed(pygame.K_SPACE):
            self._start_game()
        elif self.input_handler.is_key_pressed(pygame.K_ESCAPE):
            self.running = False
    
    def _render(self):
        """
        Render the current frame.
        Clears screen and delegates to renderer based on state.
        """
        self.renderer.clear()
        
        if self.state == GameState.MENU:
            self._render_menu()
        elif self.state == GameState.PLAYING:
            self._render_playing()
        elif self.state == GameState.GAME_OVER:
            self._render_game_over()
    
    def _render_menu(self):
        """Render the menu screen."""
        self.renderer.draw_text("SPACE INVADERS", self.screen_width // 2, 200, 
                                size=48, color=(255, 255, 255), center=True)
        self.renderer.draw_text("Press SPACE to Start", self.screen_width // 2, 350,
                                size=24, color=(200, 200, 200), center=True)
        self.renderer.draw_text("Arrow Keys to Move | SPACE to Fire", 
                                self.screen_width // 2, 450, size=18, color=(150, 150, 150), center=True)
    
    def _render_playing(self):
        """Render the playing state."""
        self.renderer.draw_text(f"Score: {self.score}", 20, 20, size=20, color=(255, 255, 255))
        self.renderer.draw_text(f"Lives: {self.lives}", self.screen_width - 100, 20, 
                                size=20, color=(255, 255, 255))
    
    def _render_game_over(self):
        """Render the game over screen."""
        self.renderer.draw_text("GAME OVER", self.screen_width // 2, 200, 
                                size=48, color=(255, 0, 0), center=True)
        self.renderer.draw_text(f"Final Score: {self.score}", self.screen_width // 2, 300,
                                size=32, color=(255, 255, 255), center=True)
        self.renderer.draw_text("Press SPACE to Restart", self.screen_width // 2, 400,
                                size=24, color=(200, 200, 200), center=True)
        self.renderer.draw_text("Press ESC to Quit", self.screen_width // 2, 450,
                                size=18, color=(150, 150, 150), center=True)
    
    def _start_game(self):
        """Start a new game."""
        self.state = GameState.PLAYING
        self.score = 0
        self.lives = 3
        self.input_handler.reset()
    
    def end_game(self):
        """End the current game and show game over."""
        self.state = GameState.GAME_OVER
    
    def add_score(self, points: int):
        """Add points to the current score."""
        self.score += points
    
    def lose_life(self):
        """Decrement lives and end game if lives reach zero."""
        self.lives -= 1
        if self.lives <= 0:
            self.end_game()
    
    def get_delta_time(self) -> float:
        """Get the time elapsed since last frame in seconds."""
        return self.delta_time
    
    def get_frame_count(self) -> int:
        """Get the current frame count."""
        return self.frame_count