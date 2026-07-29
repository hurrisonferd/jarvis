# MusicOS Rehydration and Live Activation Ledger

Status: IMPLEMENTATION VERTICAL SLICE  
Authority: Raven  
Private truth: `Jarvis-Private/MusicOS/registry/`  
Public role: carry runtime, retrieval receipts, and reference-safe shared state

## Layer coverage

| Layer | Implemented vertical slice | Boundary |
|---|---|---|
| Continuity spine | Deterministic repository rehydration command, family coverage, per-file SHA-256, RAW/CANON/LEDGER/IMPLEMENTATION separation, explicit missing-family receipt | Never promotes raw material to canon |
| Music engine | Versioned Python compile packet, corrected Raven prompt laws, two-to-four style blend, influence translation, rotating state/snapshots | Python remains the canonical local/carry engine |
| ISO sensory/shared state | MCP compile/status/record/retrieve/brief tools, service-only Supabase tables, attributed carrier observations, durable SAT ChatLink reference wake | Edge records carrier analysis; it does not claim to hear or see media |

## Confirmed public source families

- `Jorm/Vault/GLOBAL_CAPTURE_INDEX.md`
- `Jorm/Vault/Sources/MusicOS/`
- MusicOS raw exports and recovery ledgers
- `memory/BarberHistory/06_Project_Ideas/MusicOSAtlas/`
- `operations/scripts/INACTIVE/music_ears.py`
- `operations/scripts/INACTIVE/music_nlp.py`
- `operations/scripts/INACTIVE/music_distill.py`
- 2026-02-16 JX2/Cecil raw export and recovery ledger
- `JX2_SHAKA_REV2` references

## Explicit unknown or incomplete coverage

- Full parity with the 47-track private MusicOS registry
- Complete Shaka scans, bones, seed, and supersession relationships
- Complete Cecil sweeps and resolver evolution
- Old GPT MusicOS memories not present in the public repository
- 28-prompts-transferred versus 24-visible prompt reconciliation
- Missing historical audio and generated analysis outputs
- Full raw transcript digestion

## Runtime commands

```bash
cd runtime/MusicOSPortable
python -m musicos rehydrate --repo ../..
python -m musicos status
python -m musicos compile \
  --intent "neon race with elastic bass and dry drums" \
  --style "synthpop rock" \
  --style "PS1 racing-game drive"
```

The rehydration command emits `data/rehydration-receipt.json`. The receipt is derived evidence, not canon.
