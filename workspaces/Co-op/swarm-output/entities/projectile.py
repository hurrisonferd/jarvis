"""Projectile (bullet) class for player shots in Space Invaders."""

import pygame
from typing import Tuple


class Bullet:
    """Bullet projectile fired by the player."""
    
    def __init__(self, x: int, y: int):
        """Initialize bullet at given position.
        
        Args:
            x: X position (center of bullet)
            y: Y position (top of bullet)
        """
        # Bullet size: 6x15 pixels
        self.width = 6
        self.height = 15
        
        # Position: center horizontally
        self.x = x - self.width // 2
        self.y = y
        
        # Movement speed: 7 pixels per frame (upward)
        self.speed = 7
        
        # Bullet color (yellow/laser style)
        self.color = (255, 255, 0)
        
        # Active state (bullet is removed when off-screen)
        self.active = True
        
    def update(self) -> None:
        """Move bullet upward and deactivate if off-screen."""
        self.y -= self.speed
        if self.y + self.height < 0:
            self.active = False
    
    def get_rect(self) -> pygame.Rect:
        """Get the bullet's collision rectangle."""
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def get_position(self) -> Tuple[int, int]:
        """Get current position as tuple (x, y)."""
        return (self.x, self.y)
    
    def get_center(self) -> Tuple[int, int]:
        """Get center position of bullet."""
        return (self.x + self.width // 2, self.y + self.height // 2)
    
    def deactivate(self) -> None:
        """Mark bullet as inactive (for collision handling)."""
        self.active = False
    
    def is_active(self) -> bool:
        """Check if bullet is still active."""
        return self.active
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the bullet as a small rectangle.
        
        Args:
            surface: Pygame surface to draw on
        """
        if self.active:
            pygame.draw.rect(surface, self.color, 
                           (self.x, self.y, self.width, self.height))
            # Add glow effect
            pygame.draw.rect(surface, (255, 255, 200),
                           (self.x + 1, self.y + 1, self.width - 2, self.height - 2))
