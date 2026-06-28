"""
Alien Fleet Manager for Space Invaders game.
Manages a fleet of enemies in a grid formation with classic Space Invaders movement.
"""

import pygame
import random
from typing import List, Optional, Tuple
from enemy import Enemy
from enemy_types import BasicEnemy, FastEnemy, TankEnemy, create_enemy


class Bullet:
    """Represents an enemy bullet."""
    
    def __init__(self, x: float, y: float, speed: float = 5.0):
        self.x = x
        self.y = y
        self.width = 4
        self.height = 12
        self.speed = speed
        self.active = True
    
    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def move(self) -> None:
        """Move the bullet downward."""
        self.y += self.speed
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the bullet."""
        if not self.active:
            return
        pygame.draw.rect(surface, (255, 100, 0), self.rect)
        pygame.draw.rect(surface, (255, 200, 0), (self.x + 1, self.y, 2, self.height))


class AlienFleet:
    """
    Manages a fleet of enemies in grid formation.
    Implements classic Space Invaders movement: move right until edge, drop down, reverse.
    """
    
    def __init__(
        self,
        cols: int = 8,
        rows: int = 4,
        spacing_x: int = 60,
        spacing_y: int = 50,
        start_x: float = 50,
        start_y: float = 50
    ):
        """
        Initialize the alien fleet.
        
        Args:
            cols: Number of columns in the grid
            rows: Number of rows in the grid
            spacing_x: Horizontal spacing between enemies
            spacing_y: Vertical spacing between enemies
            start_x: Starting x position
            start_y: Starting y position
        """
        self.cols = cols
        self.rows = rows
        self.spacing_x = spacing_x
        self.spacing_y = spacing_y
        self.start_x = start_x
        self.start_y = start_y
        
        self.enemies: List[List[Enemy]] = []
        self.bullets: List[Bullet] = []
        
        # Movement state
        self.direction = 1  # 1 = right, -1 = left
        self.base_speed = 1.0
        self.move_timer = 0
        self.move_interval = 30  # Frames between moves
        self.drop_amount = 20
        
        # Shooting state
        self.shoot_interval = 60  # Frames between potential shots
        self.shoot_timer = 0
        self.shoot_chance = 0.3  # 30% chance per eligible enemy
        
        # Screen bounds for movement
        self.screen_width = 800
        self.screen_height = 600
        self.min_x = 10
        self.max_x = 790
        
        self._initialize_fleet()
    
    def _initialize_fleet(self) -> None:
        """Create the initial fleet in grid formation."""
        self.enemies = []
        
        for row in range(self.rows):
            enemy_row = []
            for col in range(self.cols):
                x = self.start_x + col * self.spacing_x
                y = self.start_y + row * self.spacing_y
                
                # Assign enemy type based on row
                if row == 0:
                    enemy = TankEnemy(x, y)
                elif row == 1:
                    enemy = FastEnemy(x, y)
                else:
                    enemy = BasicEnemy(x, y)
                
                enemy_row.append(enemy)
            self.enemies.append(enemy_row)
    
    def get_all_enemies(self) -> List[Enemy]:
        """Get a flat list of all active enemies."""
        all_enemies = []
        for row in self.enemies:
            for enemy in row:
                if enemy.active:
                    all_enemies.append(enemy)
        return all_enemies
    
    def get_active_count(self) -> int:
        """Get the count of active enemies."""
        return len(self.get_all_enemies())
    
    def is_empty(self) -> bool:
        """Check if all enemies are destroyed."""
        return self.get_active_count() == 0
    
    def get_fleet_bounds(self) -> Tuple[float, float, float, float]:
        """Get the bounding box of all active enemies."""
        if not self.get_all_enemies():
            return (0, 0, 0, 0)
        
        min_x = float('inf')
        min_y = float('inf')
        max_x = float('-inf')
        max_y = float('-inf')
        
        for enemy in self.get_all_enemies():
            min_x = min(min_x, enemy.x)
            min_y = min(min_y, enemy.y)
            max_x = max(max_x, enemy.x + enemy.width)
            max_y = max(max_y, enemy.y + enemy.height)
        
        return (min_x, min_y, max_x, max_y)
    
    def update(self) -> None:
        """Update fleet movement and shooting."""
        self.move_timer += 1
        
        # Calculate current move interval based on remaining enemies
        current_interval = max(5, int(self.move_interval * (50 / max(self.get_active_count(), 1))))
        
        # Move the fleet
        if self.move_timer >= current_interval:
            self.move_timer = 0
            self._move_fleet()
        
        # Update bullets
        self._update_bullets()
        
        # Handle shooting
        self.shoot_timer += 1
        if self.shoot_timer >= self.shoot_interval:
            self.shoot_timer = 0
            self._enemy_shoot()
    
    def _move_fleet(self) -> None:
        """Move the fleet and handle edge detection."""
        # Get current fleet bounds
        left, top, right, bottom = self.get_fleet_bounds()
        
        # Calculate how far we can move
        move_amount = self.base_speed * 10 * self.direction
        
        # Check if we need to change direction
        should_drop = False
        if self.direction > 0 and right + move_amount > self.max_x:
            should_drop = True
        elif self.direction < 0 and left + move_amount < self.min_x:
            should_drop = True
        
        if should_drop:
            # Drop down and reverse direction
            for enemy in self.get_all_enemies():
                enemy.y += self.drop_amount
            self.direction *= -1
        else:
            # Move horizontally
            for enemy in self.get_all_enemies():
                enemy.x += move_amount
    
    def _update_bullets(self) -> None:
        """Update all bullets and remove inactive ones."""
        for bullet in self.bullets:
            bullet.move()
            # Deactivate if off screen
            if bullet.y > self.screen_height:
                bullet.active = False
        
        # Remove inactive bullets
        self.bullets = [b for b in self.bullets if b.active]
    
    def _enemy_shoot(self) -> None:
        """Random enemies fire bullets downward."""
        # Get bottom-most enemies in each column
        shooters = self._get_shooters()
        
        if not shooters:
            return
        
        # Randomly select enemies to fire
        for enemy in shooters:
            if random.random() < self.shoot_chance:
                bullet = Bullet(
                    x=enemy.x + enemy.width / 2 - 2,
                    y=enemy.y + enemy.height,
                    speed=4.0 + enemy.speed
                )
                self.bullets.append(bullet)
    
    def _get_shooters(self) -> List[Enemy]:
        """Get the bottom-most active enemy in each column."""
        shooters = []
        
        for col in range(self.cols):
            bottom_enemy = None
            bottom_y = float('-inf')
            
            for row in range(self.rows - 1, -1, -1):  # Check from bottom to top
                enemy = self.enemies[row][col]
                if enemy.active and enemy.y > bottom_y:
                    bottom_y = enemy.y
                    bottom_enemy = enemy
            
            if bottom_enemy:
                shooters.append(bottom_enemy)
        
        return shooters
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw all enemies and bullets."""
        # Draw enemies
        for enemy in self.get_all_enemies():
            enemy.draw(surface)
        
        # Draw bullets
        for bullet in self.bullets:
            bullet.draw(surface)
    
    def check_collision(self, rect: pygame.Rect) -> Optional[Enemy]:
        """
        Check if a rectangle collides with any enemy.
        
        Args:
            rect: Pygame rectangle to check
            
        Returns:
            The enemy that was hit, or None
        """
        for enemy in self.get_all_enemies():
            if enemy.rect.colliderect(rect):
                return enemy
        return None
    
    def remove_bullet(self, bullet: Bullet) -> None:
        """Remove a bullet from the fleet."""
        bullet.active = False
    
    def set_screen_bounds(self, width: int, height: int) -> None:
        """Set the screen bounds for movement."""
        self.screen_width = width
        self.screen_height = height
        self.max_x = width - 10
    
    def reset(self) -> None:
        """Reset the fleet to initial state."""
        self.bullets = []
        self.direction = 1
        self.move_timer = 0
        self.shoot_timer = 0
        self._initialize_fleet()
    
    def increase_difficulty(self) -> None:
        """Increase fleet speed as enemies are destroyed."""
        remaining = self.get_active_count()
        if remaining > 0:
            # Speed increases as fewer enemies remain
            speed_multiplier = 1 + (self.cols * self.rows - remaining) * 0.02
            self.move_interval = max(5, int(30 / speed_multiplier))
    
    def get_lowest_enemy_y(self) -> float:
        """Get the y position of the lowest active enemy."""
        lowest_y = 0
        for enemy in self.get_all_enemies():
            if enemy.y + enemy.height > lowest_y:
                lowest_y = enemy.y + enemy.height
        return lowest_y
    
    def reached_player_line(self, player_y: float) -> bool:
        """Check if any enemy has reached the player's line."""
        return self.get_lowest_enemy_y() >= player_y
    
    def to_dict(self) -> dict:
        """Serialize fleet state."""
        return {
            'cols': self.cols,
            'rows': self.rows,
            'direction': self.direction,
            'enemies': [[e.to_dict() for e in row] for row in self.enemies],
            'bullets': [{'x': b.x, 'y': b.y, 'active': b.active} for b in self.bullets]
        }