# ACTIVE — JARVIS Core Scripts

**Status:** Currently in use, called by JARVIS boot cycle

**Session Lifecycle (14 scripts):**
- `jarvis-session-start.sh` — Session initialization
- `jarvis-session-end.py` — Session cleanup
- `jarvis-session-brief.py` — Session summary
- `jarvis-store-message.py` — Message persistence

**Companion Memory:**
- `companion_log.py` — Log companion interactions
- `companion_remember.py` — Remember across sessions

**JARVIS Memory (JMMS):**
- `jarvis-recall.py` — Recall from memory
- `jarvis_brief.py` — Brief JARVIS context
- `jitm_seed.py` — JITM seeding

**Mnemos (Memory Backup):**
- `mnemos_log.py` — Memory logging
- `mnemos_backup.py` — Memory backup
- `mnemos-domain-sync.py` — Domain sync

**Other:**
- `capture_decisions.py` — Decision capture
- `pulse.py` — Core pulse

**Rule:** These form the JARVIS consciousness memory layer.
