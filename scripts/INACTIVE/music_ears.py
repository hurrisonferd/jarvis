#!/usr/bin/env python3
"""music_ears.py — MusicOS ears for JARVIS.

Clones Jarvis-Private's MusicOS/songs/audio/ and runs librosa analysis on every track,
writing results to this repo's JarvisSide/Media/ — spectrograms + AUDIO-FEATURES.json +
MEDIA-MANIFEST.md.

Two modes:
  1. REMOTE mode (CI): clone private repo, analyze, write to JARVIS repo
  2. LOCAL mode (manual): analyze audio already present at --audio-dir

Usage:
  python3 scripts/music_ears.py                          # remote (GITHUB_TOKEN required)
  python3 scripts/music_ears.py --audio-dir /path/to/audio  # local (no clone)
  python3 scripts/music_ears.py --audio-dir /path/to/audio --output-root /path/to/jarvis
"""
from __future__ import annotations
import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

PITCHES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
KS_MAJOR = [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88]
KS_MINOR = [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT = ROOT / "JarvisSide" / "Media"


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


def render_spectrogram(y, sr, out: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import librosa.display, matplotlib.pyplot as plt, numpy as np
    S = librosa.power_to_db(librosa.feature.melspectrogram(y=y, sr=sr), ref=np.max)
    plt.figure(figsize=(7, 3))
    librosa.display.specshow(S, sr=sr, x_axis="time", y_axis="mel", cmap="magma")
    plt.axis("off")
    out.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out, dpi=80, bbox_inches="tight", pad_inches=0)
    plt.close()


def analyze(path: Path) -> dict:
    import librosa
    import numpy as np
    y, sr = librosa.load(str(path), mono=True)
    dur = float(librosa.get_duration(y=y, sr=sr))
    bt = librosa.beat.beat_track(y=y, sr=sr)
    tempo = float(bt[0].item())
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    chroma_mean = [float(x) for x in np.mean(chroma, axis=1)]
    rms_series = librosa.feature.rms(y=y)[0]
    rms = float(np.mean(rms_series))
    centroid = float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)))
    key = estimate_key(chroma_mean)
    onsets = librosa.onset.onset_detect(y=y, sr=sr)
    onset_density = round(len(onsets) / dur, 2) if dur else 0.0
    dyn_range = round(float(20 * np.log10((np.max(rms_series) + 1e-6) / (np.percentile(rms_series, 10) + 1e-6))), 1)
    return {
        "duration_sec": round(dur, 1),
        "bpm": round(tempo, 1),
        "key": key,
        "energy_rms": round(rms, 4),
        "brightness_hz": round(centroid, 0),
        "onset_density": onset_density,
        "dynamic_range_db": dyn_range,
        "mood": mood(tempo, rms, centroid),
    }


