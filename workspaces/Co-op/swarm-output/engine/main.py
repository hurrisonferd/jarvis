"""
Space Invaders Game Engine - Entry Point
Main module that initializes Pygame and starts the game.
"""

import sys
import pygame
from engine.game import Game


def main():
    """Initialize Pygame and run the game."""
    pygame.init()
    
    # Game configuration
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    FPS = 60
    
    # Create game instance
    game = Game(SCREEN_WIDTH, SCREEN_HEIGHT, FPS)
    
    # Run the game main loop
    game.run()
    
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()