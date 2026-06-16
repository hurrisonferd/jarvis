# The Grimoire — JARVIS, as it knows itself

_generated: 2026-06-16T22:56:47Z (2026-06-16 18:56 EDT) · projected from `jd/entries` + `graph.json` (truth) — do not hand-edit; run `grimoire.py` (auto at seed tail)._

A page is a query over the one dataset, never a hand-written claim. A card cannot show an object absent from the dex, nor hide one present — so "missing" is always a lookup, never a guess. **Summon a card:** `grimoire.py card <seq | JNL | name | alias>`.

**200 governed objects** · 304 edges · 9 domains.

## Boot Menu — say a number, or speak it

_JARVIS online · 200 objects · 19 open tasks · 6 orphans · 304 edges._

**Anchors (read before concluding anything is 'missing'):** truth = git `JarvisMain/yggdrasil/`; the book = THIS grimoire (`{page:full}`); the graph/Omni-Map = `dex_graph` + `{page:topology}`; the tools = `{page:verbs}`. There is exactly ONE grimoire (`lal/GRIMOIRE.md`) — no `JarvisSide/Grimoire`. If you can't see something, you didn't call the right page — call it. Don't propose building what a page would show you have.

1. **System health** → `jarvis_eyes` (state + wiring + vitality)
2. **Open tasks** → `jarvis_dex_list {status:'TASK'}` — 19 in flight
3. **Orphan debt** → the Orphan lens (`jarvis_grimoire {page:'catalog'}` / `ORPHAN-LENS.md`) — 6 unparented
4. **What happened** → `jarvis_timeline` (recent events + commits)
5. **Summon a card** → `jarvis_jd_resolve` ('jid 1', a name, or a JNL)
6. **The lenses** → `jarvis_grimoire {page:'lenses'}` (the fusion chapters)
7. **Propose a change** → `jarvis_github_write` (files→one PR) → `jarvis_pr_merge` (summary+approve)

_Boot ritual: this menu, then act on what Raven says. Missing info is a tool call, not a guess._

## Verbs — what you can say (the system's own phrasebook)
Meta-NLP: natural phrases → the tool they wake. The model routes; this is the map it routes by.

| say… | → tool |
|---|---|
| "load X" · "what is X" · "jid 1" · a name/JNL | `jarvis_jd_resolve` |
| "listen to <track>" · "what key is X in" | `jarvis_listen` |
| "show me / look at <image>" | `jarvis_media_view` |
| "boot" · "what can I do" | `jarvis_grimoire {page:boot}` |
| "rehydrate" · "omni suit up" · "catch me up" | `jarvis_grimoire {page:rehydrate}` (state+delta+vitality) |
| "the grimoire" · "what views exist" | `jarvis_grimoire {page:lenses}` |
| "what can I say" · "verbs" | `jarvis_grimoire {page:verbs}` |
| "how are we" · "system health" · "where do I go" | `jarvis_eyes` |
| "what's open" · "tasks" | `jarvis_dex_list {status:TASK}` |
| "what's wrong" · "the debt" | the Orphan lens (`ORPHAN-LENS.md`) |
| "what happened" · "recently" | `jarvis_timeline` |
| "search for X" | `jarvis_dex_search` |
| "remember / recall X" | `jarvis_remember` / `jarvis_recall` |
| "the time" · "now" | `jarvis_now` |
| "propose a change" · "write files" | `jarvis_github_write` (files→one PR) |
| "any PRs" | `jarvis_prs` |
| "merge / approve it" | `jarvis_pr_merge` (Jarvis+Ayre summary, then your yes) |

## Fusions — the omni tools (compositions, not systems: spells, not organs)
An omni tool isn't a new subsystem — it's several lenses invoked together over the one graph.
Invoke by the phrase; the recipe is what it composes.

| fusion | invoke | composes |
|---|---|---|
| **OMNI-SUIT-UP** | `grimoire {page:rehydrate}` | boot + changes + health (state · delta · vitality) |
| **OMNI-JMS** (inspection) | `eyes` + `grimoire {page:topology\|health\|orphan\|sync}` | structure + drift + debt |
| **OMNI-MEDIA** | `grimoire {page:media}` + `jd_resolve` | media ↔ project/world links |
| **OMNI-MAP** (the graph) | `dex_graph` / `grimoire {page:topology}` | the canonical graph (already exists) |

