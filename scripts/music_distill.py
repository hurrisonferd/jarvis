#!/usr/bin/env python3
"""music_distill.py — MusicOS Cognitive Distillation.

MusicOS is a cognitive music engine: music described through physics, color theory, and
mathematics — not genre tags. This script distills the creative framework from all prompts
into reusable primitives for:
  - AI-native music OS (jarvis_listen enriched responses)
  - Suno prompt generation
  - Famistudio / tracker notation
  - WAVE analysis → feature correlation

The framework lives here. Preserve the poetry; extract the physics.

Distillation layers:
  Primitives  — raw parameter atoms (BPM, key, color, physics tags)
  Grammar     — how MusicOS describes timbre, rhythm, space
  Suno Prompt — Raven's language → Suno-compatible prompt string
  Tracker     — Famistudio/N NSF structural mapping (bars, patterns, instruments)
  Wave        — audio feature → MusicOS concept correlation table
"""
from __future__ import annotations
import json
import re
from pathlib import Path
from typing import Optional

# ─── MusicOS Color Theory ────────────────────────────────────────────────────
# R = Power / propulsion / endurance   (warm, dark, dense, gravity, heavy)
# G = Groove / rhythm / elasticity      (neon, elastic, bouncy, subdivision, pocket)
# B = Range / space / clarity           (bright, steel-blue, wide, atmospheric)

COLOR_MAP: dict[str, str] = {
    "neon": "G", "green-forward": "G", "green-dominant": "G", "neon race": "G",
    "steel-blue": "B", "steel blue": "B",
    "warm": "R", "dark": "R", "dark synth": "R", "dark synth-rock": "R",
    "red propulsion": "R", "subtle red": "R",
    "gravity": "R", "heavy": "R", "dense": "R", "mass": "R",
    "elastic": "G", "bouncy": "G", "groove": "G", "bounce": "G",
    "bright": "B", "wide": "B", "atmospheric": "B", "space": "B",
    "kinetic": "R", "propulsion": "R", "forward": "R", "launch": "R",
    "subdivision": "G", "grid": "G", "pocket": "G",
    "deep": "R", "low-end": "R", "dry": "G",
    "chiptune": "G", "square-wave": "G", "pulse": "G",
    "compressed": "R", "tight": "B",
}

RGB_LABELS = {"R": "Power", "G": "Groove", "B": "Range"}

# ─── Physics / Spatial Metaphors ──────────────────────────────────────────────
PHYSICS_TAGS: list[str] = [
    "rail authority", "gravity groove", "elastic bounce", "snap-back",
    "forward momentum", "re-acceleration", "rubber", "friction",
    "subdivision precision", "grid", "pocket", "kinetic",
    "propulsion", "tension push", "breath", "space",
    "inevitability", "unwavering", "unbreakable",
    "bounce", "elastic movement", "circular bass", "gravity groove",
    "rubber-on-fire", "roll", "surge", "weight", "mass",
    "fixed grid", "bar subdivision", "phrase cycle", "loop",
    "phase", "layering", "accumulation",
    "declarative motif", "resolution", "authority",
    "multiplicity", "cohesion", "resolve",
]

# ─── Sound Design Primitives (from 80s/90s) ─────────────────────────────────
SOUND_PRIMITIVES: dict[str, list[str]] = {
    "oscillator": ["square-wave", "pulse-based", "FM synthesis", "analog synth"],
    "drum_kit": ["dry kit", "dry snare snap", "tight kick", "articulate hi-hat", "physical drums"],
    "compression": ["compressed center-weighted", "tight mix", "controlled dynamics"],
    "tonality": ["single tonal center", "restrained harmony", "minimal harmonic movement",
                 "unresolved tension", "clean chord stabs"],
    "space": ["atmospheric synth pads", "low in the mix", "reverb", "delay", "wide"],
    "texture": ["chiptune edge", "PS1-era", "16-bit", "neon accents"],
}

