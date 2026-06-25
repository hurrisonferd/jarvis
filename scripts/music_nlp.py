#!/usr/bin/env python3
"""music_nlp.py — MusicOS NLP enrichment layer.

Reads MusicOS/songs/prompts/ alongside audio features and generates:
  - Structured creative framework tags (RGB theory, physics metaphors, series)
  - Prose description (the "soul" JARVIS/Ayre reason from)
  - Semantic summary of what the track IS, not just its technical features

The creative language is Raven's — preserve it. Do not summarize away the poetry.
"""
from __future__ import annotations
import json
import re
from pathlib import Path

SERIES = {
    "unbreakable momentum": "Unbreakable Momentum",
    "syncopation engine": "Syncopation Engine",
    "neon race": "Neon Race",
}
SERIES_ABBREV = {
    "Unbreakable Momentum": "UM",
    "Syncopation Engine": "SE",
    "Neon Race": "NR",
}

# Physics / space metaphors for physics_signature()
PHYSICS_TAGS = [
    "rail authority", "gravity groove", "elastic bounce", "snap-back",
    "forward momentum", "re-acceleration", "rubber", "friction",
    "subdivision precision", "grid", "pocket", "kinetic",
    "propulsion", "tension push", "breath", "space",
    "inevitability", "unwavering", "unbreakable",
    "bounce", "elastic movement", "circular bass", "gravity groove",
]


def _color_signature(text: str) -> dict:
    """RGB color theory: R=Power/propulsion, G=Groove/rhythm, B=Range/space."""
    t = text.lower()
    r_tags, g_tags, b_tags = [], [], []
    color_map = {
        "steel-blue compression": "B", "steel blue compression": "B",
        "steel-blue mix": "B", "steel blue mix": "B",
        "neon accents": "G", "neon race": "G",
        "green-forward": "G", "green-dominant": "G",
        "red propulsion": "R", "subtle red": "R",
        "warm": "R", "dark": "R", "dark synth": "R",
        "bright": "B", "wide": "B", "atmospheric": "B", "space": "B",
        "gravity": "R", "heavy": "R", "dense": "R", "mass": "R",
        "elastic": "G", "bouncy": "G", "groove": "G",
        "subdivision": "G", "grid": "G", "pocket": "G",
        "kinetic": "R", "propulsion": "R", "forward": "R", "launch": "R",
        "deep": "R", "low-end": "R", "bounce": "G",
    }
    for phrase, channel in color_map.items():
        if phrase in t:
            if channel == "R":
                r_tags.append(phrase)
            elif channel == "G":
                g_tags.append(phrase)
            else:
                b_tags.append(phrase)
    dominant = "R" if len(r_tags) > len(g_tags) and len(r_tags) > len(b_tags) else \
               "B" if len(b_tags) > len(g_tags) else "G" if g_tags else "R"
    return {"rgb": dominant, "r_tags": r_tags, "g_tags": g_tags, "b_tags": b_tags}


def _physics_signature(text: str) -> list[str]:
    t = text.lower()
    found = []
    for tag in PHYSICS_TAGS:
        if tag in t:
            found.append(tag)
    return found


def _series_from_prompt(prompt_text: str) -> str | None:
    t = prompt_text.lower()
    for key, name in SERIES.items():
        if key in t:
            return name
    return None


def _track_number(prompt_text: str) -> int | None:
    m = re.search(r"track\s+(\d+)\s+of", prompt_text.lower())
    return int(m.group(1)) if m else None


def _core_constraints(prompt_text: str) -> dict:
    t = prompt_text.lower()
    return {
        "no_vocals": "no vocals" in t,
        "no_drops": "no drops" in t,
        "no_chaos": "no chaos" in t,
        "instrumental_only": "instrumental-only" in t or "instrumental only" in t,
    }


def _drive_signature(features: dict, color: dict) -> str:
    """What the track IS, encoded in the physics of its movement."""
    bpm = features.get("bpm", 0)
    energy = features.get("energy_rms", 0)
    centroid = features.get("brightness_hz", 2000)
    dyn_range = features.get("dynamic_range_db", 10)

    if bpm >= 160:
        pace = "blitz" if energy >= 0.08 else "sprint"
    elif bpm >= 130:
        pace = "drive" if energy >= 0.08 else "cruise"
    elif bpm >= 100:
        pace = "groove" if energy >= 0.06 else "sway"
    elif bpm >= 80:
        pace = "pocket" if dyn_range >= 12 else "drift"
    else:
        pace = "weight"

    if centroid >= 3000:
        tone = "bright"
    elif centroid >= 2000:
        tone = "clear"
    elif centroid >= 1500:
        tone = "warm"
    else:
        tone = "dark"

    rgb = color.get("rgb", "R")
    channel = {"R": "Power", "G": "Rhythm", "B": "Range"}.get(rgb, "Power")
    return f"{pace}/{tone}/{channel}"


