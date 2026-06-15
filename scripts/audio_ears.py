#!/usr/bin/env python3
"""audio_ears.py — JARVIS's ears (the librosa half).

The connector can't make a model *hear* an mp3, so we manufacture hearing: turn sound into
numbers (tempo, key, energy, brightness, duration) and numbers into words the streams can read.
Not hearing-like-a-human — but real musical bones Jarvis/Ayre can reason about and compose against.

Runs in CI (audio-ears.yml) where librosa + ffmpeg are installed — NOT in the stdlib sandbox.
Hands-free: the workflow fires when a track lands; this writes the features and the manifest.

Output:
  JarvisSide/Media/AUDIO-FEATURES.json  — machine-readable features (hash-keyed; idempotent)
  JarvisSide/Media/MEDIA-MANIFEST.md    — regenerates the '## Audio' section as a readable table
                                          (everything above '## Audio' — the image captions — is preserved)
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AUDIO = ROOT / "JarvisSide" / "Media" / "audio"
FEATURES = ROOT / "JarvisSide" / "Media" / "AUDIO-FEATURES.json"
MANIFEST = ROOT / "JarvisSide" / "Media" / "MEDIA-MANIFEST.md"

PITCHES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
# Krumhansl–Schmuckler key profiles (major / minor) — correlate against the chroma to name a key.
KS_MAJOR = [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88]
KS_MINOR = [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]


def _corr(a, b):
    n = len(a)
    ma, mb = sum(a) / n, sum(b) / n
    num = sum((a[i] - ma) * (b[i] - mb) for i in range(n))
    da = sum((x - ma) ** 2 for x in a) ** 0.5
    db = sum((x - mb) ** 2 for x in b) ** 0.5
    return num / (da * db) if da and db else 0.0


def estimate_key(chroma_mean: list[float]) -> str:
    best = ("?", -2.0)
    for i in range(12):
        maj = [KS_MAJOR[(j - i) % 12] for j in range(12)]
        minr = [KS_MINOR[(j - i) % 12] for j in range(12)]
        cm, cn = _corr(chroma_mean, maj), _corr(chroma_mean, minr)
        if cm > best[1]:
            best = (f"{PITCHES[i]} major", cm)
        if cn > best[1]:
            best = (f"{PITCHES[i]} minor", cn)
    return best[0]


def mood(bpm: float, energy: float, brightness: float) -> str:
    pace = "driving" if bpm >= 120 else "mid-tempo" if bpm >= 90 else "slow"
    en = "high-energy" if energy >= 0.08 else "moderate" if energy >= 0.03 else "soft"
    tone = "bright" if brightness >= 2500 else "warm" if brightness >= 1500 else "dark"
    return f"{pace}, {en}, {tone}"


def analyze(path: Path) -> dict:
    import librosa  # CI-only import
    import numpy as np
    y, sr = librosa.load(str(path), mono=True)
    dur = float(librosa.get_duration(y=y, sr=sr))
    tempo = float(librosa.beat.beat_track(y=y, sr=sr)[0])
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    chroma_mean = [float(x) for x in np.mean(chroma, axis=1)]
    rms = float(np.mean(librosa.feature.rms(y=y)))
    centroid = float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)))
    key = estimate_key(chroma_mean)
    return {
        "duration_sec": round(dur, 1),
        "bpm": round(tempo, 1),
        "key": key,
        "energy_rms": round(rms, 4),
        "brightness_hz": round(centroid, 0),
        "mood": mood(tempo, rms, centroid),
    }


def file_hash(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


def main() -> int:
    if not AUDIO.exists():
        print("no audio dir; nothing to hear.")
        return 0
    cache = {}
    if FEATURES.exists():
        try:
            cache = json.loads(FEATURES.read_text()).get("tracks", {})
        except Exception:
            cache = {}
    out = {}
    for mp3 in sorted(AUDIO.glob("*.mp3")):
        h = file_hash(mp3)
        prev = cache.get(mp3.name)
        if prev and prev.get("hash") == h:           # idempotent — unchanged track, reuse
            out[mp3.name] = prev
            print(f"= {mp3.name} (cached)")
            continue
        try:
            feat = analyze(mp3)
            feat["hash"] = h
            out[mp3.name] = feat
            print(f"♪ {mp3.name}: {feat['bpm']} BPM · {feat['key']} · {feat['mood']}")
        except Exception as e:
            out[mp3.name] = {"hash": h, "error": str(e)[:140]}
            print(f"! {mp3.name}: {e}")
    FEATURES.write_text(json.dumps({"note": "JARVIS ears — librosa features (audio-ears.yml).", "tracks": out}, indent=2) + "\n")

    # Rebuild only the '## Audio' section of the manifest; preserve the image captions above it.
    head = MANIFEST.read_text().split("## Audio")[0].rstrip() if MANIFEST.exists() else "# Media Manifest\n"
    rows = ["## Audio — `JarvisSide/Media/audio/` (heard via librosa features)", "",
            "| track | length | BPM | key | mood | energy · brightness |",
            "|---|---|---|---|---|---|"]
    for name, f in out.items():
        if "error" in f:
            rows.append(f"| `{name}` | — | — | — | analysis error | {f['error'][:40]} |")
        else:
            length = f"{int(f['duration_sec'] // 60)}:{int(f['duration_sec'] % 60):02d}"
            rows.append(f"| `{name}` | {length} | {f['bpm']} | {f['key']} | {f['mood']} | "
                        f"{f['energy_rms']} · {int(f['brightness_hz'])}Hz |")
    rows += ["",
             "_Features are the song's bones (tempo/key/energy), not its soul. Raven stays the ears on "
             "playback — what a track *means* lives with him, not in the BPM. Deeper vibe/captioning "
             "needs an audio model (future)._", ""]
    MANIFEST.write_text(head + "\n\n" + "\n".join(rows))
    print(f"ears: wrote {len(out)} track(s) → AUDIO-FEATURES.json + MEDIA-MANIFEST.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
