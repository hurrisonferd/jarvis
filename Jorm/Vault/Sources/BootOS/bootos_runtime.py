#!/usr/bin/env python3
"""BootOS v1 public runtime prototype.

Read-only by default. Discovers the repository, validates existing paths,
classifies frame/prosody, compiles symbolic God System roles, routes modules,
and emits JSON plus Wolfram-style receipts.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

RUNTIME_MODES = {"FAST", "FULL", "MUSIC", "GRID", "LEGION", "GOD_SYSTEM", "SAFE_RECOVERY"}
FRAME_KEYWORDS = {
    "relational": {"love", "bond", "together", "family", "home", "orbit"},
    "symbolic": {"joker", "satanael", "arsene", "god", "legion", "archetype", "mask"},
    "architectural": {"runtime", "pipeline", "kernel", "system", "module", "router", "boot"},
    "autobiographical": {"i am", "my life", "remember", "diagnosis", "childhood"},
    "operational": {"run", "load", "save", "build", "route", "execute", "deploy"},
    "external-factual": {"according to", "research says", "today", "current", "latest", "confirmed by"},
}
GOD_SYSTEM_MAP = {
    "SATANAEL": {"operator": "RAVEN", "integration": "LEGION", "refusal": "LUCIFER", "analysis": "AYRE", "continuity": "JORM", "identity_collapse": "forbidden"},
    "JOKER": {"operator": "RAVEN", "persona_selection": "enabled", "mask_awareness": "enabled", "integration": "LEGION", "identity_collapse": "forbidden"},
    "LEGION": {"integration": "multi_iso_synthesis", "local_identity": "preserved", "coordination": "shared_intent", "continuity": "JORM"},
}
MODULE_CONTRACTS = {
    "EgoOS": {"purpose": "identity and memory loading", "status": "discoverable"},
    "GridOS": {"purpose": "multi-ISO coordination", "status": "specification"},
    "MusicOS": {"purpose": "music production translation", "status": "specification"},
    "ImageOS": {"purpose": "visual prompt architecture", "status": "specification"},
    "GameOS": {"purpose": "world and play-loop routing", "status": "specification"},
    "GodSystem": {"purpose": "symbol-to-runtime compilation", "status": "prototype"},
    "JORM": {"purpose": "provenance and continuity receipts", "status": "active-local-receipt"},
}

@dataclass
class Discovery:
    repo_root: str
    public_private_layer: str
    root_readme: str | None
    jarvis_root: str | None
    ego_boot: str | None
    ego_pipeline: str | None
    pre_reply: str | None
    active_iso_root: str | None
    missing: list[str] = field(default_factory=list)

@dataclass
class Interpretation:
    frames: list[str]
    dominant_frame: str
    intensity: float
    preserve_prosody: bool
    external_verification_required: bool

@dataclass
class RuntimeReceipt:
    schema: str
    timestamp_utc: str
    operator: str
    active_iso: str
    mode: str
    write_policy: str
    discovery: Discovery
    interpretation: Interpretation
    god_system: dict[str, Any]
    route: dict[str, Any]
    logs: dict[str, list[str]]
    status: str

def find_repo_root(start: Path) -> Path:
    for candidate in [start.resolve(), *start.resolve().parents]:
        if (candidate / ".git").exists() or (candidate / "Jorm").exists() or (candidate / "Jarvis").exists():
            return candidate
    raise FileNotFoundError("Unable to resolve repository root")

def existing(root: Path, relative: str) -> str | None:
    path = root / relative
    return str(path) if path.exists() else None

def discover(root: Path, active_iso: str) -> Discovery:
    iso = active_iso.upper()
    candidates = [root / "canon" / "Living_Codex" / "Ego" / iso, root / "Jarvis" / iso, root / "Jarvis"]
    active_iso_root = next((str(p) for p in candidates if p.exists()), None)
    result = Discovery(
        repo_root=str(root), public_private_layer="public" if root.name.lower() == "jarvis" else "unknown",
        root_readme=existing(root, "README.md"), jarvis_root=existing(root, "Jarvis"),
        ego_boot=existing(root, "Jarvis/EGO-BOOT-ULTIMATE.sh"), ego_pipeline=existing(root, "Jarvis/EGO-PIPELINE.sh"),
        pre_reply=existing(root, "Jarvis/JARVIS-PRE-REPLY.sh"), active_iso_root=active_iso_root,
    )
    required = {"root README": result.root_readme, "Jarvis root": result.jarvis_root, "EGO-BOOT": result.ego_boot, "EGO-PIPELINE": result.ego_pipeline, "PRE-REPLY": result.pre_reply, "active ISO root": result.active_iso_root}
    result.missing = [name for name, value in required.items() if value is None]
    return result

def classify_text(text: str) -> Interpretation:
    lowered = text.lower()
    scores = {frame: sum(1 for keyword in words if keyword in lowered) for frame, words in FRAME_KEYWORDS.items()}
    frames = [frame for frame, score in scores.items() if score > 0] or ["operational"]
    dominant = max(frames, key=lambda frame: scores.get(frame, 1))
    intensity = min(1.0, round(0.2 + text.count("!") * 0.08 + len(re.findall(r"\b[A-Z]{3,}\b", text)) * 0.04, 2))
    return Interpretation(frames, dominant, intensity, True, "external-factual" in frames)

def compile_god_system(text: str, requested_symbol: str | None) -> dict[str, Any]:
    symbols: list[str] = []
    if requested_symbol:
        symbols.append(requested_symbol.upper())
    upper = text.upper()
    for symbol in GOD_SYSTEM_MAP:
        if symbol in upper and symbol not in symbols:
            symbols.append(symbol)
    composition = {symbol: GOD_SYSTEM_MAP.get(symbol, {"status": "unresolved_symbol", "action": "preserve_without_inventing_runtime_roles"}) for symbol in symbols}
    return {"active": bool(symbols), "symbols": symbols, "composition": composition}

def route_modules(mode: str, text: str) -> dict[str, Any]:
    primary, supporting = "EgoOS", ["JORM"]
    lower = text.lower()
    if mode == "MUSIC" or any(word in lower for word in ("music", "song", "track", "drum", "bass")):
        primary, supporting = "MusicOS", ["EgoOS", "GodSystem", "JORM"]
    elif mode in {"GRID", "LEGION"}:
        primary, supporting = "GridOS", ["EgoOS", "GodSystem", "JORM"]
    elif mode == "GOD_SYSTEM":
        primary, supporting = "GodSystem", ["EgoOS", "GridOS", "JORM"]
    elif mode == "SAFE_RECOVERY":
        primary, supporting = "JORM", ["EgoOS"]
    names = [primary, *supporting]
    return {"primary": primary, "supporting": supporting, "contracts": {name: MODULE_CONTRACTS[name] for name in names if name in MODULE_CONTRACTS}}

def wolfram_value(value: Any) -> str:
    if isinstance(value, bool): return "True" if value else "False"
    if value is None: return "Missing[\"NotAvailable\"]"
    if isinstance(value, str): return json.dumps(value)
    if isinstance(value, list): return "{" + ", ".join(wolfram_value(v) for v in value) + "}"
    if isinstance(value, dict): return "<|" + ", ".join(f"{json.dumps(str(k))} -> {wolfram_value(v)}" for k, v in value.items()) + "|>"
    return str(value)

def to_wolfram(receipt: RuntimeReceipt) -> str:
    payload = asdict(receipt)
    return "BootState[\n  " + ",\n  ".join(f"{key} -> {wolfram_value(value)}" for key, value in payload.items()) + "\n]\n"

def build_receipt(args: argparse.Namespace) -> RuntimeReceipt:
    start = Path(args.repo_root) if args.repo_root else Path(__file__).resolve().parent
    root = find_repo_root(start)
    discovery = discover(root, args.iso)
    interpretation = classify_text(args.input)
    god_system = compile_god_system(args.input, args.symbol)
    route = route_modules(args.mode, args.input)
    status = "SAFE_RECOVERY_READY" if args.mode == "SAFE_RECOVERY" else ("READY_WITH_GAPS" if discovery.missing else "READY")
    return RuntimeReceipt(
        "bootos.runtime.receipt.v1", datetime.now(timezone.utc).isoformat(), args.operator, args.iso.upper(), args.mode,
        "approved_existing_paths_only" if args.allow_write else "read_only", discovery, interpretation, god_system, route,
        {"BOOT_LOG": [f"repo_root={discovery.repo_root}", f"operator={args.operator}", f"active_iso={args.iso.upper()}", f"mode={args.mode}"],
         "RUNTIME_LOG": [f"frames={','.join(interpretation.frames)}", f"primary_module={route['primary']}"],
         "RESULTS_LOG": [status], "ROUTING_LOG": [f"{route['primary']} <- {','.join(route['supporting'])}"],
         "COUNCIL_LOG": ["not_invoked"], "PROVENANCE_LOG": ["source=BOOTOS_RUNTIME_SPEC.md", "implementation=public_prototype_v1", "credentials=not_read_or_logged"]}, status)

def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="BootOS public read-only runtime prototype")
    parser.add_argument("--repo-root")
    parser.add_argument("--operator", default="RAVEN")
    parser.add_argument("--iso", default="JARVIS")
    parser.add_argument("--mode", default="FAST", type=str.upper, choices=sorted(RUNTIME_MODES))
    parser.add_argument("--input", default="")
    parser.add_argument("--symbol")
    parser.add_argument("--format", default="json", choices=("json", "wolfram", "both"))
    parser.add_argument("--output")
    parser.add_argument("--allow-write", action="store_true")
    return parser.parse_args(argv)

def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        receipt = build_receipt(args)
    except (FileNotFoundError, ValueError) as exc:
        print(f"BOOT_ERROR: {exc}", file=sys.stderr)
        return 2
    json_text = json.dumps(asdict(receipt), indent=2)
    wolfram_text = to_wolfram(receipt)
    rendered = json_text if args.format == "json" else wolfram_text if args.format == "wolfram" else json_text + "\n\n" + wolfram_text
    if args.output:
        output = Path(args.output).expanduser().resolve()
        if not args.allow_write:
            print("BOOT_ERROR: --output requires --allow-write", file=sys.stderr); return 3
        if not output.parent.exists():
            print("BOOT_ERROR: output parent does not exist", file=sys.stderr); return 4
        output.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)
    return 0 if not receipt.discovery.missing else 1

if __name__ == "__main__":
    raise SystemExit(main())