# ─── Series Definitions ───────────────────────────────────────────────────────
SERIES: dict[str, dict] = {
    "Unbreakable Momentum": {
        "abbr": "UM",
        "bpm_range": (78, 88),
        "keys": ["E minor", "B minor", "E major", "? minor"],
        "genre_tags": ["dark synth-rock", "synth-rock", "funk-rock"],
        "color_bias": "R",
        "constraints": ["no vocals", "no drops", "no chaos"],
        "physics": ["rail authority", "gravity groove", "inevitability", "elastic bounce"],
        "description": "Physics of persistence. Minimal harmony, maximal groove. The track moves because it chooses to.",
    },
    "Syncopation Engine": {
        "abbr": "SE",
        "bpm_range": (98, 106),
        "keys": ["B minor", "F# minor", "C# minor", "F minor"],
        "genre_tags": ["neon race", "dry kit synthpop", "synthpop rock", "synthpop propulsion"],
        "color_bias": "G",
        "physics": ["subdivision precision", "snap-back", "elastic bass", "groove density"],
        "description": "Groove as mechanical engineering. Dry kit, elastic bass, subdivision as propulsion.",
    },
    "Neon Race": {
        "abbr": "NR",
        "bpm_range": (70, 75),
        "keys": ["F minor", "C# minor"],
        "genre_tags": ["steel blue synthpop", "synthpop"],
        "color_bias": "B",
        "physics": ["gravity groove", "fixed grid", "rail authority", "mechanical propulsion"],
        "description": "Steel blue gravity groove. Dense mechanical propulsion with disciplined digital precision.",
    },
}

# ─── Suno Prompt Grammar ──────────────────────────────────────────────────────
# Raven's language → Suno-compatible prompt tokens
SUNO_GRAMMAR: dict[str, list[str]] = {
    "mood": {
        "driving": "driving", "fast-twitch": "energetic", "steady": "steady groove",
        "heavy": "heavy", "kinetic": "kinetic", "bouncy": "bouncy",
    },
    "synth": {
        "neon": "neon synthpop", "chiptune": "chiptune", "analog synth": "analog synthwave",
        "square-wave": "square wave", "dark synth": "dark synthwave",
        "dry kit": "dry electronic drums",
    },
    "bass": {
        "elastic bass": "elastic bass", "circular bass": "circular bass line",
        "warm bass": "warm bass", "reactive bass": "reactive bass",
    },
    "structure": {
        "no vocals": "instrumental", "no drops": "", "no chaos": "",
        "repetitive motif": "repetitive", "8-bar loop": "looping",
        "strip-down rebuild": "minimal bridge", "declarative motif": "resolving hook",
    },
}


# ─── Tracker / Famistudio Mapping ───────────────────────────────────────────
# MusicOS structural concepts → NSF/Famistudio pattern concepts
TRACKER_MAP: dict[str, str] = {
    "4/4 locked": "4/4", "steady kick": "kick on 1 and 3", "snare on 2 and 4": "snare",
    "16th-note hats": "16th hi-hat pattern", "hi-hat subdivision": "hi-hat subdivision",
    "8-bar loop": "8-row pattern", "bar subdivision": "pattern step",
    "phrase cycle": "sequence length", "snap-back": "pitch bend", "elastic": "portamento",
    "dry snare": "short decay", "kick rail": "bass drum", "snare snap": "noise channel",
    "chiptune": "2A03/N163", "square-wave": "pulse channel", "NES": "NSF format",
}


def color_from_text(text: str) -> tuple[str, list[str], list[str], list[str]]:
    t = text.lower()
    r, g, b = [], [], []
    for phrase, channel in COLOR_MAP.items():
        if phrase in t:
            if channel == "R": r.append(phrase)
            elif channel == "G": g.append(phrase)
            else: b.append(phrase)
    dominant = "R" if len(r) >= len(g) and len(r) >= len(b) else \
               "G" if len(g) >= len(b) else "B" if b else "R"
    return dominant, r, g, b


def physics_from_text(text: str) -> list[str]:
    t = text.lower()
    return [tag for tag in PHYSICS_TAGS if tag in t]


def series_from_text(text: str) -> Optional[str]:
    t = text.lower()
    for key in SERIES:
        if key.lower() in t:
            return key
    return None


