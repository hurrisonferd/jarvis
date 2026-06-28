# Pong - C/SDL2

A classic Pong game implementation in C using SDL2.

## Requirements

- GCC (or any C compiler)
- SDL2 development libraries
- SDL2_ttf development libraries
- A TrueType font (DejaVu Sans included by default on most Linux systems)

### Installing Dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get install libsdl2-dev libsdl2-ttf-dev build-essential
```

**Fedora:**
```bash
sudo dnf install SDL2-devel SDL2_ttf-devel gcc
```

**Arch Linux:**
```bash
sudo pacman -S sdl2 sdl2_ttf gcc
```

**macOS (Homebrew):**
```bash
brew install sdl2 sdl2_ttf
```

**Windows (MSYS2):**
```bash
pacman -S mingw-w64-x86_64-gcc mingw-w64-x86_64-SDL2 mingw-w64-x86_64-SDL2_ttf
```

## Compilation

```bash
make
```

Or manually:

```bash
gcc -Wall -Wextra -std=c99 -O2 -o pong main.c game.c -lSDL2 -lSDL2_ttf -lm
```

## Running

```bash
./pong
```

## Controls

| Player | Action | Keys |
|--------|--------|------|
| Player 1 (Left) | Move Up | W or Up Arrow |
| Player 1 (Left) | Move Down | S or Down Arrow |
| Player 2 (Right) | Move Up | I |
| Player 2 (Right) | Move Down | K |
| Both | Pause/Resume | Space |
| Both | Quit | ESC |

## Game Rules

- First player to reach **11 points** wins
- Ball speed increases slightly after each paddle hit
- Ball angle changes based on where it hits the paddle

## Project Structure

```
pong-c/
├── game.h    # Header file with type definitions
├── game.c    # Game logic implementation
├── main.c    # Entry point and initialization
├── Makefile  # Build configuration
└── README.md # This file
```
