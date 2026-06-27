"""
Terminal Emulator Package

A basic VT100-compatible terminal emulator with escape code support.
"""

from .core import (
    TerminalEmulator,
    Buffer,
    Cursor,
    Cell,
    EscapeSequenceParser,
    InputHandler,
    CursorStyle,
    ANSI_COLORS,
)

__all__ = [
    "TerminalEmulator",
    "Buffer",
    "Cursor",
    "Cell",
    "EscapeSequenceParser",
    "InputHandler",
    "CursorStyle",
    "ANSI_COLORS",
]

__version__ = "0.1.0"