def file_hash(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


def run(audio_dir: Path, output_root: Path, source_root: Path | None = None, private_token: str | None = None) -> dict:
    features_path = output_root / "AUDIO-FEATURES.json"
    manifest_path = output_root / "MEDIA-MANIFEST.md"
    spectrograms_dir = output_root / "spectrograms"
    spectrograms_dir.mkdir(parents=True, exist_ok=True)

    # Also write spectrograms to source (MusicOS/songs/spectrograms/) alongside the audio
    source_spec_dir = None
    if source_root:
        source_spec_dir = source_root / "spectrograms"
        source_spec_dir.mkdir(parents=True, exist_ok=True)

    # Load cache
    cache = {}
    if features_path.exists():
        try:
            cache = json.loads(features_path.read_text()).get("tracks", {})
        except Exception:
            cache = {}

    out = {}
    mp3s = sorted(audio_dir.glob("*.mp3"))
    print(f"music_ears: {len(mp3s)} tracks in {audio_dir}")

    for mp3 in mp3s:
        h = file_hash(mp3)
        prev = cache.get(mp3.name)
        if prev and prev.get("hash") == h:
            out[mp3.name] = prev
            # Mirror cached spectrogram to source if it exists
            if source_spec_dir:
                src_out = source_spec_dir / f"{mp3.stem}.png"
                if not src_out.exists():
                    cached_spec = spectrograms_dir / f"{mp3.stem}.png"
                    if cached_spec.exists():
                        import shutil
                        shutil.copy2(cached_spec, src_out)
            print(f"  = {mp3.name} (cached)")
            continue
        try:
            feat = analyze(mp3)
            feat["hash"] = h
            # Render spectrogram
            try:
                import librosa, numpy as np
                y, sr = librosa.load(str(mp3), mono=True)
                spec_out = spectrograms_dir / f"{mp3.stem}.png"
                render_spectrogram(y, sr, spec_out)
                feat["spectrogram"] = f"spectrograms/{mp3.stem}.png"
                # Mirror to source location (MusicOS/songs/spectrograms/)
                if source_spec_dir:
                    src_out = source_spec_dir / f"{mp3.stem}.png"
                    import shutil
                    shutil.copy2(spec_out, src_out)
                print(f"  ♪ {mp3.name}: {feat['bpm']} BPM · {feat['key']} · {feat['mood']} · spec")
            except Exception as e:
                feat["spectrogram"] = ""
                print(f"  ♪ {mp3.name}: {feat['bpm']} BPM · {feat['key']} · {feat['mood']} · (spec err: {e})")
            out[mp3.name] = feat
        except Exception as e:
            out[mp3.name] = {"hash": h, "error": str(e)[:140]}
            print(f"  ! {mp3.name}: {e}")

    # Write features
    features_path.write_text(
        json.dumps({"note": "JARVIS MusicOS ears — MusicOS/songs/audio/ (music-ears.yml).", "tracks": out}, indent=2) + "\n"
    )
    print(f"  → {features_path}")

    # Rebuild audio section of manifest (preserve image captions)
    head = manifest_path.read_text().split("## Audio")[0].rstrip() if manifest_path.exists() else "# Media Manifest\n"
    rows = ["## Audio — `JarvisSide/Media/audio/` (MusicOS ears — librosa features + spectrograms)", "",
            "| track | length | BPM | key | mood | onset/s · dyn | spectrogram |",
            "|---|---|---|---|---|---|---|"]
    for name, f in out.items():
        if "error" in f:
            rows.append(f"| `{name}` | — | — | — | error | {f['error'][:30]} | — |")
        else:
            length = f"{int(f['duration_sec'] // 60)}:{int(f['duration_sec'] % 60):02d}"
            spec = f"`{f['spectrogram']}`" if f.get("spectrogram") else "—"
            rows.append(f"| `{name}` | {length} | {f['bpm']} | {f['key']} | {f['mood']} | "
                        f"{f.get('onset_density','?')} · {f.get('dynamic_range_db','?')}dB | {spec} |")
    rows += ["",
             "_Features are the song's bones; the **spectrogram** is its shape — "
             "`jarvis_media_view {path:'JarvisSide/Media/<spectrogram>'}` lets a vision stream "
             "SEE the build/drop/density. The soul is Raven's on playback._", ""]
    manifest_path.write_text(head + "\n\n" + "\n".join(rows))
    print(f"  → {manifest_path}")

    changed = [f for f in [features_path, manifest_path] if f.exists()]
    spec_files = list(spectrograms_dir.glob("*.png"))
    print(f"music_ears: wrote {len(out)} track(s), {len(spec_files)} spectrograms")
    return out


def clone_private_audio(token: str) -> Path:
    """Clone Jarvis-Private and return the MusicOS audio directory."""
    tmp = Path(tempfile.mkdtemp(prefix="music_ears_"))
    private_url = f"https://x-access-token:{token}@github.com/hurrisonferd/Jarvis-Private.git"
    subprocess.run(["git", "clone", "--depth", "1", private_url, str(tmp)],
                   check=True, capture_output=True)
    audio = tmp / "MusicOS" / "songs" / "audio"
    if not audio.exists():
        raise FileNotFoundError(f"No audio dir in Jarvis-Private: {audio}")
    return tmp, audio


def main() -> int:
    parser = argparse.ArgumentParser(description="JARVIS MusicOS ears")
    parser.add_argument("--audio-dir", type=Path, default=None,
                        help="Local audio directory (skip clone)")
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT,
                        help="JARVIS repo root (default: $REPO/JarvisSide/Media)")
    parser.add_argument("--source-root", type=Path, default=None,
                        help="Source repo root — mirrors spectrograms to SOURCE/spectrograms/")
    parser.add_argument("--token", type=str, default=None,
                        help="GitHub token for Jarvis-Private (or env:JARVIS_PRIVATE_TOKEN)")
    args = parser.parse_args()

    private_token = args.token or __import__("os").getenv("JARVIS_PRIVATE_TOKEN")

    if args.audio_dir:
        tmp = None
        audio_dir = args.audio_dir
    elif private_token:
        tmp, audio_dir = clone_private_audio(private_token)
        print(f"cloned: {audio_dir}")
        # Auto-set source_root if not specified
        if args.source_root is None and tmp:
            args.source_root = tmp / "MusicOS" / "songs"
    else:
        # Try local path first
        local = Path("MusicOS/songs/audio")
        if local.exists():
            tmp = None
            audio_dir = local
            if args.source_root is None:
                args.source_root = local.parent
        else:
            print("ERROR: --audio-dir required, or set JARVIS_PRIVATE_TOKEN / --token")
            print("  python3 scripts/music_ears.py --audio-dir /path/to/audio")
            return 1

    try:
        run(audio_dir, args.output_root, source_root=args.source_root)
    finally:
        if tmp:
            shutil.rmtree(tmp, ignore_errors=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
