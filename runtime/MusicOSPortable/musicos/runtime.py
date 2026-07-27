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
    "preserve the hook and rhythmic identity",
    "keep the pocket continuous",
    "avoid copying lyrics or melodies",
]


class MusicOSRuntime:
    def __init__(self, root: Path | None = None):
        self.root = (root or Path(__file__).resolve().parent.parent).resolve()
        self.config_path = self.root / "config" / "default.json"
        self.config = json.loads(self.config_path.read_text(encoding="utf-8"))
        self.store = StateStore(self.root)
        self.state = self.store.load()
        self.source_index_path = self.root / "data" / "source-index.json"

    def status(self) -> dict:
        source_status = None
        if self.source_index_path.exists():
            source_status = json.loads(self.source_index_path.read_text(encoding="utf-8"))
        return {
            "runtime": self.state.to_dict(),
            "laws": self.config["gold_laws"],
            "modules": self.config["modules"],
            "source_index": {
                "present": source_status is not None,
                "source_count": source_status.get("source_count", 0) if source_status else 0,
                "status_counts": source_status.get("status_counts", {}) if source_status else {},
            },
        }

    def import_vault(self, vault: Path) -> dict:
        result = index_vault(vault.resolve(), self.source_index_path)
        self.state.source_count = result["source_count"]
        self.state.last_import_at = result["sources"][-1]["indexed_at"] if result["sources"] else None
        self.store.event(self.state, "VAULT_IMPORTED", {
            "vault": str(vault.resolve()),
            "source_count": result["source_count"],
            "status_counts": result["status_counts"],
        })
        return result

    @staticmethod
    def _physics(text: str) -> list[str]:
        lower = text.lower()
        found = [term for term in PHYSICS_TERMS if term in lower]
        inferred = []
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
                inferred.append(term)
        return (found + inferred)[:8] or ["forward momentum", "gravity groove"]

    @staticmethod
    def _sanitize(text: str) -> str:
        text = re.sub(r"\s+", " ", text).strip()
        return text.rstrip(". ")

    def compile(self, intent: MusicIntent) -> CompiledTrack:
        bpm = intent.bpm or self.config["defaults"]["bpm"]
        key = intent.key or self.config["defaults"]["key"]
        physics = self._physics(intent.text)
        rgb = {channel: max(0, min(100, int(value))) for channel, value in intent.rgb.items()}
        constraints = list(dict.fromkeys(DEFAULT_CONSTRAINTS + intent.constraints))

        channel_language = (
            f"R{rgb.get('R', 0)} power and gravity, "
            f"G{rgb.get('G', 0)} groove and elasticity, "
            f"B{rgb.get('B', 0)} range and spatial clarity"
        )
        instrumental = "instrumental" if intent.instrumental else "vocal-capable"
        mechanism = ", ".join(physics)
        prompt = (
            f"{self._sanitize(intent.text)}. {instrumental}, hook-first and groove-first, "
            f"with {channel_language}. Maintain {mechanism}; tight rhythmic continuity, "
            f"clear motif identity, controlled contrast, and repeatable forward motion. "
            f"State profile: {intent.state}. {bpm} BPM, {key}."
        )
        summary = f"This track creates {physics[0]} through {physics[1] if len(physics) > 1 else 'shared-clock repetition'}, {bpm} BPM"
        provenance = [
            "MusicOS Gold Laws",
            "MusicOS Atlas control stack",
            "JORM/Vault runtime source index" if self.source_index_path.exists() else "runtime defaults pending Vault import",
        ]
        track = CompiledTrack(
            prompt=prompt,
            summary=summary,
            bpm=bpm,
            key=key,
            rgb=rgb,
            physics=physics,
            constraints=constraints,
            provenance=provenance,
        )
        self.state.last_compilation = track.to_dict()
        self.store.event(self.state, "TRACK_COMPILED", {
            "bpm": bpm,
            "key": key,
            "physics": physics,
            "state": intent.state,
        })
        return track

    def snapshot(self, name: str) -> Path:
        return self.store.snapshot(self.state, name)
