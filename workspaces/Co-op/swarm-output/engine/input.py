"""
Game Engine Core - Input Handler
Handles keyboard input for player controls.
"""

import pygame


class InputHandler:
    """
    Handles keyboard input for the game.
    
    Tracks key states (pressed, held, released) and provides
    convenient methods for checking input in the game loop.
    
    Attributes:
        keys_pressed: Set of currently held keys.
        keys_just_pressed: Set of keys pressed this frame.
        keys_just_released: Set of keys released this frame.
    """
    
    def __init__(self):
        """Initialize the input handler with empty key states."""
        self.keys_pressed = set()
        self.keys_just_pressed = set()
        self.keys_just_released = set()
    
    def on_key_down(self, key: int):
        """
        Handle key press event.
        
        Args:
            key: Pygame key code (e.g., pygame.K_SPACE).
        """
        if key not in self.keys_pressed:
            self.keys_just_pressed.add(key)
        self.keys_pressed.add(key)
    
    def on_key_up(self, key: int):
        """
        Handle key release event.
        
        Args:
            key: Pygame key code (e.g., pygame.K_SPACE).
        """
        if key in self.keys_pressed:
            self.keys_pressed.remove(key)
            self.keys_just_released.add(key)
    
    def end_frame(self):
        """
        Clear per-frame key states.
        
        Called at the end of each game frame to reset just_pressed
        and just_released states.
        """
        self.keys_just_pressed.clear()
        self.keys_just_released.clear()
    
    def reset(self):
        """
        Reset all input state.
        
        Clears all key tracking when starting a new game.
        """
        self.keys_pressed.clear()
        self.keys_just_pressed.clear()
        self.keys_just_released.clear()
    
    def is_key_pressed(self, key: int) -> bool:
        """
        Check if a key is currently held down.
        
        Args:
            key: Pygame key code.
            
        Returns:
            True if the key is currently pressed.
        """
        return key in self.keys_pressed
    
    def is_key_just_pressed(self, key: int) -> bool:
        """
        Check if a key was just pressed this frame.
        
        Use this for actions that should trigger once per press,
        like firing bullets or starting a game.
        
        Args:
            key: Pygame key code.
            
        Returns:
            True if the key was pressed this frame.
        """
        return key in self.keys_just_pressed
    
    def is_key_just_released(self, key: int) -> bool:
        """
        Check if a key was just released this frame.
        
        Args:
            key: Pygame key code.
            
        Returns:
            True if the key was released this frame.
        """
        return key in self.keys_just_released
    
    def get_pressed_keys(self) -> set:
        """
        Get all currently pressed keys.
        
        Returns:
            Set of pressed key codes.
        """
        return self.keys_pressed.copy()
    
    # Player movement helpers
    def is_left_pressed(self) -> bool:
        """Check if left arrow key is pressed."""
        return self.is_key_pressed(pygame.K_LEFT)
    
    def is_right_pressed(self) -> bool:
        """Check if right arrow key is pressed."""
        return self.is_key_pressed(pygame.K_RIGHT)
    
    def is_up_pressed(self) -> bool:
        """Check if up arrow key is pressed."""
        return self.is_key_pressed(pygame.K_UP)
    
    def is_down_pressed(self) -> bool:
        """Check if down arrow key is pressed."""
        return self.is_key_pressed(pygame.K_DOWN)
    
    def is_fire_pressed(self) -> bool:
        """Check if fire key (SPACE) was just pressed."""
        return self.is_key_just_pressed(pygame.K_SPACE)
    
    def is_pause_pressed(self) -> bool:
        """Check if pause key (ESCAPE) was just pressed."""
        return self.is_key_just_pressed(pygame.K_ESCAPE)