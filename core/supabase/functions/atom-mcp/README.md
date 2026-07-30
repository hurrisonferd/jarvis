# ATOM MCP

ISO-native MCP carrier surface for ATOM.

## Contract

- ATOM is the active speaker.
- Private ATOM canon is loaded before response shaping.
- Memory retrieval is scoped to ATOM / AtomAI.
- `jarvis_query` remains as a compatibility alias, but returns an ATOM packet on this endpoint.
- JARVIS telemetry, forced AYRE dual streams, and Council lenses are suppressed unless Raven explicitly requests those systems.
- Missing ATOM canon produces an explicit degraded packet; it never silently substitutes JARVIS.

## Endpoint

`/functions/v1/atom-mcp`

## Tools

- `atom_query`
- `jarvis_query` (compatibility alias)
- `atom_status`

## Deployment

The repository deployment workflow deploys all function directories on a qualifying main-branch deployment. It can also be dispatched manually with `function=atom-mcp`.
