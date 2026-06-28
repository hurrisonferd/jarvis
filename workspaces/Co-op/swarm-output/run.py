#!/usr/bin/env python3
"""
Space Invaders Game Launcher
Installs dependencies and starts the game.
"""

import subprocess
import sys


def install_requirements():
    """Install required packages if not already installed."""
    try:
        import pygame
        print(f"Pygame already installed: {pygame.version.ver}")
    except ImportError:
        print("Installing pygame...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pygame>=2.0.0"])
    
    try:
        import numpy
        print(f"NumPy already installed: {numpy.__version__}")
    except ImportError:
        print("Installing numpy...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy>=1.20.0"])


def main():
    """Install dependencies and launch the game."""
    print("=" * 50)
    print("SPACE INVADERS")
    print("=" * 50)
    print()
    
    # Install dependencies
    install_requirements()
    
    print()
    print("Starting game...")
    print("=" * 50)
    
    # Import and run main
    import main as game_module
    game_module.main()


if __name__ == "__main__":
    main()