def constraints_from_text(text: str) -> dict[str, bool]:
    t = text.lower()
    return {
        "no_vocals": "no vocals" in t,
        "no_drops": "no drops" in t,
        "no_chaos": "no chaos" in t,
        "instrumental_only": "instrumental-only" in t or "instrumental only" in t,
        "loop_based": "8-bar" in t or "repeating" in t or "loop" in t,
        "strip_rebuild": "strip-down" in t or "rebuild" in t,
        "declarative_ending": "clean declarative" in t,
    }


def bpm_from_text(text: str) -> Optional[float]:
    m = re.search(r"(\d+)\s*BPM", text)
    return float(m.group(1)) if m else None


def key_from_text(text: str) -> Optional[str]:
    m = re.search(r"in\s+([A-G]#?\s+[Mm]inor|[A-G]#?\s+[Mm]ajor)", text)
    return m.group(1) if m else None


def genre_tags(text: str) -> list[str]:
    tags = []
    known = ["dark synth-rock", "synth-rock", "synthpop", "synthpop rock",
             "synthpop propulsion", "funk-rock", "dry kit", "neon race",
             "chiptune", "PS1-era", "steel blue synthpop", "dark synth",
             "glitch-tinged rock", "synth-rock / glitch-tinged rock",
             "synth-rock / funk-rock"]
    for tag in known:
        if tag in text.lower():
            tags.append(tag)
    return tags


def dominant_rgb(dominant: str, r_tags: list, g_tags: list, b_tags: list) -> str:
    """Encode RGB as hex for vision-layer visualization."""
    return dominant  # R/G/B single letter — hex version computed on output


def spectral_correlates(features: dict) -> dict:
    """Map audio features → MusicOS physics concepts."""
    bpm = features.get("bpm", 0)
    centroid = features.get("brightness_hz", 2000)
    dyn_range = features.get("dynamic_range_db", 10)
    onset = features.get("onset_density", 0)

    correlates = []
    if bpm >= 140: correlates.append("blitz/sprint physics")
    elif bpm >= 120: correlates.append("driving/propulsion")
    elif bpm >= 90: correlates.append("pocket/groove")
    else: correlates.append("weight/mass")

    if centroid >= 3000: correlates.append("airborne highs (B-range)")
    elif centroid >= 2000: correlates.append("articulate clarity")
    else: correlates.append("warm low-end (R-power)")

    if dyn_range >= 14: correlates.append("wide dynamic swings")
    elif dyn_range >= 8: correlates.append("controlled dynamics")
    else: correlates.append("compressed density")

    if onset >= 8: correlates.append("dense rhythmic surface")
    elif onset >= 5: correlates.append("subdivision layering")
    else: correlates.append("clean rhythmic space")

    return {"concepts": correlates, "dominant_feel": correlates[0] if correlates else "?"}


def suno_prompt(track: dict, prompt_text: str) -> str:
    """Convert MusicOS track into a Suno-compatible prompt string."""
    parts = []

    # Genre
    genre_tags_list = track.get("genre_tags", [])
    if genre_tags_list:
        parts.append(", ".join(genre_tags_list[:2]))

    # BPM + key
    bpm = track.get("bpm", "?")
    key = track.get("key", "?")
    if bpm != "?" and key != "?":
        parts.append(f"{int(bpm)} BPM {key}")

    # RGB / color
    rgb = track.get("rgb", "R")
    if rgb == "R":
        parts.append("dark warm synth-rock, heavy bass")
    elif rgb == "G":
        parts.append("neon synthpop, elastic groove, dry drums")
    else:
        parts.append("bright steel-blue synthpop, atmospheric space")

    # Physics
    physics = track.get("physics", [])
    if physics:
        parts.append(", ".join(physics[:3]))

    # Constraints
    constraints = track.get("constraints", {})
    if constraints.get("no_vocals"):
        parts.append("instrumental only")
    if constraints.get("no_drops"):
        parts.append("no drops")
    if constraints.get("no_chaos"):
        parts.append("no chaos")

    # The "does" line from prompt — this is the soul
    prose = track.get("prose", "")
    if prose and "does" in prose.lower():
        # Extract the "This track does X through Y" sentence
        sentences = prose.split(".")
        for s in sentences:
            if "does" in s.lower() and ("track does" in s.lower() or "this track does" in s.lower()):
                parts.append(s.strip().rstrip("., "))
                break

    return " | ".join(parts)