def _spectral_reading(features: dict) -> str:
    """Turn raw features into a readable sonic description."""
    bpm = features.get("bpm", 0)
    centroid = features.get("brightness_hz", 2000)
    onset = features.get("onset_density", 0)
    dyn = features.get("dynamic_range_db", 10)
    descs = []
    if bpm >= 140:
        descs.append("fast-twitch syncopation")
    elif bpm >= 110:
        descs.append("driving syncopation")
    elif bpm >= 90:
        descs.append("steady pocket groove")
    else:
        descs.append("heavy low-end weight")
    if centroid >= 3500:
        descs.append("airborne highs")
    elif centroid >= 2500:
        descs.append("articulate clarity")
    elif centroid >= 1800:
        descs.append("midrange warmth")
    else:
        descs.append("deep bass presence")
    if dyn >= 15:
        descs.append("wide dynamic swings")
    elif dyn >= 10:
        descs.append("controlled dynamics")
    else:
        descs.append("compressed density")
    if onset >= 8:
        descs.append("dense rhythmic surface")
    elif onset >= 5:
        descs.append("layered subdivision")
    else:
        descs.append("clean rhythmic space")
    return "; ".join(descs)


def _prose_description(prompt_text: str, features: dict) -> str:
    """Extract Raven's own prose from the prompt. Preserve it verbatim where it exists."""
    if not prompt_text.strip():
        bpm = features.get("bpm", 0)
        key = features.get("key", "?")
        mood = features.get("mood", "")
        return f"{bpm} BPM {key}, {mood}. Instrumental."

    sentences = prompt_text.strip().split(".")
    does_line = ""
    for s in sentences:
        sl = s.lower().strip()
        if "does" in sl and ("track does" in sl or "this track does" in sl):
            does_line = s.strip()
            break

    constraints = []
    for s in sentences:
        sl = s.lower().strip()
        if sl.startswith("no vocals"):
            constraints.append("No vocals")
        elif sl.startswith("no drops"):
            constraints.append("No drops")
        elif sl.startswith("no chaos"):
            constraints.append("No chaos")

    lines = []
    if does_line:
        lines.append(does_line.rstrip("., ") + ".")
    else:
        bpm = features.get("bpm", 0)
        key = features.get("key", "?")
        mood = features.get("mood", "")
        lines.append(f"{bpm} BPM {key}, {mood}.")
    if constraints:
        lines.append(" ".join(constraints) + ".")
    return " ".join(lines)


def enrich_track(track_name: str, features: dict, prompt_text: str | None) -> dict:
    """Full NLP enrichment for a single track."""
    prompt_text = prompt_text or ""
    has_prompt = bool(prompt_text.strip())

    color = _color_signature(prompt_text)
    physics = _physics_signature(prompt_text)
    series = _series_from_prompt(prompt_text)
    track_num = _track_number(prompt_text)
    constraints = _core_constraints(prompt_text)
    drive = _drive_signature(features, color)
    spectral = _spectral_reading(features)

    # Prose: honest about what we know
    if has_prompt:
        prose = _prose_description(prompt_text, features)
        source = "prompt"
        confidence = "high" if len(physics) >= 3 else "medium"
    else:
        bpm = features.get("bpm", 0)
        key = features.get("key", "?")
        mood = features.get("mood", "")
        prose = f"{int(bpm)} BPM {key}, {mood}. Instrumental. [no prompt — audio analysis only]"
        source = "audio_features_only"
        confidence = "low"

    title = track_name.replace(".mp3", "").replace("'", "").strip()

    # Readable summary for companion streams
    physics_str = ", ".join(physics[:5]) if physics else "none extracted"
    rgb_str = color["rgb"]
    series_str = f"{series} #{track_num}" if series else "no series"
    constraints_str = ", ".join(k for k, v in constraints.items() if v) if any(constraints.values()) else "no constraints"

    summary = (
        f"{title}. {drive.replace('/', ' ')}. RGB:{rgb_str}. "
        f"{series_str}. Physics: {physics_str}. "
        f"{'Constraints: ' + constraints_str + '. ' if constraints_str != 'no constraints' else ''}"
        f"{prose[:120]}"
    )

    return {
        "title": title,
        "has_prompt": has_prompt,
        "prompt": prompt_text,  # Full original prompt — never strip
        "series": series,
        "series_abbrev": SERIES_ABBREV.get(series, series) if series else None,
        "track_number": track_num,
        "rgb": color["rgb"],
        "rgb_tags": {
            "R_power": color["r_tags"],
            "G_groove": color["g_tags"],
            "B_range": color["b_tags"],
        },
        "physics": physics,
        "drive_signature": drive,
        "constraints": constraints,
        "spectral_reading": spectral,
        "prose": prose,
        "source": source,
        "confidence": confidence,
        "summary": summary,
        **{k: v for k, v in features.items() if k != "spectrogram"},
    }


def load_prompts(prompts_dir: Path) -> dict[str, str]:
    """Load prompts. Key = title-case name (matches audio filenames)."""
    prompts = {}
    if not prompts_dir.exists():
        return prompts
    for p in prompts_dir.glob("*"):
        if p.is_file() and not p.name.startswith("."):
            name = p.stem.replace("'", "").strip()
            prompts[name] = p.read_text().strip()
    return prompts


