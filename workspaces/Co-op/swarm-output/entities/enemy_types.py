"""
Enemy type definitions for Space Invaders game.
Contains three distinct enemy types with unique attributes.
"""

import pygame
from typing import Tuple
from enemy import Enemy


# Color definitions
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)


class BasicEnemy(Enemy):
    """
    Basic enemy type - standard Space Invaders alien.
    1 hit to destroy, 10 points, moderate speed.
    """
    
    def __init__(self, x: float, y: float):
        super().__init__(
            x=x,
            y=y,
            width=40,
            height=30,
            health=1,
            speed=1.0,
            points=10,
            color=GREEN
        )
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the basic enemy with classic Space Invaders look."""
        if not self.active:
            return
            
        # Main body
        pygame.draw.rect(surface, self.color, self.rect)
        
        # Antennae
        antenna_y = self.y - 5
        pygame.draw.line(surface, self.color, (self.x + 8, self.y), (self.x + 5, antenna_y), 2)
        pygame.draw.line(surface, self.color, (self.x + self.width - 8, self.y), (self.x + self.width - 5, antenna_y), 2)
        
        # Eyes
        eye_y = self.y + 10
        eye_size = 4
        pygame.draw.circle(surface, (0, 0, 0), (int(self.x + 12), int(eye_y)), eye_size)
        pygame.draw.circle(surface, (0, 0, 0), (int(self.x + self.width - 12), int(eye_y)), eye_size)
        
        # Border
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 2)


class FastEnemy(Enemy):
    """
    Fast enemy type - quick but fragile alien.
    1 hit to destroy, 20 points, faster movement.
    """
    
    def __init__(self, x: float, y: float):
        super().__init__(
            x=x,
            y=y,
            width=30,
            height=25,
            health=1,
            speed=1.8,
            points=20,
            color=YELLOW
        )
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the fast enemy with streamlined appearance."""
        if not self.active:
            return
            
        # Sleek body shape (diamond-like)
        center_x = self.x + self.width / 2
        top_y = self.y + 5
        bottom_y = self.y + self.height - 5
        
        points = [
            (center_x, top_y),           # Top point
            (self.x + self.width, self.y + self.height / 2),  # Right
            (center_x, bottom_y),        # Bottom point
            (self.x, self.y + self.height / 2)   # Left
        ]
        pygame.draw.polygon(surface, self.color, points)
        
        # Speed lines
        for i in range(3):
            line_y = self.y - 3 - i * 3
            pygame.draw.line(surface, self.color, (self.x + 5, line_y), (self.x + 10, line_y), 1)
            pygame.draw.line(surface, self.color, (self.x + self.width - 10, line_y), (self.x + self.width - 5, line_y), 1)
        
        # Border
        pygame.draw.polygon(surface, (255, 255, 255), points, 2)


class TankEnemy(Enemy):
    """
    Tank enemy type - slow but heavily armored alien.
    3 hits to destroy, 30 points, slower movement.
    """
    
    def __init__(self, x: float, y: float):
        super().__init__(
            x=x,
            y=y,
            width=50,
            height=40,
            health=3,
            speed=0.6,
            points=30,
            color=RED
        )
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the tank enemy with armored appearance."""
        if not self.active:
            return
            
        # Main body
        pygame.draw.rect(surface, self.color, self.rect)
        
        # Armor plating (top)
        armor_rect = pygame.Rect(self.x + 2, self.y + 2, self.width - 4, 10)
        pygame.draw.rect(surface, (180, 0, 0), armor_rect)
        
        # Shield/armor lines
        for i in range(3):
            line_x = self.x + 12 + i * 12
            pygame.draw.line(surface, (100, 0, 0), (line_x, self.y), (line_x, self.y + self.height), 2)
        
        # Eyes (multiple)
        eye_y = self.y + 20
        for i in range(3):
            eye_x = self.x + 12 + i * 13
            pygame.draw.circle(surface, (0, 0, 0), (int(eye_x), int(eye_y)), 3)
        
        # Border
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 3)
        
        # Health bar below enemy
        self._draw_health_bar(surface)
    
    def _draw_health_bar(self, surface: pygame.Surface) -> None:
        """Draw health bar below the tank enemy."""
        bar_width = self.width
        bar_height = 4
        bar_y = self.y + self.height + 3
        
        # Background
        pygame.draw.rect(surface, (50, 50, 50), (self.x, bar_y, bar_width, bar_height))
        
        # Health fill
        health_ratio = self.health / self.max_health
        fill_width = int(bar_width * health_ratio)
        if health_ratio > 0.6:
            health_color = GREEN
        elif health_ratio > 0.3:
            health_color = YELLOW
        else:
            health_color = RED
        pygame.draw.rect(surface, health_color, (self.x, bar_y, fill_width, bar_height))


def create_enemy(enemy_type: str, x: float, y: float) -> Enemy:
    """
    Factory function to create enemies by type.
    
    Args:
        enemy_type: Type of enemy ('basic', 'fast', or 'tank')
        x: X position
        y: Y position
        
    Returns:
        Appropriate Enemy subclass instance
        
    Raises:
        ValueError: If enemy_type is not recognized
    """
    enemy_types = {
        'basic': BasicEnemy,
        'fast': FastEnemy,
        'tank': TankEnemy
    }
    
    enemy_class = enemy_types.get(enemy_type.lower())
    if enemy_class is None:
        raise ValueError(f"Unknown enemy type: {enemy_type}. Valid types: {list(enemy_types.keys())}")
    
    return enemy_class(x, y)


def get_enemy_info(enemy_type: str) -> dict:
    """
    Get static information about an enemy type.
    
    Args:
        enemy_type: Type of enemy ('basic', 'fast', or 'tank')
        
    Returns:
        Dictionary with enemy stats
    """
    info = {
        'basic': {
            'name': 'Basic Enemy',
            'health': 1,
            'speed': 1.0,
            'points': 10,
            'color': GREEN
        },
        'fast': {
            'name': 'Fast Enemy',
            'health': 1,
            'speed': 1.8,
            'points': 20,
            'color': YELLOW
        },
        'tank': {
            'name': 'Tank Enemy',
            'health': 3,
            'speed': 0.6,
            'points': 30,
            'color': RED
        }
    }
    
    return info.get(enemy_type.lower(), {})