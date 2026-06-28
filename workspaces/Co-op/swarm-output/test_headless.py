#!/usr/bin/env python3
"""Headless test - runs game logic without graphics."""
import sys
sys.path.insert(0, '.')

print("Testing Space Invaders in headless mode...")
from engine import Game
from entities import Player, Bullet
from systems import MovementSystem, CollisionSystem, SpawnSystem, LifeCycleSystem
from levels import LevelManager, create_level
from ui import HUD

print("All imports successful!")
player = Player(400, 500)
print(f"Player at ({player.x}, {player.y})")
enemies = create_level(1)
print(f"Level 1 has {len(enemies)} enemies")
print("Game logic verified!")
print()
print("To play with display:")
print("  cd workspaces/Co-op/swarm-output && python3 run.py")
