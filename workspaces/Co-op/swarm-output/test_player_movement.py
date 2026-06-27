"""Test script for player movement and shooting mechanics."""

import pygame
import sys

# Add parent directory to path
sys.path.insert(0, '/workspace/project/Jarvis-Private/workspaces/Co-op/swarm-output')

from entities import Player, Bullet, GameController


def test_player_creation():
    """Test 1: Player initializes correctly."""
    print("Test 1: Player creation...")
    player = Player(800, 600)
    
    # Check position (should be bottom center)
    assert player.x == 380, f"Expected x=380, got {player.x}"
    assert player.y == 540, f"Expected y=540, got {player.y}"  # 600 - 40 - 20
    
    # Check size
    assert player.width == 40, f"Expected width=40, got {player.width}"
    assert player.height == 40, f"Expected height=40, got {player.height}"
    
    # Check speed
    assert player.speed == 5, f"Expected speed=5, got {player.speed}"
    
    # Check health
    assert player.health == 3, f"Expected health=3, got {player.health}"
    
    print("  ✓ Player creation passed!")
    return True


def test_player_movement():
    """Test 2: Player movement with boundary checking."""
    print("Test 2: Player movement...")
    player = Player(800, 600)
    
    # Test initial position
    initial_x = player.x
    
    # Move right
    player.move_right()
    assert player.x == initial_x + 5, f"Right movement failed: x={player.x}"
    
    # Move left
    player.move_left()
    assert player.x == initial_x, f"Left movement failed: x={player.x}"
    
    # Test boundary - left edge
    for _ in range(200):
        player.move_left()
    assert player.x == 0, f"Left boundary failed: x={player.x}"
    
    # Test boundary - right edge
    for _ in range(200):
        player.move_right()
    assert player.x == 800 - 40, f"Right boundary failed: x={player.x}"
    
    print("  ✓ Movement and boundary checking passed!")
    return True


def test_bullet():
    """Test 3: Bullet creation and movement."""
    print("Test 3: Bullet mechanics...")
    bullet = Bullet(400, 500)
    
    # Check initial position
    assert bullet.x == 397, f"Bullet x incorrect: {bullet.x}"  # 400 - 6//2
    assert bullet.y == 500, f"Bullet y incorrect: {bullet.y}"
    
    # Check speed
    assert bullet.speed == 7, f"Bullet speed incorrect: {bullet.speed}"
    
    # Check active state
    assert bullet.is_active() == True, "Bullet should be active initially"
    
    # Move bullet upward
    bullet.update()
    assert bullet.y == 493, f"Bullet update failed: y={bullet.y}"
    
    # Move bullet off screen
    for _ in range(80):
        bullet.update()
    assert bullet.is_active() == False, "Bullet should be inactive after off-screen"
    
    print("  ✓ Bullet mechanics passed!")
    return True


def test_game_controller():
    """Test 4: Game controller initialization."""
    print("Test 4: Game controller...")
    controller = GameController(800, 600)
    
    # Check player exists
    assert controller.player is not None, "Player should exist"
    
    # Check bullets list
    assert len(controller.bullets) == 0, "Bullets should start empty"
    
    # Check cooldown
    assert controller.shoot_cooldown_ms == 250, "Cooldown should be 250ms"
    
    print("  ✓ Game controller passed!")
    return True


def test_shooting_cooldown():
    """Test 5: Shooting cooldown mechanism."""
    print("Test 5: Shooting cooldown...")
    controller = GameController(800, 600)
    
    # First shot should work
    result = controller.shoot()
    assert result == True, "First shot should succeed"
    assert len(controller.bullets) == 1, "Should have 1 bullet"
    
    # Second shot immediately should fail (cooldown)
    result = controller.shoot()
    assert result == False, "Second shot should fail (cooldown)"
    assert len(controller.bullets) == 1, "Should still have 1 bullet"
    
    print("  ✓ Shooting cooldown passed!")
    return True


def test_sprite_styles():
    """Test 6: Sprite style selection."""
    print("Test 6: Sprite styles...")
    
    # Triangle style (default)
    player_tri = Player(800, 600, sprite_style="triangle")
    assert player_tri.sprite_style == "triangle"
    
    # Detailed style
    player_det = Player(800, 600, sprite_style="detailed")
    assert player_det.sprite_style == "detailed"
    
    # Classic style
    player_cls = Player(800, 600, sprite_style="classic")
    assert player_cls.sprite_style == "classic"
    
    print("  ✓ Sprite styles passed!")
    return True


def run_all_tests():
    """Run all tests."""
    print("=" * 50)
    print("Running Player Movement System Tests")
    print("=" * 50)
    
    pygame.init()
    pygame.display.set_mode((1, 1))  # Minimal display for pygame
    
    tests = [
        test_player_creation,
        test_player_movement,
        test_bullet,
        test_game_controller,
        test_shooting_cooldown,
        test_sprite_styles,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"  ✗ {test.__name__} FAILED: {e}")
            failed += 1
    
    pygame.quit()
    
    print("=" * 50)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 50)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