def famistudio_nsf(track: dict, prompt_text: str) -> dict:
    """Structural mapping: MusicOS → Famistudio NSF concepts."""
    bpm = track.get("bpm", 100)
    constraints = track.get("constraints", {})
    physics = track.get("physics", [])

    # NSF/Famistudio parameters
    nsf = {
        "time_signature": "4/4",
        "tempo_hz": round(bpm * 65536 / 60),  # Famistudio uses int tempo
        "pattern_length_bars": 8 if constraints.get("loop_based") else 1,
        "instruments": [],
        "channels_used": [],
        "structural_notes": [],
    }

    # Channel mapping from physics
    if any(p in physics for p in ["chiptune", "square-wave", "PS1-era"]):
        nsf["channels_used"].extend(["pulse1", "pulse2", "triangle", "noise"])
        nsf["instruments"].append({"type": "2A03", "oscillator": "square/pulse", "note_limit": "N163"})
    else:
        nsf["channels_used"].extend(["pulse1", "triangle", "noise", " DMC"])

    # Pattern structure from constraints
    if constraints.get("strip_rebuild"):
        nsf["structure"] = "drums+bass(8bars) → full → rebuild"
    elif constraints.get("loop_based"):
        nsf["structure"] = f"8-bar loop, {len(physics)} phrase layers"
    else:
        nsf["structure"] = "continuous groove"

    # Declarative ending
    if constraints.get("declarative_ending"):
        nsf["ending"] = "clean declarative 2-bar motif"

    return nsf


def distill_track(track_name: str, features: dict, prompt_text: str | None) -> dict:
    """Full distillation for one track."""
    prompt_text = prompt_text or ""

    rgb, r_tags, g_tags, b_tags = color_from_text(prompt_text)
    physics = physics_from_text(prompt_text)
    series = series_from_text(prompt_text)
    cons = constraints_from_text(prompt_text)
    bpm_t = bpm_from_text(prompt_text) or features.get("bpm", 0)
    key_t = key_from_text(prompt_text) or features.get("key", "?")
    genres = genre_tags(prompt_text)

    spectral = spectral_correlates(features)

    # Suno prompt from full prompt text
    suno = suno_prompt({
        "title": track_name.replace(".mp3", "").strip(),
        "bpm": bpm_t, "key": key_t,
        "rgb": rgb, "genre_tags": genres,
        "physics": physics, "constraints": cons,
        "prose": prompt_text[:300],
    }, prompt_text)
    nsf = famistudio_nsf({
        "bpm": bpm_t, "constraints": cons, "physics": physics,
    }, prompt_text)

    return {
        "title": track_name.replace(".mp3", "").strip(),
        "series": series,
        "series_abbr": SERIES[series]["abbr"] if series else None,
        "bpm": bpm_t,
        "key": key_t,
        "rgb": rgb,
        "rgb_tags": {"R_power": r_tags, "G_groove": g_tags, "B_range": b_tags},
        "rgb_interpretation": f"{RGB_LABELS.get(rgb,'?')}: {'+'.join(r_tags[:2]) if r_tags else g_tags[:2] if g_tags else b_tags[:2]}",
        "physics": physics,
        "genre_tags": genres,
        "constraints": cons,
        "suno_prompt": suno,
        "famistudio_nsf": nsf,
        "audio_correlates": spectral,
        "prompt_excerpt": prompt_text.strip()[:500] if prompt_text else None,
        "audio": {k: v for k, v in features.items() if k != "spectrogram"},
    }


