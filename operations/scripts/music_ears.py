#!/usr/bin/env python3
"""MusicOS Ears: turn repository or HTTPS audio into durable feature receipts."""
from __future__ import annotations

import argparse
import hashlib
import ipaddress
import json
import re
import socket
import tempfile
import urllib.parse
import urllib.request
from pathlib import Path

PITCHES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
KS_MAJOR = [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88]
KS_MINOR = [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]
ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "JarvisSide" / "Media"
SUPPORTED_AUDIO = {".mp3", ".wav", ".flac", ".m4a", ".ogg", ".opus"}
MAX_DOWNLOAD_BYTES = 250 * 1024 * 1024


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
        major = [KS_MAJOR[(j - i) % 12] for j in range(12)]
        minor = [KS_MINOR[(j - i) % 12] for j in range(12)]
        for label, score in (
            (f"{PITCHES[i]} major", _corr(chroma_mean, major)),
            (f"{PITCHES[i]} minor", _corr(chroma_mean, minor)),
        ):
            if score > best[1]:
                best = (label, score)
    return best[0]


def mood(bpm: float, energy: float, brightness: float) -> str:
    pace = "driving" if bpm >= 120 else "mid-tempo" if bpm >= 90 else "slow"
    force = "high-energy" if energy >= 0.08 else "moderate" if energy >= 0.03 else "soft"
    tone = "bright" if brightness >= 2500 else "warm" if brightness >= 1500 else "dark"
    return f"{pace}, {force}, {tone}"


def render_spectrogram(y, sr, out: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import librosa
    import librosa.display
    import matplotlib.pyplot as plt
    import numpy as np

    spectrum = librosa.power_to_db(
        librosa.feature.melspectrogram(y=y, sr=sr), ref=np.max
    )
    plt.figure(figsize=(7, 3))
    librosa.display.specshow(
        spectrum, sr=sr, x_axis="time", y_axis="mel", cmap="magma"
    )
    plt.axis("off")
    out.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out, dpi=80, bbox_inches="tight", pad_inches=0)
    plt.close()


def analyze(path: Path, spectrogram_path: Path) -> dict:
    import librosa
    import numpy as np

    y, sr = librosa.load(str(path), mono=True)
    duration = float(librosa.get_duration(y=y, sr=sr))
    tempo_value = librosa.beat.beat_track(y=y, sr=sr)[0]
    tempo = float(tempo_value.item() if hasattr(tempo_value, "item") else tempo_value)
    chroma_mean = [
        float(value)
        for value in np.mean(librosa.feature.chroma_cqt(y=y, sr=sr), axis=1)
    ]
    rms_series = librosa.feature.rms(y=y)[0]
    energy = float(np.mean(rms_series))
    brightness = float(
        np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
    )
    onsets = librosa.onset.onset_detect(y=y, sr=sr)
    dynamic_range = float(
        20
        * np.log10(
            (np.max(rms_series) + 1e-6)
            / (np.percentile(rms_series, 10) + 1e-6)
        )
    )
    render_spectrogram(y, sr, spectrogram_path)
    return {
        "duration_sec": round(duration, 1),
        "bpm": round(tempo, 1),
        "key": estimate_key(chroma_mean),
        "energy_rms": round(energy, 4),
        "brightness_hz": round(brightness, 0),
        "onset_density": round(len(onsets) / duration, 2) if duration else 0.0,
        "dynamic_range_db": round(dynamic_range, 1),
        "mood": mood(tempo, energy, brightness),
        "spectrogram": f"spectrograms/{spectrogram_path.name}",
    }


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()[:16]


def safe_name(value: str, source_url: str = "") -> str:
    name = Path(urllib.parse.unquote(value)).name
    stem = re.sub(r"[^A-Za-z0-9._ -]+", "_", Path(name).stem).strip(" ._")
    suffix = Path(name).suffix.lower()
    if suffix not in SUPPORTED_AUDIO:
        source_suffix = Path(urllib.parse.urlsplit(source_url).path).suffix.lower()
        suffix = source_suffix if source_suffix in SUPPORTED_AUDIO else ".audio"
    return f"{stem or 'internet-track'}{suffix}"


def normalize_url(value: str) -> str:
    parsed = urllib.parse.urlsplit(value.strip())
    if parsed.scheme != "https" or not parsed.hostname:
        raise ValueError("source URL must be HTTPS")
    if parsed.username or parsed.password:
        raise ValueError("source URL must not contain credentials")
    if parsed.query:
        raise ValueError("source URL must not contain query parameters")
    if parsed.hostname.lower() == "github.com":
        parts = parsed.path.strip("/").split("/")
        if len(parts) >= 5 and parts[2] == "blob":
            owner, repo, _, ref, *path = parts
            parsed = urllib.parse.urlsplit(
                f"https://raw.githubusercontent.com/{owner}/{repo}/{ref}/"
                + "/".join(path)
            )
    return urllib.parse.urlunsplit(parsed)


def public_host(url: str) -> None:
    host = urllib.parse.urlsplit(url).hostname
    if not host:
        raise ValueError("source URL has no host")
    for result in socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM):
        address = ipaddress.ip_address(result[4][0])
        if not address.is_global:
            raise ValueError("source URL resolves to a non-public address")


class PublicHttpsRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        target = normalize_url(newurl)
        public_host(target)
        return super().redirect_request(req, fp, code, msg, headers, target)