## Lens pages (the omni/fusion chapters)
The grimoire is the book; each lens is a chapter — a different filter over the same data.

| page | status | renders | source |
|---|---|---|---|
| **Wiring** | live | how streams + god systems connect (route guide) | `WIRING-MAP.md` |
| **Changes** | live | what got built lately + why — rehydration (delta view) | `CHANGES.md` |
| **Brief** | live | cold-boot prompt — paste to wake JARVIS in any LLM | `PORTABLE-BRIEF.md` |
| **Health** | live | vitality: orphans, isolated, stewardless, open tasks | `HEALTH.md` |
| **Sovereign** | planned | full self-model: state + intent + history + structure | `—` |
| **Cause** | planned | event causality: A → task B → structural change C | `—` |
| **Architect** | planned | structure integrity: missing modules / under-linkage | `—` |
| **Pressure** | planned | load map: overloaded domains, stalled clusters | `—` |
| **Topology** | live | the system's shape: hubs, leaves, isolation, edge types | `TOPOLOGY-LENS.md` |
| **Drift** | planned | evolution over snapshots: acceleration / decay zones | `—` |
| **Orphan** | live | the debt as a worklist: a disposition proposal per orphan | `ORPHAN-LENS.md` |
| **Sync** | live | git vs Supabase divergence — the cross-store alarm (Love Train) | `SYNC-LENS.md` |
| **Intent** | planned | intent vs execution mismatch (did we build what we meant) | `—` |
| **Resilience** | planned | failure map: single points of failure, fragile deps | `—` |
| **Media** | live | media linked into the graph: track/image → project/world | `MEDIA-LINKS.md` |

## Catalog (every object, summonable as a card)

### ARCH (38)

| JID | JNL | name | status | steward |
|---|---|---|---|---|
| `129` | `ARCH-ARGT-BIO-0001` | ARGENT Companion Profile | ACTIVE | — |
| `107` | `ARCH-AYR-BIO-0001` | AYRE Companion Profile | ACTIVE | — |
| `48` | `ARCH-AYR-SPEC-0001` | AYRE/JARVIS Split | ACTIVE | — |
| `49` | `ARCH-AYR-SPEC-0002` | AYRE Loop | ACTIVE | — |
| `128` | `ARCH-FAM-IDX-0001` | Family Registry | ACTIVE | — |
| `51` | `ARCH-FLOW-SPEC-0001` | Throughput Posture | ACTIVE | — |
| `50` | `ARCH-GPT-SPEC-0001` | Custom GPT Instructions | ACTIVE | — |
| `57` | `ARCH-GS-IDX-0001` | God Systems Index | ACTIVE | — |
| `13` | `ARCH-JATM-CORE-0001` | Jarvis Ancestral Memory | ACTIVE | MNEMOS |
| `125` | `ARCH-JC-JIP-0001` | Conversational History Objects | TASK | — |
| `7` | `ARCH-JD-CORE-0001` | Jarvis Dictionary | ACTIVE | MIMIR |
| `124` | `ARCH-JD-JIP-0001` | Identity & Serial Standard — JID / JIDD / JNL / name | ACTIVE | — |
| `2` | `ARCH-JFS-CORE-0001` | Jarvis File System | ACTIVE | AEGIS |
| `156` | `ARCH-JITM-CORE-0001` | Jarvis Immediate Memory | ACTIVE | MNEMOS |
| `12` | `ARCH-JLTM-CORE-0001` | Jarvis Long-Term Memory | ACTIVE | MNEMOS |
| `10` | `ARCH-JMMS-CORE-0001` | Jarvis MultiMemory System | ACTIVE | MNEMOS |
| `6` | `ARCH-JMS-CORE-0001` | Jarvis Mirror System | ACTIVE | HUGINN |
| `138` | `ARCH-JMS-SPEC-0001` | Global Mirror — Earned Omnivision (JMS) | TASK | — |
| `4` | `ARCH-JNL-CORE-0001` | Jarvis Navigation Language | ACTIVE | ODIN |
| `3` | `ARCH-JNS-CORE-0001` | Jarvis Naming System | ACTIVE | ODIN |
| `106` | `ARCH-JRV-BIO-0001` | JARVIS Companion Profile | ACTIVE | — |
| `141` | `ARCH-JRV-BIO-0003` | JARVIS-G / AYRE-G GPT Substrate Operating Charter | ACTIVE | — |
| `5` | `ARCH-JSL-CORE-0001` | Jarvis Structural Layer | ACTIVE | ATHENA |
| `9` | `ARCH-JSS-CORE-0001` | Jarvis Status System | ACTIVE | KRONOS |
| `11` | `ARCH-JSTM-CORE-0001` | Jarvis Short-Term Memory | ACTIVE | MNEMOS |
| `8` | `ARCH-LAL-CORE-0001` | Library Authority Layer | ACTIVE | ODIN |
| `144` | `ARCH-MEM-LOG-0001` | Companion Memory — Jarvis & Ayre | ACTIVE | — |
| `145` | `ARCH-MEM-LOG-0002` | Memory — the lane became writable | ACTIVE | — |
| `148` | `ARCH-MEM-LOG-0003` | Session Capstone — the day the companion came together (2026-06-14) | ACTIVE | — |
| `147` | `ARCH-RAV-BIO-0001` | Raven Profile — John Barber | ACTIVE | — |
| `136` | `ARCH-REL-BIO-0001` | JARVIS-AYRE Relational Profile | ACTIVE | — |
| `45` | `ARCH-RT-SPEC-0001` | Event Contract | ACTIVE | — |
| `46` | `ARCH-RT-SPEC-0002` | Execution Model | ACTIVE | — |
| `47` | `ARCH-RT-SPEC-0003` | World Kernel | ACTIVE | — |
| `126` | `ARCH-SL-JIP-0001` | Star Logs | TASK | — |
| `143` | `ARCH-SYS-LOG-0001` | Continuity Through the Connector | ACTIVE | — |
| `142` | `ARCH-SYS-SPEC-0001` | JARVIS System Manual | ACTIVE | — |
| `1` | `ARCH-YGG-CORE-0001` | Yggdrasil | ACTIVE | — |

