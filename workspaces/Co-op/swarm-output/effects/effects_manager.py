"""
Effects Manager - Manages visual effects.
"""

class EffectsManager:
    """Manages visual effects like explosions and particles."""
    
    def __init__(self, renderer):
        self.renderer = renderer
        self.effects = []
    
    def add_explosion(self, x, y):
        """Add an explosion effect at the given position."""
        self.effects.append({'type': 'explosion', 'x': x, 'y': y})
    
    def update(self):
        """Update all active effects."""
        pass
    
    def render(self):
        """Render all active effects."""
        pass
    
    def clear(self):
        """Clear all effects."""
        self.effects.clear()
