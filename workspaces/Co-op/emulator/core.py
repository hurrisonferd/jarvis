"""
Terminal Emulator Core Module
Provides VT100 escape code parsing, buffer management, and input handling.
"""

import asyncio
import re
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Callable, Optional


class CursorStyle(Enum):
    """Cursor visibility and style."""
    HIDDEN = 0
    BLOCK = 1
    UNDERLINE = 2
    BEAM = 3


@dataclass
class Cell:
    """Represents a single character cell in the terminal."""
    char: str = " "
    fg: int = 7       # Default foreground (white)
    bg: int = 0       # Default background (black)
    bold: bool = False
    dim: bool = False
    italic: bool = False
    underline: bool = False
    inverse: bool = False
    blink: bool = False

    def reset(self) -> None:
        """Reset cell to default state."""
        self.char = " "
        self.fg = 7
        self.bg = 0
        self.bold = False
        self.dim = False
        self.italic = False
        self.underline = False
        self.inverse = False
        self.blink = False


@dataclass
class Cursor:
    """Terminal cursor state."""
    x: int = 0
    y: int = 0
    visible: bool = True
    style: CursorStyle = CursorStyle.BLOCK

    def move(self, x: int, y: int) -> None:
        """Move cursor to position."""
        self.x = max(0, x)
        self.y = max(0, y)

    def move_relative(self, dx: int, dy: int) -> None:
        """Move cursor relative to current position."""
        self.x = max(0, self.x + dx)
        self.y = max(0, self.y + dy)


@dataclass
class TerminalState:
    """Terminal state for save/restore cursor."""
    cursor_x: int = 0
    cursor_y: int = 0
    origin_mode: bool = False
    wrap: bool = True


