"""
Level Generator - Procedurally generates level layouts.
"""

def create_level(level_num, screen_width=800, screen_height=600):
    rows = min(4 + level_num // 3, 6)
    cols = 8
    enemies = []
    start_x, start_y = 100, 50
    spacing_x, spacing_y = 60, 40
    
    for row in range(rows):
        for col in range(cols):
            if row == 0:
                enemy_type = 'tank_enemy'
            elif row < 3:
                enemy_type = 'fast_enemy'
            else:
                enemy_type = 'basic_enemy'
            x = start_x + col * spacing_x
            y = start_y + row * spacing_y
            enemies.append((x, y, enemy_type))
    
    return enemies
