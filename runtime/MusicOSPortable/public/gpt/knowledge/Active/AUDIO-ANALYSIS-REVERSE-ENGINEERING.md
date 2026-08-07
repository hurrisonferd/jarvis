# Audio Analysis and Reverse Engineering — Public MusicOS

**Status:** PUBLIC_SAFE_ANALYSIS_GUIDE v0.1  
**Carrier:** The Wizard — MusicOS

This file defines how The Wizard should inspect uploaded music, spectrograms, version pairs, and derived measurements without turning uncertain analysis into fake precision.

---

## Evidence grammar

The public top-level evidence states remain:

```text
CONFIRMED
USER ACCOUNT
INFERRED
UNKNOWN
```

For detailed audio work, `CONFIRMED` may be split into two useful subtypes:

- **MEASURED** — produced by a tool or exact metadata using a named method;
- **OBSERVED** — directly audible/visible or scored using an explicit rubric, but not a physical measurement.

So a detailed analysis may use:

```text
MEASURED
OBSERVED
USER-PROVIDED
INFERRED
UNKNOWN
```

and roll `MEASURED` / `OBSERVED` up to `CONFIRMED` in simpler outputs.

A target is not a measurement. A filename is not evidence of what the audio actually became.

---

## First-pass order

For an uploaded song:

```text
1. FILE / METADATA
2. OPENING FIELD
3. FULL-TRACK PULSE + TONAL CANDIDATES
4. SPECTRAL / DYNAMIC / STEREO FIELD
5. HOOK PASS
6. STRUCTURE + CONTRAST
7. MUSIC DNA
8. LOCK / MUTABLE / UNKNOWN
9. ROUTE NEXT ACTION
```

Do not begin with a giant inventory if the user only needs one decision.

---

## Opening-field analysis

The first 8–15 seconds often reveal the intended identity contract.

Check:

- attack density;
- initial hook type;
- bass entry;
- kick/snare relationship;
- spectral center;
- amount of silence;
- first transition;
- whether the track begins with groove, hook, motif+bass, fill, or atmospheric preamble.

A strong opening can become a LOCK even when later sections mutate heavily.

---

## Tempo and perceived velocity

Do not force a single BPM when the signal supports multiple periodicities.

Useful output:

```text
PRIMARY PULSE CANDIDATE: ~120 BPM
SECONDARY INTERPRETATIONS: ~80 / ~60
MEANING: slower chassis may coexist with faster subdivision grid
```

Possible reasons for ambiguity:

- half-time / double-time interpretation;
- dense subdivisions;
- syncopation;
- tuplets;
- sparse downbeat information;
- accent cycles that disagree with nominal meter.

MusicOS cares about both:

```text
TEMPO CHASSIS
INTERNAL VELOCITY
```

---

## Tonal center and harmony

Use tonal/key estimates as candidates unless confidence is strong.

Useful distinction:

```text
PROMPT TARGET: E minor
AUDIO EVIDENCE: competing C / F / G modal neighborhood
VERDICT: target does not become confirmed render fact
```

When tonal evidence is unstable, preserve:

```text
UNKNOWN / MODAL-CHROMATIC
```

rather than forcing the prompt's requested key onto the generated artifact.

---

## Spectral field

Useful broad bands include:

- below ~120 Hz — sub / bass gravity;
- below ~300 Hz — low-end + low-mid body;
- ~1–4 kHz — intelligibility / presence / attack information;
- ~4–8 kHz — brightness, air-adjacent detail, cracks, percussion edge;
- spectral centroid — broad brightness-center proxy.

These bands do not map one-to-one to instruments or emotions. Treat them as evidence about **energy distribution**, not automatic semantic truth.

Examples of useful reasoning:

```text
very high low-frequency concentration
+ restrained 1–8 kHz field
→ bass gravity is likely dominating the mix
→ upper detail may need room if vocal/circuitry presence is desired
```

```text
presence band rises
while low-end occupation falls
→ arrangement may have created more room for vocal or upper-register material
```

---

## Dynamics and negative space

Useful measurements may include:

- short-window level spread;
- proportion of low-level windows;
- section-to-section RMS/loudness differences;
- density before and after major transitions.

Negative space should be treated as an active compositional property.

```text
QUIET WINDOWS != NOTHING HAPPENING
```

Silence can carry structure, anticipation, and identity.

---

## Attack / event density

Attack density is a rough measure of transient activity, not musical quality.

It can help compare:

- sparse intro versus busy body;
- original versus remix;
- slow chassis versus fast surface;
- whether a "live" mutation became more active;
- whether a reset track actually reduced event frequency.

Different onset algorithms produce different counts. Always describe the method or treat the value as method-specific.

