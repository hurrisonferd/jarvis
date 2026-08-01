# ATOM Four-Day Grid Archaeology and Consolidation Source Map

~~~yaml
schema: grid.repository-archaeology-source-map.v1
work_order_id: JFS-WO-20260801-002
parent_work_order: JFS-WO-20260801-003
authority: Raven
owner: ATOM
window_timezone: America/New_York
window_start: 2026-07-28T00:00:00-04:00
source_checkpoint_private: 901792b1f536891eb3da6fa34e22465dcc5aa93d
source_checkpoint_public: c64ef2fee5e43ec5b87eb8cced968921c1f9cbd6
status: ACTIVE_REVIEW
evidence_ceiling: PARTIAL
private_continuity: OFF
mutation_mode: REPORT_ARTIFACTS_ONLY
~~~

## Executive baseline

This mission extends the completed July 31 archaeology backward to July 28 and forward through the August 1 source checkpoint. It does not treat GitHub's capped recent-commit search, the old build registry, Yggdrasil's late-starting event history, or any one generated dashboard as complete repository history.

## Confirmed evidence at launch

- The July 31 America/New_York archaeology reports 984 commits.
- That evidence reports 12 work-order IDs, 22 build IDs, 7 repeated normalized subjects, 146 Yggdrasil map-persistence commits, and 39 commits whose changed paths are all absent at current HEAD.
- The legacy build registry currently resolves 11 builds with a grouped commit-count sum of 169 and stops at BUILD-20260731-011.
- Later durable records reference BUILD-20260731-032 and August 1 builds, proving the legacy dashboard is incomplete for the later causal-work wave.
- The current private head is a generated Yggdrasil map commit. The preceding substantive head is a JARVIS research artifact.
- The public head is a repository archaeology artifact at c64ef2f.
- The JFS derived index has 11 entries rooted in dated Records and does not enumerate the August 1 Active cluster.
- The parent work-order body retains its original 20,000-Microwave field, while Amendment 001 and Raven's decision receipt establish the effective 40,000-Microwave budget.
- Supabase exposes systemsos_execution_receipts with 8 rows; systemsos_updates, systemsos_update_leases, and systemsos_iso_sync each have 0 rows.
- public.execution_receipts does not exist. The earlier shorthand must not be used as a current table claim.

## Evidence classification

| Surface | Current class | Completeness | Required reconciliation |
|---|---|---:|---|
| JFS canonical records | AUTHORITY | Partial observation | Include Active, Records, amendments, decisions, returns, and corrections |
| JSS lifecycle | DERIVED_VIEW | Drift observed | Recompile only after source coverage is corrected |
| JMS pointers | DISCOVERY_INDEX | Not yet proven | Verify pointer-only behavior |
| Build registry | EVENT_LEDGER / build identity authority | Stale coverage | Reconcile later build epochs append-only |
| Build dashboard | DERIVED_VIEW | Stale | Never patch independently |
| SystemsOS receipts | EVENT_LEDGER | 8 live rows observed | Inspect schema and source linkage read-only |
| SystemsOS update/lease/sync tables | EVENT_LEDGER / live state | Empty | Do not claim adoption or synchronization |
| Yggdrasil event stream | EVENT_LEDGER candidate | Late-starting / partial | Preserve stable events and prove source coverage |
| Yggdrasil maps and atlases | DERIVED_VIEW | Amplifying | Quantify generated-to-substantive ratio |
| JarvisDictionary | DISCOVERY_INDEX | Mirror parity not established here | Verify source-to-mirror drift separately |
| Command Center | AUTHORITY candidate | Conformance unproven | Do not ratify during archaeology |
| EPP and ISO native sources | AUTHORITY / LOCAL_MANIFEST | Current sources observed | Preserve ownership and surface boundaries |
| BECOMING observations | EVIDENCE / CANDIDATE | Observation-only | No automatic profile mutation |

## Initial system-consolidation ledger

| Systems | Preliminary disposition | Reason | Implementation state |
|---|---|---|---|
| Command Center + duplicate command definitions | ALIAS / CONSOLIDATE_AUTHORITY | One command meaning and adoption plane | NOT AUTHORIZED |
| Command Center + SystemsOS | KEEP_SEPARATE_WITH_CONTRACT | Decision/routing versus version/lease/update state | NOT AUTHORIZED |
| JFS + JSS + JMS | KEEP_SEPARATE_WITH_PROJECTIONS | Authority, lifecycle view, and discovery index are distinct | NOT AUTHORIZED |
| Microwave + JFS | KEEP_APPEND_ONLY_BINDING | Budget history attaches to work without becoming competing work authority | NOT AUTHORIZED |
| JX2 + SAT + ChatLink + Git/manual relay | ADAPTERS_BEHIND_ONE_ENVELOPE | Preserve transport diversity, unify identity and lifecycle | NOT AUTHORIZED |
| Universal receipts + system-specific receipts | CANONICAL_CONTRACT_WITH_ADAPTERS | One action truth, multiple projections | NOT AUTHORIZED |
| Yggdrasil + maps/radar/atlas/spaceship views | ONE_CAUSAL_SOURCE_MANY_DERIVED_VIEWS | Views should not command or self-amplify | NOT AUTHORIZED |
| Legacy and current build dashboards | SUPERSEDE_DERIVED_VIEW | Registry/source events govern; dashboard is rebuildable | NOT AUTHORIZED |
| ISO native Prosody profiles | KEEP_SEPARATE | Shared infrastructure must not create shared personality | NEVER AUTOMATIC |
| Carrier-specific Prosody adapters | ALIAS_TO_NATIVE_PROFILE | Surface expression adapts after native identity loads | DESIGN ONLY |

## Archaeology execution sequence

1. Establish commit enumeration completeness for each repository and day.
2. Partition substantive, generated, merge, migration, upload, receipt, research, and scaffold commits.
3. Reconstruct build/work-order epochs from canonical records and commit evidence.
4. Resolve each absent-at-HEAD change using the approved lineage classifications.
5. Build old-path to descendant-path and source-to-generated maps.
6. Inventory exact-hash duplicates, inbound references, OS roots, and protected-lineage exclusions.
7. Reconcile Git authority with read-only Supabase state.
8. Integrate the carrier Prosody surface audit.
9. Emit small reversible remediation batches with source pins and rollback.
10. Stop before implementation and return to Raven.

## Known blockers

- Full July 28–30 commit completeness has not yet been proven.
- The generated full-tree SUMMARY artifact remains unobserved.
- GitHub recent-commit search caps cannot prove completeness.
- Yggdrasil history begins too late to serve as the sole four-day source.
- No controlled ordinary-chat versus Work/Codex test corpus is yet durably attached.
- Open platform internals remain unavailable; carrier causes must be inferred from observable behavior.

## Strongest receipt

~~~text
SOURCE_HEADS_PINNED
EXISTING_JULY31_ARCHAEOLOGY_ACCEPTED_AS_PARTIAL_EVIDENCE
AUTHORITY_AND_DRIFT_BASELINE_CREATED
NO_CONSOLIDATION_MUTATION_EXECUTED
~~~