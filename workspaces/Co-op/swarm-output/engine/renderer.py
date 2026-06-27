"""
Game Engine Core - Renderer
Handles all drawing operations, clearing screen, and updating display.
"""

import pygame


class Renderer:
    """
    Handles all rendering operations for the game.
    
    Provides methods for clearing the screen, drawing text, shapes,
    and sprites. All drawing operations go through this class.
    
    Attributes:
        screen: Pygame surface to draw on.
        screen_width: Width of the render surface.
        screen_height: Height of the render surface.
        background_color: Default background color (RGB tuple).
    """
    
    def __init__(self, screen: pygame.Surface, screen_width: int, screen_height: int):
        """
        Initialize the renderer with screen dimensions.
        
        Args:
            screen: Pygame surface to draw on.
            screen_width: Width of the screen.
            screen_height: Height of the screen.
        """
        self.screen = screen
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.background_color = (0, 0, 0)  # Black background
    
    def clear(self):
        """
        Clear the screen with the background color.
        Called at the start of each frame before drawing.
        """
        self.screen.fill(self.background_color)
    
    def set_background_color(self, color: tuple):
        """
        Set the background color for clearing.
        
        Args:
            color: RGB tuple, e.g., (0, 0, 0) for black.
        """
        self.background_color = color
    
    def draw_text(self, text: str, x: int, y: int, 
                  size: int = 24, color: tuple = (255, 255, 255),
                  center: bool = False, bold: bool = False):
        """
        Draw text on the screen.
        
        Args:
            text: The text string to render.
            x: X coordinate for text position.
            y: Y coordinate for text position.
            size: Font size in points.
            color: RGB color tuple, default white.
            center: If True, x and y are the center of the text.
            bold: If True, use bold font weight.
        """
        font = pygame.font.Font(None, size)
        font.set_bold(bold)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        
        if center:
            text_rect.center = (x, y)
        else:
            text_rect.topleft = (x, y)
        
        self.screen.blit(text_surface, text_rect)
        return text_rect
    
    def draw_rect(self, x: int, y: int, width: int, height: int,
                  color: tuple = (255, 255, 255), filled: bool = True,
                  border_width: int = 0):
        """
        Draw a rectangle on the screen.
        
        Args:
            x: X coordinate of top-left corner.
            y: Y coordinate of top-left corner.
            width: Width of the rectangle.
            height: Height of the rectangle.
            color: RGB color tuple.
            filled: If True, rectangle is filled; otherwise outline only.
            border_width: Width of border when not filled.
        """
        rect = pygame.Rect(x, y, width, height)
        if filled:
            pygame.draw.rect(self.screen, color, rect)
        else:
            pygame.draw.rect(self.screen, color, rect, border_width)
        return rect
    
    def draw_circle(self, x: int, y: int, radius: int,
                    color: tuple = (255, 255, 255), filled: bool = True,
                    border_width: int = 0):
        """
        Draw a circle on the screen.
        
        Args:
            x: X coordinate of center.
            y: Y coordinate of center.
            radius: Radius of the circle.
            color: RGB color tuple.
            filled: If True, circle is filled; otherwise outline only.
            border_width: Width of border when not filled.
        """
        if filled:
            pygame.draw.circle(self.screen, color, (x, y), radius)
        else:
            pygame.draw.circle(self.screen, color, (x, y), radius, border_width)
    
    def draw_line(self, start_x: int, start_y: int, end_x: int, end_y: int,
                  color: tuple = (255, 255, 255), width: int = 1):
        """
        Draw a line on the screen.
        
        Args:
            start_x: X coordinate of start point.
            start_y: Y coordinate of start point.
            end_x: X coordinate of end point.
            end_y: Y coordinate of end point.
            color: RGB color tuple.
            width: Width of the line.
        """
        pygame.draw.line(self.screen, color, (start_x, start_y), (end_x, end_y), width)
    
    def draw_polygon(self, points: list, color: tuple = (255, 255, 255), filled: bool = True):
        """
        Draw a polygon on the screen.
        
        Args:
            points: List of (x, y) tuples defining the polygon vertices.
            color: RGB color tuple.
            filled: If True, polygon is filled; otherwise outline only.
        """
        if filled:
            pygame.draw.polygon(self.screen, color, points)
        else:
            pygame.draw.polygon(self.screen, color, points, 1)
    
    def draw_surface(self, surface: pygame.Surface, x: int, y: int,
                     center: bool = False):
        """
        Draw a Pygame surface (sprite) on the screen.
        
        Args:
            surface: Pygame surface to draw.
            x: X coordinate for surface position.
            y: Y coordinate for surface position.
            center: If True, x and y are the center of the surface.
        """
        surface_rect = surface.get_rect()
        if center:
            surface_rect.center = (x, y)
        else:
            surface_rect.topleft = (x, y)
        self.screen.blit(surface, surface_rect)
        return surface_rect
    
    def draw_sprite(self, sprite: pygame.Surface, x: int, y: int,
                    width: int = None, height: int = None, center: bool = False):
        """
        Draw a sprite with optional scaling.
        
        Args:
            sprite: Pygame surface to draw as sprite.
            x: X coordinate for sprite position.
            y: Y coordinate for sprite position.
            width: Optional width to scale sprite to.
            height: Optional height to scale sprite to.
            center: If True, x and y are the center of the sprite.
        """
        if width and height:
            sprite = pygame.transform.scale(sprite, (width, height))
        self.draw_surface(sprite, x, y, center=center)
    
    def get_surface(self) -> pygame.Surface:
        """
        Get the underlying Pygame surface.
        
        Returns:
            The Pygame surface this renderer draws to.
        """
        return self.screen