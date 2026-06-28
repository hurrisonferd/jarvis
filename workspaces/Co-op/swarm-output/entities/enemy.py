"""
Enemy base class for Space Invaders game.
"""

import pygame
from typing import Tuple, Optional


class Enemy:
    """Base class for all enemy types in the Space Invaders game."""
    
    def __init__(
        self,
        x: float,
        y: float,
        width: int = 40,
        height: int = 30,
        health: int = 1,
        speed: float = 1.0,
        points: int = 10,
        color: Tuple[int, int, int] = (0, 255, 0)
    ):
        """
        Initialize an enemy.
        
        Args:
            x: Initial x position
            y: Initial y position
            width: Enemy width in pixels
            height: Enemy height in pixels
            health: Number of hits to kill
            speed: Movement speed multiplier
            points: Score points awarded when destroyed
            color: RGB color tuple for the sprite
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.health = health
        self.max_health = health
        self.speed = speed
        self.points = points
        self.color = color
        self.active = True
        
    @property
    def rect(self) -> pygame.Rect:
        """Get the enemy's collision rectangle."""
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    @property
    def center(self) -> Tuple[float, float]:
        """Get the center position of the enemy."""
        return (self.x + self.width / 2, self.y + self.height / 2)
    
    @property
    def bottom(self) -> float:
        """Get the bottom edge y position."""
        return self.y + self.height
    
    def take_damage(self, damage: int = 1) -> bool:
        """
        Apply damage to the enemy.
        
        Args:
            damage: Amount of damage to apply
            
        Returns:
            True if enemy is destroyed, False otherwise
        """
        self.health -= damage
        if self.health <= 0:
            self.active = False
            return True
        return False
    
    def move(self, dx: float, dy: float) -> None:
        """
        Move the enemy by the given delta.
        
        Args:
            dx: Horizontal movement
            dy: Vertical movement
        """
        self.x += dx * self.speed
        self.y += dy * self.speed
    
    def set_position(self, x: float, y: float) -> None:
        """
        Set the enemy's position.
        
        Args:
            x: New x position
            y: New y position
        """
        self.x = x
        self.y = y
    
    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the enemy on the given surface.
        
        Args:
            surface: Pygame surface to draw on
        """
        if not self.active:
            return
            
        # Draw main body
        pygame.draw.rect(surface, self.color, self.rect)
        
        # Draw border
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 2)
        
        # Draw health indicator if damaged
        if self.health < self.max_health:
            health_ratio = self.health / self.max_health
            health_width = int(self.width * health_ratio)
            health_rect = pygame.Rect(self.x, self.y - 5, health_width, 3)
            pygame.draw.rect(surface, (255, 0, 0), health_rect)
    
    def get_sprite(self) -> pygame.Surface:
        """
        Get a pygame Surface representing the enemy's sprite.
        
        Returns:
            Pygame surface with the enemy sprite
        """
        sprite = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(sprite, (*self.color, 255), (0, 0, self.width, self.height))
        pygame.draw.rect(sprite, (255, 255, 255, 255), (0, 0, self.width, self.height), 2)
        return sprite
    
    def to_dict(self) -> dict:
        """Convert enemy state to dictionary for serialization."""
        return {
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height,
            'health': self.health,
            'max_health': self.max_health,
            'speed': self.speed,
            'points': self.points,
            'color': self.color,
            'active': self.active
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Enemy':
        """Create enemy from dictionary data."""
        enemy = cls(
            x=data['x'],
            y=data['y'],
            width=data['width'],
            height=data['height'],
            health=data['health'],
            speed=data['speed'],
            points=data['points'],
            color=tuple(data['color'])
        )
        enemy.active = data['active']
        return enemy