def download_audio(source_url: str, destination: Path) -> str:
    url = normalize_url(source_url)
    public_host(url)
    opener = urllib.request.build_opener(PublicHttpsRedirects())
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Jarvis-MusicOS-Ears/1.0"},
    )
    with opener.open(request, timeout=45) as response:
        final_url = normalize_url(response.geturl())
        public_host(final_url)
        length = response.headers.get("Content-Length")
        if length and int(length) > MAX_DOWNLOAD_BYTES:
            raise ValueError("source audio exceeds the 250 MiB limit")
        total = 0
        with destination.open("wb") as output:
            while chunk := response.read(1024 * 1024):
                total += len(chunk)
                if total > MAX_DOWNLOAD_BYTES:
                    raise ValueError("source audio exceeds the 250 MiB limit")
                output.write(chunk)
    return urllib.parse.urlunsplit(
        urllib.parse.urlsplit(final_url)._replace(query="", fragment="")
    )


def load_cache(features_path: Path) -> dict:
    if not features_path.exists():
        return {}
    try:
        return json.loads(features_path.read_text()).get("tracks", {})
    except (json.JSONDecodeError, OSError):
        return {}


def analyze_one(
    audio_path: Path,
    track_name: str,
    output_root: Path,
    source: dict,
) -> dict:
    spec_name = f"{Path(track_name).stem}.png"
    feature = analyze(audio_path, output_root / "spectrograms" / spec_name)
    feature["hash"] = file_hash(audio_path)
    feature["source"] = source
    return feature


def write_outputs(output_root: Path, tracks: dict) -> None:
    output_root.mkdir(parents=True, exist_ok=True)
    features_path = output_root / "AUDIO-FEATURES.json"
    manifest_path = output_root / "MEDIA-MANIFEST.md"
    features_path.write_text(
        json.dumps(
            {
                "note": "JARVIS MusicOS Ears — durable librosa feature receipts.",
                "tracks": dict(sorted(tracks.items())),
            },
            indent=2,
        )
        + "\n"
    )
    rows = [
        "# Media Manifest",
        "",
        "## Audio — MusicOS Ears",
        "",
        "| track | length | BPM | key | mood | onset/s · dyn | source |",
        "|---|---|---|---|---|---|---|",
    ]
    for name, feature in sorted(tracks.items()):
        if "error" in feature:
            rows.append(f"| `{name}` | — | — | — | analysis error | — | — |")
            continue
        length = (
            f"{int(feature['duration_sec'] // 60)}:"
            f"{int(feature['duration_sec'] % 60):02d}"
        )
        source_kind = feature.get("source", {}).get("kind", "repository")
        rows.append(
            f"| `{name}` | {length} | {feature['bpm']} | {feature['key']} | "
            f"{feature['mood']} | {feature['onset_density']} · "
            f"{feature['dynamic_range_db']}dB | {source_kind} |"
        )
    manifest_path.write_text("\n".join(rows) + "\n")


def run_directory(
    audio_dir: Path,
    output_root: Path,
    source_root: Path | None,
    force: bool,
) -> dict:
    features_path = output_root / "AUDIO-FEATURES.json"
    cache = load_cache(features_path)
    tracks = {
        name: feature
        for name, feature in cache.items()
        if feature.get("source", {}).get("kind") == "url"
    }
    audio_files = sorted(
        path for path in audio_dir.iterdir() if path.suffix.lower() in SUPPORTED_AUDIO
    )
    print(f"music_ears: {len(audio_files)} repository track(s)")
    for audio_path in audio_files:
        digest = file_hash(audio_path)
        previous = cache.get(audio_path.name)
        if (
            not force
            and previous
            and "error" not in previous
            and previous.get("hash") == digest
        ):
            tracks[audio_path.name] = previous
            print(f"  = {audio_path.name} (cached)")
            continue
        try:
            tracks[audio_path.name] = analyze_one(
                audio_path,
                audio_path.name,
                output_root,
                {"kind": "repository"},
            )
            print(f"  ♪ {audio_path.name}")
        except Exception as error:
            tracks[audio_path.name] = {
                "hash": digest,
                "error": str(error)[:140],
                "source": {"kind": "repository"},
            }
            print(f"  ! {audio_path.name}: {error}")
    write_outputs(output_root, tracks)
    if source_root:
        source_specs = source_root / "spectrograms"
        source_specs.mkdir(parents=True, exist_ok=True)
        for audio_path in audio_files:
            spectrogram = output_root / "spectrograms" / f"{audio_path.stem}.png"
            if spectrogram.exists():
                (source_specs / spectrogram.name).write_bytes(spectrogram.read_bytes())
    return tracks


def run_url(source_url: str, track_name: str | None, output_root: Path) -> dict:
    features_path = output_root / "AUDIO-FEATURES.json"
    tracks = load_cache(features_path)
    inferred_name = safe_name(
        track_name or urllib.parse.urlsplit(source_url).path or "internet-track",
        source_url,
    )
    with tempfile.TemporaryDirectory(prefix="music_ears_url_") as temp:
        audio_path = Path(temp) / inferred_name
        receipt_url = download_audio(source_url, audio_path)
        tracks[inferred_name] = analyze_one(
            audio_path,
            inferred_name,
            output_root,
            {"kind": "url", "url": receipt_url},
        )
    write_outputs(output_root, tracks)
    print(f"music_ears: heard URL as {inferred_name}")
    return tracks


def main() -> int:
    parser = argparse.ArgumentParser(description="JARVIS MusicOS Ears")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--audio-dir", type=Path)
    source.add_argument("--source-url")
    parser.add_argument("--track-name")
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--source-root", type=Path)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    if args.source_url:
        run_url(args.source_url, args.track_name, args.output_root)
    else:
        if not args.audio_dir.is_dir():
            parser.error(f"audio directory not found: {args.audio_dir}")
        run_directory(args.audio_dir, args.output_root, args.source_root, args.force)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
