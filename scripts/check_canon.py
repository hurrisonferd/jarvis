#!/usr/bin/env python3
"""MERIDIAN — god-system canon guard.

Enforces the ARCH constraint in CI: the 27 god systems are fixed. Do not
redefine, renumber, or add. This fails the build if a system directory is
added, removed, or renamed — catching canon drift before it merges.

Run: python3 scripts/check_canon.py
"""
import sys
from pathlib import Path

# The canonical 27, by tier (P26 Canon Spec v1.0). This list is the contract.
CANON = {
    "T0_CHAOS", "T0_HADES", "T0_POSEIDON", "T0_ZEUS",
    "T1_AEGIS", "T1_AYRE", "T1_ERIS", "T1_ODIN", "T1_SKADI",
    "T2_KRONOS",
    "T3_HALO", "T3_HUGINN", "T3_MIMIR", "T3_MNEMOS",
    "T4_BIFROST", "T4_JANUS",
    "T5_ARGUS", "T5_ATHENA", "T5_LOKI", "T5_NEMESIS", "T5_PROMETHEUS",
    "T6_IRIS", "T6_MERIDIAN",
    "T7_APOLLO", "T7_DANTE",
    "T8_ATLAS",
    "T9_HERMES",
}

root = Path(__file__).resolve().parent.parent / "JarvisMain" / "god_systems"
present = {p.name for p in root.iterdir() if p.is_dir() and p.name.startswith("T")}

added = present - CANON
removed = CANON - present

if added or removed:
    print("CANON FAIL — god-system drift detected (ARCH violation)")
    if added:
        print(f"  added/renamed (not in canon): {sorted(added)}")
    if removed:
        print(f"  missing (expected by canon): {sorted(removed)}")
    print("\n  The 27 god systems are fixed. Do not redefine, renumber, or add.")
    sys.exit(1)

print(f"CANON OK — {len(present)}/27 god systems intact")
