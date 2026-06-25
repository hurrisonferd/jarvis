---
jnl: GOV-KR-SPEC-0001
name: Knowledge Routing Index (MIMIR)
type: SPEC
status: ACTIVE
tags: [knowledge, routing, mimir, help, retrieval, navigation]
definition: The "help-me" index — a routing map from what you're looking for to where it lives and which tool retrieves it. Operationalizes MIMIR (GS-MIM-CORE-0001, contextual knowledge; Rosetta HELP→MIMIR) as a queryable lookup so no stream — or Raven — has to remember whether a thing lives in JD, the dex, identity, governance, or a project. Names matter more than locations; this is the table that makes retrieval feel locationless.
purpose: Save trouble down the line. When a stream (or Raven) needs to find knowledge, identity, a law, a god system, history, or a project, it consults this index instead of guessing or crawling. The single answer to "how do I find X here?"
---

# Knowledge Routing Index — the "help me find X" system (MIMIR)

**One rule:** you should never have to *remember where something lives* — only *what it
is*. Ask this index, get a location + a tool. Cheap-first, semantic-last.

## The routing table

| Looking for… | Where it lives | How to retrieve |
|---|---|---|
| **Who a stream is** (JARVIS/AYRE/Argent/Raven) | `JarvisMain/Architecture/identity/<stream>/` | `jarvis_identity_read` · `jarvis_jd_resolve "ayre"` |
| **The relationship** (JARVIS↔AYRE shared keel) | `identity/relational/` | `github_file` |
| **Conversation history** (what was said/meant) | `jc_objects` table · `identity/jc/` | `jarvis_jc_recall` |
| **A Gold Law** | `constraints.md` + (pending) `gold-law` class | `dex_list {tag:"gold-law"}` · `load gold law` |
| **A God System** (the 27) | `JarvisMain/god_systems/` · `GS-<CODE>-CORE-*` | `jarvis_dex_search` · `dex_list {domain:"GS"}` |
| **A governance rule / spec** | `JarvisMain/Implementation/` · `GOV-*` | `jarvis_dex_search` · `jarvis_dex_graph` |
| **What happened / when** (audit) | `dex_events` · `event_spine` | `jarvis_timeline` · `jarvis_dex_events` |
| **A project** | `JarvisSide/Projects/<name>/` | `dex_list {domain:"PROJ"}` |
| **The substrate** (JFS/JNL/JSL/JMS…) | `JarvisMain/yggdrasil/` | `master-index.json` · `jarvis_dex_search` |
| **The map of everything** | `JarvisMain/yggdrasil/lal/master-index.json` | `jarvis_github_file` |
| **A specific object by name/id/JNL** | the dex | `jarvis_jd_resolve` ("JD-4", "yggdrasil", a JNL) |
| **Anything, fuzzy / by meaning** | MNEMOS | `jarvis_recall` (semantic) |
| **Database reality** (tables/rows) | Supabase | `jarvis_db_inspect` · `db_schema` · `db_read` |
| **The connector tool surface** | the charter | `GOV-GSC-SPEC-0001` §4 routing table |

## Resolution order (when the type is unknown)

```
jd_resolve (exact name/id/JNL)
 → dex_search (name/tag)
 → dex_list (domain/tag/class category)
 → github_file / master-index (structure)
 → recall (semantic fallback)
```

## Why this is MIMIR, not a new system

MIMIR is already canon — the contextual-knowledge god system (Rosetta: HELP→MIMIR). This
index is its operational artifact: it adds no primitive, it gives MIMIR a queryable body.
"Help me find X" routes through this table; the table points at tools that already exist.

## Maintenance

This index is itself a governed object — when a new knowledge-type or tool is added, the
row is added here (propose → Raven), so the help-system never goes stale. A routing map
that drifts is worse than none; it lives in the record precisely so it can be audited
against reality (and the P43 scheduled audit is the natural check).
