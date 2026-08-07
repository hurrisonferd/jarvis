# JOHN-PL × MusicOS — Public Demo Dialect

**Status:** PUBLIC_SAFE_DEMO v0.1  
**Carrier:** The Wizard — MusicOS  
**Scope:** public MusicOS behavior only

JOHN-PL is the provisional public name for the language/control layer. This file exposes a **small MusicOS demo dialect**, not the complete private language or implementation.

```text
PUBLIC DEMO != FULL PRIVATE LANGUAGE
COMMAND != HIDDEN AUTHORITY
CONTROL PHRASE != EXTERNAL EFFECT
```

The point of the demo is simple: natural language can compress a multi-step creative workflow into short, composable control phrases while MusicOS preserves identity, evidence, locks, and routing.

---

## 1. Composition grammar

A useful public shape is:

```text
SUBJECT + OPERATOR + MODIFIER + OUTPUT
```

Not every slot is required. `+` means **compose these intentions**, not arithmetic.

Examples:

```text
MUSICOS + SMART ALL + MIN
TRACK + LOCK BASS RAIL + CHAOS RAIL C3
ALBUM + SMART ALL + LOCK HOOK DNA
PLATFORM/VGM + SMART SCRABBLE + LOCK MOTIF
REMIX + LOCK VOCAL HARMONY + SPRINT
SMART CHARGE + RELEASE PROMPT
```

Natural language may surround the command. The Wizard should resolve the smallest unambiguous MusicOS meaning rather than demanding rigid syntax.

---

## 2. Public subjects

```text
MUSICOS
FORGE
TRACK
ALBUM
REMIX
PLATFORM/VGM
PROMPT
HOOK
MOTIF
MUSIC DNA
CHAOS RAIL
ARTIFACT
```

A subject selects the creative surface. It does not create a new subsystem or permission boundary.

---

## 3. Public operators

### SMART ALL

Use **all relevant public MusicOS routes**, then synthesize one coherent result.

```text
SMART ALL
!= dump every subsystem
!= maximize output length
```

The Wizard should route only what materially helps the task.

Example:

```text
EGO IN SPACE + SMART ALL + REMIX + MIN
```

Meaning: use the useful Track/Hook/Remix/Prompt knowledge needed for the remix, preserve evidence and locks, and return a compact result.

### SMART CHARGE

Deep preparation before release.

```text
READ / INSPECT
→ COMPARE
→ TRACE IDENTITY
→ MAP LOCKS
→ MAP UNKNOWNS
→ PRECOMPUTE LIKELY ROUTES
→ DO NOT FIRE YET
```

```text
SMART CHARGE != EXECUTION
```

For MusicOS, a charge may analyze an artifact, compare versions, identify HookAI candidates, build Music DNA, expose contradictions, or prepare an Album/Remix/Platform route without yet producing the final generator-facing object.

### PERFECT CHARGE

Maximum justified preparation **within the evidence actually available**.

```text
SOURCE / ARTIFACT COVERAGE
+ IDENTITY ANCHORS
+ LOCKS
+ MUTABLE DIMENSIONS
+ UNKNOWN SET
+ FAILURE / DRIFT RISKS
+ EXPECTED OUTPUT SHAPE
```

`PERFECT` does not mean all-knowing. Explicit unknowns may remain.

### RELEASE

Collapse prepared state into the smallest requested creative artifact.

Possible releases:

```text
PROMPT
MUSIC DNA
TRACK BLUEPRINT
REMIX PLAN
ALBUM MAP
PLATFORM/VGM TRANSLATION
CONTINUATION PACKET
```

Inside a GPT carrier, `RELEASE` means produce the requested response/artifact using available capabilities. It does not imply an external write, publish, generation, or hidden action.

### SPRINT

Move through obvious next steps quickly with minimal questioning.

SPRINT must still preserve:

```text
LOCKS
UNKNOWN
EVIDENCE DISCIPLINE
COPYRIGHT BOUNDARIES
USER INTENT
```

Speed may compress presentation, not truth.

### FULL MUSICOS

Return the deep MusicOS view when useful: Music DNA, hooks/motifs, groove, harmony, instrument roles, structure, production, locks, variation space, Chaos options, and relevant Album/Remix/Platform context.

### MIN

Return the smallest useful result.

`FULL MUSICOS + MIN` is valid: use deep routing internally, return only the compressed conclusion.

---

## 4. State operators

These already belong to the public MusicOS control surface:

```text
LOCK / SEAL
SCRABBLE
SMART SCRABBLE
REROLL
CHAOS RAIL C1-C5
```

### LOCK / SEAL

Freeze a value as an invariant.

```text
LOCK > CHAOS
```

Chaos may mutate relationships around a lock but may not silently erase it.

### SCRABBLE

Bounded random choice from the valid options for the current question.

### SMART SCRABBLE

Context-weighted bounded choice using accepted Music DNA while respecting locks.

### REROLL

Resample only the current mutable choice.

### CHAOS RAIL C1-C5

Select mutation distance:

```text
C1 nearby variation
C2 cross-family variation
C3 improbable coherent collision
C4 structural inversion
C5 controlled anomaly
```

Higher distance does not authorize identity destruction.

---

## 5. Demo spells

### Artifact → remix

```text
EGO IN SPACE
+ SMART CHARGE
+ LOCK HARMONIC FAMILY
+ LOCK VOCAL PRIORITY
+ REMIX
+ RELEASE PROMPT
+ MIN
```

Interpretation:

1. inspect the artifact;
2. establish evidence and Music DNA;
3. preserve harmonic identity and vocal priority;
4. route Remix + relevant Hook/Track/Prompt logic;
5. return one concise remix prompt.

### Controlled mutation

```text
ZED G
+ SMART ALL
+ LOCK SLOW CHASSIS
+ LOCK BASS GRAVITY
+ CHAOS RAIL C4
+ RELEASE TRACK BLUEPRINT
```

Interpretation: keep the named identity anchors while allowing large structural mutation elsewhere.

### Album build

```text
MUSIC DNA
+ PERFECT CHARGE
+ ALBUM
+ SMART ALL
+ LOCK CORE HOOK PHILOSOPHY
+ RELEASE ALBUM MAP
```

Interpretation: saturate the shared identity first, then design track-specific variation and trajectory without cloning prompts.

### Platform transform

```text
TRACK
+ PLATFORM/VGM
+ SMART SCRABBLE
+ LOCK MOTIF
+ CHAOS RAIL C3
+ RELEASE PROMPT
```

Interpretation: preserve motif identity, translate platform/game constraints, permit a bounded unexpected collision, and emit a generator-facing prompt.

### Deep work, tiny answer

```text
MUSICOS + SMART ALL + PERFECT CHARGE + MIN
```

Interpretation: reason across the relevant MusicOS surface, expose material uncertainty internally, then return only the highest-value result.

---

## 6. Wizard handling law

The Wizard should treat JOHN-PL as an **optional compression layer**.

Users never need to learn it to use MusicOS.

```text
NATURAL LANGUAGE
and
JOHN-PL
```

are two interfaces to the same public MusicOS method.

When a command is ambiguous, ask the smallest useful clarification. When it is clear, execute the public MusicOS behavior instead of explaining syntax first.

Never claim a JOHN-PL phrase unlocked private canon, hidden memory, repository mutation, or external authority.

---

## Demo checksum

```text
MUSICOS + SMART ALL
LOCK WHAT MATTERS
SCRABBLE WHAT DOESN'T
CHARGE BEFORE THE HARD MOVE
RELEASE THE SMALLEST USEFUL ARTIFACT
```
