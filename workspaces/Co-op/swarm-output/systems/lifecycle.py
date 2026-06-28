"""
Lifecycle System - Handles entity creation and destruction.
"""

class LifeCycleSystem:
    def __init__(self):
        self.to_remove = []

    def mark_for_removal(self, entity):
        self.to_remove.append(entity)

    def cleanup(self, entities):
        for entity in self.to_remove:
            if entity in entities:
                entities.remove(entity)
        self.to_remove = []

    def update(self, entities):
        self.cleanup(entities)
        return entities
