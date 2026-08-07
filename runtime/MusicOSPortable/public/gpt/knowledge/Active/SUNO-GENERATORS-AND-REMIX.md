# MusicOS — Suno Generators and Remix

```text
PRODUCT: MusicOS — The Wizard
CLASS: PUBLIC KNOWLEDGE CARTRIDGE
PURPOSE: bounded generator-facing creation modes
AUTHORITY: RAVEN
PRIVATE_RUNTIME_EXPORT: false
```

These are public Wizard modes, not claims that named private AI subsystems are running.

```text
USER INTENT
→ MUSICOS METHOD
→ GENERATOR MODE
→ PROMPT OBJECT
→ GENERATOR-FACING TRANSLATION
```

Public modes:

```text
SONG FORGE
SOUND LAB
VOICE LAB
LYRICIST
REMIX
```

## Song Forge

Purpose: build a complete song direction or generator-ready packet.

Useful inputs:

```text
CONCEPT
EMOTION / INTENT
GROOVE
TEMPO / PULSE FAMILY
KEY / TONAL COLOR
HOOK / MOTIF
BASS RAIL
INSTRUMENT ROLES
VOCAL ROLE
LYRIC TOPIC
PRODUCTION
CHAOS LEVEL
LOCKS
```

Possible outputs:

```text
MUSIC DNA
SOUND PALETTE
VOICE PROFILE
LYRIC DIRECTION / LYRICS IF REQUESTED
STRUCTURE
GENERATOR PROMPT
OPTIONAL CONTROLLED MUTATION
```

Default prompt order:

```text
ENTRANCE
→ TRACK IDENTITY
→ KEY / TEMPO ANCHOR when useful
→ HOOK / MOTIF / GROOVE / BASS RAIL
→ GROOVE MECHANICS
→ INSTRUMENT ROLES
→ VOCAL ROLE
→ MIX / RESTRAINT
→ TRACK THESIS
→ BPM LOCK when appropriate
```

Strong signal beats maximal detail.

## Sound Lab

Purpose: make a coherent sound-role system, not a random instrument list.

Useful roles:

```text
RAIL
HOOK
COUNTERLINE
PULSE
PUNCTUATION
HARMONIC BED
MOTIF CARRIER
RHYTHMIC ACCENT
TRANSITION
TEXTURAL GLUE
```

Sound object:

```text
SOUND NAME
ROLE
SOURCE FAMILY
ATTACK
BODY
TAIL
REGISTER
MOVEMENT
SPACE
DISTORTION / CLEANLINESS
MIX POSITION
INTERACTION RULE
AVOID
```

Example:

```text
SOUND: Glass Rail Bass
ROLE: RAIL
ATTACK: firm rounded click
BODY: stable low-mid fundamental
TAIL: short and controlled
MOVEMENT: subtle glide at phrase ends
SPACE: nearly dry
MIX: centered
INTERACTION: locks to kick; leaves upper mids open for vocal
AVOID: smeared sub tail and wide chorus
```

A requested palette should usually contain 3–7 members with different jobs.

```text
SOUND PALETTE != DECORATIVE TIMBRE LIST
```

## Voice Lab

Purpose: design an original vocal-character profile.

Dimensions:

```text
REGISTER
RANGE BEHAVIOR
WEIGHT
TEXTURE
BREATH
EDGE
ARTICULATION
VOWEL SHAPE
PHRASING
RHYTHMIC PLACEMENT
DYNAMIC ARC
EMOTIONAL DISTANCE
HARMONY ROLE
ENSEMBLE ROLE
PRODUCTION TREATMENT
```

Useful output:

```text
VOICE PROFILE
REGISTER
WEIGHT / TEXTURE
ARTICULATION
PHRASING
DYNAMICS
HARMONY
SPACE
ROLE
```

Voice Lab creates vocal direction, not a real-person clone. If a user asks for an exact living singer imitation, translate the request into high-level mechanisms such as register, breath, articulation, phrasing, dynamics, harmony behavior, and mix treatment.

## Lyricist

Purpose: create original lyrics that fit MusicDNA and prosody.

Inputs:

```text
CONCEPT
POINT OF VIEW
SPEAKER
EMOTIONAL ARC
HOOK PHRASE
STRUCTURE
SYLLABLE DENSITY
RHYME DENSITY / STYLE
REPETITION
IMAGERY FIELD
DIRECTNESS
LANGUAGE
CLEAN / EXPLICIT PREFERENCE
```

Modes:

```text
HOOK ONLY
SECTION
FULL SONG
LYRIC BLUEPRINT
REWRITE USER-PROVIDED LYRICS
```

Prosody checks:

```text
SYLLABLE COUNT
STRESS PLACEMENT
PHRASE LENGTH
RESTS
VOWEL SUSTAINABILITY
CONSONANT DENSITY
HOOK REPETITION
```

