# MNEMOS — Memory System

Partitioned memory for the JARVIS companion. Modular, findable, token-cheap.

**Truth model:** JARVIS repo = software/system. Jarvis-Private = personal/canonical.

---

## Truth Model

| Content | Where | Why |
|---------|-------|-----|
| System + reader | `JARVIS/mnemos/` | Public, software |
| Technical knowledge | `JARVIS/mnemos/knowledge/` | Public, reusable |
| Personal identity | `Jarvis-Private/mnemos/` | Private, canonical |

**Personal content (Jarvis-Private):** `companion_core.md`, `knowledge/raven.md`,
`knowledge/jarvis.md`, `knowledge/relationship.md`, `knowledge/mission.md`,
`knowledge/projects/`

**Public content (this repo):** `mnemos_vector.py`, `knowledge/ml-ai.md`,
`knowledge/techniques.md`, `knowledge/governance.md`, `memories/`, `logs/`,
`context/`

---

## Where things live (this repo)

| Need | Open | What it holds |
|------|------|---------------|
| Technical ML/AI reference | `knowledge/ml-ai.md` | ML/DL concepts, embeddings, RAG, agents, tools |
| Coding patterns + GL7 | `knowledge/techniques.md` | GL7, naming, functions, git, Python, testing |
| Architecture + Gold Laws | `knowledge/governance.md` | God Systems, Gold Laws, pipeline |
| Pipeline state | `memories/` | Events, decisions, sessions, growth ledger |
| Session journals | `logs/` | Narrative records by date |
| System config | `context/` | System.json, patches.json |
| Vector reader | `mnemos_vector.py` | The memory reader tool |

## Operational ledgers

| File | What it holds |
|------|---------------|
| `memories/decisions.jsonl` | Governance-significant decisions |
| `memories/events.jsonl` | GitHub issue/PR events |
| `memories/learned.jsonl` | Insights captured by the remember loop |
| `memories/growth_ledger.json` | Per-session growth/alignment |
| `memories/recent.json` | Last 50 memories |

---

## The remember loop

```bash
python3 scripts/companion_remember.py <category> "the insight"
# categories: raven jarvis mission relationship governance session
```

Personal insights → `Jarvis-Private/mnemos/`. Technical insights → this repo.
