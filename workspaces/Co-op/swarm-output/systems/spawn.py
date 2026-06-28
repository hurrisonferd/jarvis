"""
Spawn System - Handles spawning entities.
"""

class SpawnSystem:
    def __init__(self):
        self.spawn_timer = 0
        self.spawn_interval = 2.0

    def update(self, entities, delta_time):
        self.spawn_timer += delta_time
        return entities
