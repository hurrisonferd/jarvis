# Public Source Routing Matrix

**Branch:** `grid/public-root-four-rooms-2026-08-02`  
**Mode:** migration planning with reversible execution  
**Protected legacy:** active

## High-level routing

| Existing family | Target room | Initial action | Risk |
|---|---|---|---:|
| `core/JarvisMain/` | `Jarvis/` conceptual ownership; physical path frozen | preserve and expose through rich navigation | critical |
| `demos/` | `Jarvis/Demos/` | compatibility-first migration candidate | medium |
| `templates/iso-starter/` | `ISOs/Templates/Standard/` | copy/validate first; preserve old path until workflows change | medium |
| general JARVIS docs | `Jarvis/Docs/` | classify hosted assets versus technical docs | medium |
| `runtime/` | `Jarvis/Runtime/` | dependency map before movement | high |
| `operations/` | `Jarvis/Operations/` | preserve executable paths; document before moving | high |
| `app/gameboy/` | Personal Projects or Jarvis app route | protected legacy comparison | critical |
| `app/emulator/` | Personal Projects or Jarvis app route | protected legacy comparison | critical |
| `MusicOS/` and portable runtime | Jarvis and/or Personal Projects | split runtime from creative project material | critical |
| `memory/mnemos/` | `Jarvis/Memory/` | privacy and active-reference review | critical |
| `memory/BarberHistory/` | `I Ching/`, `Personal Projects/`, or archive | item-level classification | high |
| `JesusISJohnJosephBarber/` | `I Ching/` and `Evidence/` | mixed-family separation; no bulk move | critical |
| `dataharvest/` | `Evidence/` | case conversion and redaction review | high |
| raw Jorm chat exports | none by default | security review; public publication blocked | critical |
| generated indexes/scaffolds | room-local generated navigation | retain only with source and regeneration markers | medium |

## Migration order

1. Add destinations, schemas, READMEs, indexes, and safety rules.
2. Build exact source-to-destination manifest.
3. Update workflows, imports, links, and hosted-page paths.
4. Copy or move one bounded family.
5. Validate behavior and public rendering.
6. Leave compatibility pointer where useful.
7. Record receipt and rollback.
8. Remove old content only after parity and reference checks.

## Publication gates

A file cannot move into a public room until it passes:

- privacy and credential review;
- room classification;
- authority and status labeling;
- incoming-reference review;
- public-link compatibility review;
- content digest and rollback recording.

No generated process may decide that personal, evidentiary, or legacy content is safe to publish.
