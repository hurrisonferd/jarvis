# Live Mesh Heartbeat

The first practical step toward a future JARVIS live neural mesh is an observe-only heartbeat.

Current behavior:

- observes Git repo state
- observes `memory/intake/` files
- records added, changed, and removed intake files
- records repo state changes
- writes local machine state under `%LOCALAPPDATA%\JARVIS\heartbeat`

Non-goals for this first layer:

- no autonomous pulls
- no automatic code edits
- no automatic intake processing
- no Supabase mutation
- no self-modification

This gives JARVIS a heartbeat without violating Gold Law or Raven authority. Later layers can add PROMETHEUS logging, MNEMOS memory writes, Supabase event rows, and dashboard signals after each trigger is explicit and reviewable.
