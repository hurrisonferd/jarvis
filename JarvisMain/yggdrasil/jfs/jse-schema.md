# JSE — Jarvis Schema Envelope

**JNL:** ARCH-JSE-SPEC-0001 · The umbrella that guarantees **every JD entry carries the same
complete format — no missing fields, ever.** JSE is not a new store or a new system; it is the
*named contract* for the frontmatter envelope that `seed.py` writes and `validate.py` enforces.
One shape for every object, from `ARCH-YGG-CORE-0001` to the newest spell. Code is ground truth
where this and code disagree (the envelope list lives in `validate.py` as `JSE_ENVELOPE`).

## The envelope — 19 frontmatter keys, always present

Every governed object's `.md` opens with this block. **Every key is present on every entry**;
values may be *empty* where legitimate (a root has no `parent`; a substrate root may have no
`steward`; `related`/`references`/`aliases` may be `[]`). Present-but-empty is fine. **Absent is
a defect** — that is the `steward: null`-class bug JSE exists to make impossible.

| Key | Meaning | May be empty? |
|---|---|---|
| `name` | human name | no |
| `type` | JNL type token (RT/SPEC/CORE/…) — *is* the address ontology | no |
| `class` | SYSTEM/SPEC/MODULE/ENTITY/EVENT/REGISTRY | no |
| `tier` | MAIN / SIDE | no |
| `authority` | CANON | no |
| `owner` | owning team/system | no |
| `steward` | tending god system | yes (roots) |
| `parent` | parent JNL (the family tree) | yes (roots) |
| `jnl` | the immutable address | no |
| `seq` | immutable creation serial | no |
| `status` | JSS lifecycle (TASK/ACTIVE/…) | no |
| `created` | YYYY-MM-DD | no |
| `updated` | YYYY-MM-DD | no |
| `source` | path to the truth file (location) | no |
| `related` | cross-ref JNLs | yes (`[]`) |
| `references` | reference tiers | yes (`[]`) |
| `tags` | semantic tags | no |
| `aliases` | alternate names | yes (`[]`) |
| `ref` | reference tier flags (PRI/IDX/SPEC) | no |
| `memory_tier` | JMMS tier this object lives in (JITM/JSTM/JLTM/JHTM/JATM) | no |

Body (after frontmatter): **`**Definition:**`** (what it is) + **`**Purpose:**`** (why it exists).

## The rules

1. **Completeness.** Every entry carries all 19 envelope keys. `validate.py` (the JSE gate)
   fails the build on any missing key — closing the gap where GL12 only required 10 of them.
2. **Uniformity.** `seed.jd_entry_md` is the single writer; every object gets the identical shape.
   No hand-rolled entries with bespoke fields.
3. **Empty ≠ missing.** A legitimately empty value (root `parent`, `[]` lists) is valid; a missing
   *key* is not. Visibility over silence — an unassigned steward shows as empty, never vanishes.
4. **Identity is immutable.** `jnl`, `seq`, `type`, `class` never change for a live object
   (mint a successor + deprecate; never rewrite the address).

## Relationship to the rest

JSE is the **format** layer of the JFS family — it sits beside JNL (address grammar) and JNS
(filename grammar): JNS says what the file is *called*, JNL says how it's *addressed*, **JSE says
what it *contains***. Together they make every object Yggdrasil-compliant and Pokédex-uniform.
(Elevation to a substrate CORE primitive — `ARCH-JSE-CORE` — is a one-command `extend.py` step
if Raven wants JSE as a first-class peer of JFS/JD; SPEC for now.)