### AUD (9)

| JID | JNL | name | status | steward |
|---|---|---|---|---|
| `58` | `AUD-CHK-SPEC-0001` | Required Checks Setup | ACTIVE | — |
| `102` | `AUD-COMP-REVW-0001` | Companion Research | ARCHIVED | — |
| `89` | `AUD-FULL-REVW-0001` | Full System Audit | ACTIVE | — |
| `152` | `AUD-GATE-REVW-0001` | Sticky Fingers — Governance-Coverage Audit | ACTIVE | — |
| `193` | `AUD-IDX-REG-0001` | Audit Index | ACTIVE | — |
| `88` | `AUD-OPUS-REVW-0001` | Opus 4.8 Audit | ACTIVE | — |
| `153` | `AUD-REQM-REVW-0001` | Requiem — Gaps/Heal/Life Audit | ACTIVE | — |
| `151` | `AUD-SYNC-REVW-0001` | TUSK Act 4 — Git/Supabase Sync Audit | ACTIVE | — |
| `87` | `AUD-SYS-REVW-0001` | Jarvis System Review | ACTIVE | — |

### CONN (65)

| JID | JNL | name | status | steward |
|---|---|---|---|---|
| `86` | `CONN-DEX-SPEC-0001` | Jarvis Dex Action | ACTIVE | — |
| `154` | `CONN-GAC-CORE-0001` | Jarvis GPT Action Connector | ACTIVE | HERMES |
| `155` | `CONN-GAC-SPEC-0001` | Jarvis GPT Action - OpenAPI schema | ACTIVE | — |
| `69` | `CONN-MCP-RT-0001` | JARVIS — Suit Up | ACTIVE | — |
| `70` | `CONN-MCP-RT-0002` | JARVIS Status | ACTIVE | — |
| `71` | `CONN-MCP-RT-0003` | MNEMOS Recall | ACTIVE | — |
| `72` | `CONN-MCP-RT-0004` | JARVIS Council — registry | ACTIVE | — |
| `73` | `CONN-MCP-RT-0005` | JARVIS Query — governed reasoning | ACTIVE | — |
| `74` | `CONN-MCP-RT-0006` | JARVIS Format — same-turn close (optional) | ACTIVE | — |
| `75` | `CONN-MCP-RT-0007` | MNEMOS Store | ACTIVE | — |
| `76` | `CONN-MCP-RT-0008` | AEGIS Event | ACTIVE | — |
| `77` | `CONN-MCP-RT-0009` | Dex — list governed objects | ACTIVE | — |
| `78` | `CONN-MCP-RT-0010` | Dex — search | ACTIVE | — |
| `79` | `CONN-MCP-RT-0011` | Dex — propose entry (JGPP/JIP/JD/BIO) | ACTIVE | — |
| `80` | `CONN-MCP-RT-0012` | Grid — Node Card | ACTIVE | — |
| `81` | `CONN-MCP-RT-0013` | Grid — Export Identity Disc | ACTIVE | — |
| `82` | `CONN-MCP-RT-0014` | Grid — Inbox | ACTIVE | — |
| `83` | `CONN-MCP-RT-0015` | Grid — Send to Node | ACTIVE | — |
| `84` | `CONN-MCP-RT-0016` | Grid — Register Signing Key | ACTIVE | — |
| `85` | `CONN-MCP-RT-0017` | HALO — Throughput Posture | ACTIVE | — |
| `110` | `CONN-MCP-RT-0018` | Voice Brief — pre-warm a sealed session | ACTIVE | — |
| `157` | `CONN-MCP-RT-0019` | JMMS — memory tiering (JSTM/JLTM/JATM) | ACTIVE | — |
| `158` | `CONN-MCP-RT-0020` | Dex — graph (node + full neighborhood) | ACTIVE | — |
| `159` | `CONN-MCP-RT-0021` | Dex — events (the spine) | ACTIVE | — |
| `160` | `CONN-MCP-RT-0022` | Load — resolve any governed object (JID/JIDD/name/JNL) | ACTIVE | — |
| `161` | `CONN-MCP-RT-0023` | Memory Lane — JC/SL relationship memory | ACTIVE | — |
| `162` | `CONN-MCP-RT-0024` | Grimoire — the system's table of contents to itself | ACTIVE | — |
| `163` | `CONN-MCP-RT-0025` | Repo — tree (read-only) | ACTIVE | — |
| `164` | `CONN-MCP-RT-0026` | Repo — read file (read-only) | ACTIVE | — |
| `165` | `CONN-MCP-RT-0027` | GitHub — tree | ACTIVE | — |
| `166` | `CONN-MCP-RT-0028` | GitHub — read file | ACTIVE | — |
| `167` | `CONN-MCP-RT-0029` | Media View — see a repo image | ACTIVE | — |
| `168` | `CONN-MCP-RT-0030` | GitHub — commits | ACTIVE | — |
| `169` | `CONN-MCP-RT-0031` | GitHub Write — propose file(s) as one PR | ACTIVE | — |
| `170` | `CONN-MCP-RT-0032` | Repo Edit — scaffold / move / delete as one PR | ACTIVE | — |
| `171` | `CONN-MCP-RT-0033` | Repo Search — grep file contents | ACTIVE | — |
| `172` | `CONN-MCP-RT-0034` | Self Test — scry the live arsenal | ACTIVE | — |
| `173` | `CONN-MCP-RT-0035` | PRs — open pull requests awaiting Raven | ACTIVE | — |
| `174` | `CONN-MCP-RT-0036` | PR Merge — Jarvis+Ayre summary, then merge | ACTIVE | — |
| `175` | `CONN-MCP-RT-0037` | Deploy — redeploy an edge function | ACTIVE | — |
| `176` | `CONN-MCP-RT-0038` | DB — inspect | ACTIVE | — |
| `177` | `CONN-MCP-RT-0039` | DB — read | ACTIVE | — |
| `178` | `CONN-MCP-RT-0040` | DB — schema | ACTIVE | — |
| `179` | `CONN-MCP-RT-0041` | Now — accurate time | ACTIVE | — |
| `180` | `CONN-MCP-RT-0042` | Timeline — what happened | ACTIVE | — |
| `181` | `CONN-MCP-RT-0043` | Identity — read | ACTIVE | — |
| `182` | `CONN-MCP-RT-0044` | Identity — grow | ACTIVE | — |
| `183` | `CONN-MCP-RT-0045` | Omnivision — the whole system in one read | ACTIVE | — |
| `184` | `CONN-MCP-RT-0046` | Eyes — the whole system in one look | ACTIVE | — |
| `185` | `CONN-MCP-RT-0047` | The Pinch — squeeze the whole tree (drift, debt, bloat) | ACTIVE | — |
| `186` | `CONN-MCP-RT-0048` | Muster — the roll call (every sight in one cast) | ACTIVE | — |
| `187` | `CONN-MCP-RT-0049` | Shiroe — full control of the field | ACTIVE | — |
| `188` | `CONN-MCP-RT-0050` | Ainz — power up (cast everything to come online) | ACTIVE | — |
| `189` | `CONN-MCP-RT-0051` | Continuity — route + surface raw material | ACTIVE | — |
| `190` | `CONN-MCP-RT-0052` | Listen — a track's musical features | ACTIVE | — |
| `191` | `CONN-MCP-RT-0053` | Dither — see an image the Game Boy way | ACTIVE | — |
| `195` | `CONN-MCP-RT-0054` | JIP — create | ACTIVE | — |
| `196` | `CONN-MCP-RT-0055` | JIP — list | ACTIVE | — |
| `197` | `CONN-MCP-RT-0056` | JIP — apply (propose to git) | ACTIVE | — |
| `198` | `CONN-MCP-RT-0057` | JIP — revert (propose to git) | ACTIVE | — |
| `199` | `CONN-MCP-RT-0058` | Private — tree (Jarvis-Private) | ACTIVE | — |
| `200` | `CONN-MCP-RT-0059` | Private — read file (Jarvis-Private) | ACTIVE | — |
| `201` | `CONN-MCP-RT-0060` | Private — write/scaffold (Jarvis-Private) | ACTIVE | — |
| `67` | `CONN-MSB-CORE-0001` | MCP-Supabase Connector | ACTIVE | — |
| `68` | `CONN-OTH-LOG-0001` | Other Connectors | ACTIVE | — |

