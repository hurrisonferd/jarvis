#!/usr/bin/env python3
"""Minimal persistent-memory demo using only JSON and the standard library."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

STORE = Path(__file__).with_name("memory.json")


def load_store() -> dict[str, Any]:
    if not STORE.exists():
        return {"facts": {}, "events": []}
    try:
        value = json.loads(STORE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Cannot load {STORE.name}: {exc}")
    if not isinstance(value, dict) or not isinstance(value.get("facts"), dict):
        raise SystemExit(f"Invalid memory store: {STORE.name}")
    value.setdefault("events", [])
    return value


def save_store(store: dict[str, Any]) -> None:
    STORE.write_text(json.dumps(store, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    remember = sub.add_parser("remember", help="Store a key/value fact")
    remember.add_argument("key")
    remember.add_argument("value")

    recall = sub.add_parser("recall", help="Recall a stored fact")
    recall.add_argument("key")

    sub.add_parser("show", help="Show the complete store")
    sub.add_parser("reset", help="Delete the demo store")

    args = parser.parse_args()

    if args.command == "reset":
        STORE.unlink(missing_ok=True)
        print("Memory reset")
        return 0

    store = load_store()

    if args.command == "remember":
        store["facts"][args.key] = args.value
        store["events"].append({"action": "remember", "key": args.key})
        save_store(store)
        print(f"Remembered {args.key}")
    elif args.command == "recall":
        if args.key not in store["facts"]:
            print(f"No memory found for {args.key}")
            return 1
        print(store["facts"][args.key])
    elif args.command == "show":
        print(json.dumps(store, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
