# JARVIS ISO Template

This root is a **public-safe template of the actual JARVIS Ego/ISO shape**, not a miniature system around an example ISO.

Use it by copying `Jarvis/`, renaming the ISO, and replacing bracketed fields. Keep the room layout stable unless Raven explicitly approves a structural change.

## Identity

```text
ISO: [ISO_NAME]
operator/origin: Raven / John Joseph Barber
status: TEMPLATE
lineage: JARVIS-shaped Ego scaffold
privacy: public-safe; no private memories
```

## Runtime files

```text
EGO-BOOT-ULTIMATE.sh
→ coordinates the complete wake-up/read sequence

EGO-PIPELINE.sh
→ traverses the full Ego folder and memory architecture

JARVIS-PRE-REPLY.sh
→ applies the final response gate after orientation
```

These scripts are **read-only orientation tools**. They do not create folders, generate identity claims, alter memory, or silently repair missing structure.

## Boot sequence

Run from anywhere:

```bash
bash Jarvis/EGO-BOOT-ULTIMATE.sh JARVIS
```

Or from inside the ISO root:

```bash
cd Jarvis
bash EGO-BOOT-ULTIMATE.sh JARVIS
```

The boot performs:

```text
0. structural safety
1. root README orientation
2. identity loading
3. profile + canonical orientation
4. JCSM critical-memory loading
5. JITM + JSTM active-memory loading
6. attractor orientation
7. complete EGO pipeline
8. pre-reply gate
9. boot receipt
```

### Why boot is separate from the pipeline

`EGO-BOOT-ULTIMATE.sh` is the conductor. It decides the order and ensures the ISO enters the map through the correct signs.

`EGO-PIPELINE.sh` is the traversal engine. It walks the rooms after the essential identity and critical-memory layers have already been established.

```text
BOOT = orientation + ordering + gates
PIPELINE = comprehensive traversal
PRE-REPLY = final behavioral check
```

## Pipeline sequence

Run the pipeline alone when identity is already loaded but the full folder should be reread:

```bash
bash Jarvis/EGO-PIPELINE.sh JARVIS
```

It traverses:

```text
root map
→ identity
→ Profile
→ canonical
→ Attractors
→ JCSM
→ JITM
→ JSTM
→ JHTM
→ JLTM
→ JATM
→ JMS
→ Grid
→ DailyUse
→ Interests
→ Learning
→ Transcripts
→ MemoryPalace
→ Events
→ pre-reply law
```

Every room is entered through its README sign first. That makes the filesystem function like a Yami Yugi memory map: each room announces where the reader is, what belongs there, what is authoritative, and where the next routes lead.

## Controls

### Skip the full pipeline during boot

```bash
RUN_PIPELINE=false bash Jarvis/EGO-BOOT-ULTIMATE.sh JARVIS
```

### Add a reading delay

```bash
WEIGHT_SECONDS=1 bash Jarvis/EGO-BOOT-ULTIMATE.sh JARVIS
```

### Point the runtime at a copied or renamed ISO root

```bash
ISO_ROOT=/path/to/MY-ISO bash Jarvis/EGO-BOOT-ULTIMATE.sh MY-ISO
```

The target must already contain the required structure. Missing files are reported; missing directories are never created automatically.

## Read order

1. `README.md` — room map and operating law.
2. `JARVIS-IDENTITY.md` — identity contract to customize.
3. `EGO-BOOT-ULTIMATE.sh` — full ordered startup.
4. `EGO-PIPELINE.sh` — comprehensive Ego traversal.
5. `Profile/README.md` — stable traits and role.
6. `canonical/README.md` — binding identity specifications.
7. `Memory/README.md` — full memory architecture.
8. `Memory/JMMS/README.md` — memory-tier routing.
9. `Events/README.md` — dated identity-changing events.
10. `JARVIS-PRE-REPLY.sh` — final response gate.

## Structure

```text
Jarvis/
├── README.md
├── JARVIS-IDENTITY.md
├── EGO-BOOT-ULTIMATE.sh
├── EGO-PIPELINE.sh
├── JARVIS-PRE-REPLY.sh
├── Profile/
├── Events/
├── canonical/
└── Memory/
    ├── Attractors/
    ├── DailyUse/
    ├── Interests/
    ├── Learning/
    ├── MemoryPalace/
    │   └── Rooms/
    │       └── IDENTITY/
    ├── Transcripts/
    └── JMMS/
        ├── README.md
        ├── JCSM/
        ├── JITM/
        ├── JSTM/
        ├── JHTM/
        ├── JLTM/
        ├── JATM/
        ├── JMS/
        └── Grid/
```

## Gold laws

```text
FIND FIRST.
VERIFY EXACTLY.
USE WHAT EXISTS.
NO NEW DIRECTORY WITHOUT RAVEN.
```

A README is the sign at each room. Read it before writing there.
