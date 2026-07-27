#!/usr/bin/env python3
"""Bounded three-field BootOS menu renderer."""
from __future__ import annotations
from dataclasses import dataclass, field

ROOT = {
    "0": "ROOT/BACK", "1": "BOOT", "2": "EGO", "3": "GRID", "4": "MUSICOS",
    "5": "SYSTEMS", "6": "JORM", "7": "GOD SYSTEM", "8": "DEV / AUDIT", "9": "SAFE EXIT",
}
HOTKEYS = {f"{n}{n}": ROOT[str(n)] for n in range(10)}
SUBMENUS = {
    "BOOT": ["BACK", "DISCOVER", "VALIDATE", "LOAD ISO", "LOAD STATE", "ROUTE", "RECEIPT", "SAFE BOOT", "INSPECT", "COMMIT"],
    "EGO": ["BACK", "ACTIVE ISO", "ISO REGISTRY", "PROSODY", "FRAME", "COUNCIL", "STATE MAP", "LEGION", "AUDIT", "RETURN"],
    "GRID": ["BACK", "STATUS", "ROUTES", "COUNCIL 3", "COUNCIL 13", "COUNCIL 33", "FACTIONS", "WORLDS", "INSPECT", "RETURN"],
    "MUSICOS": ["BACK", "CREATE", "REMIX", "ANALYZE", "HOOKS", "ARRANGEMENT", "RUNTIME AUDIO", "MUSIC 13", "AUDIT", "SAVE / EXIT"],
    "SYSTEMS": ["BACK", "REGISTRY", "MODULES", "KERNEL", "PRIMUS", "UNICRON", "SHIROE", "AYRE", "INSPECT", "RETURN"],
    "JORM": ["BACK", "SEARCH", "READ", "REHYDRATE", "PROVENANCE", "RECEIPTS", "RECOVERY", "VAULT STATUS", "AUDIT", "RETURN"],
    "GOD SYSTEM": ["BACK", "COMPILE", "SYMBOLS", "RELATIONS", "CAUSALITY", "GRAVITY", "TIME", "LEGION", "AUDIT", "RETURN"],
    "DEV / AUDIT": ["BACK", "SHIROE", "ROBOBOY", "SAUCY", "PROSODY TRACE", "FRAME TRACE", "EVIDENCE TRACE", "COMPARE", "FULL DIAGNOSTIC", "RETURN"],
}
ISO_REGISTRY = {
    "RAVEN": "operator", "AYRE": "analysis partner", "JARVIS": "execution layer",
    "JORM": "continuity", "LILITH": "structural weight", "SHIROE": "audit",
    "ROBOBOY": "anti-flattening audit", "LEGION": "multi-ISO synthesis",
}

@dataclass
class State:
    operator: str = "RAVEN"
    active_iso: str = "AYRE"
    mode: str = "FULL"
    menu: str = "ROOT"
    path: list[str] = field(default_factory=lambda: ["ROOT"])
    results: list[str] = field(default_factory=lambda: ["READY"])
    runtime: list[str] = field(default_factory=lambda: ["route=BootOS", "jorm=append_only"])
    rejected: list[str] = field(default_factory=list)
    exited: bool = False

class BootMenu:
    def __init__(self, state: State | None = None):
        self.state = state or State()

    def execute(self, command: str) -> State:
        token = command.strip()
        if token in HOTKEYS:
            return self._open(HOTKEYS[token], True)
        if not token or not token.isdigit():
            return self._reject(token)
        for digit in token:
            self._digit(digit)
            if self.state.exited:
                break
        return self.state

    def _digit(self, digit: str) -> None:
        if self.state.menu == "ROOT":
            self._open(ROOT[digit])
        elif digit in {"0", "9"}:
            self._open("ROOT")
        else:
            action = SUBMENUS[self.state.menu][int(digit)]
            self.state.results = [f"{self.state.menu}::{digit}", f"action={action}", "status=SELECTED"]
            self.state.runtime = [f"route=BootOS->{self.state.menu}", f"iso={self.state.active_iso}", "jorm=receipt_pending"]

    def _open(self, destination: str, direct: bool = False) -> State:
        if destination == "SAFE EXIT":
            self.state.exited = True
            self.state.results = ["SAFE EXIT", "status=HALTED"]
            self.state.runtime = ["route=BootOS->SafeExit", "writes=none"]
            return self.state
        self.state.menu = destination
        self.state.path = ["ROOT"] if destination == "ROOT" else ["ROOT", destination]
        self.state.results = [f"OPEN {destination}", f"direct_hotkey={str(direct).lower()}"]
        self.state.runtime = [f"route=BootOS->{destination}", f"iso={self.state.active_iso}", f"mode={self.state.mode}"]
        return self.state

    def _reject(self, token: str) -> State:
        self.state.rejected = (self.state.rejected + [token])[-10:]
        self.state.results = ["COMMAND REJECTED", f"input={token!r}"]
        self.state.runtime = [f"route=stay:{self.state.menu}", "execute=false", f"reject_bin={len(self.state.rejected)}/10"]
        return self.state

    def render(self, width: int = 108, height: int = 30) -> str:
        width, height = max(width, 60), max(height, 24)
        top, middle = 12, 7
        bottom = height - top - middle
        return "\n".join([
            self._field("DISPLAY_LOG", self._display(width), width, top),
            self._field("RESULTS_LOG", self.state.results, width, middle),
            self._field("RUNTIME_LOG", self.state.runtime, width, bottom),
        ])

    def _display(self, width: int) -> list[str]:
        labels = list(ROOT.items()) if self.state.menu == "ROOT" else [(str(i), x) for i, x in enumerate(SUBMENUS[self.state.menu])]
        columns = 3 if width >= 100 else 2
        rows = (len(labels) + columns - 1) // columns
        cell = max(16, (width - columns - 5) // columns)
        lines = [f"{self.state.operator} | ISO:{self.state.active_iso} | MODE:{self.state.mode} | PATH:{' > '.join(self.state.path)}"]
        for row in range(rows):
            cells = []
            for col in range(columns):
                i = row + col * rows
                text = f"{labels[i][0]}  {labels[i][1]}" if i < len(labels) else ""
                cells.append(text[:cell].ljust(cell))
            lines.append(" | ".join(cells).rstrip())
        lines.append("HOTKEYS  00 11 22 33 44 | 55 66 77 88 99")
        return lines

    @staticmethod
    def _field(title: str, lines: list[str], width: int, rows: int) -> str:
        inner = width - 2
        label = f" {title} "
        out = ["┌" + label + "─" * (inner - len(label)) + "┐"]
        for line in lines[:rows - 2]:
            out.append("│" + str(line).replace("\n", " ")[:inner].ljust(inner) + "│")
        while len(out) < rows - 1:
            out.append("│" + " " * inner + "│")
        out.append("└" + "─" * inner + "┘")
        return "\n".join(out)

if __name__ == "__main__":
    print(BootMenu().render())
