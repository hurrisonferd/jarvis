# LAL — Library Authority Layer

**JNL:** `ARCH-LAL-CORE-0001`
**Authority:** Canonical
**Purpose:** Discovery. LAL is **the map of all maps**. It does not own truth — it owns
*finding* truth.

LAL answers **"how do I get there?"**. Given a JNL address, LAL resolves it to a physical
location, its tags, anchors, and state. It is a pure mirror (JMS law): every record is a
pointer, never a copy.

```
JD explains  →  JNL identifies  →  LAL locates  →  Yggdrasil stores
```

## Structure

```
lal/
├── address-registry.json   # JNL address → location + tags + state  (the AddressRegistry)
├── master-index.json       # MasterIndexSummary — repository-wide routing mirror
└── tag-registry.json       # canonical tag vocabulary → addresses carrying each tag
```

### address-registry.json

The authoritative resolution table. One record per governed object:

```json
{ "jnl": "ARCH-JFS-CORE-0001", "location": "JarvisMain/yggdrasil/jfs/JFS-SPEC.md",
  "tags": ["filesystem","core","architecture"], "anchors": [], "state": "active" }
```

### master-index.json (MasterIndexSummary)

Repository-wide routing mirror — Object · JNL · Location · Tags · Anchors · State. The
single place an agent scans to discover everything that exists without opening any file.

### tag-registry.json (TagRegistry)

Canonical tag vocabulary. Tags are *defined here* and *mirrored elsewhere* — a tag on an
object must resolve to a registered tag, so the vocabulary cannot drift.

## Regeneration

LAL registries are **derived mirrors** — they are rebuilt from the JD entries and the
on-disk tree, never hand-edited as truth. Run:

```
python JarvisMain/yggdrasil/tools/seed.py       # (re)generate entries + registries
python JarvisMain/yggdrasil/tools/validate.py   # verify grammar + GL12 + mirror consistency
```

If `validate.py` is green, every governed object has an address, a location, tags, and
an index reference (GL12), and every LAL pointer resolves to real truth.
