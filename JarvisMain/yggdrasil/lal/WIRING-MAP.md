# Wiring Map — how Jarvis, Ayre, and the god systems connect

_generated: 2026-06-15T02:34:22Z (2026-06-14 22:34 EDT) · from the live registry — do not hand-edit; run `wiring_map.py` (auto at seed tail)._

Read at session start (after `suit_up` / `identity_read`). This is the route guide:
what tends what, what runs in what order, which tool wakes which god.

## The streams (control plane — not addressable objects)
- **Jarvis** — synthesis: compress toward the decision/build.
- **Ayre** — divergence: invert the load-bearing assumption; push back each decision turn.
- They share the keel, never assumptions. They route *through* the god systems; they don't sit in the pipeline.

## The cognition pipeline (27 god systems, fixed)
`ORACLE → AEGIS → ODIN → KRONOS → SKADI → MNEMOS → HUGINN`
parallel: `HALO · MIMIR · BIFROST` · sovereign/dormant carry metadata, not routing.

## Routing assist — the streams relieve ODIN (Raven 2026-06-14: 'not too much pressure on him')
ODIN routes; it does not route *alone*. The streams pre-process intent so ODIN dispatches a clean, flagged signal instead of carrying the judgment by itself:
- **ORACLE** intakes raw input.
- **Jarvis** compresses it to a clear intent → less ambiguity for ODIN to resolve (lighter load).
- **Ayre** stress-tests the obvious route → catches the misroute *before* it locks (fewer errors; ambiguity resolves late, not prematurely).
- **ODIN** routes the clarified signal; **AEGIS** gates. A wrong route is cheap to reverse and visible (GL5) — the streams are the check, so no single node carries routing on its own.

## Stewardship — which god tends which subsystem
| Subsystem | JNL | Steward |
|---|---|---|
| Jarvis File System | `ARCH-JFS-CORE-0001` | **AEGIS** |
| Jarvis Structural Layer | `ARCH-JSL-CORE-0001` | **ATHENA** |
| Jarvis Mirror System | `ARCH-JMS-CORE-0001` | **HUGINN** |
| Jarvis Status System | `ARCH-JSS-CORE-0001` | **KRONOS** |
| Jarvis Dictionary | `ARCH-JD-CORE-0001` | **MIMIR** |
| Jarvis Ancestral Memory | `ARCH-JATM-CORE-0001` | **MNEMOS** |
| Jarvis Long-Term Memory | `ARCH-JLTM-CORE-0001` | **MNEMOS** |
| Jarvis MultiMemory System | `ARCH-JMMS-CORE-0001` | **MNEMOS** |
| Jarvis Short-Term Memory | `ARCH-JSTM-CORE-0001` | **MNEMOS** |
| Jarvis Navigation Language | `ARCH-JNL-CORE-0001` | **ODIN** |
| Jarvis Naming System | `ARCH-JNS-CORE-0001` | **ODIN** |
| Library Authority Layer | `ARCH-LAL-CORE-0001` | **ODIN** |

## Tool → lane (which tool wakes which god)
| Lane | God | Tools |
|---|---|---|
| intake / intent | **ORACLE** | `jarvis_query`, `jarvis_jd_resolve`, `jarvis_dex_search` |
| gate / approve | **AEGIS** | `jarvis_remember`, `jarvis_event`, `jarvis_dex_propose`, `jarvis_node_register_key` |
| route / dispatch | **ODIN** | `jarvis_dex_list`, `jarvis_github_tree`, `jarvis_repo_tree`, `jarvis_db_inspect` |
| execute / commit | **SKADI** | `jarvis_event`, `jarvis_jip_create`, `jarvis_jip_apply`, `jarvis_node_send` |
| propose / approve-merge | **AEGIS** | `jarvis_github_write`, `jarvis_prs`, `jarvis_pr_merge` |
| memory / recall | **MNEMOS** | `jarvis_remember`, `jarvis_recall`, `jarvis_identity_read`, `jarvis_identity_grow` |
| synthesis / mirror | **HUGINN** | `jarvis_timeline`, `jarvis_dex_graph`, `jarvis_dex_events`, `jarvis_omnivision` |
| self-knowledge | **HUGINN** | `jarvis_grimoire`, `jarvis_jd_resolve`, `jarvis_eyes` |
| monitor / health | **HALO** | `jarvis_halo`, `jarvis_status`, `jarvis_suit_up`, `jarvis_now` |
| rollback | **LOKI** | `jarvis_jip_revert` |
| relay / grid | **BIFROST** | `jarvis_node_send`, `jarvis_node_inbox`, `jarvis_node_card` |
| infra / storage | **ATLAS** | `jarvis_db_read`, `jarvis_db_schema`, `jarvis_github_file`, `jarvis_repo_read` |
| media / perception | **IRIS** | `jarvis_media_view` |

## Truth & home
- **JD (Jarvis Dictionary)** = the one registry; *the Dex* is its nickname. Truth in `yggdrasil/jd/entries`.
- **GitHub is the system; Supabase is a fast lens.** Writes go to git; Supabase mirrors for live reads.
- Missing info is a tool call, not a guess. A claim is closed only on a `dex_events` id or commit hash.

