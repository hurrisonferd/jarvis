"""
Level Manager - Manages game levels.
"""

class LevelManager:
    """Manages game level progression."""
    
    def __init__(self):
        self.levels = {}
        self.current_level = 1
    
    def add_level(self, level_num, level_data):
        """Add a level to the manager."""
        self.levels[level_num] = level_data
    
    def get_current_level(self):
        """Get the current level data."""
        return self.levels.get(self.current_level)
    
    def next_level(self):
        """Advance to the next level."""
        self.current_level += 1
