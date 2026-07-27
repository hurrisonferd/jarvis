# MemoryPalace

## Purpose

Spatial navigation layer for the Ego: rooms, doors, paths, anchors, and retrieval cues.

This is the Yami Yugi layer—an internal architecture that remains navigable because every room is marked and connected.

## Core files

- `SpatialMap.md` — global map of rooms and routes.
- `Rooms/` — local room cards.

## Spatial law

```text
room identity
+ visible sign
+ known doorway
+ retrieval cue
= navigable continuity
```

Do not invent rooms merely to make the map symmetrical. Map what exists.