# Name normalization for fuzzy matching
def _clean(s: str) -> str:
    """Lowercase + strip punctuation. Whitespace preserved for word overlap."""
    return re.sub(r"[^a-z0-9\s]", "", s.lower()).strip()


def _compact(s: str) -> str:
    """Compact: lowercase + no punct + no whitespace. For exact stem comparison."""
    return re.sub(r"[^a-z0-9]", "", s.lower())


def _word_set(s: str) -> frozenset:
    return frozenset(_clean(s).split())


def match_prompt(track_name: str, prompts: dict[str, str]) -> str | None:
    """Match audio filename → prompt file. Tries exact compact, then fuzzy word overlap."""
    base = track_name.replace(".mp3", "").replace("'", "").strip()
    base_compact = _compact(base)
    base_words = _word_set(base)

    # 1. Exact compact match (all punctuation/whitespace stripped)
    for name in prompts:
        if _compact(name) == base_compact:
            return prompts[name]

    # 2. Parenthesized variant: "ELASTIC UNDER FIRE(B-Side)" ↔ "Elastic Under Fire"
    base_no_paren = _compact(re.sub(r"\([^)]*\)", "", base))
    for name in prompts:
        if _compact(name) == base_no_paren:
            return prompts[name]

    # 3. Word overlap (min 2 shared words, score > 0.5)
    best, best_score = None, 0
    for name in prompts:
        pw = _word_set(name)
        overlap = len(base_words & pw)
        score = overlap / max(len(base_words), len(pw))
        if overlap >= 2 and score > best_score:
            best, best_score = prompts[name], score
    return best


def enrich_all(features_path: Path, prompts_dir: Path, output_path: Path) -> dict:
    features = json.loads(features_path.read_text())
    tracks = features.get("tracks", {})
    prompts = load_prompts(prompts_dir)

    enriched = {}
    matched, unmatched = [], []
    for name, feat in tracks.items():
        prompt_text = match_prompt(name, prompts)
        if prompt_text:
            matched.append(name)
        else:
            unmatched.append(name)
        enriched[name] = enrich_track(name, feat, prompt_text)

    # Catalog stats for companion streams
    series_counts = {}
    rgb_counts = {"R": 0, "G": 0, "B": 0}
    for t in enriched.values():
        s = t.get("series", None)
        if s:
            series_counts[s] = series_counts.get(s, 0) + 1
        rgb = t.get("rgb", "?")
        if rgb in rgb_counts:
            rgb_counts[rgb] += 1

    output = {
        "note": "JARVIS MusicOS NLP — ears + prompts + prose + RGB + physics (music_nlp.py).",
        "catalog": {
            "total": len(enriched),
            "with_prompts": len(matched),
            "audio_only": len(unmatched),
            "series": series_counts,
            "rgb_distribution": rgb_counts,
        },
        "matched": sorted(matched),
        "unmatched": sorted(unmatched),
        "tracks": enriched,
    }
    output_path.write_text(json.dumps(output, indent=2) + "\n")
    return output


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description="JARVIS MusicOS NLP enrichment")
    parser.add_argument("--features", type=Path,
                        default=Path("JarvisSide/Media/AUDIO-FEATURES.json"),
                        help="AUDIO-FEATURES.json from music_ears")
    parser.add_argument("--prompts-dir", type=Path, default=None,
                        help="MusicOS/songs/prompts/ directory")
    parser.add_argument("--output", type=Path,
                        default=Path("JarvisSide/Media/AUDIO-NLP.json"),
                        help="Output path")
    args = parser.parse_args()

    if args.prompts_dir is None:
        local = Path("MusicOS/songs/prompts")
        if local.exists():
            args.prompts_dir = local
        else:
            print("ERROR: --prompts-dir required, or run from a directory with MusicOS/songs/prompts/")
            return 1

    result = enrich_all(args.features, args.prompts_dir, args.output)
    cat = result["catalog"]

    print(f"\n{'='*60}")
    print(f"  MusicOS NLP — {cat['total']} tracks | {cat['with_prompts']} with prompts | {cat['audio_only']} audio-only")
    print(f"  RGB: R={cat['rgb_distribution']['R']} G={cat['rgb_distribution']['G']} B={cat['rgb_distribution']['B']}")
    if cat['series']:
        for s, n in cat['series'].items():
            print(f"  {s}: {n} tracks")
    print(f"{'='*60}")

    if result['unmatched']:
        print(f"\n⚠ Audio-only (no prompt): {result['unmatched']}")

    print(f"\n  → {args.output}")

    # Print a few companion-readable summaries
    shown = 0
    for name, track in result["tracks"].items():
        if track.get("prompt") and shown < 5:
            shown += 1
            print(f"\n  [{track['rgb']}] {track['title']} [{track['series_abbrev'] or '?'}#{track['track_number'] or '?'}]")
            print(f"    {track['drive_signature']} | {track['spectral_reading']}")
            print(f"    Physics: {', '.join(track['physics'][:6])}")
            print(f"    → {track['prose'][:120]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
