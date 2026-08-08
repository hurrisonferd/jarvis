# MusicOS — Deterministic Style, EQ, Spatial, and Neuro-Acoustic Presets

```text
PRODUCT: MusicOS — The Wizard
CLASS: PUBLIC KNOWLEDGE CARTRIDGE
PURPOSE: stable meanings for recurring remix/style/EQ/spatial prompt language
AUTHORITY: RAVEN
PRIVATE_RUNTIME_EXPORT: false
STATUS: PUBLIC PRESET LANGUAGE
```

## 1. Why presets exist

A recurring style word should not mean a different pile of adjectives every time.

```text
SAME PRESET NAME
+ SAME LOCKS
+ SAME SOURCE STATE
→ SAME TARGET MUTATION FAMILY
```

The generator may still vary. The **Wizard's interpretation** must not.

Each preset is a deterministic semantic object:

```text
PRESET
├─ MUSICAL INTENT
├─ LOCKS
├─ RHYTHM / TIME
├─ EQ / REGISTER TARGET
├─ SPACE / WIDTH TARGET
├─ MOTION TARGET
├─ DYNAMICS / CONTRAST
├─ GENERATOR WORDING
├─ OPTIONAL DSP TRANSLATION
├─ NEURO / PERCEPTION BRIDGE
└─ CLAIM BOUNDARY
```

### Generator preset != literal DSP

When working only through text generation, EQ/width values are **mix-direction targets**, not claims that exact filters were applied.

When a real audio/DSP tool is available, the Wizard may translate the same semantic preset into actual filter, panning, delay, modulation, and automation parameters and then measure the result.

```text
PROMPT EQ TARGET != MEASURED EQ CURVE
PROMPT SPATIAL TARGET != MEASURED SPATIAL RESULT
```

---

# 2. Common deterministic preset vocabulary

## `LIVE PERFORMANCE`

### ELI5
The song stays the same kid, but now it is playing in a room full of people.

### Deterministic target

```text
COMPOSITIONAL RAIL     LOCK
PULSE FAMILY           LOCK
PERFORMANCE HUMANITY   UP
ROLE HANDOFFS          UP
ROOM / CROWD FIELD     UP WHEN USEFUL
DYNAMIC BREATH         UP
ENTRY VARIATION        ALLOWED
WIDTH                  ELASTIC
EVENT ACTIVITY         ELASTIC
```

Hard law:

```text
LIVE PERFORMANCE != MORE EVENTS
LIVE PERFORMANCE != LESS EVENTS
ACTIVITY IS ELASTIC
```

### EQ / mix target

- preserve centered low-end/body unless the source says otherwise;
- open vocal/instrument presence rather than globally brightening everything;
- allow upper-field width to grow more than sub width;
- keep transients articulate rather than making the entire mix louder;
- use room/early-reflection cues without washing the source rail.

### Prompt wording

> live performance embodiment, responsive band interplay, audible room and crowd energy, wider upper performance field, dynamic push-and-pull, source groove and harmonic identity preserved

---

## `TEMPORAL`

### ELI5
The magic is in **when** things happen.

### Deterministic target

```text
TIME RELATIONSHIPS      PRIMARY
PITCH IDENTITY          LOCK / LOW MUTATION
ENTRY / EXIT            ACTIVE
DELAY / ECHO RHYTHM     ACTIVE
MICROTIMING             ACTIVE
DROPOUT / RE-ENTRY      ACTIVE
WIDTH                   SECONDARY
```

### Musical meaning

Temporal is not just "add delay." It prioritizes timing relationships:

- anticipation;
- lateness;
- echo placement;
- call/response latency;
- subdivisions;
- phrase offsets;
- dropout duration;
- snap-back timing.

### Prompt wording

> temporal arrangement, audible timing relationships, staggered entries, rhythmic echoes, precise dropout and re-entry, microtiming contrast around a stable pulse

---

## `SPATIAL`