def distill_all(nlp_path: Path, output_path: Path) -> dict:
    """Distill the full NLP catalog into working formats."""
    nlp = json.loads(nlp_path.read_text())
    tracks = nlp.get("tracks", {})
    catalog = nlp.get("catalog", {})

    result = {}
    series_catalog = {name: [] for name in SERIES}
    rgb_catalog = {"R": [], "G": [], "B": []}
    physics_catalog: dict[str, int] = {}
    issues: list[dict] = []

    for name, data in tracks.items():
        # data = NLP output; features are at the top level, prompt is separate
        audio_features = {k: v for k, v in data.items()
                         if k in ("bpm", "key", "mood", "duration_sec", "energy_rms",
                                  "brightness_hz", "onset_density", "dynamic_range_db")}
        prompt_text = data.get("prompt", "") or ""

        distilled = distill_track(name, audio_features, prompt_text)
        result[name] = distilled

        # Flag audio-only tracks
        if not prompt_text.strip():
            issues.append({"track": data.get("title", name), "issue": "audio_only", "note": "no prompt — audio analysis only"})
        elif not distilled["physics"]:
            issues.append({"track": data.get("title", name), "issue": "no_physics", "note": "no physics extracted from prompt"})

        # Index
        if distilled["series"]:
            series_catalog[distilled["series"]].append(distilled["title"])
        rgb_catalog[distilled["rgb"]].append(distilled["title"])
        for p in distilled["physics"]:
            physics_catalog[p] = physics_catalog.get(p, 0) + 1

    for series in series_catalog:
        series_catalog[series] = sorted(set(series_catalog[series]))

    # Proto-OS layer: extract framework atoms from all prompts
    framework_atoms = _extract_framework_atoms(tracks)

    output = {
        "note": "MusicOS Cognitive Distillation — primitives, Suno grammar, Famistudio NSF, Wave correlates. "
                "Source: GPT-era MusicOS proto-OS (CNS/rail/weight theory).",
        "catalog": catalog,
        "issues": issues,
        "series_catalog": series_catalog,
        "rgb_catalog": {k: sorted(set(v)) for k, v in rgb_catalog.items()},
        "physics_frequency": dict(sorted(physics_catalog.items(), key=lambda x: -x[1])),
        "framework": {
            name: {
                "abbr": info["abbr"],
                "bpm_range": info["bpm_range"],
                "keys": info["keys"],
                "rgb_bias": info["color_bias"],
                "description": info["description"],
                "physics_core": info["physics"],
            }
            for name, info in SERIES.items()
        },
        "atoms": framework_atoms,
        "tracks": result,
    }
    output_path.write_text(json.dumps(output, indent=2) + "\n")
    return output


