"""
Systems package for Space Invaders game.
ECS-style systems for game logic processing.
"""

from systems.movement import MovementSystem
from systems.collision import CollisionSystem
from systems.spawn import SpawnSystem
from systems.lifecycle import LifeCycleSystem
from systems.score import ScoreSystem

__all__ = [
    'MovementSystem',
    'CollisionSystem',
    'SpawnSystem',
    'LifeCycleSystem',
    'ScoreSystem',
]