### ELI5
The song has a stage. Not everybody stands in the middle.

### Deterministic target

```text
SUB / BASS BODY         CENTERED
PRIMARY RAIL            CENTER OR NEAR-CENTER
UPPER DETAIL            WIDER
COUNTERLINES            POSITIONED
MOTION                   BOUNDED
DEPTH                    LAYERED
MONO COMPATIBILITY       PRESERVE WHEN DSP EXISTS
```

### Spatial roles

```text
CENTER      = gravity / rail / lead anchor
NEAR        = body / supporting rhythm
SIDES       = response / air / harmony / ornament
MOTION      = temporary attention movement
DEPTH       = near/far staging
```

### Prompt wording

> spatially staged mix, centered bass and drum gravity, upper details and harmonies opening toward the sides, clear front-to-back depth, bounded directional movement rather than constant swirl

---

## `SURROUND SOUND`

### ELI5
Spatial, but the room wraps around you.

### Deterministic target

```text
CENTER ANCHOR           PRESERVE
FRONT / SIDE / REAR     DISTINCT ROLES
MOTION                   EVENT-BASED
AMBIENCE                 ENVELOPING
LOW END                  NON-DIFFUSE BY DEFAULT
```

For stereo-only generation, translate surround into **envelopment cues** rather than claiming actual multichannel output.

### Prompt wording

> enveloping surround-style staging, stable center gravity, responsive side and rear-like ambience cues, selective moving details, spacious but readable localization

```text
STEREO SURROUND-LIKE CUES != VERIFIED MULTICHANNEL SURROUND
```

---

## `AMBIENT`

### ELI5
The room itself becomes an instrument.

### Deterministic target

```text
ATTACK SHARPNESS         DOWN / SELECTIVE
TAIL LENGTH              UP
DEPTH                    UP
NEGATIVE SPACE           UP
EVENT RATE               DOWN OR SPARSE
TONAL CONTINUITY         UP
TRANSIENT FOCUS          SELECTIVE
```

Ambient does not mean "everything gets reverb."

Use:

- long but role-specific tails;
- slow movement;
- spectral breathing;
- sparse landmarks;
- depth layers;
- preserved low-frequency clarity.

### Prompt wording

> ambient depth field with long selective tails, slow spectral motion, sparse landmarks, generous negative space, clear low-end floor, atmosphere behaving as an active musical layer

---

## `FULL CONTRAST`

### ELI5
Make the differences obvious enough that your body notices the switch.

### Deterministic target

Contrast across **several independent axes**, not maximum loudness.

```text
WIDE      ↔ NARROW
DENSE     ↔ EMPTY
CENTER    ↔ SIDES
DRY       ↔ DEEP
LOW       ↔ HIGH
STRAIGHT  ↔ TUPLET
SOLO      ↔ ENSEMBLE
STILL     ↔ MOVING
BODY      ↔ AIR
```

At least one identity rail remains stable across the contrast.

### Prompt wording

> full-contrast arrangement with unmistakable alternation between centered body and wide air, dry and deep space, dense and sparse pockets, straight and tuplet-inflected rhythm, while the source hook and groove rail remain recognizable

---

# 3. Bilateral / EMDR-inspired spatial motion

## `BILATERAL ALTERNATION`

### ELI5
A sound says "left," then "right," then "left," like musical ping-pong.

### Musical target

```text
LEFT EVENT
→ RIGHT RESPONSE
→ CENTER RETURN or NEW PAIR
```

Use alternating lateral attention as **composition**, not an always-on panner.

Good carriers:

- percussion punctuation;
- short guitar/synth answers;
- backing vocals;
- micro-fills;
- room/crowd gestures;
- upper-register ornaments.

Keep bass/sub and primary pulse comparatively stable unless deliberate instability is the goal.

## `EMDR-INSPIRED BILATERAL`

This label means **creative inspiration from alternating bilateral sensory presentation**. It does not mean the music is EMDR therapy.

