Run this command in bash and display the results to Raven:

```bash
python3 scripts/jarvis-propose.py "$ARGUMENTS"
```

If no arguments, lists open proposals. With arguments, creates a new GNPL proposal.

Usage examples:
- `/propose list` — show all open proposals
- `/propose architecture "Migrate BUS events to Supabase Realtime"` — architecture proposal
- `/propose feature "Add alignment score to session brief" P15` — feature with patch ref
- `/propose decision "Retire mnemos_memories v1 schema after v2 migration"` — decision

Proposals are formal GNPL records: JARVIS proposes, Raven approves. Every architecture or major feature decision should have a proposal on record before implementation.