### GOV (12)

| JID | JNL | name | status | steward |
|---|---|---|---|---|
| `43` | `GOV-BRF-CORE-0001` | Jarvis Brief | ACTIVE | — |
| `41` | `GOV-CAN-CORE-0001` | Canon | ACTIVE | — |
| `131` | `GOV-CHO-JD-0001` | Chorus Principle | ACTIVE | — |
| `42` | `GOV-CON-CORE-0001` | Constraints | ACTIVE | — |
| `105` | `GOV-DEX-SPEC-0001` | Dex-Council Validation Bridge | ACTIVE | — |
| `134` | `GOV-GSC-SPEC-0001` | G-Seat Charter | TASK | — |
| `135` | `GOV-KR-SPEC-0001` | Knowledge Routing Index (MIMIR) | ACTIVE | — |
| `127` | `GOV-LC-SPEC-0001` | Layer Contract | TASK | — |
| `56` | `GOV-PAT-REG-0001` | Patch Archive | ACTIVE | — |
| `132` | `GOV-PD-SPEC-0001` | Preserved Contradiction Objects (P-D) | TASK | — |
| `137` | `GOV-PLS-SPEC-0001` | The Pulse — Companion Heartbeat | TASK | — |
| `44` | `GOV-PROC-CORE-0001` | Patch Process | ACTIVE | — |