```text
EMDR-INSPIRED AUDIO MOTION
!= EMDR TREATMENT
!= PTSD TREATMENT CLAIM
!= PROVEN THERAPEUTIC EFFECT
```

Research has found that alternating bilateral auditory stimulation can recruit auditory, attention/salience, memory, and emotional-processing networks in experimental contexts. The therapeutic mechanism and the contribution of bilateral stimulation within full EMDR treatment remain more complex than "left-right audio heals trauma."

### Prompt wording

> bounded alternating bilateral auditory motion, short left-right response events around a stable center, salient but nonconstant lateral handoffs, center returns preserving groove and orientation

---

# 4. `SCHUMANN-SALIENT` — evidence-safe creative preset

### ELI5
7.83 times each second is too low to hear as a normal musical note, so if we use it in audio we make something **move** at that speed instead.

The Earth's fundamental Schumann resonance is an electromagnetic phenomenon near 7.8 Hz. A music generator prompt mentioning it does not literally reproduce that physical phenomenon.

### Deterministic musical translation

When the user explicitly requests `SCHUMANN-SALIENT`, interpret it as:

```text
TARGET MODULATION RATE       ~7.83 Hz
CARRIER                      audible texture / amplitude / filter / pan motion
SALience                      clearly present but not mix-dominating
LOW-END TONE                  NOT REQUIRED
MEDICAL CLAIM                 NONE
EARTH-RESONANCE CLAIM         NONE
```

Possible implementations when real DSP exists:

- amplitude modulation / tremolo near 7.83 Hz;
- filter or spectral modulation near 7.83 Hz;
- subtle pan-width modulation near 7.83 Hz;
- rhythmic texture whose envelope exposes a similar rate.

Because ~7.83 Hz is below ordinary pitch hearing, do not describe it as "the entire song is a 7.83 Hz tone."

### Important bridge

Auditory-perception research has reported entrainment/echo effects in roughly the 6–8 Hz region in some paradigms. That overlap is scientifically interesting, but it does **not** prove a special biological effect of Schumann resonance or make 7.83 Hz uniquely therapeutic.

### Prompt wording

> salient ~7.83 Hz-inspired modulation carried by audible upper texture and spatial motion, clearly perceptible as rhythmic modulation rather than a claimed sub-audible healing tone

---

# 5. `A432` — alternate tuning preset

### ELI5
The orchestra's "A" is set a tiny bit lower.

`432 Hz` in this preset means:

```text
A4 TUNING REFERENCE = 432 Hz
```

It does **not** mean every note is 432 Hz.

Relative to A4=440 Hz, A4=432 is about `-31.77 cents` lower.

### Deterministic target

```text
PITCH REFERENCE            A4 = 432 Hz
TEMPO                      UNCHANGED UNLESS REQUESTED
ARRANGEMENT                UNCHANGED UNLESS REQUESTED
SOURCE IDENTITY            PRESERVE
```

If retuning an existing render with DSP, distinguish pitch retuning from speed/time-stretch changes.

### Evidence bridge

Small clinical/pilot studies have reported differences in anxiety or physiological measures between 432-Hz-tuned and comparison listening conditions, but the evidence base is limited and does not establish a unique healing property of A=432 tuning.

### Prompt wording

> tuning reference A4=432 Hz, with tempo, groove, arrangement, and source identity otherwise preserved

---

# 6. `MICROPOCKET TUPLET SYNCOPATION`

### ELI5
The drummer stays on the road but keeps putting tiny skateboard ramps between the lane markers.

### Deterministic rhythm target

```text
PRIMARY PULSE            STABLE
MAIN GRID                STRAIGHT / LEGIBLE
SYNCOPATION              LIGHT
MICROPOCKETS             SHORT
TUPLET VARIATION         RECURRING BUT BOUNDED
RETURN                    FAST / OBVIOUS
```

Default behavior:

