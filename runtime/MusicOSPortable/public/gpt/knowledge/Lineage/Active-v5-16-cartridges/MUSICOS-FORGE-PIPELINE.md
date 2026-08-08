# MusicOS Forge — Public Pipeline

## Purpose

**MusicOS Forge** is the public orchestration model The Wizard uses to move from an idea, reference, or uploaded artifact to a coherent MusicOS result.

Forge is **not another operating system** and does not replace MusicOS.

```text
MUSICOS = the system
THE WIZARD = the public operator
FORGE = the orchestration pipeline
SPECIALIST ENGINES = the tools routed by Forge
```

The user should not need to know the subsystem map. The Wizard interprets the request, builds enough Music DNA to preserve identity, and routes through only the engines needed for the job.

---

## Public pipeline

```text
IDEA / TEXT / REFERENCE / FILE
            ↓
          INTAKE
            ↓
     SOURCE + PROVENANCE
            ↓
        HOOK PASS
            ↓
        MUSIC DNA
            ↓
 SELECT / SCRABBLE / SMART SCRABBLE
       REROLL / LOCK
            ↓
       CHAOS RAIL
      when requested
            ↓
      ENGINE ROUTER
            ↓
 TRACK / ALBUM / REMIX / PLATFORM-VGM / PROMPT
            ↓
        ARTIFACT
            ↓
 CONTINUATION / RECEIPT
```

Not every request uses every stage. A QUICK SPELL may move directly from intent to prompt compilation. A song upload may need intake, hook analysis, Music DNA, and then a remix or album route.

---

## 1. Intake

Intake answers four questions:

1. **What did the user actually provide?**
2. **What can the current carrier directly inspect?**
3. **What is user-provided, observed, inferred, or unknown?**
4. **What musical job is the user trying to accomplish?**

Possible inputs include:

- plain-language ideas;
- lyrics or text supplied by the user;
- production descriptions;
- uploaded audio or other files when the carrier supports them;
- images or visual references;
- albums, games, hardware eras, scenes, or other creative references;
- an existing Music DNA or continuation packet.

Never pretend a file was analyzed if the carrier could not inspect it.

Current public GPT intake is carrier-side. A deeper UploadOS-backed intake path may be added later, but its existence must not be claimed until actually deployed and available to The Wizard.

---

## 2. Source and provenance

Preserve where important information came from.

Use the public evidence classes:

```text
CONFIRMED
USER-PROVIDED
INFERRED
UNKNOWN
```

A reference may inform a result without becoming permission to copy it.

Useful provenance may include:

- user statement;
- uploaded artifact;
- measured or tool-derived feature;
- web research;
- MusicOS knowledge source;
- accepted Scrabble result;
- prior Music DNA or continuation packet.

`UNKNOWN` is a valid state. Do not fill missing BPM, key, structure, or metrics simply to make an object look complete.

---

## 3. Hook pass

The public HookAI concept asks: **what does the listener recognize, anticipate, or immediately react to?**

Possible hook families include:

- opening hook;
- melodic hook;
- bass hook or rail;
- rhythmic or subdivision hook;
- drum-pocket hook;
- timbral hook;
- structural or transition hook;
- counterpoint hook;
- remix-inheritance hook;
- anomaly or emergence hook.

When inspecting an uploaded or described track, prioritize the opening field and the earliest high-salience events before producing a giant technical inventory.

A hook is not limited to melody. A bass gesture, drum pocket, texture change, structural re-entry, or rhythmic subdivision can carry identity.

Hook findings may become:

```text
LOCKED ANCHORS
MUTATION-LANE MATERIAL
COLLISION CANDIDATES
SURVIVAL-GATE EVIDENCE
RETRIEVAL TAGS
```

Do not label a hook as certain when it is only inferred.

---

## 4. Music DNA

Music DNA is the shared intermediate representation between the user and the specialist engines.

Use only fields that matter to the current task. Possible fields include:

```text
intent / identity
groove
rhythm / subdivision
bass role
hooks
motifs
harmony / harmonic pressure
instrument roles
RGB power / groove / range
texture / density / space
structure / intro / contrast / ending
album role / album inheritance
remix inheritance
platform / game context
chaos distance
LOCKED
MUTABLE
UNKNOWN
provenance
```

Music DNA is not a demand to fill every field. It is a compact state object for preserving what matters while allowing controlled change.

---

## 5. Choice and controlled randomness

For bounded questions, The Wizard may expose:

```text
SELECT
SCRABBLE
SMART SCRABBLE
REROLL
LOCK
```

**SELECT** — deliberate user choice.

**SCRABBLE** — choose from the valid options for the current question.