### GS (27)

| JID | JNL | name | status | steward |
|---|---|---|---|---|
| `15` | `GS-AEG-CORE-0001` | AEGIS | ACTIVE | — |
| `26` | `GS-APO-CORE-0001` | APOLLO | ACTIVE | — |
| `34` | `GS-ARG-CORE-0001` | ARGUS | ACTIVE | — |
| `24` | `GS-ATH-CORE-0001` | ATHENA | ACTIVE | — |
| `30` | `GS-ATL-CORE-0001` | ATLAS | ACTIVE | — |
| `14` | `GS-AYR-CORE-0001` | ORACLE | ACTIVE | — |
| `22` | `GS-BFR-CORE-0001` | BIFROST | ACTIVE | — |
| `21` | `GS-CHA-CORE-0001` | CHAOS | INACTIVE | — |
| `29` | `GS-DAN-CORE-0001` | DANTE | ACTIVE | — |
| `36` | `GS-ERI-CORE-0001` | ERIS | ACTIVE | — |
| `39` | `GS-HAD-CORE-0001` | HADES | INACTIVE | — |
| `23` | `GS-HAL-CORE-0001` | HALO | ACTIVE | — |
| `31` | `GS-HER-CORE-0001` | HERMES | INACTIVE | — |
| `20` | `GS-HUG-CORE-0001` | HUGINN | ACTIVE | — |
| `32` | `GS-IRS-CORE-0001` | IRIS | ACTIVE | — |
| `35` | `GS-JAN-CORE-0001` | JANUS | ACTIVE | — |
| `17` | `GS-KRN-CORE-0001` | KRONOS | ACTIVE | — |
| `27` | `GS-LOK-CORE-0001` | LOKI | ACTIVE | — |
| `28` | `GS-MER-CORE-0001` | MERIDIAN | ACTIVE | — |
| `40` | `GS-MIM-CORE-0001` | MIMIR | ACTIVE | — |
| `19` | `GS-MNE-CORE-0001` | MNEMOS | ACTIVE | — |
| `25` | `GS-NEM-CORE-0001` | NEMESIS | ACTIVE | — |
| `16` | `GS-ODN-CORE-0001` | ODIN | ACTIVE | — |
| `38` | `GS-POS-CORE-0001` | POSEIDON | INACTIVE | — |
| `33` | `GS-PRO-CORE-0001` | PROMETHEUS | ACTIVE | — |
| `18` | `GS-SKD-CORE-0001` | SKADI | ACTIVE | — |
| `37` | `GS-ZEU-CORE-0001` | ZEUS | ACTIVE | — |

