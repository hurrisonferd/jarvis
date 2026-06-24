## Definition
A governed autonomy contract is a bounded execution scope approved by Raven once. The agent executes all actions within the scope without re-prompting. Anything that exits the scope triggers an AEGIS hold and surfaces to Raven before proceeding.

## Structure of a contract
- `scope` — explicit list of what the agent is authorized to do (file paths, operations, systems touched)
- `hard_stops` — conditions that immediately halt execution and surface to Raven (scope exits, write conflicts, missing dependencies, anything that would affect JATM or governance records)
- `completion_condition` — how the agent knows it's done (all tasks checked off, no open hard stops)
- `end_report` — what the agent writes when done (what was done, what was skipped, what needs Raven's attention)

## What is never in scope without explicit authorization
- JATM writes or promotions
- Deleting any file (archiving with a `folded` tag is permitted)
- Modifying governance specs (JMMS-SPEC, JGLF, Gold Law, keel profiles)
- Any Supabase write (MNEMOS, dex) — repo only unless explicitly authorized

## AEGIS exits
If the agent hits a hard stop, it writes a `HOLD.md` file to `JarvisMain/Implementation/task/` describing exactly what it encountered, why it stopped, and what decision is needed from Raven. Then it stops.

## Ratification
`author: RAVEN · ratified: 2026-06-24`
