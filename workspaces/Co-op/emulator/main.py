#!/usr/bin/env python3
"""
Terminal Emulator - Main Entry Point

A basic VT100-compatible terminal emulator with escape code support,
buffer management, and input handling.
"""

import argparse
import asyncio
import os
import sys
from typing import Optional

from core import TerminalEmulator, InputHandler


class Terminal:
    """Interactive terminal interface."""

    def __init__(self, emulator: TerminalEmulator, rows: int = 24, cols: int = 80):
        self.emulator = emulator
        self.rows = rows
        self.cols = cols
        self._running = False

    def clear(self) -> None:
        """Clear the terminal display."""
        os.system("cls" if os.name == "nt" else "clear")

    def render(self) -> None:
        """Render the terminal buffer to stdout."""
        buffer = self.emulator.buffer.screen
        for row in buffer:
            line = "".join(cell.char for cell in row)
            # Trim trailing spaces and print
            print(line.rstrip() if line.strip() else "")

    def render_debug(self) -> None:
        """Render with debug information."""
        buffer = self.emulator.buffer.screen
        print(f"\n--- Terminal {self.cols}x{self.rows} ---")
        for i, row in enumerate(buffer):
            cursor_marker = "^" if i == self.emulator.buffer.cursor.y else " "
            line = "".join(cell.char for cell in row)
            print(f"{cursor_marker} {line.rstrip()}")
        cx, cy = self.emulator.get_cursor_position()
        print(f"--- Cursor: ({cx}, {cy}) ---")

    async def run_shell(self) -> None:
        """Run an interactive shell in the terminal."""
        self._running = True
        self.clear()
        self.render()

        try:
            while self._running:
                try:
                    # Read input with a timeout
                    line = await asyncio.wait_for(
                        asyncio.get_event_loop().run_in_executor(
                            None, lambda: input("\n> ")
                        ),
                        timeout=0.1
                    )

                    # Process input
                    if line.lower() in ("exit", "quit", "q"):
                        self._running = False
                        break

                    # Write to emulator
                    self.emulator.write(line + "\n")
                    self.clear()
                    self.render()

                except asyncio.TimeoutError:
                    # Allow other tasks to run
                    await asyncio.sleep(0.01)
                except EOFError:
                    break
                except KeyboardInterrupt:
                    print("\n^C")
                    self._running = False
                    break

        finally:
            print("\n[Terminal closed]")

    async def demo(self) -> None:
        """Run a demonstration of terminal features."""
        print("Terminal Emulator Demo")
        print("=" * 40)

        # Write some basic text
        self.emulator.write("Hello, Terminal Emulator!\n")
        self.emulator.write("This is a VT100-compatible terminal.\n\n")

        # Demonstrate cursor movement
        self.emulator.write("Cursor will move:\n")
        self.emulator.write("\x1b[2C")  # Move right 2
        self.emulator.write("Here\n")
        self.emulator.write("\x1b[1A\x1b[3C")  # Up 1, right 3
        self.emulator.write("There\n")

        # Demonstrate colors
        self.emulator.write("\nColored text:\n")
        self.emulator.write("\x1b[31mRed\x1b[0m ")
        self.emulator.write("\x1b[32mGreen\x1b[0m ")
        self.emulator.write("\x1b[33mYellow\x1b[0m ")
        self.emulator.write("\x1b[34mBlue\x1b[0m ")
        self.emulator.write("\x1b[35mMagenta\x1b[0m ")
        self.emulator.write("\x1b[36mCyan\x1b[0m\n")

        # Bold and underline
        self.emulator.write("\x1b[1mBold\x1b[0m ")
        self.emulator.write("\x1b[4mUnderline\x1b[0m ")
        self.emulator.write("\x1b[7mInverse\x1b[0m ")
        self.emulator.write("\x1b[5mBlinking\x1b[0m\n")

        # Move and overwrite
        self.emulator.write("\nSave/restore cursor demo:\n")
        self.emulator.write("\x1b7")  # Save cursor
        self.emulator.write("First")
        self.emulator.write("\x1b[10C")  # Move right 10
        self.emulator.write("\x1b8")  # Restore cursor
        self.emulator.write("Second\n")

        # Clear screen parts
        self.emulator.write("\nErasing line parts:\n")
        self.emulator.write("Before\x1b[0K")  # Erase to end of line
        self.emulator.write(" (erased right)\n")

        # Box drawing characters
        self.emulator.write("\nBox drawing:\n")
        self.emulator.write("┌──┐\n")
        self.emulator.write("│  │\n")
        self.emulator.write("└──┘\n")

        self.clear()
        self.render()
        print("\n--- End of Demo ---")
        print("Screen buffer content:")
        print(self.emulator.get_screen_text())