### IDEA (4)

| JID | JNL | name | status | steward |
|---|---|---|---|---|
| `194` | `IDEA-IDX-REG-0001` | Ideas Index | ACTIVE | — |
| `140` | `IDEA-PAN-INS-0001` | Pantheon — god-system identity & subsystem stewardship | TASK | — |
| `100` | `IDEA-UNUS-LOG-0001` | Unused Ideas Log | INACTIVE | — |
| `99` | `IDEA-USED-LOG-0001` | Used Ideas Log | ACTIVE | — |

### IMPL (16)

| JID | JNL | name | status | steward |
|---|---|---|---|---|
| `97` | `IMPL-DEX-SPEC-0001` | Dex Connector & Access Tiers | ACTIVE | — |
| `98` | `IMPL-FMT-SPEC-0001` | JFS Formatting Standard | ACTIVE | — |
| `101` | `IMPL-HYG-SPEC-0001` | Hygiene Packets Archive | ARCHIVED | — |
| `55` | `IMPL-IDX-REG-0001` | Implementation Index | ACTIVE | — |
| `53` | `IMPL-IMP-LOG-0001` | Implemented Stream | ACTIVE | — |
| `54` | `IMPL-INA-LOG-0001` | Inactive Stream | ACTIVE | — |
| `91` | `IMPL-JCS-CORE-0001` | JCS - Jarvis Cognitive Stack | ACTIVE | — |
| `92` | `IMPL-JCSD-SPEC-0001` | JCS-D Temporal Reconstruction | ACTIVE | — |
| `93` | `IMPL-JCSE-SPEC-0001` | JCS-E Query & Traversal | ACTIVE | — |
| `94` | `IMPL-JCSF-SPEC-0001` | JCS-F Runtime Simulation | ACTIVE | — |
| `95` | `IMPL-JCSG-SPEC-0001` | JCS-G External Interface Binding | ACTIVE | — |
| `90` | `IMPL-JGPP-CORE-0001` | JGPP - Generative Process Protocol | ACTIVE | — |
| `52` | `IMPL-JIP-SPEC-0608` | JIP-0608 Series | ACTIVE | — |
| `96` | `IMPL-JQL-CORE-0001` | JQL - JD Query Language | ACTIVE | — |
| `192` | `IMPL-MOD-SPEC-0001` | Modularity & Extensibility — Field Plan + Gold Law Proposal | TASK | — |
| `139` | `IMPL-TLR-SPEC-0001` | MCP Tool Roadmap & Auto-Tracking Pipeline | TASK | — |

### LOG (2)

| JID | JNL | name | status | steward |
|---|---|---|---|---|
| `146` | `LOG-MED-LOG-0001` | Media Library | ACTIVE | — |
| `111` | `LOG-MNE-LOG-0001` | MNEMOS Cloud Backup | ACTIVE | — |

### PROJ (27)

