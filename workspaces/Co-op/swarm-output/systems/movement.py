"""
Movement System - Handles entity movement.
"""

class MovementSystem:
    """System for processing entity movement."""

    def __init__(self):
        pass

    def update(self, entities, delta_time):
        """Update positions of all movable entities."""
        for entity in entities:
            if hasattr(entity, 'velocity') and hasattr(entity, 'x') and hasattr(entity, 'y'):
                entity.x += entity.velocity.get('x', 0) * delta_time
                entity.y += entity.velocity.get('y', 0) * delta_time
                
                # Clamp to screen bounds if entity has bounds
                if hasattr(entity, 'screen_width') and hasattr(entity, 'screen_height'):
                    entity.x = max(0, min(entity.x, entity.screen_width - getattr(entity, 'width', 32)))
                    entity.y = max(0, min(entity.y, entity.screen_height - getattr(entity, 'height', 32)))
