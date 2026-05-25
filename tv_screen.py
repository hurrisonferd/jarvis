"""
JARVIS TV Screen — Image Display
Watches a folder for new images and displays them fullscreen.
Wire to any image gen output folder.

Install: pip install pillow
Run:     python tv_screen.py

Drop images into the watch folder and they appear on screen.
Press ESC or Q to quit. Space to manually advance.
"""

import os
import sys
import time
import glob
from pathlib import Path
from PIL import Image, ImageTk, ImageDraw, ImageFont
import tkinter as tk

# ─── CONFIG ──────────────────────────────────────────────────────────────────

WATCH_FOLDER  = Path(__file__).parent / "grid_images"
POLL_SECONDS  = 2
BG_COLOR      = "#020408"
TEXT_COLOR    = "#f5a623"
SUPPORTED_EXT = {".png", ".jpg", ".jpeg", ".webp", ".gif"}

# ─── SETUP ───────────────────────────────────────────────────────────────────

WATCH_FOLDER.mkdir(exist_ok=True)


class TVScreen:
    def __init__(self, root):
        self.root       = root
        self.root.title("JARVIS Grid — Image Display")
        self.root.configure(bg=BG_COLOR)
        self.root.attributes("-fullscreen", True)

        self.canvas = tk.Canvas(
            root, bg=BG_COLOR,
            highlightthickness=0,
            cursor="none"
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.photo    = None
        self.seen     = set()
        self.queue    = []
        self.current  = None

        self.root.bind("<Escape>", lambda e: self.quit())
        self.root.bind("q",        lambda e: self.quit())
        self.root.bind("Q",        lambda e: self.quit())
        self.root.bind("<space>",  lambda e: self.next_image())
        self.root.bind("f",        lambda e: self.toggle_fullscreen())

        self.show_standby()
        self.poll()

    def show_standby(self):
        w = self.root.winfo_screenwidth()
        h = self.root.winfo_screenheight()
        self.canvas.delete("all")
        self.canvas.create_text(
            w // 2, h // 2 - 20,
            text="JARVIS GRID",
            fill=TEXT_COLOR,
            font=("Courier", 32, "bold")
        )
        self.canvas.create_text(
            w // 2, h // 2 + 20,
            text=f"Watching: {WATCH_FOLDER}",
            fill="#1e3a52",
            font=("Courier", 12)
        )
        self.canvas.create_text(
            w // 2, h // 2 + 50,
            text="Drop images here to display — ESC to quit",
            fill="#1e3a52",
            font=("Courier", 10)
        )

    def display_image(self, path):
        try:
            img = Image.open(path)
            sw = self.root.winfo_screenwidth()
            sh = self.root.winfo_screenheight()
            img.thumbnail((sw, sh), Image.LANCZOS)
            self.photo = ImageTk.PhotoImage(img)
            self.canvas.delete("all")
            self.canvas.create_image(sw // 2, sh // 2, anchor=tk.CENTER, image=self.photo)
            name = Path(path).stem[:40]
            self.canvas.create_text(
                20, sh - 20,
                text=name,
                fill="#1e3a52",
                font=("Courier", 9),
                anchor=tk.SW
            )
            self.current = path
        except Exception as e:
            print(f"Error displaying {path}: {e}")

    def next_image(self):
        if self.queue:
            path = self.queue.pop(0)
            self.display_image(path)

    def poll(self):
        files = []
        for ext in SUPPORTED_EXT:
            files.extend(glob.glob(str(WATCH_FOLDER / f"*{ext}")))
            files.extend(glob.glob(str(WATCH_FOLDER / f"*{ext.upper()}")))

        new_files = sorted(
            [f for f in files if f not in self.seen],
            key=lambda f: os.path.getmtime(f)
        )

        for f in new_files:
            self.seen.add(f)
            self.queue.append(f)

        if self.queue and self.current is None:
            self.next_image()
        elif self.queue:
            self.next_image()

        self.root.after(POLL_SECONDS * 1000, self.poll)

    def toggle_fullscreen(self):
        state = self.root.attributes("-fullscreen")
        self.root.attributes("-fullscreen", not state)

    def quit(self):
        self.root.destroy()


def main():
    print(f"JARVIS TV Screen")
    print(f"Watching: {WATCH_FOLDER}")
    print(f"Drop images into that folder to display them.")
    print(f"Press ESC or Q to quit. Space to advance manually.")
    print()

    root = tk.Tk()
    app  = TVScreen(root)

    try:
        root.mainloop()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