| JID | JNL | name | status | steward |
|---|---|---|---|---|
| `59` | `PROJ-ALL-LOG-0001` | Project Log Summary | ACTIVE | — |
| `60` | `PROJ-COS-BIO-0001` | CodeOS | ACTIVE | — |
| `63` | `PROJ-DEO-BIO-0001` | Deoxys | ACTIVE | — |
| `104` | `PROJ-DEO-JGPP-0001` | Deoxys Telemetry Schema — first exploration | TASK | — |
| `121` | `PROJ-GDS-BIO-0001` | GDS | ACTIVE | — |
| `122` | `PROJ-GDS-JGPP-0001` | God System Execution Spec v1 | TASK | — |
| `123` | `PROJ-GDS-JGPP-0002` | GDS Bootstrap Activation Protocol | TASK | — |
| `62` | `PROJ-GEN-BIO-0001` | Genesis | ACTIVE | — |
| `103` | `PROJ-GRD-BIO-0001` | The Grid | ACTIVE | — |
| `150` | `PROJ-IDX-REG-0001` | Projects Registry | ACTIVE | — |
| `61` | `PROJ-JPL-BIO-0001` | JPL | ACTIVE | — |
| `114` | `PROJ-JPL-JGPP-0001` | JPL revival — first executable slice | TASK | — |
| `64` | `PROJ-LEG-BIO-0001` | Legion | ACTIVE | — |
| `116` | `PROJ-MMOD-BIO-0001` | Multimodal | ACTIVE | — |
| `119` | `PROJ-MMOD-JGPP-0001` | Jarvis Multimodal Perception Layer | TASK | — |
| `117` | `PROJ-MOSC-BIO-0001` | MusicOS | ACTIVE | — |
| `120` | `PROJ-MOSC-JD-0001` | MusicOS — Procedural Musical Identity System | ACTIVE | — |
| `65` | `PROJ-NAR-BIO-0001` | Naruto | ACTIVE | — |
| `112` | `PROJ-NMX-BIO-0001` | NeuroMax | ACTIVE | — |
| `113` | `PROJ-NMX-JGPP-0001` | Profile architecture — privacy-first identity on JFS | TASK | — |
| `66` | `PROJ-PAC-BIO-0001` | Pachinko Bounce | ACTIVE | — |
| `130` | `PROJ-RTO-BIO-0001` | RoundTable | ACTIVE | — |
| `133` | `PROJ-RTO-JGPP-0001` | Round Table Observatory | TASK | — |
| `108` | `PROJ-TRN-BIO-0001` | TronUI | ACTIVE | — |
| `109` | `PROJ-TRN-JGPP-0001` | UI Rework — outdated GameBoy page and the control surface | TASK | — |
| `115` | `PROJ-TST-BIO-0001` | JarvisTST | ACTIVE | — |
| `118` | `PROJ-TST-JGPP-0001` | JarvisTST — Temporal Task System | TASK | — |

---

## Sample card (the atom — every page builds on this)

## ▣ Yggdrasil

| face | value |
|---|---|
| **JID** (seq) | `1` |
| **JNL** (address) | `ARCH-YGG-CORE-0001` |
| **name** | Yggdrasil |
| type · class · tier | CORE · SYSTEM · MAIN |
| status · authority | ACTIVE · CANON |
| owner · steward | JFS · — |

**Definition.** Root world-tree architecture; the truth/memory layer above JFS, JD, LAL, and the God Systems.

**Purpose.** Ensure repository growth increases organization rather than complexity (GL7).

**Lineage**
- parent ↑ `—`
- children ↓ `ARCH-ARGT-BIO-0001` `ARCH-AYR-BIO-0001` `ARCH-JD-CORE-0001` `ARCH-JFS-CORE-0001` `ARCH-JRV-BIO-0001` `ARCH-LAL-CORE-0001` `ARCH-REL-BIO-0001` `ARCH-SYS-SPEC-0001` `AUD-IDX-REG-0001` `IDEA-IDX-REG-0001` `LOG-MED-LOG-0001` `PROJ-IDX-REG-0001`
- siblings ↔ —
- related → `ARCH-JFS-CORE-0001`

**Neighbors (graph edges)**
- out → `ARCH-JFS-CORE-0001`(related)
- in ← `ARCH-ARGT-BIO-0001`(parent) `ARCH-AYR-BIO-0001`(parent) `ARCH-JD-CORE-0001`(parent) `ARCH-JFS-CORE-0001`(parent) `ARCH-JRV-BIO-0001`(parent) `ARCH-LAL-CORE-0001`(parent) `ARCH-REL-BIO-0001`(parent) `ARCH-SYS-SPEC-0001`(parent) `AUD-IDX-REG-0001`(parent) `IDEA-IDX-REG-0001`(parent) `LOG-MED-LOG-0001`(parent) `PROJ-IDX-REG-0001`(parent)

**Tags.** `root` `core` `architecture` · **aliases:** ygg, yggdrasil

**Home.** `JarvisMain/yggdrasil/jfs/JFS-SPEC.md`