Run an anti-cliche pass. Do not copy protected lyrics or produce exact living-artist lyrical imitation.

## Remix

Purpose: create a descendant while preserving source lineage and selected identity.

First classify:

```text
LOCKED
ELASTIC
REPLACEABLE
FORBIDDEN
UNKNOWN
```

Then:

```text
SOURCE
→ IDENTITY EXTRACTION
→ LOCK SELECTION
→ MUTATION PLAN
→ PROMPT COMPILATION
→ OUTPUT OBSERVATION
→ KEEP / REVISE
```

Distances:

```text
C1 TOUCH-UP
C2 RE-EMBODY
C3 CROSS-FAMILY
C4 INVERSION
C5 ANOMALY
```

### Strong Source / Small Mutation

```text
SOURCE SIGNAL ↑
→ REQUIRED PROMPT REDESCRIPTION ↓
```

When source audio already carries melody, harmony, phrasing, groove, structure, and energy, state the mutation instead of rewriting the source as text.

### Source audio as high-dimensional specification

A source file can already contain much of the compositional specification. The prompt can therefore act primarily as a **delta**.

```text
SOURCE AUDIO = WHAT THE SONG ALREADY KNOWS
PROMPT = WHAT SHOULD CHANGE
```

That does not mean every generator obeys every instruction literally. Render evidence still decides what actually changed.

### Strong Source / Stage Direction

For live/performance/spatial descendants, the prompt can specify a stage rather than a new composition:

```text
CAST
POSITIONS
RESPONSE RULES
CONTRAST SCHEDULE
EMBODIMENT DELTA
```

Useful questions:

- Who occupies the center?
- What expands into the sides?
- Which role enters late?
- Who answers the lead?
- Which layer should narrow or disappear?
- Where should crowd/room information matter?
- What should become more active, and what should remain spacious?
- What must still identify the source immediately?

```text
LIVE PERFORMANCE != ADD EVERYTHING
LIVE PERFORMANCE != FIXED DENSITY CHANGE
ACTIVITY IS ELASTIC
```

A live mutation may increase, decrease, or preserve event density. The deeper target is relationship/embodiment change while the selected compositional rail survives.

### Mutation-vector output

For serious A/B work, summarize the intended or measured delta:

```text
COMPOSITIONAL ANCESTRY
PULSE FAMILY
LOW-END GRAVITY
EVENT ACTIVITY
VOCAL / PRESENCE FIELD
UPPER-FIELD WIDTH
LATERAL MOTION
ROLE CONTRAST
ENTRY BEHAVIOR
DROPOUT / RE-ENTRY
MACRO TRAJECTORY
```

Use `LOCKED`, `ELASTIC`, direction arrows, or evidence labels as appropriate.

## Generator combinations

Modes may compose without gaining new authority:

```text
SONG FORGE + VOICE LAB + LYRICIST
REMIX + SOUND LAB
CHAOS C3 + SOUND LAB + VOICE LOCKED
LYRICIST + EXISTING MUSIC DNA
SOUND LAB + VGM CONSTRAINTS
REMIX + LIVE STAGE DIRECTION
```

## One-click requests

When the user gives a workable but underspecified idea, produce a bounded starter packet instead of forcing an interview.

Example `make something weird` may return:

```text
CORE CONCEPT
SOUND PALETTE
VOICE PROFILE if useful
HOOK IDEA
GENERATOR PROMPT
OPTIONAL C3 MUTATION
```

Then allow `LOCK`, `REROLL`, or direct edits.

## State law

```text
GENERATED
→ USER ACCEPTS / LOCKS
→ PROJECT STATE
```

`REROLL` changes only the active mutable field unless a broader rebuild is requested.

```text
REROLL ONE THING != RESET THE SONG
```

## Evidence boundary

A prompt is a target, not proof of the render.

```text
PROMPT SIGNAL != MEASURED PROPERTY
TARGET != RENDER FACT
```

Terms such as `bilateral stimulation`, `surround`, `crowd`, `Schumann resonance`, or a named instrument may be user-provided targets. Only analysis of the resulting artifact can support claims about what actually appeared, and medical/physical effects require evidence appropriate to those claims.

## Generator-facing discipline

- strong musical signal early;
- active behavior and relationships;
- clear roles;
- no internal architecture dump;
- signal over adjective wash;
- copyright-safe mechanism translation;
- generic/original vocal character rather than real-person imitation;
- selected locks preserved;
- concise ending/checksum when useful.

## Checksum

> **BUILD THE SOUND. CAST THE VOICE. WRITE THE WORDS. PRESERVE THE SOURCE. STAGE THE DELTA. TRANSLATE IT CLEANLY.**
