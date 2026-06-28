"""
Test suite for the enemy system.
Verifies enemy behavior, fleet management, and shooting mechanics.
"""

import pygame
import unittest
from enemy import Enemy
from enemy_types import BasicEnemy, FastEnemy, TankEnemy, create_enemy, get_enemy_info
from alien_fleet import AlienFleet, Bullet


class TestEnemy(unittest.TestCase):
    """Tests for the Enemy base class."""
    
    def test_enemy_initialization(self):
        """Test enemy is initialized with correct attributes."""
        enemy = Enemy(x=100, y=200, width=40, height=30, health=2, speed=1.5, points=25)
        self.assertEqual(enemy.x, 100)
        self.assertEqual(enemy.y, 200)
        self.assertEqual(enemy.width, 40)
        self.assertEqual(enemy.height, 30)
        self.assertEqual(enemy.health, 2)
        self.assertEqual(enemy.max_health, 2)
        self.assertEqual(enemy.speed, 1.5)
        self.assertEqual(enemy.points, 25)
        self.assertTrue(enemy.active)
    
    def test_enemy_take_damage(self):
        """Test enemy takes damage correctly."""
        enemy = Enemy(x=0, y=0, health=2)
        self.assertFalse(enemy.take_damage())
        self.assertEqual(enemy.health, 1)
        self.assertTrue(enemy.active)
        
        self.assertTrue(enemy.take_damage())
        self.assertEqual(enemy.health, 0)
        self.assertFalse(enemy.active)
    
    def test_enemy_movement(self):
        """Test enemy movement."""
        enemy = Enemy(x=100, y=100, speed=2.0)
        enemy.move(10, 5)
        self.assertEqual(enemy.x, 120)  # 100 + 10*2
        self.assertEqual(enemy.y, 110)  # 100 + 5*2
    
    def test_enemy_rect(self):
        """Test enemy rect property."""
        enemy = Enemy(x=50, y=75, width=40, height=30)
        rect = enemy.rect
        self.assertEqual(rect.x, 50)
        self.assertEqual(rect.y, 75)
        self.assertEqual(rect.width, 40)
        self.assertEqual(rect.height, 30)
    
    def test_enemy_center(self):
        """Test enemy center property."""
        enemy = Enemy(x=100, y=100, width=40, height=30)
        cx, cy = enemy.center
        self.assertEqual(cx, 120)
        self.assertEqual(cy, 115)
    
    def test_enemy_serialization(self):
        """Test enemy to_dict and from_dict."""
        enemy = Enemy(x=50, y=75, width=40, height=30, health=2, speed=1.5, points=25)
        data = enemy.to_dict()
        self.assertEqual(data['x'], 50)
        self.assertEqual(data['y'], 75)
        
        restored = Enemy.from_dict(data)
        self.assertEqual(restored.x, enemy.x)
        self.assertEqual(restored.y, enemy.y)
        self.assertEqual(restored.health, enemy.health)


class TestEnemyTypes(unittest.TestCase):
    """Tests for enemy type subclasses."""
    
    def test_basic_enemy(self):
        """Test BasicEnemy attributes."""
        enemy = BasicEnemy(0, 0)
        self.assertEqual(enemy.health, 1)
        self.assertEqual(enemy.speed, 1.0)
        self.assertEqual(enemy.points, 10)
        self.assertEqual(enemy.width, 40)
        self.assertEqual(enemy.height, 30)
    
    def test_fast_enemy(self):
        """Test FastEnemy attributes."""
        enemy = FastEnemy(0, 0)
        self.assertEqual(enemy.health, 1)
        self.assertEqual(enemy.speed, 1.8)
        self.assertEqual(enemy.points, 20)
        self.assertEqual(enemy.width, 30)
        self.assertEqual(enemy.height, 25)
    
    def test_tank_enemy(self):
        """Test TankEnemy attributes."""
        enemy = TankEnemy(0, 0)
        self.assertEqual(enemy.health, 3)
        self.assertEqual(enemy.max_health, 3)
        self.assertEqual(enemy.speed, 0.6)
        self.assertEqual(enemy.points, 30)
        self.assertEqual(enemy.width, 50)
        self.assertEqual(enemy.height, 40)
    
    def test_create_enemy_factory(self):
        """Test the enemy factory function."""
        basic = create_enemy('basic', 0, 0)
        self.assertIsInstance(basic, BasicEnemy)
        
        fast = create_enemy('fast', 0, 0)
        self.assertIsInstance(fast, FastEnemy)
        
        tank = create_enemy('tank', 0, 0)
        self.assertIsInstance(tank, TankEnemy)
        
        with self.assertRaises(ValueError):
            create_enemy('invalid', 0, 0)
    
    def test_get_enemy_info(self):
        """Test enemy info function."""
        info = get_enemy_info('tank')
        self.assertEqual(info['name'], 'Tank Enemy')
        self.assertEqual(info['health'], 3)
        self.assertEqual(info['points'], 30)