def _extract_framework_atoms(tracks: dict) -> dict:
    """Extract the reusable atoms from the full prompt corpus.

    Raven's MusicOS corpus encodes: rail/weight theory, CNS-safe constraints,
    dual-layer prompt structure (max metric + art), triad metrics, style lanes.
    This function distills those atoms for use in future prompt construction.
    """
    # Gather all constraint patterns
    constraint_counts: dict[str, int] = {}
    physics_counts: dict[str, int] = {}
    color_counts: dict[str, int] = {}
    bpm_vals: list[float] = []

    for name, data in tracks.items():
        prompt = data.get("prompt", "") or ""
        if not prompt:
            continue
        if data.get("bpm"):
            bpm_vals.append(float(data["bpm"]))

        # Constraints
        for k, v in data.get("constraints", {}).items():
            if v:
                constraint_counts[k] = constraint_counts.get(k, 0) + 1

        # Physics
        for p in data.get("physics", []):
            physics_counts[p] = physics_counts.get(p, 0) + 1

        # Colors
        for tag in data.get("rgb_tags", {}).get("R_power", []):
            color_counts[tag] = color_counts.get(tag, 0) + 1
        for tag in data.get("rgb_tags", {}).get("G_groove", []):
            color_counts[tag] = color_counts.get(tag, 0) + 1
        for tag in data.get("rgb_tags", {}).get("B_range", []):
            color_counts[tag] = color_counts.get(tag, 0) + 1

    # Rail/Weight theory atoms
    rail_atoms = {
        "description": "Rail = predictable structural repetition. Weight = body-locked groove mass.",
        "constraints": {
            "rail_minimum": "Rail must be present in all tracks — identity anchor",
            "contrast_gradual": "Dynamic contrast must be gradual — CNS-safe",
            "no_sudden_spikes": "No sudden dynamic spikes — autism-safe default",
            "density_phases_in": "Density layering must phase in — not slam",
        },
        "failure_modes": {
            "rail_drops": "anxiety risk",
            "contrast_drops": "boredom risk",
            "repetition_drops": "identity instability risk",
        },
    }

    # Dual-layer prompt structure
    dual_layer = {
        "description": "Max Metric (structural) + Art Prompt (theme/color). Baked together.",
        "max_metric_layer": "Groove density, rail authority, harmonic gravity, spatial density, subdivision behavior, stage presence weight",
        "art_layer": "Emotional tone, visual metaphor, color weighting, environmental space, symbolic gravity",
        "rule": "Max Metric controls the skeleton. Art Prompt controls the nervous system tone. They must not contradict.",
    }

    # CNS-safe constraints (from corpus)
    cns_constraints = {
        "no_vocals": constraint_counts.get("no_vocals", 0),
        "no_drops": constraint_counts.get("no_drops", 0),
        "no_chaos": constraint_counts.get("no_chaos", 0),
        "instrumental_only": constraint_counts.get("instrumental_only", 0),
    }

    return {
        "rail_theory": rail_atoms,
        "dual_layer_prompt": dual_layer,
        "cns_safe_constraints": cns_constraints,
        "top_physics": dict(sorted(physics_counts.items(), key=lambda x: -x[1])[:15]),
        "top_colors": dict(sorted(color_counts.items(), key=lambda x: -x[1])[:12]),
        "bpm_range_observed": (min(bpm_vals), max(bpm_vals)) if bpm_vals else (0, 0),
        "bpm_mean_observed": round(sum(bpm_vals) / len(bpm_vals), 1) if bpm_vals else 0,
        "note": "Extracted from corpus. These atoms encode the MusicOS proto-OS — "
                "not a finished system, but the living creative grammar that produced the tracks.",
    }


def run() -> int:
    import argparse
    p = argparse.ArgumentParser(description="MusicOS Cognitive Distillation")
    p.add_argument("--nlp", type=Path, default=Path("JarvisSide/Media/AUDIO-NLP.json"),
                   help="AUDIO-NLP.json from music_nlp.py")
    p.add_argument("--output", type=Path, default=Path("JarvisSide/Media/MUSICOS-DISTILLED.json"),
                   help="Output path")
    args = p.parse_args()

    if not args.nlp.exists():
        print(f"ERROR: {args.nlp} not found. Run music_nlp.py first.")
        return 1

    result = distill_all(args.nlp, args.output)
    cat = result["catalog"]
    atoms = result["atoms"]

    print(f"\n{'='*60}")
    print(f"  MusicOS Distilled — {len(result['tracks'])} tracks")
    print(f"  Series: {', '.join(f'{k}({len(v)})' for k,v in result['series_catalog'].items() if v)}")
    print(f"  RGB: R={len(result['rgb_catalog']['R'])} G={len(result['rgb_catalog']['G'])} B={len(result['rgb_catalog']['B'])}")
    print(f"{'='*60}")

    if result["issues"]:
        print(f"\n⚠ Issues:")
        for issue in result["issues"]:
            print(f"  [{issue['issue']}] {issue['track']}: {issue['note']}")

    print(f"\n  Framework atoms extracted from corpus:")
    print(f"    BPM range: {atoms['bpm_range_observed'][0]:.0f}–{atoms['bpm_range_observed'][1]:.0f} (mean {atoms['bpm_mean_observed']})")
    print(f"    Top physics: {', '.join(list(atoms['top_physics'].keys())[:8])}")
    print(f"    CNS constraints: no_vocals={atoms['cns_safe_constraints']['no_vocals']}, "
          f"no_drops={atoms['cns_safe_constraints']['no_drops']}, "
          f"no_chaos={atoms['cns_safe_constraints']['no_chaos']}")

    print(f"\n  → {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
