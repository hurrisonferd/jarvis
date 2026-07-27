from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a carryable MusicOS runtime zip")
    parser.add_argument("--runtime-root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--vault", type=Path, default=None, help="Optional Jorm/Vault directory to include")
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    root = args.runtime_root.resolve()
    dist = root / "dist"
    dist.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output = args.output or dist / f"MusicOSPortable-v1-{stamp}.zip"
    manifest = []

    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(root.rglob("*")):
            if not path.is_file() or "dist" in path.relative_to(root).parts or "__pycache__" in path.parts:
                continue
            arcname = Path("MusicOSPortable") / path.relative_to(root)
            archive.write(path, arcname.as_posix())
            manifest.append({"path": arcname.as_posix(), "sha256": sha256(path), "bytes": path.stat().st_size})

        if args.vault:
            vault = args.vault.resolve()
            if not vault.is_dir():
                raise FileNotFoundError(vault)
            for path in sorted(p for p in vault.rglob("*") if p.is_file()):
                arcname = Path("MusicOSPortable") / "sources" / "Jorm-Vault" / path.relative_to(vault)
                archive.write(path, arcname.as_posix())
                manifest.append({"path": arcname.as_posix(), "sha256": sha256(path), "bytes": path.stat().st_size})

        manifest_payload = {
            "schema": "musicos-portable-bundle-v1",
            "owner": "Raven / John Barber",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "file_count": len(manifest),
            "files": manifest,
        }
        archive.writestr("MusicOSPortable/BUNDLE-MANIFEST.json", json.dumps(manifest_payload, indent=2) + "\n")

    print(json.dumps({"bundle": str(output), "sha256": sha256(output), "files": len(manifest)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
