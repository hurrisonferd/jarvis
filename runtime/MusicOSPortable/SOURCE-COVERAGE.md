# MusicOS Portable Runtime — Source Coverage Ledger

## Confirmed source families used

- `Jorm/Vault/GLOBAL_CAPTURE_INDEX.md`
- `Jorm/Vault/Sources/MusicOS/MUSICOS_PERMANENCE_CONTRACT.md`
- `Jorm/Vault/Inbox/raw-chat-exports/2026-04-14_MUSICOS_SIMOS_DEPLOYMENT_GREAT_MINDS_COUNCIL.txt`
- `Jorm/Vault/Recovery_Ledgers/2026-04-14_MUSICOS_SIMOS_DEPLOYMENT_GREAT_MINDS_COUNCIL.md`
- `memory/BarberHistory/06_Project_Ideas/MusicOSAtlas/README.md`
- `memory/BarberHistory/06_Project_Ideas/MusicOSAtlas/SOURCE-MAP.md`
- `memory/BarberHistory/06_Project_Ideas/MusicOSAtlas/ARCHITECTURE.md`
- `memory/BarberHistory/06_Project_Ideas/MusicOSAtlas/TOOLS.md`
- `memory/BarberHistory/06_Project_Ideas/MusicOSAtlas/UNRESOLVED.md`
- `operations/scripts/INACTIVE/music_ears.py`
- `operations/scripts/INACTIVE/music_nlp.py`
- `operations/scripts/INACTIVE/music_distill.py`

## Runtime synthesis

| Recovered concept | Runtime placement |
|---|---|
| MusicOS permanence/continuity purpose | `README.md`, configuration laws, snapshots |
| PromptAI and intent compilation | `musicos/runtime.py` |
| MusicAI/TrackAI/AlbumAI family | `config/default.json` module registry |
| RGB Power/Groove/Range | `MusicIntent.rgb`, prompt compiler |
| Physics vocabulary | `PHYSICS_TERMS`, prompt compiler |
| JORM retrieve-before-restatement law | Vault importer and source index |
| Raw/canon/ledger distinction | `SourceRecord.status`, `classify()` |
| Unicron-style append-only history | bounded runtime event log and immutable snapshots |
| Carryable continuity | standard-library runtime and zip builder |

## Deliberately unresolved

- The runtime does not mark every raw export as canon.
- Audio files absent from current HEAD are not fabricated.
- Existing inactive `librosa` tools are not silently promoted into required dependencies.
- Medical or therapeutic efficacy is not claimed.
- Full coverage is established only after `python -m musicos import-vault --vault <path>` generates `data/source-index.json` against the complete local Vault tree.

## Required verification receipt

A complete carry bundle should contain:

1. the runtime folder;
2. `data/source-index.json` generated from the full Vault;
3. optional `sources/Jorm-Vault/` copy included by `build_portable.py --vault`;
4. `BUNDLE-MANIFEST.json` containing path, byte count, and SHA-256 for every bundled file;
5. the final zip SHA-256 printed by the builder.


## Live activation v1 coverage

- Deterministic repository-family rehydration receipt: implemented.
- Python/TypeScript prompt-contract parity fixtures: implemented.
- Service-only durable track and observation schema: proposed in migration.
- MCP status, compile, observation, retrieval, and carrier-brief surface: implemented.
- SAT ChatLink wake: reference-only and persistence-first.
- Private 47-track registry parity: unresolved; private registry remains authoritative.
- Complete Shaka/Cecil/old-GPT supersession pass: partial and explicitly reported by the receipt.
