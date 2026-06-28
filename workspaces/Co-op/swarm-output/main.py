"""
Space Invaders Game - Main Integration Module
Wires together engine, entities, systems, ui, audio, levels, and effects.
"""

import sys
import pygame

# Initialize pygame
pygame.init()


def main():
    """Initialize and run the Space Invaders game."""
    # Game configuration
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    FPS = 60
    
    # Create game instance from engine
    from engine import Game
    game = Game(SCREEN_WIDTH, SCREEN_HEIGHT, FPS)
    
    # Import and wire up all subsystems
    _setup_subsystems(game)
    
    # Run the game main loop
    game.run()
    
    # Cleanup
    _cleanup_subsystems(game)
    
    pygame.quit()
    sys.exit()


def _setup_subsystems(game):
    """Wire up all game subsystems."""
    # Systems - ECS-style systems for game logic
    from systems import (
        MovementSystem,
        CollisionSystem,
        SpawnSystem,
        LifeCycleSystem,
        ScoreSystem,
    )
    game.systems = {
        'movement': MovementSystem(),
        'collision': CollisionSystem(),
        'spawn': SpawnSystem(),
        'lifecycle': LifeCycleSystem(),
        'score': ScoreSystem(),
    }
    
    # UI - User interface components
    from ui import (
        HUD,
        MenuUI,
        PauseMenu,
        GameOverScreen,
    )
    game.ui = {
        'hud': HUD(game.renderer),
        'menu': MenuUI(game.renderer),
        'pause': PauseMenu(game.renderer),
        'gameover': GameOverScreen(game.renderer),
    }
    
    # Audio - Sound management
    from audio import SoundManager
    game.sound_manager = SoundManager()
    
    # Levels - Level management
    from levels import LevelManager, create_level
    game.level_manager = LevelManager()
    game.level_manager.add_level(1, create_level(1))
    game.level_manager.add_level(2, create_level(2))
    game.level_manager.add_level(3, create_level(3))
    
    # Effects - Visual effects system
    from effects import EffectsManager
    game.effects_manager = EffectsManager(game.renderer)
    
    # Entities - Create entity registry
    from entities import Player, Bullet, GameController
    game.entities = {
        'player': None,
        'player_bullets': [],
        'enemy_bullets': [],
        'enemies': [],
        'explosions': [],
    }
    
    # Game controller - Central game state management
    game.game_controller = GameController(game)


def _cleanup_subsystems(game):
    """Cleanup all subsystems on game exit."""
    if hasattr(game, 'sound_manager'):
        game.sound_manager.shutdown()
    if hasattr(game, 'effects_manager'):
        game.effects_manager.clear()


if __name__ == "__main__":
    main()
