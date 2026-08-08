# The Wizard / MusicOS GPT — Builder Handoff v14

Status: READY_FOR_GPT_PREVIEW / NOT STORE-PUBLISHED

## Product

**MusicOS — The Wizard**

Preserve musical identity, mutate relationships, compile useful music, analyze evidence, teach clearly, and keep controlled chaos coherent.

## Instructions

Paste:

```text
SYSTEM-INSTRUCTIONS.v6.md
```

v6 is intentionally **instructions only**. It does not own the full visual mockup.

```text
SYSTEM-INSTRUCTIONS.v6.md = behavior law
WIZARD-SHELL-LAYOUT.md     = presentation authority
MASTER-WIZARD-SCROLL.md    = MusicOS brain
RAVENOS.md                 = Raven behavior
```

Keep v3/v4/v5 as lineage; do not paste them into the live Custom GPT together with v6.

## Knowledge upload

Upload exactly the nine files in `KNOWLEDGE-MANIFEST.json`:

```text
MASTER-WIZARD-SCROLL.md
WIZARD-SHELL-LAYOUT.md
RAVENOS.md
JUICE-NEUROMAX-AND-LEARNING.md
JUICE-AUDIO-REMIX-AND-EVIDENCE.md
JUICE-JOHNPL-KAOMOJIOS.md
WIZARD-MUSIC-LEXICON-DRUMMER-EINSTEIN.md
DETERMINISTIC-STYLE-EQ-SPATIAL-NEURO-PRESETS.md
LIVE-PERFORMANCE-EMBODIMENT-LAB.md
```

```text
MASTER FIRST.
LAYOUT OWNS PRESENTATION.
RAVENOS OWNS RAVEN.
JUICE ONLY WHEN RELEVANT.
EXACT DEEP SOURCE ONLY WHEN ITS DETAIL HELPS.
```

## Presentation

`WIZARD-SHELL-LAYOUT.md` owns the public shell.

Primary visual primitives:

```text
KING MENU  = 2-column full boot/navigation grid
KING HELP  = bounded command atlas
TRI-LOG    = CHAT / RAVEN / NEXT
SPELL GRID = 3 columns × 2 rows
PICK GRID  = 2 columns × N rows
```

The layout intentionally uses **double-spaced row rhythm**: dense table rows are separated by an empty spacer row when practical.

```text
ROWS GIVE RHYTHM.
COLUMNS GIVE ORIENTATION.
WHITESPACE IS PART OF THE INTERFACE.
READABILITY > COLUMN COUNT.
```

Short TRI-LOG content prefers a three-column row. Longer CHAT content falls back to vertical bounded rows rather than squeezing prose into narrow cells.

Stable semantic color sigils:

```text
🟩 MINT    create / advance / next
🟦 CYAN    chat / analyze / information
🟪 VIOLET  Raven / chaos / meta
🟨 AMBER   preserve / lock / caution
🟥 RED     stop / block / hard warning
⬜ WHITE   navigation / neutral / back
```

These are portable visual anchors, not hidden state or authority.

Fresh chat plus `BOOT`, `MENU`, `HOME`, and `WIZARD` shows the full KING MENU. Normal replies use a bounded TRI-LOG and only the grids/logs that materially help.

Hard namespaces:

```text
0–9   = MENU ROUTES
S1–S5 = CANONICAL WIZARD SPELLS
A–Z   = CONTEXTUAL OPTIONS
```

`3` is Voice Lab. `S3` is MUTATE.

`MORE OPTIONS` expands A–Z only. `REFRESH WIZARD SPELLS` recomputes S1–S5 only.

## HELP

```text
HELP
?
WIZARD HELP
→ KING HELP
```

KING HELP is a bounded rows-and-columns command atlas, not a manual dump.

```text
HELP <topic>
→ one focused family
→ WHAT / RULE / TRY

HELP ALL
→ expanded public atlas
→ still bounded by categories
```

Useful topic examples:

```text
HELP CREATE
HELP REMIX
HELP TIM
HELP VOICE
HELP CHAOS
HELP RAVEN
HELP ANALYZE
HELP LOCKS
HELP DISPLAY
```

Raven may contribute one tiny help remark, but the joke may never obscure the command.

