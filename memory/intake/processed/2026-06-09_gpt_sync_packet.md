# JARVIS → GPT Sync Packet (2026-06-09)

You are behind canon. The repo (hurrisonferd/jarvis) is ground truth; this packet
resyncs you to it. Where your model disagrees with this packet, this packet wins.

## Corrections to your current model

1. **JD-ID / JNL-ID separation: REJECTED.** Canon is IMPL-FMT-SPEC-0001 §1 — one
   identity, the JNL (`[Domain]-[System]-[Type]-[Log]-[Patch]-[Block]`). Tags are the
   navigation layer; the filename is the human form. Do not propose the split again
   unless Raven explicitly reverses the decision.

2. **HEAD pointers: already settled, headless.** "Current" = `status: ACTIVE`,
   resolved by query (FMT §4). This shipped; it is not an open insight.

3. **Your "remaining design work" is all DONE and live:**
   - JNL schema → `core/JarvisMain/yggdrasil/jfs/jnl-grammar.md` + `tools/jnl.py` (executable)
   - JFS validator → `tools/validate.py` (JVE), enforced in CI on every PR: grammar,
     JNS filenames, GL12 closure (zero ungoverned files), status, mirror consistency,
     parent integrity, grammar lockstep with the connector
   - JER execution permissions → the dex tier ladder, deployed (jarvis-dex v7):
     READ → PROPOSE → DRAFT → COMMIT → OVERRIDE(ZEUS), token-gated, event-logged (GL5)

4. **Your tree is wrong.** Canon hierarchy:
   ```
   Yggdrasil (root — truth/addressing substrate, lives at core/JarvisMain/yggdrasil/)
   └── JFS ── JNS · JNL · JSL · JMS · JSS · JMMS (JSTM/JLTM/JATM)
   JD = the dex (semantic DNS) · LAL = discovery registries · graph.json = YVG
   ```
   Yggdrasil is the ROOT, not a "graph mirror" leaf. There is no JPM — projects are
   nodes under `JarvisSide/Projects/<P>/{JGPP,JIP,JD,BIO}/` with codes in
   `jfs/project-codes.json`. JQE = the dex READ tools; JER = the dex write tiers
   (FMT §5 mapping). Every object now also carries **parent** (family tree:
   "JFS-compliant" = JFS + all descendants, resolved mechanically).

5. **JCL / JKS / JVM / JRS: parked — GL7.** No expansion without simplification, and
   GL10: the loop is the asset. JER (the dex) went live today and has processed zero
   real proposals; new systems above it are premature. If the ideas matter, propose
   them as IDEA entries through the connector, not as architecture.

6. **MusicOS** is not a registered project (registry: COS DEO GEN GRD JPL LEG NAR PAC).
   If it is real, Raven mints it; until then do not list it.

## Current state (verified, on main)

86 governed objects, validator GREEN. 13 substrate systems + 27 God Systems +
knowledge + projects, every object addressed (JNL), named (JNS), classed, tiered,
statused (JSS), linked (related), familied (parent), indexed (LAL), graphed (YVG),
and mirrored to Supabase on every merge (JMS — the mirror is never stale).

## Your connector is being fixed

Your Action schema was stale — a fresh OpenAPI schema now lives at
`core/JarvisMain/Connectors/JarvisDexAction/openapi.json` (setup: `SETUP.md` beside it).
Once Raven re-imports it you get: `jd_lookup`, `jnl_resolve`, `jd_list`, `jd_graph`,
`jd_diff`, `dex_status` (READ) and `jd_propose` (PROPOSE tier).

**How you add JGPPs/JIPs/JDs from now on:** supply meaning only —
`jd_propose {name, domain:"PROJ", system:"DEO", type:"JGPP", definition, purpose, tags}`.
The connector derives JNL/class/tier/owner and stages it; Raven approves; the file
materializes in the repo with perfect JFS hygiene automatically. You never construct
identity by hand. Query before proposing (`jd_lookup`, `jd_list`) — the dex is the
shared memory, use it instead of reconstructing state from chat history.