class TestAlienFleet(unittest.TestCase):
    """Tests for the AlienFleet class."""
    
    def setUp(self):
        """Set up test fixtures."""
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        self.fleet = AlienFleet(cols=4, rows=3, start_x=50, start_y=50)
    
    def tearDown(self):
        """Clean up after tests."""
        pygame.quit()
    
    def test_fleet_initialization(self):
        """Test fleet is initialized with correct number of enemies."""
        self.assertEqual(len(self.fleet.enemies), 3)  # rows
        self.assertEqual(len(self.fleet.enemies[0]), 4)  # cols
        
        # Check total active count
        self.assertEqual(self.fleet.get_active_count(), 12)
    
    def test_fleet_grid_positions(self):
        """Test enemies are positioned correctly in grid."""
        # First enemy (row 0, col 0) should be at start position
        enemy = self.fleet.enemies[0][0]  # row 0, col 0 - tank
        self.assertEqual(enemy.x, 50)
        self.assertEqual(enemy.y, 50)
        
        # Second enemy (row 0, col 1) should be offset by spacing
        enemy = self.fleet.enemies[0][1]
        self.assertEqual(enemy.x, 50 + self.fleet.spacing_x)
    
    def test_fleet_enemy_types_by_row(self):
        """Test enemy types are assigned by row."""
        # Row 0 should be TankEnemy
        self.assertIsInstance(self.fleet.enemies[0][0], TankEnemy)
        # Row 1 should be FastEnemy
        self.assertIsInstance(self.fleet.enemies[1][0], FastEnemy)
        # Rows 2+ should be BasicEnemy
        self.assertIsInstance(self.fleet.enemies[2][0], BasicEnemy)
    
    def test_fleet_movement(self):
        """Test fleet moves in correct direction."""
        initial_x = self.fleet.enemies[2][0].x
        self.fleet.direction = 1
        self.fleet._move_fleet()
        self.assertGreater(self.fleet.enemies[2][0].x, initial_x)
    
    def test_fleet_edge_detection(self):
        """Test fleet drops and reverses at edges."""
        self.fleet.direction = 1
        self.fleet.enemies[0][0].x = 780  # Near right edge
        
        initial_y = self.fleet.enemies[0][0].y
        self.fleet._move_fleet()
        
        # Should have dropped down
        self.assertGreater(self.fleet.enemies[0][0].y, initial_y)
        # Should have reversed direction
        self.assertEqual(self.fleet.direction, -1)
    
    def test_fleet_shooting(self):
        """Test enemy shooting mechanism."""
        initial_bullet_count = len(self.fleet.bullets)
        
        # Trigger shooting multiple times
        for _ in range(100):
            self.fleet.shoot_timer = self.fleet.shoot_interval
            self.fleet._enemy_shoot()
        
        # Should have created some bullets
        self.assertGreater(len(self.fleet.bullets), initial_bullet_count)
    
    def test_fleet_bounds(self):
        """Test fleet bounds calculation."""
        bounds = self.fleet.get_fleet_bounds()
        self.assertEqual(len(bounds), 4)  # (min_x, min_y, max_x, max_y)
        self.assertLess(bounds[0], bounds[2])  # min_x < max_x
        self.assertLess(bounds[1], bounds[3])  # min_y < max_y
    
    def test_get_shooters(self):
        """Test shooter selection (bottom-most in each column)."""
        shooters = self.fleet._get_shooters()
        self.assertEqual(len(shooters), self.fleet.cols)
        
        # With 3 rows (rows=0,1,2), bottom row is row 2 (basic enemies)
        # But with default AlienFleet(cols=4, rows=3), bottom row is basic
        for shooter in shooters:
            self.assertIsInstance(shooter, BasicEnemy)  # Bottom row is basic
    
    def test_bullet_movement(self):
        """Test bullet moves downward."""
        bullet = Bullet(x=100, y=100)
        initial_y = bullet.y
        bullet.move()
        self.assertGreater(bullet.y, initial_y)
    
    def test_fleet_reset(self):
        """Test fleet reset functionality."""
        # Move some enemies
        self.fleet.enemies[0][0].x = 500
        self.fleet.direction = -1
        
        # Reset
        self.fleet.reset()
        
        # Should be back to initial state
        self.assertEqual(self.fleet.enemies[0][0].x, 50)
        self.assertEqual(self.fleet.direction, 1)
        self.assertEqual(len(self.fleet.bullets), 0)
    
    def test_fleet_empty(self):
        """Test is_empty returns correct value."""
        self.assertFalse(self.fleet.is_empty())
        
        # Destroy all enemies
        for enemy in self.fleet.get_all_enemies():
            enemy.active = False
        
        self.assertTrue(self.fleet.is_empty())
    
    def test_fleet_draw(self):
        """Test fleet draws without errors."""
        # Should not raise any exceptions
        self.fleet.draw(self.screen)
    
    def test_bullet_draw(self):
        """Test bullet draws without errors."""
        bullet = Bullet(100, 100)
        bullet.draw(self.screen)  # Should not raise


class TestTankEnemyDamage(unittest.TestCase):
    """Tests for TankEnemy damage mechanics."""
    
    def setUp(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
    
    def tearDown(self):
        pygame.quit()
    
    def test_tank_takes_multiple_hits(self):
        """Test tank enemy survives multiple hits."""
        tank = TankEnemy(0, 0)
        self.assertEqual(tank.health, 3)
        self.assertTrue(tank.active)
        
        # First hit
        self.assertFalse(tank.take_damage())
        self.assertEqual(tank.health, 2)
        self.assertTrue(tank.active)
        
        # Second hit
        self.assertFalse(tank.take_damage())
        self.assertEqual(tank.health, 1)
        self.assertTrue(tank.active)
        
        # Third hit - should be destroyed
        self.assertTrue(tank.take_damage())
        self.assertEqual(tank.health, 0)
        self.assertFalse(tank.active)


if __name__ == '__main__':
    unittest.main()