class Buffer:
    """Manages the terminal screen buffer and scrollback."""

    def __init__(self, width: int = 80, height: int = 24, scrollback: int = 1000):
        self.width = width
        self.height = height
        self.scrollback_size = scrollback
        self.scrollback: list[list[Cell]] = []
        self.screen: list[list[Cell]] = self._create_empty_screen()
        self.cursor = Cursor()
        self.saved_cursor: Optional[TerminalState] = None
        self._setup_state()

    def _create_empty_row(self) -> list[Cell]:
        """Create an empty row of cells."""
        return [Cell() for _ in range(self.width)]

    def _create_empty_screen(self) -> list[list[Cell]]:
        """Create an empty screen buffer."""
        return [self._create_empty_row() for _ in range(self.height)]

    def _setup_state(self) -> None:
        """Initialize terminal state."""
        self.margins_top = 0
        self.margins_bottom = self.height - 1
        self.origin_mode = False
        self.auto_wrap = True
        self.cursor_visible = True
        self.bracketed_paste = False
        self.application_mode = False
        self.keypad_mode = False
        self._current_fg = 7
        self._current_bg = 0
        self._bold = False
        self._dim = False
        self._italic = False
        self._underline = False
        self._inverse = False
        self._blink = False
        self._reverse = False
        self._hidden = False

    def resize(self, width: int, height: int) -> None:
        """Resize the terminal buffer."""
        old_screen = self.screen
        old_height = len(old_screen)
        old_width = len(old_screen[0]) if old_height > 0 else width

        self.width = width
        self.height = height
        self.screen = self._create_empty_screen()

        # Copy old content
        for y in range(min(height, old_height)):
            for x in range(min(width, old_width)):
                self.screen[y][x] = old_screen[y][x]

        # Clamp cursor
        self.cursor.x = min(self.cursor.x, width - 1)
        self.cursor.y = min(self.cursor.y, height - 1)

    def _get_cell(self, x: int, y: int) -> Cell:
        """Get cell at position, creating if necessary."""
        while y >= len(self.screen):
            self.screen.append(self._create_empty_row())
        while x >= len(self.screen[y]):
            self.screen[y].append(Cell())
        return self.screen[y][x]

    def set_cell(self, x: int, y: int, char: str) -> None:
        """Write a character to the buffer."""
        if 0 <= y < self.height and 0 <= x < self.width:
            cell = self._get_cell(x, y)
            cell.char = char
            cell.fg = self._current_fg
            cell.bg = self._current_bg
            cell.bold = self._bold
            cell.dim = self._dim
            cell.italic = self._italic
            cell.underline = self._underline
            cell.inverse = self._inverse
            cell.blink = self._blink

    def write(self, text: str) -> None:
        """Write text to the terminal at cursor position."""
        for char in text:
            if char == "\n":
                self._linefeed()
            elif char == "\r":
                self.cursor.x = 0
            elif char == "\t":
                tab_stop = (self.cursor.x // 8 + 1) * 8
                self.cursor.x = min(tab_stop, self.width - 1)
            elif char == "\b":
                if self.cursor.x > 0:
                    self.cursor.x -= 1
            else:
                self.set_cell(self.cursor.x, self.cursor.y, char)
                self.cursor.x += 1
                if self.cursor.x >= self.width:
                    if self.auto_wrap:
                        self.cursor.x = 0
                        self._linefeed()
                    else:
                        self.cursor.x = self.width - 1

    def _linefeed(self) -> None:
        """Move cursor down one line with scrolling."""
        self.cursor.x = 0  # CR+LF moves to start of next line
        if self.cursor.y >= self.margins_bottom:
            self._scroll()
        else:
            self.cursor.y += 1

    def _scroll(self) -> None:
        """Scroll the screen up by one line."""
        # Save line to scrollback
        if self.scrollback_size > 0:
            self.scrollback.append(self.screen[self.margins_top].copy())
            if len(self.scrollback) > self.scrollback_size:
                self.scrollback.pop(0)

        # Shift lines
        for y in range(self.margins_top, self.margins_bottom):
            self.screen[y] = self.screen[y + 1]
        self.screen[self.margins_bottom] = self._create_empty_row()

    def _reverse_scroll(self) -> None:
        """Scroll the screen down by one line (reverse scroll)."""
        # Shift lines down
        for y in range(self.margins_bottom, self.margins_top, -1):
            self.screen[y] = self.screen[y - 1]
        self.screen[self.margins_top] = self._create_empty_row()

    def scroll_region(self, top: int, bottom: int) -> None:
        """Set the scrolling region."""
        if 0 <= top < bottom < self.height:
            self.margins_top = top
            self.margins_bottom = bottom
            self.cursor.y = self.margins_top

    def clear_screen(self, mode: int = 2) -> None:
        """Clear screen: 0=below, 1=above, 2=all, 3=entire with scrollback."""
        if mode == 0:
            # Clear from cursor to end
            for x in range(self.cursor.x, self.width):
                self.set_cell(x, self.cursor.y, " ")
            for y in range(self.cursor.y + 1, self.height):
                self.screen[y] = self._create_empty_row()
        elif mode == 1:
            # Clear from start to cursor
            for y in range(self.cursor.y):
                self.screen[y] = self._create_empty_row()
            for x in range(self.cursor.x + 1):
                self.set_cell(x, self.cursor.y, " ")
        elif mode == 2:
            # Clear entire screen
            self.screen = self._create_empty_screen()
        elif mode == 3:
            # Clear entire screen and scrollback
            self.screen = self._create_empty_screen()
            self.scrollback.clear()

    def erase_line(self, mode: int = 2) -> None:
        """Erase line: 0=right, 1=left, 2=entire."""
        y = self.cursor.y
        if mode == 0:
            for x in range(self.cursor.x, self.width):
                self.set_cell(x, y, " ")
        elif mode == 1:
            for x in range(self.cursor.x + 1):
                self.set_cell(x, y, " ")
        else:
            self.screen[y] = self._create_empty_row()

    def delete_lines(self, count: int = 1) -> None:
        """Delete lines at cursor position."""
        y = self.cursor.y
        for _ in range(count):
            if y <= self.margins_bottom:
                del self.screen[y]
                self.screen.insert(self.margins_bottom, self._create_empty_row())

    def insert_lines(self, count: int = 1) -> None:
        """Insert blank lines at cursor position."""
        y = self.cursor.y
        for _ in range(count):
            if y <= self.margins_bottom:
                del self.screen[y]
                self.screen.insert(self.margins_bottom, self._create_empty_row())

    def save_cursor(self) -> None:
        """Save cursor position and state."""
        self.saved_cursor = TerminalState(
            cursor_x=self.cursor.x,
            cursor_y=self.cursor.y,
            origin_mode=self.origin_mode,
            wrap=self.auto_wrap
        )

    def restore_cursor(self) -> None:
        """Restore saved cursor position and state."""
        if self.saved_cursor:
            self.cursor.x = self.saved_cursor.cursor_x
            self.cursor.y = self.saved_cursor.cursor_y
            self.origin_mode = self.saved_cursor.origin_mode
            self.auto_wrap = self.saved_cursor.wrap

    def reset(self) -> None:
        """Reset terminal to initial state."""
        self.screen = self._create_empty_screen()
        self.scrollback.clear()
        self.cursor = Cursor()
        self._setup_state()

    def get_text(self) -> str:
        """Get screen content as string."""
        lines = []
        for row in self.screen:
            lines.append("".join(cell.char for cell in row).rstrip())
        return "\n".join(lines)


class EscapeSequenceParser:
    """Parser for VT100/XTerm escape sequences."""

    # CSI (Control Sequence Introducer) patterns
    CSI_PATTERNS = {
        "cursor_up": re.compile(r"^\x1b\[(\d*)A"),           # CUU
        "cursor_down": re.compile(r"^\x1b\[(\d*)B"),         # CUD
        "cursor_forward": re.compile(r"^\x1b\[(\d*)C"),       # CUF
        "cursor_back": re.compile(r"^\x1b\[(\d*)D"),          # CUB
        "cursor_next_line": re.compile(r"^\x1b\[(\d*)E"),     # CNL
        "cursor_prev_line": re.compile(r"^\x1b\[(\d*)F"),     # CPL
        "cursor_column": re.compile(r"^\x1b\[(\d*)G"),        # CHA
        "cursor_position": re.compile(r"^\x1b\[(\d*);(\d*)H"),# CUP
        "erase_display": re.compile(r"^\x1b\[(\d*)J"),        # ED
        "erase_line": re.compile(r"^\x1b\[(\d*)K"),           # EL
        "scroll_up": re.compile(r"^\x1b\[(\d*)S"),             # SU
        "scroll_down": re.compile(r"^\x1b\[(\d*)T"),          # SD
        "delete_chars": re.compile(r"^\x1b\[(\d*)P"),         # DCH
        "insert_chars": re.compile(r"^\x1b\[(\d*)@"),         # ICH
        "delete_lines": re.compile(r"^\x1b\[(\d*)M"),         # DL
        "insert_lines": re.compile(r"^\x1b\[(\d*)L"),         # IL
        "set_tabs": re.compile(r"^\x1b\[(\d*)g"),             # TBC
        "device_attributes": re.compile(r"^\x1b\[(\d*)c"),   # DA
        "set_mode": re.compile(r"^\x1b\[(\d*)h"),             # SM
        "reset_mode": re.compile(r"^\x1b\[(\d*)l"),           # RM
        "set_cursor_style": re.compile(r"^\x1b\[(\d*) q"),    # DECSCUSR
        "scroll_region": re.compile(r"^\x1b\[(\d*);(\d*)r"),  # DECSTBM
        "save_cursor": re.compile(r"^\x1b7"),                 # SC
        "restore_cursor": re.compile(r"^\x1b8"),             # RC
        "screen_alignment": re.compile(r"^\x1b\[2J"),         # DECALN
    }

    # OSC (Operating System Command) patterns
    OSC_PATTERNS = {
        "set_title": re.compile(r"^\x1b\](.*?)\x07"),         # ST
        "set_title_bel": re.compile(r"^\x1b\](.*?)\x07"),
    }

    # SGR (Select Graphic Rendition) sequences
    SGR_PATTERNS = {
        "bold": re.compile(r"^\x1b\[1m"),
        "dim": re.compile(r"^\x1b\[2m"),
        "italic": re.compile(r"^\x1b\[3m"),
        "underline": re.compile(r"^\x1b\[4m"),
        "blink": re.compile(r"^\x1b\[5m"),
        "inverse": re.compile(r"^\x1b\[7m"),
        "hidden": re.compile(r"^\x1b\[8m"),
        "reset_bold": re.compile(r"^\x1b\[22m"),
        "reset_italic": re.compile(r"^\x1b\[23m"),
        "reset_underline": re.compile(r"^\x1b\[24m"),
        "reset_blink": re.compile(r"^\x1b\[25m"),
        "reset_inverse": re.compile(r"^\x1b\[27m"),
        "reset_hidden": re.compile(r"^\x1b\[28m"),
        "reset": re.compile(r"^\x1b\[0m"),
        "fg_color": re.compile(r"^\x1b\[3(\d)m"),           # 30-37
        "bg_color": re.compile(r"^\x1b\[4(\d)m"),           # 40-47
        "fg_bright": re.compile(r"^\x1b\[9(\d)m"),          # 90-97
        "bg_bright": re.compile(r"^\x1b\[10(\d)m"),         # 100-107
        "fg_256": re.compile(r"^\x1b\[38;5;(\d+)m"),
        "bg_256": re.compile(r"^\x1b\[48;5;(\d+)m"),
        "fg_rgb": re.compile(r"^\x1b\[38;2;(\d+);(\d+);(\d+)m"),
        "bg_rgb": re.compile(r"^\x1b\[48;2;(\d+);(\d+);(\d+)m"),
    }

    # DEC Private sequences (mode numbers >= 1)
    DEC_MODES = {
        1: "cursor_key_mode",      # DECCKM
        6: "origin_mode",          # DECOM
        7: "auto_wrap",            # DECAWM
        25: "cursor_visible",      # DECTCEM
        47: "alternate_buffer",    # alternate screen
        1047: "alternate_buffer", # alternate screen
        1048: "save_cursor",       # save/restore cursor
        1049: "alternate_buffer",  # alternate screen + save/restore cursor
    }

    def __init__(self, buffer: Buffer):
        self.buffer = buffer
        self.osc_buffer = ""
        self._mode_handlers: dict[int, Callable[[bool], None]] = {}

    def parse(self, data: str) -> str:
        """
        Parse escape sequences from input data.
        
        Processes sequences and writes characters to buffer with appropriate
        attributes as they are encountered (streaming style).
        """
        output = []
        i = 0
        
        while i < len(data):
            char = data[i]
            
            # Handle OSC sequences
            if char == "\x1b]" and i + 1 < len(data):
                j = i + 2
                while j < len(data) and data[j - 1] != "\x07" and not (data[j - 2:j] == "\x1b["):
                    j += 1
                if j <= len(data) and (data[j - 1] == "\x07" or data[j - 1] == "\x1b"):
                    osc = data[i + 2:j - 1]
                    self._handle_osc(osc)
                    i = j
                    if data[j - 1] == "\x1b":
                        i -= 1  # Back up for CSI
                    continue
            
            # Handle CSI sequences
            if char == "\x1b" and i + 1 < len(data) and data[i + 1] == "[":
                # Check for SGR first (most common)
                sgr_match = re.match(r"^\x1b\[((?:\d+;?)*)m", data[i:])
                if sgr_match:
                    params = sgr_match.group(1)
                    self._handle_sgr(params)
                    i += len(sgr_match.group(0))
                    continue
                
                # Check DEC private sequences
                dec_match = re.match(r"^\x1b\[(\?)([0-9;]+)([hl])", data[i:])
                if dec_match:
                    mode_nums = dec_match.group(2).split(";")
                    is_set = dec_match.group(3) == "h"
                    for num in mode_nums:
                        if num.isdigit():
                            self._handle_dec_mode(int(num), is_set)
                    i += len(dec_match.group(0))
                    continue
                
                # Check other CSI patterns
                matched = False
                for name, pattern in self.CSI_PATTERNS.items():
                    match = pattern.match(data[i:])
                    if match:
                        self._handle_csi(name, match.groups())
                        i += len(match.group(0))
                        matched = True
                        break
                
                if matched:
                    continue
                
                # Unknown CSI - skip the escape
                i += 1
                continue
            
            # Handle escape sequences without CSI
            if char == "\x1b":
                if i + 1 < len(data):
                    next_char = data[i + 1]
                    if next_char == "7":
                        self.buffer.save_cursor()
                        i += 2
                        continue
                    elif next_char == "8":
                        self.buffer.restore_cursor()
                        i += 2
                        continue
                    elif next_char == "c":
                        self.buffer.reset()
                        i += 2
                        continue
                i += 1
                continue
            
            # Regular printable character - write immediately to buffer
            if ord(char) >= 32 or char in "\n\r\t\b":
                self.buffer.write(char)
                output.append(char)
            
            i += 1
        
        return "".join(output)

    def _handle_csi(self, name: str, params: tuple) -> None:
        """Handle CSI sequences."""
        buf = self.buffer
        # Extract numeric parameters (empty strings become 1 or 0)
        p = [int(x) if x else (1 if name in ["cursor_up", "cursor_down", "cursor_forward",
                                              "cursor_back", "delete_chars", "insert_chars",
                                              "delete_lines", "insert_lines", "scroll_up",
                                              "scroll_down"] else 0) for x in params]

        if name == "cursor_up":
            buf.cursor.y = max(buf.margins_top, buf.cursor.y - p[0])
        elif name == "cursor_down":
            buf.cursor.y = min(buf.margins_bottom, buf.cursor.y + p[0])
        elif name == "cursor_forward":
            buf.cursor.x = min(buf.width - 1, buf.cursor.x + p[0])
        elif name == "cursor_back":
            buf.cursor.x = max(0, buf.cursor.x - p[0])
        elif name == "cursor_next_line":
            buf.cursor.y = min(buf.margins_bottom, buf.cursor.y + p[0])
            buf.cursor.x = 0
        elif name == "cursor_prev_line":
            buf.cursor.y = max(buf.margins_top, buf.cursor.y - p[0])
            buf.cursor.x = 0
        elif name == "cursor_column":
            buf.cursor.x = min(int(p[0]) - 1, buf.width - 1) if p[0] else 0
        elif name == "cursor_position":
            row = int(p[0]) - 1 if p[0] else 0
            col = int(p[1]) - 1 if len(p) > 1 and p[1] else 0
            buf.cursor.y = row
            buf.cursor.x = col
        elif name == "erase_display":
            buf.clear_screen(int(p[0]) if p[0] else 0)
        elif name == "erase_line":
            buf.erase_line(int(p[0]) if p[0] else 0)
        elif name == "scroll_up":
            for _ in range(p[0]):
                buf._scroll()
        elif name == "scroll_down":
            for _ in range(p[0]):
                buf._reverse_scroll()
        elif name == "delete_chars":
            for _ in range(p[0]):
                if buf.cursor.y < len(buf.screen) and buf.cursor.x < len(buf.screen[buf.cursor.y]):
                    del buf.screen[buf.cursor.y][buf.cursor.x]
                    buf.screen[buf.cursor.y].append(Cell())
        elif name == "insert_chars":
            for _ in range(p[0]):
                if buf.cursor.y < len(buf.screen) and buf.cursor.x < len(buf.screen[buf.cursor.y]):
                    buf.screen[buf.cursor.y].insert(buf.cursor.x, Cell())
                    if len(buf.screen[buf.cursor.y]) > buf.width:
                        buf.screen[buf.cursor.y].pop()
        elif name == "delete_lines":
            buf.delete_lines(p[0])
        elif name == "insert_lines":
            buf.insert_lines(p[0])
        elif name == "set_tabs":
            # Tabs handling - simplified
            pass
        elif name == "device_attributes":
            # Report terminal capabilities
            pass
        elif name == "scroll_region":
            top = int(p[0]) - 1 if p[0] else 0
            bottom = int(p[1]) if len(p) > 1 and p[1] else buf.height
            buf.scroll_region(top, bottom - 1)

    def _handle_sgr(self, params: str) -> None:
        """Handle SGR (Select Graphic Rendition) sequences."""
        if not params:
            # Reset
            self.buffer._current_fg = 7
            self.buffer._current_bg = 0
            self.buffer._bold = False
            self.buffer._dim = False
            self.buffer._italic = False
            self.buffer._underline = False
            self.buffer._inverse = False
            self.buffer._blink = False
            self.buffer._hidden = False
            return

        values = [int(x) for x in params.split(";")]
        i = 0
        while i < len(values):
            code = values[i]
            if code == 0:
                # Reset all
                self.buffer._current_fg = 7
                self.buffer._current_bg = 0
                self.buffer._bold = False
                self.buffer._dim = False
                self.buffer._italic = False
                self.buffer._underline = False
                self.buffer._inverse = False
                self.buffer._blink = False
                self.buffer._hidden = False
            elif code == 1:
                self.buffer._bold = True
            elif code == 2:
                self.buffer._dim = True
            elif code == 3:
                self.buffer._italic = True
            elif code == 4:
                self.buffer._underline = True
            elif code == 5:
                self.buffer._blink = True
            elif code == 7:
                self.buffer._inverse = True
            elif code == 8:
                self.buffer._hidden = True
            elif code == 22:
                self.buffer._bold = False
                self.buffer._dim = False
            elif code == 23:
                self.buffer._italic = False
            elif code == 24:
                self.buffer._underline = False
            elif code == 25:
                self.buffer._blink = False
            elif code == 27:
                self.buffer._inverse = False
            elif code == 28:
                self.buffer._hidden = False
            elif 30 <= code <= 37:
                self.buffer._current_fg = code - 30
            elif code == 39:
                self.buffer._current_fg = 7
            elif 40 <= code <= 47:
                self.buffer._current_bg = code - 40
            elif code == 49:
                self.buffer._current_bg = 0
            elif 90 <= code <= 97:
                self.buffer._current_fg = code - 90 + 8
            elif 97 <= code <= 100:
                self.buffer._current_bg = code - 100 + 8
            elif code == 38 and i + 2 < len(values):
                # Extended fg color
                if values[i + 1] == 5 and i + 2 < len(values):
                    self.buffer._current_fg = values[i + 2]
                    i += 2
                elif values[i + 1] == 2 and i + 4 < len(values):
                    # RGB fg
                    i += 4
                i += 1
            elif code == 48 and i + 2 < len(values):
                # Extended bg color
                if values[i + 1] == 5 and i + 2 < len(values):
                    self.buffer._current_bg = values[i + 2]
                    i += 2
                elif values[i + 1] == 2 and i + 4 < len(values):
                    # RGB bg
                    i += 4
                i += 1
            else:
                pass
            i += 1

    def _handle_osc(self, params: str) -> None:
        """Handle OSC (Operating System Command) sequences."""
        if ";" in params:
            cmd, value = params.split(";", 1)
            if cmd == "0" or cmd == "2":
                # Set window title
                self._title = value
            elif cmd == "1":
                # Set icon name
                pass
            elif cmd == "12":
                # Set cursor color
                pass

    def _handle_dec_mode(self, mode: int, set_mode: bool) -> None:
        """Handle DEC private mode sequences."""
        handlers = {
            1: lambda s: setattr(self.buffer, "_cursor_key_mode", s),
            6: lambda s: setattr(self.buffer, "origin_mode", s),
            7: lambda s: setattr(self.buffer, "auto_wrap", s),
            25: lambda s: setattr(self.buffer, "cursor_visible", s),
        }
        if mode in handlers:
            handlers[mode](set_mode)


class TerminalEmulator:
    """
    Main terminal emulator class.
    Handles input, output, and escape sequence processing.
    """

    def __init__(self, width: int = 80, height: int = 24, scrollback: int = 1000):
        self.buffer = Buffer(width, height, scrollback)
        self.parser = EscapeSequenceParser(self.buffer)
        self._title = "Terminal"
        self._alternate_buffer: Optional[list[list[Cell]]] = None
        self._on_output: Optional[Callable[[str], None]] = None
        self._running = False
        self._input_queue: asyncio.Queue[str] = asyncio.Queue()

    @property
    def title(self) -> str:
        """Get terminal title."""
        return self._title

    async def start(self) -> None:
        """Start the terminal emulator."""
        self._running = True

    async def stop(self) -> None:
        """Stop the terminal emulator."""
        self._running = False

    def write(self, data: str) -> str:
        """
        Write data to the terminal.
        Parses escape sequences and writes to buffer.
        Returns the plain text content.
        """
        # Parse escape sequences - the parser handles CSI/SGR sequences and writes
        # characters directly to the buffer with appropriate attributes
        return self.parser.parse(data)

    def process_input(self, data: str) -> str:
        """
        Process keyboard input and return escape sequences.
        """
        output = ""
        for char in data:
            if char == "\r":
                if self.buffer._application_mode:
                    output += "\r"
                else:
                    output += "\r\n"
            elif char == "\x1b":
                # Handle special keys
                pass
            else:
                output += char
        return output

    def resize(self, width: int, height: int) -> None:
        """Resize the terminal."""
        self.buffer.resize(width, height)

    def get_screen_text(self) -> str:
        """Get current screen content as plain text."""
        return self.buffer.get_text()

    def get_cell(self, x: int, y: int) -> Optional[Cell]:
        """Get cell at position."""
        if 0 <= y < self.buffer.height and 0 <= x < self.buffer.width:
            return self.buffer.screen[y][x]
        return None

    def get_cursor_position(self) -> tuple[int, int]:
        """Get current cursor position."""
        return (self.buffer.cursor.x, self.buffer.cursor.y)

    def clear(self) -> None:
        """Clear the terminal screen."""
        self.buffer.clear_screen(2)


class InputHandler:
    """Handles keyboard input mapping."""

    KEY_SEQUENCES = {
        # Arrow keys
        "UP": "\x1b[A",
        "DOWN": "\x1b[B",
        "RIGHT": "\x1b[C",
        "LEFT": "\x1b[D",
        # Function keys
        "F1": "\x1bOP",
        "F2": "\x1bOQ",
        "F3": "\x1bOR",
        "F4": "\x1bOS",
        "F5": "\x1b[15~",
        "F6": "\x1b[17~",
        "F7": "\x1b[18~",
        "F8": "\x1b[19~",
        "F9": "\x1b[20~",
        "F10": "\x1b[21~",
        "F11": "\x1b[23~",
        "F12": "\x1b[24~",
        # Control keys
        "ENTER": "\r",
        "TAB": "\t",
        "ESCAPE": "\x1b",
        "BACKSPACE": "\x7f",
        "DELETE": "\x1b[3~",
        "HOME": "\x1b[H",
        "END": "\x1b[F",
        "PAGE_UP": "\x1b[5~",
        "PAGE_DOWN": "\x1b[6~",
        # Application mode sequences (DECSET 1)
        "APP_UP": "\x1bOA",
        "APP_DOWN": "\x1bOB",
        "APP_RIGHT": "\x1bOC",
        "APP_LEFT": "\x1bOD",
    }

    @classmethod
    def get_sequence(cls, key: str, application_mode: bool = False) -> str:
        """Get escape sequence for a key."""
        if application_mode and key in ["UP", "DOWN", "RIGHT", "LEFT"]:
            return cls.KEY_SEQUENCES.get(f"APP_{key}", cls.KEY_SEQUENCES.get(key, ""))
        return cls.KEY_SEQUENCES.get(key, key)

    @staticmethod
    def parse_modifiers(event: dict) -> dict:
        """Parse modifier keys from input event."""
        return {
            "shift": event.get("shift", False),
            "ctrl": event.get("ctrl", False),
            "alt": event.get("alt", False),
            "meta": event.get("meta", False),
        }

    @staticmethod
    def apply_ctrl(key: str, modifiers: dict) -> str:
        """Apply control modifier to key."""
        if modifiers.get("ctrl") and len(key) == 1:
            ctrl = chr(ord(key.upper()) - ord("A") + 1)
            if 1 <= ord(ctrl) <= 26:
                return ctrl
        return key


# ANSI color names
ANSI_COLORS = {
    0: "black",
    1: "red",
    2: "green",
    3: "yellow",
    4: "blue",
    5: "magenta",
    6: "cyan",
    7: "white",
    8: "bright_black",
    9: "bright_red",
    10: "bright_green",
    11: "bright_yellow",
    12: "bright_blue",
    13: "bright_magenta",
    14: "bright_cyan",
    15: "bright_white",
}
