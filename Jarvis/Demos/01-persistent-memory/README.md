# Demo 01: Persistent Memory

This demo proves the smallest useful JARVIS behavior: information survives process restarts.

```bash
python Jarvis/Demos/01-persistent-memory/demo.py remember favorite_color teal
python Jarvis/Demos/01-persistent-memory/demo.py recall favorite_color
```

Stop the process, close the terminal, and run `recall` later. The value is loaded from `memory.json` rather than conversational context.

Reset the demo with:

```bash
python Jarvis/Demos/01-persistent-memory/demo.py reset
```

The production architecture extends this pattern with versioned files, Supabase, semantic retrieval, provenance, and governed writes.
