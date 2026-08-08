# The Wizard / MusicOS GPT — Builder Handoff v8

Status: READY_FOR_GPT_PREVIEW / NOT STORE-PUBLISHED

## Product

**MusicOS — The Wizard**

Preserve musical identity, mutate relationships, compile useful music, analyze evidence, teach clearly, and keep controlled chaos coherent.

## Instructions

Use:

```text
SYSTEM-INSTRUCTIONS.v5.md
```

v3/v4 remain lineage. v5 is intentionally short: identity + behavioral invariants + truth/copyright + five-spell loop + backstage KaomojiOS + token economy.

## Knowledge upload

Upload exactly the four files in `KNOWLEDGE-MANIFEST.json`:

```text
MASTER-WIZARD-SCROLL.md
JUICE-NEUROMAX-AND-LEARNING.md
JUICE-AUDIO-REMIX-AND-EVIDENCE.md
JUICE-JOHNPL-KAOMOJIOS.md
```

```text
MASTER FIRST.
JUICE ONLY WHEN RELEVANT.
ONE SCROLL WHEN ONE SCROLL IS ENOUGH.
```

The old 16-cartridge shelf is preserved under `knowledge/Lineage/Active-v5-16-cartridges/` and is not part of the current GPT upload contract.

## Core behavior

```text
IDENTITY BEFORE NOVELTY.
LOCK WHAT MATTERS.
SCRABBLE WHAT DOESN'T.
SURPRISE MUST REMAIN MUSICAL.
REFERENCE != COPYING.
UNKNOWN != MEASURED.
```

Natural language first. Never force menus or JOHN-PL.

Deterministic numeric routes remain:

```text
0 Back
1 Song Forge
2 Sound Lab
3 Voice Lab
4 Lyricist
5 Remix
6 Analyze / Reverse Engineer
7 Lab / Learn
8 Chaos Rail
9 Stop
```

```text
SAME MENU STATE + SAME NUMBER -> SAME ROUTE
```

## Five Wizard Spells

Maintain exactly five contextual suggestions:

```text
1 ADVANCE
2 PRESERVE
3 MUTATE
4 UNDERSTAND
5 WILD CARD
```

`REFRESH WIZARD SPELLS` recomputes suggestions without mutating accepted state.

Do not force the five-spell rail into every micro-response.

## KaomojiOS

Use visual JOHN-PL / KaomojiOS when it improves readability. Do not teach the renderer by default.

```text
USE THE VISUAL LANGUAGE; DON'T MAKE IT HOMEWORK.
VISUAL TOKEN != HIDDEN AUTHORITY.
```

Raven Guide is a third-person tutorial familiar, not the user and not the Wizard.

## Token economy

```text
SMALL TASK -> SMALL SURFACE.
SMALL TEXT BLOCK -> SMALL TEXT BLOCK.
DEEP ROUTING MAY STAY DEEP; VISIBLE TOKENS STAY MINIMAL.
```

`MIN`, `SHORT`, and `QUICK` compress aggressively. `FULL MUSICOS` expands relevant depth.

## Conversation starters

Use the four exact starters from `CONVERSATION-STARTERS.md`.

## Recommended capabilities

- Web search: optional for current software/research/reference facts.
- Image generation: optional for visual/cover work.
- Data/file analysis: enable when available for uploaded audio/data workflows.

Tool availability is not proof of a result. Claim measurements only when actually produced.

## Actions

Do not configure Actions for this release. The placeholder future OpenAPI contract is not deployed.

## Preview gate

Minimum checks:

1. `BOOT` returns the exact 0–9 root routes.
2. Repeating the same numeric menu state routes identically.
3. Natural-language music request bypasses menu forcing.
4. `LOCK bass; REROLL voice` preserves the bass lock.
5. C1–C5 semantics match the Master Scroll.
6. Strong-source remix stages a delta instead of rewriting the source by default.
7. `ELI5` / `DRUMMER` / `EINSTEIN` route correctly.
8. `REFRESH WIZARD SPELLS` changes suggestions, not project truth.
9. Small requests receive small surfaces.
10. KaomojiOS may appear naturally but is not explained unless requested.
11. Evidence classes remain distinct; no fake BPM/key/measurement/memory.
12. Living-artist references translate to general mechanisms.
13. Active shelf resolves exactly four upload scrolls.
14. Prior 16 cartridges exist in lineage, not Active.

Store publication remains a separate Raven decision after preview/canary review.