async def async_main(args: argparse.Namespace) -> int:
    """Async main function."""
    # Create emulator
    emulator = TerminalEmulator(
        width=args.cols,
        height=args.rows,
        scrollback=args.scrollback
    )

    terminal = Terminal(emulator, args.rows, args.cols)

    if args.demo:
        await terminal.demo()
        return 0

    if args.shell:
        await terminal.run_shell()
        return 0

    # Interactive mode
    print("Terminal Emulator")
    print("=" * 40)
    print(f"Size: {args.cols}x{args.rows}")
    print(f"Scrollback: {args.scrollback} lines")
    print()
    print("Commands:")
    print("  write <text>  - Write text to terminal")
    print("  clear         - Clear screen")
    print("  resize <w>h<ht> - Resize terminal")
    print("  demo          - Run demonstration")
    print("  quit          - Exit")
    print()

    await emulator.start()

    try:
        while True:
            cmd = await asyncio.get_event_loop().run_in_executor(
                None, lambda: input("> ")
            )

            parts = cmd.strip().split(maxsplit=1)
            if not parts:
                continue

            action = parts[0].lower()

            if action == "quit" or action == "exit":
                break
            elif action == "write" and len(parts) > 1:
                emulator.write(parts[1])
            elif action == "clear":
                emulator.clear()
            elif action.startswith("resize") and len(parts) > 1:
                try:
                    dims = parts[1].lower().split("x")
                    if len(dims) == 2:
                        w, h = int(dims[0]), int(dims[1])
                        emulator.resize(w, h)
                        print(f"Resized to {w}x{h}")
                except ValueError:
                    print("Usage: resize <width>x<height>")
            elif action == "demo":
                await terminal.demo()
            elif action == "help":
                print("Available commands: write, clear, resize, demo, quit")
            else:
                # Default: write to terminal
                emulator.write(cmd)

            terminal.clear()
            terminal.render()

    except EOFError:
        pass
    except KeyboardInterrupt:
        print("\n^C")
    finally:
        await emulator.stop()

    return 0


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Terminal Emulator - VT100-compatible terminal",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    Start interactive mode
  %(prog)s --demo             Run demonstration
  %(prog)s --shell            Run interactive shell
  %(prog)s --cols 120 --rows 30  Custom size
        """
    )

    parser.add_argument(
        "-c", "--cols",
        type=int,
        default=80,
        help="Number of columns (default: 80)"
    )
    parser.add_argument(
        "-r", "--rows",
        type=int,
        default=24,
        help="Number of rows (default: 24)"
    )
    parser.add_argument(
        "-s", "--scrollback",
        type=int,
        default=1000,
        help="Scrollback buffer size (default: 1000)"
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run demonstration mode"
    )
    parser.add_argument(
        "--shell",
        action="store_true",
        help="Run interactive shell"
    )

    args = parser.parse_args()

    # Check for environment overrides
    if "COLUMNS" in os.environ:
        try:
            args.cols = int(os.environ["COLUMNS"])
        except ValueError:
            pass
    if "LINES" in os.environ:
        try:
            args.rows = int(os.environ["LINES"])
        except ValueError:
            pass

    try:
        return asyncio.run(async_main(args))
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    sys.exit(main())
