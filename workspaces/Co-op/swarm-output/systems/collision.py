"""
Collision System - Handles entity collision detection.
"""

class CollisionSystem:
    """System for collision detection between entities."""

    def __init__(self):
        pass

    def check_collision(self, a, b):
        """Check if two entities are colliding (AABB)."""
        if not hasattr(a, 'x') or not hasattr(b, 'x'):
            return False
        return (a.x < b.x + getattr(b, 'width', 32) and
                a.x + getattr(a, 'width', 32) > b.x and
                a.y < b.y + getattr(b, 'height', 32) and
                a.y + getattr(a, 'height', 32) > b.y)

    def update(self, entities):
        """Check and resolve collisions between entities."""
        bullets = [e for e in entities if getattr(e, 'type', None) == 'bullet' and getattr(e, 'is_player', False)]
        enemies = [e for e in entities if getattr(e, 'type', None) in ('enemy', 'basic_enemy', 'fast_enemy', 'tank_enemy')]
        
        collisions = []
        for bullet in bullets:
            for enemy in enemies:
                if self.check_collision(bullet, enemy):
                    collisions.append((bullet, enemy))
        
        return collisions

    def player_enemy_collision(self, player, enemies):
        """Check if player collides with any enemy."""
        for enemy in enemies:
            if self.check_collision(player, enemy):
                return enemy
        return None
