"""Game controller handling player input, movement, and shooting."""

import pygame
import time
from typing import List

from .player import Player
from .projectile import Bullet


class GameController:
    """Handles player input, movement, and shooting mechanics."""
    
    def __init__(self, screen_width: int, screen_height: int):
        """Initialize game controller.
        
        Args:
            screen_width: Width of the game screen
            screen_height: Height of the game screen
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Create player
        self.player = Player(screen_width, screen_height)
        
        # Bullets list
        self.bullets: List[Bullet] = []
        
        # Shooting cooldown: 250ms between shots
        self.shoot_cooldown_ms = 250
        self.last_shot_time = 0
        
        # Input state tracking
        self.keys_pressed = pygame.key.get_pressed()
        
    def handle_input(self) -> None:
        """Process keyboard input for player movement."""
        self.keys_pressed = pygame.key.get_pressed()
        
        # Movement: Arrow keys or A/D
        if self.keys_pressed[pygame.K_LEFT] or self.keys_pressed[pygame.K_a]:
            self.player.move_left()
            
        if self.keys_pressed[pygame.K_RIGHT] or self.keys_pressed[pygame.K_d]:
            self.player.move_right()
            
        if self.keys_pressed[pygame.K_UP] or self.keys_pressed[pygame.K_w]:
            self.player.move_up()
            
        if self.keys_pressed[pygame.K_DOWN] or self.keys_pressed[pygame.K_s]:
            self.player.move_down()
    
    def can_shoot(self) -> bool:
        """Check if enough time has passed since last shot.
        
        Returns:
            True if cooldown has elapsed
        """
        current_time_ms = int(time.time() * 1000)
        return (current_time_ms - self.last_shot_time) >= self.shoot_cooldown_ms
    
    def shoot(self) -> bool:
        """Fire a bullet from player position if cooldown allows.
        
        Returns:
            True if bullet was fired
        """
        if self.can_shoot():
            # Create bullet at player's center top
            bullet_x = self.player.x + self.player.width // 2
            bullet_y = self.player.y
            new_bullet = Bullet(bullet_x, bullet_y)
            self.bullets.append(new_bullet)
            
            # Update last shot time
            self.last_shot_time = int(time.time() * 1000)
            return True
        return False
    
    def handle_shooting(self, event: pygame.event.Event) -> None:
        """Handle shooting event (spacebar).
        
        Args:
            event: Pygame event to check for spacebar
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.shoot()
    
    def update(self) -> None:
        """Update all game entities."""
        # Handle continuous movement
        self.handle_input()
        
        # Update all bullets
        for bullet in self.bullets:
            bullet.update()
        
        # Remove inactive bullets
        self.bullets = [b for b in self.bullets if b.is_active()]
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw player and all bullets.
        
        Args:
            surface: Pygame surface to draw on
        """
        # Draw player
        self.player.draw(surface)
        
        # Draw all bullets
        for bullet in self.bullets:
            bullet.draw(surface)
    
    def get_bullets(self) -> List[Bullet]:
        """Get list of active bullets."""
        return self.bullets
    
    def reset(self) -> None:
        """Reset game state."""
        self.player.reset(self.screen_width, self.screen_height)
        self.bullets = []
        self.last_shot_time = 0