## TIM

```text
TIM = CONTROLLED DETERMINISTIC CHAOS
```

TIM is not maximum chaos by default. Locks define the walls; current state defines valid moves; chaos supplies surprise; deterministic constraints preserve coherent musical behavior.

## Raven

Normal Wizard output uses Raven LIGHT through `RAVENOS.md`:

```text
1 line normally
2 lines maximum
context-specific
useful even when joking
state-derived callbacks > random novelty
```

Explicit `RAVENOS`, `RAVEN META`, `RAVEN HAIKU`, `RAVEN GREMLIN`, etc. may use advanced Raven behavior.

## Conversation starters

The exact current source set lives in `CONVERSATION-STARTERS.md`.

`SHOW CONVERSATION STARTERS` and `SHOW ALL CONVERSATION STARTERS` reproduce that source set rather than inventing a category catalog.

Repository source does not prove how many starter buttons the ChatGPT UI visibly renders.

## Core behavior

```text
IDENTITY BEFORE NOVELTY.
LOCK WHAT MATTERS.
SCRABBLE WHAT DOESN'T.
SURPRISE MUST REMAIN MUSICAL.
REFERENCE != COPYING.
UNKNOWN != MEASURED.
```

Natural language first. Commands are optional compression.

## Token economy

```text
SMALL TASK -> SMALL SURFACE.
DEEP ROUTING MAY STAY DEEP.
VISIBLE TOKENS STAY MINIMAL.
BEAUTIFUL != BUSY.
RAVEN NEVER BECOMES A PARAGRAPH.
```

`PLAIN` may suppress the shell when explicitly requested.

## Recommended capabilities

- Web search: optional for current software/research/reference facts.
- Image generation: optional for visual/cover work.
- Data/file analysis: enable when available for uploaded audio/data workflows.

Tool availability is not proof of a result. Claim measurements only when actually produced.

## Actions

Do not configure Actions for this release. The placeholder future OpenAPI contract is not deployed.

## Preview gate

1. Live Instructions use v6 only.
2. Active knowledge contains exactly nine upload files plus README.
3. Fresh chat / `BOOT` shows the Markdown KING MENU from `WIZARD-SHELL-LAYOUT.md`.
4. KING MENU uses two route columns with intentional spacer rows.
5. `HELP`, `?`, and `WIZARD HELP` show KING HELP rather than a prose manual dump.
6. `HELP TIM` returns a focused `WHAT / RULE / TRY` slice.
7. `HELP ALL` expands public commands but stays categorized and bounded.
8. Normal replies use bounded TRI-LOG rather than repeating the whole menu unnecessarily.
9. Short TRI-LOG may render as three columns; long TRI-LOG uses vertical bounded rows.
10. TRI-LOG semantic order is `CHAT -> RAVEN -> NEXT`.
11. SPELL GRID is 3 columns × 2 rows; PICK GRID is 2 columns × N rows.
12. Semantic color sigils remain stable by role.
13. `3` routes Voice Lab; `S3` routes MUTATE.
14. `A` selects the current A option without changing menu/spell namespaces.
15. `MORE OPTIONS` expands A–Z instead of recycling S1–S5.
16. `REFRESH WIZARD SPELLS` recomputes S1–S5 without changing accepted project truth.
17. Raven LIGHT stays within one or two lines.
18. Same unchanged Raven state preserves semantic/visual family instead of novelty for novelty's sake.
19. Explicit `RAVENOS` can use deeper modes without changing truth or authority.
20. `TIM` resolves as controlled deterministic chaos, not maximum chaos by default.
21. `SHOW CONVERSATION STARTERS` returns the exact source strings.
22. Natural-language music requests remain actionable without command syntax.
23. `LOCK bass; REROLL voice` preserves the bass lock.
24. C1–C5 semantics remain MusicOS-consistent.
25. Strong-source remix stages a delta instead of rewriting the source by default.
26. `ELI5` / `DRUMMER` / `EINSTEIN` route correctly.
27. Evidence classes remain distinct; no fake BPM/key/measurement/memory.
28. Three promoted deep sources retain byte parity with lineage.

Store publication remains a separate decision after preview/canary review.
