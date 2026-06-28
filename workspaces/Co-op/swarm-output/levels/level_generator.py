"""
Level Generator - Creates level configurations.
"""

def create_level(level_num):
    """Create a level configuration based on level number."""
    return {
        'level': level_num,
        'enemy_count': 5 + (level_num * 2),
        'enemy_speed': 1 + (level_num * 0.2),
        'enemy_spawn_delay': max(1, 3 - (level_num * 0.3)),
    }