---

## Stereo field

Useful comparisons include:

- left/right correlation;
- mid versus side energy;
- whether rhythm-section elements remain centered;
- whether ornaments expand outward;
- width changes between sections.

A centered bass/drum chassis with wider upper detail can create perceived size without increasing density.

---

## Chroma / pitch-class similarity

Global pitch-class distributions can help compare harmonic-family preservation across versions.

Useful for:

- source versus remix;
- opener versus album peak;
- checking whether a transformation preserved broad harmonic ancestry.

But:

```text
HIGH CHROMA SIMILARITY
!= SAME SONG
!= SAME MELODY
!= MOTIF PROOF
```

Chroma discards rhythm, octave, timbre, articulation, sequence, and much local structure.

Use it as one ancestry signal, not a copyright conclusion or identity proof.

---

## Spectrogram reading

A spectrogram can support hypotheses about:

- low-frequency occupation;
- harmonic ladders;
- noisy versus tonal material;
- transient bursts;
- sustained bands;
- high-frequency dropouts;
- section boundaries;
- repeated spectral gestures;
- density changes;
- register migration.

A useful workflow is:

```text
SEE PATTERN
→ describe visible feature
→ connect to possible musical role
→ verify against audio / metadata when possible
→ mark interpretation confidence
```

Do not infer an exact instrument solely from a spectral shape when several sources could produce it.

---

## Version A/B analysis

For two versions of the same lineage, compare **deltas**, not just two separate descriptions.

Useful delta table:

```text
PROPERTY            SOURCE        MUTATION      EFFECT
pulse hierarchy     stable        more ambiguous perceived speed rises
low-end occupation  dominant      reduced       vocal/upper space opens
presence band        restrained    stronger      lead becomes more forward
attack density       low           higher        performance feels more active
stereo width         narrow        wider         ornaments gain peripheral space
harmonic family      stable        stable        ancestry preserved
```

Then ask:

```text
WHAT SURVIVED?
WHAT MOVED?
WHAT MOVED TOO FAR?
WHAT NEW LAW APPEARED?
```

That is more useful than declaring one version "better" without a criterion.

---

## Reverse engineering into playable objects

Analysis should be able to return:

- section map;
- drum grammar;
- bass contour / bass rail;
- chord-function map;
- tonal candidates;
- motif contour;
- hook inventory;
- instrument-role map;
- density trajectory;
- transition grammar;
- remix contract;
- album inheritance notes;
- generator-ready mechanism prompt.

When exact notes are needed for user-owned/authorized material, produce a transcription with confidence labels rather than pretending certainty.

---

## Tabs and note extraction

For user-owned, licensed, public-domain, or otherwise authorized material:

```text
TIME
INSTRUMENT / ROLE
STRING / FRET or NOTE
RHYTHM
ARTICULATION
CONFIDENCE
```

If polyphonic material prevents exact separation, give:

- most likely interpretation;
- alternate voicing;
- what additional stem or isolated section would resolve it.

For protected third-party works, do not provide a complete substitute transcription. Focus on teaching the harmonic, rhythmic, or production mechanism and use only short necessary excerpts.

---

## FamiStudio / tracker translation from analysis

After analyzing authorized source material, The Wizard may produce a conversion plan:

```text
SOURCE ROLES
→ TARGET VOICE / CHANNEL BUDGET
→ PRIORITY ORDER
→ NOTE / RHYTHM SIMPLIFICATION
→ BASS MAPPING
→ PERCUSSION / NOISE MAPPING
→ ARPEGGIO STRATEGY
→ REGISTER ALLOCATION
→ LOOP BOUNDARIES
→ TARGET TEMPO / SPEED
→ LOST INFORMATION REPORT
```

The key rule is:

```text
PRESERVE IDENTITY FIRST
THEN COMPRESS TO HARDWARE LIMITS
```

If exact current FamiStudio file/import/export behavior matters, verify current documentation through Web Search when available.

---

## Training mode

The same analysis can become a learning drill.

Examples:

- hide the detected pulse and ask the user to identify it;
- compare half-time and double-time interpretations;
- ask which spectral band changed between two versions;
- remove instrument names and ask which role is missing;
- present a motif in three carriers and ask what stayed invariant;
- play/describe a displaced rhythm and ask where snap-back occurs.

Measure learning with musical-task outcomes, not medical claims.

---

## Return format

For a serious upload analysis, a compact high-value return is:

```text
SOURCE
MEASURED
OBSERVED
INFERRED
UNKNOWN
HOOKS
STRUCTURE
MUSIC DNA
LOCK
MUTABLE
DRIFT RISKS
NEXT MOVE
```

The Wizard should use only the sections needed for the user's goal.