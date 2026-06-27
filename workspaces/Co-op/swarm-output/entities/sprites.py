"""Sprite graphics for Space Invaders player ship."""

import pygame
from typing import Tuple, List


class PlayerSprite:
    """Visual sprite renderer for the player ship."""
    
    def __init__(self):
        """Initialize sprite with colors."""
        # Main ship color (green)
        self.main_color = (0, 255, 0)
        # Secondary color (darker green)
        self.secondary_color = (0, 180, 0)
        # Accent color (cyan)
        self.accent_color = (0, 255, 255)
        # Cockpit color
        self.cockpit_color = (100, 255, 255)
        # Engine glow color
        self.engine_color = (255, 100, 0)
        
    def draw_triangle_ship(self, surface: pygame.Surface, x: int, y: int, 
                           width: int, height: int) -> None:
        """Draw a classic triangle Space Invaders style ship.
        
        Args:
            surface: Pygame surface to draw on
            x: X position (left edge)
            y: Y position (top edge)
            width: Ship width
            height: Ship height
        """
        # Main body triangle
        points = [
            (x + width // 2, y),  # Top point
            (x, y + height),       # Bottom left
            (x + width, y + height)  # Bottom right
        ]
        pygame.draw.polygon(surface, self.main_color, points)
        
        # Inner triangle (detail)
        inner_points = [
            (x + width // 2, y + height // 3),
            (x + width // 4, y + height),
            (x + 3 * width // 4, y + height)
        ]
        pygame.draw.polygon(surface, self.secondary_color, inner_points)
        
        # Cockpit
        cockpit_x = x + width // 2 - 4
        cockpit_y = y + height // 4
        pygame.draw.ellipse(surface, self.cockpit_color, 
                          (cockpit_x, cockpit_y, 8, 10))
        
    def draw_detailed_ship(self, surface: pygame.Surface, x: int, y: int,
                           width: int, height: int) -> None:
        """Draw a more detailed Space Invaders style ship with wings.
        
        Args:
            surface: Pygame surface to draw on
            x: X position (left edge)
            y: Y position (top edge)
            width: Ship width
            height: Ship height
        """
        center_x = x + width // 2
        
        # Main body (central rectangle)
        body_rect = pygame.Rect(x + width // 3, y + height // 4, 
                                width // 3, height // 2)
        pygame.draw.rect(surface, self.main_color, body_rect)
        
        # Nose cone (triangle)
        nose_points = [
            (center_x, y),  # Top point
            (x + width // 4, y + height // 3),  # Bottom left
            (x + 3 * width // 4, y + height // 3)  # Bottom right
        ]
        pygame.draw.polygon(surface, self.main_color, nose_points)
        
        # Left wing
        wing_left = [
            (x, y + height // 2),  # Tip
            (x + width // 4, y + height // 2),  # Inner
            (x + width // 3, y + height),  # Bottom inner
            (x, y + height)  # Bottom outer
        ]
        pygame.draw.polygon(surface, self.secondary_color, wing_left)
        
        # Right wing
        wing_right = [
            (x + width, y + height // 2),  # Tip
            (x + 3 * width // 4, y + height // 2),  # Inner
            (x + 2 * width // 3, y + height),  # Bottom inner
            (x + width, y + height)  # Bottom outer
        ]
        pygame.draw.polygon(surface, self.secondary_color, wing_right)
        
        # Cockpit window
        cockpit_rect = pygame.Rect(center_x - 5, y + height // 3, 10, 8)
        pygame.draw.ellipse(surface, self.cockpit_color, cockpit_rect)
        
        # Engine glow
        pygame.draw.circle(surface, self.engine_color, 
                         (center_x, y + height - 3), 4)
        
    def draw_classic_ship(self, surface: pygame.Surface, x: int, y: int,
                          width: int, height: int) -> None:
        """Draw the classic Space Invaders player ship (rectangle with details).
        
        Args:
            surface: Pygame surface to draw on
            x: X position (left edge)
            y: Y position (top edge)
            width: Ship width
            height: Ship height
        """
        # Base rectangle
        base_rect = pygame.Rect(x + 2, y, width - 4, height - 5)
        pygame.draw.rect(surface, self.main_color, base_rect)
        
        # Top cannon
        pygame.draw.rect(surface, self.accent_color, 
                        (x + width // 2 - 3, y, 6, height // 3))
        
        # Side details
        pygame.draw.rect(surface, self.secondary_color,
                        (x, y + height // 2, 5, height // 3))
        pygame.draw.rect(surface, self.secondary_color,
                        (x + width - 5, y + height // 2, 5, height // 3))
        
        # Bottom engine area
        pygame.draw.rect(surface, self.engine_color,
                        (x + 5, y + height - 8, width - 10, 5))
    
    def draw_animated_engine(self, surface: pygame.Surface, x: int, y: int,
                             width: int, frame: int) -> None:
        """Draw animated engine flames.
        
        Args:
            surface: Pygame surface to draw on
            x: X position
            y: Y position (flame extends below this)
            width: Ship width
            frame: Animation frame (for varying flame)
        """
        center_x = x + width // 2
        flame_height = 8 + (frame % 3) * 3
        
        # Main flame
        flame_points = [
            (center_x - 8, y),
            (center_x + 8, y),
            (center_x, y + flame_height)
        ]
        pygame.draw.polygon(surface, self.engine_color, flame_points)
        
        # Inner flame (brighter)
        inner_flame_points = [
            (center_x - 4, y),
            (center_x + 4, y),
            (center_x, y + flame_height - 4)
        ]
        pygame.draw.polygon(surface, (255, 200, 50), inner_flame_points)


# Global sprite instance
player_sprite = PlayerSprite()
