"""Player character for Space Invaders game."""

import pygame
from typing import Tuple

from .sprites import player_sprite


class Player:
    """Player ship that can move and shoot in Space Invaders."""
    
    def __init__(self, screen_width: int, screen_height: int, 
                 sprite_style: str = "triangle"):
        """Initialize the player at bottom center of screen.
        
        Args:
            screen_width: Width of the game screen
            screen_height: Height of the game screen
            sprite_style: Sprite style - "triangle", "detailed", or "classic"
        """
        # Size: 40x40 pixels
        self.width = 40
        self.height = 40
        
        # Position: start at bottom center
        self.x = (screen_width - self.width) // 2
        self.y = screen_height - self.height - 20  # 20px from bottom
        
        # Movement speed: 5 pixels per frame
        self.speed = 5
        
        # Health: 3 lives
        self.health = 3
        self.max_health = 3
        
        # Screen boundaries
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Sprite style
        self.sprite_style = sprite_style
        self.animation_frame = 0
        
    def move_left(self) -> None:
        """Move player left by speed amount, respecting left boundary."""
        self.x = max(0, self.x - self.speed)
        
    def move_right(self) -> None:
        """Move player right by speed amount, respecting right boundary."""
        self.x = min(self.screen_width - self.width, self.x + self.speed)
        
    def move_up(self) -> None:
        """Move player up by speed amount (for future use)."""
        self.y = max(0, self.y - self.speed)
        
    def move_down(self) -> None:
        """Move player down by speed amount (for future use)."""
        self.y = min(self.screen_height - self.height, self.y + self.speed)
    
    def get_rect(self) -> pygame.Rect:
        """Get the player's collision rectangle."""
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def get_position(self) -> Tuple[int, int]:
        """Get current position as tuple (x, y)."""
        return (self.x, self.y)
    
    def take_damage(self) -> bool:
        """Reduce health by 1. Returns True if player is still alive."""
        self.health = max(0, self.health - 1)
        return self.health > 0
    
    def is_alive(self) -> bool:
        """Check if player still has health remaining."""
        return self.health > 0
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the player ship based on selected sprite style.
        
        Args:
            surface: Pygame surface to draw on
        """
        if self.sprite_style == "triangle":
            player_sprite.draw_triangle_ship(surface, self.x, self.y, 
                                            self.width, self.height)
        elif self.sprite_style == "detailed":
            player_sprite.draw_detailed_ship(surface, self.x, self.y,
                                            self.width, self.height)
        elif self.sprite_style == "classic":
            player_sprite.draw_classic_ship(surface, self.x, self.y,
                                            self.width, self.height)
        else:
            # Default triangle
            player_sprite.draw_triangle_ship(surface, self.x, self.y,
                                            self.width, self.height)
        
        # Animate engine
        self.animation_frame += 1
        if self.animation_frame > 10:
            self.animation_frame = 0
    
    def reset(self, screen_width: int, screen_height: int) -> None:
        """Reset player to starting position.
        
        Args:
            screen_width: Width of the game screen
            screen_height: Height of the game screen
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.x = (screen_width - self.width) // 2
        self.y = screen_height - self.height - 20
        self.health = self.max_health
