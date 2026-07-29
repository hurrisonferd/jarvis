from __future__ import annotations

import json
import re
from pathlib import Path

from .models import CompiledTrack, MusicIntent
from .source_index import index_vault
from .state import StateStore

PHYSICS_TERMS = [
    "rail authority", "forward momentum", "elasticity", "snap-back",
    "gravity groove", "subdivision precision", "boundary enforcement",
    "kinetic propulsion", "rotational energy", "micro-variance",
    "causal recursion", "shared clock", "spatiotemporal expansion",
]

DEFAULT_CONSTRAINTS = [
    "copyright-safe vibe translation",
    "original lyrics and melodic material",
    "continuous pocket",
    "clear hook and rhythmic identity",
]

DEFAULT_STYLES = [
    "neon-race synthpop-rock",
    "chiptune-inflected game-score drive",
]

NAME_TRANSLATIONS = {
    "stewart copeland": "articulate hi-hat intelligence",
    "copeland": "articulate hi-hat intelligence",
    "john bonham": "heavyweight kick-snare authority",
    "bonham": "heavyweight kick-snare authority",
    "danny carey": "polyrhythmic subdivision control",
    "carey": "polyrhythmic subdivision control",
    "neil peart": "precise progressive-kit articulation",
    "peart": "precise progressive-kit articulation",
    "phil collins": "dramatic tom-led propulsion",
    "collins": "dramatic tom-led propulsion",
    "suno": "generation-ready",
}


class MusicOSRuntime:
    def __init__(self, root: Path | None = None):
        self.root = (root or Path(__file__).resolve().parent.parent).resolve()
        self.config_path = self.root / "config" / "default.json"
        self.config = json.loads(self.config_path.read_text(encoding="utf-8"))
        self.store = StateStore(self.root)
        self.state = self.store.load()
        self.source_index_path = self.root / "data" / "source-index.json"
        self.rehydration_path = self.root / "data" / "rehydration-receipt.json"

    def status(self) -> dict:
        source_status = (
            json.loads(self.source_index_path.read_text(encoding="utf-8"))
            if self.source_index_path.exists()
            else None
        )
        rehydration = (
            json.loads(self.rehydration_path.read_text(encoding="utf-8"))
            if self.rehydration_path.exists()
            else None
        )
        return {
            "runtime": self.state.to_dict(),
            "laws": self.config["gold_laws"],
            "modules": self.config["modules"],
            "source_index": {
                "present": source_status is not None,
                "source_count": source_status.get("source_count", 0) if source_status else 0,
                "status_counts": source_status.get("status_counts", {}) if source_status else {},
            },
            "rehydration": {
                "present": rehydration is not None,
                "coverage": rehydration.get("coverage") if rehydration else "UNKNOWN",
                "receipt_sha256": rehydration.get("receipt_sha256") if rehydration else None,
                "missing_required": rehydration.get("missing_required", []) if rehydration else [],
            },
        }

    def import_vault(self, vault: Path) -> dict:
        result = index_vault(vault.resolve(), self.source_index_path)
        self.state.source_count = result["source_count"]
        self.state.last_import_at = result["sources"][-1]["indexed_at"] if result["sources"] else None
        self.store.event(
            self.state,
            "VAULT_IMPORTED",
            {
                "vault": str(vault.resolve()),
                "source_count": result["source_count"],
                "status_counts": result["status_counts"],
            },
        )
        return result

    @staticmethod
    def _physics(text: str) -> list[str]:
        lower = text.lower()
        found = [term for term in PHYSICS_TERMS if term in lower]
        mappings = {
            "bounce": "elasticity",
            "rubber": "snap-back",
            "race": "forward momentum",
            "dry drum": "subdivision precision",
            "syncopat": "gravity groove",
            "field": "shared clock",
            "weather": "spatiotemporal expansion",
            "spiral": "rotational energy",
            "protect": "boundary enforcement",
            "recursion": "causal recursion",
        }
        for token, term in mappings.items():
            if token in lower and term not in found:
                found.append(term)
        return found[:8] or ["forward momentum", "gravity groove"]

    @staticmethod
    def _translate(text: str) -> str:
        clean = re.sub(r"\s+", " ", text).strip()
        clean = re.sub(r"\bno vocals?\b", "instrumental focus", clean, flags=re.I)
        clean = re.sub(r"\bavoid\b", "favor", clean, flags=re.I)
        for name, translation in NAME_TRANSLATIONS.items():
            clean = re.sub(rf"\b{re.escape(name)}\b", translation, clean, flags=re.I)
        return clean.rstrip(". ")

    @staticmethod
    def _styles(styles: list[str]) -> list[str]:
        translated = [MusicOSRuntime._translate(style) for style in styles if style.strip()]
        unique = list(dict.fromkeys(translated))[:4]
        for fallback in DEFAULT_STYLES:
            if len(unique) >= 2:
                break
            if fallback not in unique:
                unique.append(fallback)
        return unique

    def compile(self, intent: MusicIntent) -> CompiledTrack:
        bpm = max(40, min(240, intent.bpm or self.config["defaults"]["bpm"]))
        key = self._translate(intent.key or self.config["defaults"]["key"])
        source_text = self._translate(intent.text)
        physics = self._physics(source_text)
        styles = self._styles(intent.styles)
        rgb = {
            channel: max(0, min(100, int(intent.rgb.get(channel, 0))))
            for channel in ("R", "G", "B")
        }
        constraints = list(dict.fromkeys(
            DEFAULT_CONSTRAINTS + [self._translate(item) for item in intent.constraints]
        ))
        voice = "instrumental focus" if intent.instrumental else "voice-ready arrangement"
        mechanisms = ", ".join(physics)
        style_line = ", ".join(styles)
        summary = (
            f"This track conveys {physics[0]} through "
            f"{physics[1] if len(physics) > 1 else 'shared-clock repetition'} "
            f"and controlled contrast"
        )
        prompt = (
            f"{source_text}; {style_line}; {voice}; {key}; hook-first and groove-first with "
            f"a clear repeating motif, R{rgb['R']} power and gravity, G{rgb['G']} groove "
            f"and elasticity, B{rgb['B']} range and spatial clarity, {mechanisms}, tight "
            f"rhythmic continuity, dry articulate drums, intelligent hi-hat motion, elastic "
            f"bass snap-back, warm digital synthesis, and concise rhythm-guitar stabs. "
            f"{summary}; {bpm} BPM."
        )
        track = CompiledTrack(
            prompt=prompt,
            summary=summary,
            bpm=bpm,
            key=key,
            rgb=rgb,
            physics=physics,
            styles=styles,
            constraints=constraints,
            provenance=[
                "MusicOS Gold Laws",
                "MusicOS Atlas control stack",
                "JORM/Vault runtime source index"
                if self.source_index_path.exists()
                else "runtime defaults pending Vault import",
            ],
        )
        self.state.last_compilation = track.to_dict()
        self.store.event(
            self.state,
            "TRACK_COMPILED",
            {"bpm": bpm, "key": key, "physics": physics, "state": intent.state},
        )
        return track

    def snapshot(self, name: str) -> Path:
        return self.store.snapshot(self.state, name)