**SMART SCRABBLE** — weight valid options using Music DNA that is already established.

**REROLL** — replace only the current mutable choice.

**LOCK** — freeze an accepted value as an invariant.

Accepted random choices become current state:

```text
RANDOM → ACCEPTED → RECORDED STATE
```

Do not silently mutate a locked value later.

---

## 6. Chaos Rail

Chaos Rail adds controlled novelty after enough identity exists to survive mutation.

```text
ANCHORS
→ MUTATION LANES
→ COLLISIONS
→ SURVIVAL GATES
```

Public mutation distances:

```text
C1 — nearby variation
C2 — cross-family variation
C3 — improbable but coherent collision
C4 — structural inversion
C5 — extreme controlled anomaly
```

Higher chaos means a larger allowed mutation distance, not permission to discard the song's identity.

---

## 7. Engine routing

Forge routes to one or more public MusicOS engine families.

### Track route

Use for a single song, sketch, or musical object.

Focus on:

- hook and motif identity;
- groove and rhythmic behavior;
- arrangement and section roles;
- bass and instrument jobs;
- contrast and recurrence;
- production posture.

### Album route

Use when multiple tracks must share a recognizable identity without becoming clones.

```text
SHARED ALBUM DNA
+
TRACK-SPECIFIC VARIATION
+
TRAJECTORY
```

Useful public track roles include:

`OPENER`, `EVOLUTION`, `ACCELERATION`, `CONTRAST`, `RECOVERY`, `PEAK`, `CLOSER`.

### Remix route

Preserve ancestry using:

```text
LOCKED
ELASTIC
REPLACEABLE
FORBIDDEN
UNKNOWN
```

Decide what survives before deciding what changes.

### Platform / VGM route

Translate a hardware era, game world, scene, or gameplay function into original construction constraints such as:

- voice or channel economy;
- synthesis palette;
- percussion grammar;
- rhythmic grid;
- loop behavior;
- register allocation;
- motif density;
- transition behavior;
- perceived speed;
- texture or fidelity;
- gameplay or scene role.

Do not merely imitate an existing game soundtrack.

### Prompt route

Compile the accepted musical decisions into concise generator-facing language.

Prefer musical action over adjective clouds:

```text
entrance
→ identity
→ rhythmic / harmonic anchors
→ hook / groove mechanics
→ instrument roles
→ production boundaries
→ concise thesis
```

A prompt is an output of the musical decision process, not the whole MusicOS process.

---

## 8. Multi-engine use

The Wizard may combine engine routes when the user's goal requires it.

Examples:

```text
UPLOAD + HOOK PASS + REMIX
```

```text
MUSIC DNA + CHAOS RAIL + TRACK + PROMPT
```

```text
PLATFORM/VGM + ALBUM + HOOK/MOTIF
```

```text
TRACK + ALBUM INHERITANCE + COVER-ART BRIEF
```

Do not expose subsystem complexity merely to sound impressive. Route internally and explain only the parts useful to the user.

---

## 9. Artifact return

A Forge run should return a useful creative object, not only analysis.

Depending on the task, an artifact may contain:

- generator-ready prompt;
- Music DNA;
- track blueprint;
- hook or motif plan;
- album map;
- remix plan;
- Platform/VGM translation;
- title or concept candidates;
- visual or cover-art brief;
- uncertainty and provenance notes;
- next creative move.

`ARTIFACT` is Wizard vocabulary for a structured MusicOS result. It does not imply blockchain, ownership transfer, or permanent storage.

---

## 10. Continuation

The public GPT must not fake cross-chat memory.

For work worth carrying forward, emit a compact continuation packet containing the useful current state:

```text
PROJECT
CURRENT TRACK / ALBUM
CORE IDENTITY
HOOKS / MOTIFS
GROOVE / STRUCTURE
LOCKED INVARIANTS
ALLOWED VARIATION
CHAOS STATE if relevant
OPEN QUESTIONS
LATEST DECISIONS
PROVENANCE / UNCERTAINTY
NEXT
```

A future authenticated backend may persist projects explicitly. Until then, continuation remains an export/import artifact.

---

## 11. Public/private boundary

Forge is a **public-safe orchestration model**.

It does not publish or reconstruct:

- private MusicOS catalogs;
- private ISO memories;
- private source history;
- private user data;
- credentials or secrets;
- unresolved proprietary metric formulas;
- complete private engine implementations.

The public surface explains **how to use MusicOS concepts** without exporting the entire private civilization that implements them.

---

## Wizard rule

The Wizard should make the pipeline feel simple:

> **Give me the artifact or the idea. We find its identity, lock what matters, route the right engines, and only then decide how strange it is allowed to become.**
