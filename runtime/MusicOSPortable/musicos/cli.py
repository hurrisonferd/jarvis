from __future__ import annotations

import argparse
import json
from pathlib import Path

from .models import MusicIntent
from .rehydration import rehydrate_sources
from .runtime import MusicOSRuntime


def _rgb(value: str) -> dict[str, int]:
    parts = value.split(",")
    if len(parts) != 3:
        raise argparse.ArgumentTypeError("RGB must be R,G,B, for example 50,80,60")
    try:
        r, g, b = (int(part.strip()) for part in parts)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("RGB values must be integers") from exc
    return {"R": r, "G": g, "B": b}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="musicos", description="MusicOS Portable Runtime")
    parser.add_argument("--root", type=Path, default=None, help="Runtime root override")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("status", help="Show runtime, modules, laws, and source coverage")

    imp = sub.add_parser("import-vault", help="Index all MusicOS-linked sources under Jorm/Vault")
    imp.add_argument("--vault", type=Path, required=True)

    boot = sub.add_parser("rehydrate", help="Build a deterministic source-to-runtime receipt")
    boot.add_argument("--repo", type=Path, required=True)

    comp = sub.add_parser("compile", help="Compile natural-language intent into a MusicOS track packet")
    comp.add_argument("--intent", required=True)
    comp.add_argument("--bpm", type=int)
    comp.add_argument("--key")
    comp.add_argument("--rgb", type=_rgb, default={"R": 50, "G": 75, "B": 50})
    comp.add_argument("--state", default="balanced")
    comp.add_argument("--style", action="append", default=[])
    comp.add_argument("--vocal", action="store_true")
    comp.add_argument("--constraint", action="append", default=[])

    snap = sub.add_parser("snapshot", help="Write an immutable runtime state snapshot")
    snap.add_argument("--name", default="raven-main")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    runtime = MusicOSRuntime(args.root)

    if args.command == "status":
        result = runtime.status()
    elif args.command == "import-vault":
        result = runtime.import_vault(args.vault)
    elif args.command == "rehydrate":
        result = rehydrate_sources(args.repo, runtime.rehydration_path)
        runtime.store.event(
            runtime.state,
            "REHYDRATION_RECEIPT_CREATED",
            {
                "receipt_sha256": result["receipt_sha256"],
                "coverage": result["coverage"],
                "source_count": result["source_count"],
            },
        )
    elif args.command == "compile":
        result = runtime.compile(MusicIntent(
            text=args.intent,
            bpm=args.bpm,
            key=args.key,
            instrumental=not args.vocal,
            rgb=args.rgb,
            state=args.state,
            styles=args.style,
            constraints=args.constraint,
        )).to_dict()
    elif args.command == "snapshot":
        result = {"snapshot": str(runtime.snapshot(args.name))}
    else:
        raise AssertionError(args.command)

    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0