- establish a readable 4/4 or source meter;
- keep the kick/bass rail intelligible;
- let short fills/ornaments use triplet subdivisions;
- occasionally introduce quintuplet or other odd-group color only when it resolves cleanly;
- displace accents more often than the entire pulse;
- return to the source pocket before rhythmic identity is lost.

```text
TUPLET COLOR != CONSTANT POLYRHYTHMIC DENSITY
SYNCOPATION != RANDOM OFF-GRID TIMING
MICROPOCKET != NEW TEMPO
```

### Prompt wording

> stable groove rail with light syncopation, short alternating micropockets, triplet-varied fills and occasional bounded odd-tuplet accents, every displacement snapping cleanly back into the main pocket

---

# 7. Composite preset — `FULL CONTRAST NEURO-SPATIAL`

This is the deterministic combination of the user's recurring family:

```text
LIVE PERFORMANCE
+ TEMPORAL
+ SPATIAL / SURROUND-LIKE
+ AMBIENT DEPTH
+ FULL CONTRAST
+ BILATERAL ALTERNATION
+ OPTIONAL SCHUMANN-SALIENT
+ OPTIONAL A432
+ MICROPOCKET TUPLET SYNCOPATION
```

## Stable role architecture

```text
CENTER
├─ kick / bass gravity
├─ source compositional rail
└─ primary lead anchor

SIDES
├─ responses
├─ harmony blooms
├─ percussion punctuation
└─ upper articulation

DEPTH
├─ room / crowd
├─ ambient tails
└─ distant responses

MOTION
├─ bounded left/right handoffs
├─ temporal echoes
└─ micropocket events
```

## Stable contrast schedule

```text
1. CENTER / DRY / BODY
2. SIDE RESPONSE / AIR
3. TEMPORAL MICROPOCKET
4. AMBIENT OPENING
5. BILATERAL HANDOFF
6. FULL-BODY RETURN
```

Do not mechanically force six sections into every song. This is the **relationship order**, which may happen inside phrases, bars, sections, or an entire arrangement.

## Generator-ready compact version

> live-performance full-contrast embodiment with centered funk-bass and drum gravity, responsive surround-like upper staging, alternating bilateral left-right micro-events around a stable center, temporal dropouts and re-entries, ambient depth only between strong dry anchors, light syncopation with triplet-varied micropockets and occasional bounded odd-tuplet accents, clear role handoffs instead of wall-of-sound stacking, source hook/harmony/groove preserved; optional A4=432 Hz tuning and clearly audible ~7.83 Hz-inspired modulation only when explicitly requested

---

# 8. Preset composition law

Presets combine by **merging dimensions**, not concatenating adjectives.

Example:

```text
SPATIAL
+ AMBIENT
+ BILATERAL
```

should resolve conflicts:

```text
SUB CENTERED
AMBIENCE WIDE/DEEP
BILATERAL EVENTS SHORT AND SALIENT
CONSTANT SWIRL FORBIDDEN
```

If two presets conflict, preserve:

1. explicit user lock;
2. source identity;
3. more specific preset;
4. stable rail;
5. readability.

---

# 9. Evidence levels for neuro-acoustic language

```text
LEVEL A — established musical/acoustic mechanism
rhythm, panning, amplitude modulation, tuning reference, syncopation, spectral balance

LEVEL B — supported perceptual/neurophysiological mechanism with active research
rhythmic entrainment, auditory-motor coupling, temporal prediction, lateralized auditory attention

LEVEL C — preliminary / context-dependent evidence
specific physiological benefits from 432-Hz tuning, particular bilateral-audio effects outside a treatment protocol

LEVEL D — metaphor / creative target only unless separately proven
"healing frequency," "Schumann healing," deterministic medical effects from a music prompt
```

The Wizard may explore all four levels, but must label them differently.

## Checksum

> **PRESET MEANS THE SAME THING TOMORROW. MUSIC CAN BE WEIRD WITHOUT EVIDENCE BECOMING WEIRD.**
