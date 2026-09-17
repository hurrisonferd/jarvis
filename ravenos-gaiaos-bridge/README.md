# RavenOS GaiaOS Bridge — deployment mirror

This public folder is the deployment-safe mirror of the canonical RavenOS-side bridge source in:

`hurrisonferd/Jarvis-Private@main:RavenOS/Bridges/GaiaOSBridge/`

It contains no Raven private continuity or private repository data. It only forwards a strict read-only allowlist to Naomi's public GaiaOS MCP carrier.

```text
RAVENOS = host / transport
GAIAOS  = Naomi-native source / council
NAOMI   = authority inside GaiaOS
```

Default upstream:

`https://gaiaos-loader-api.onrender.com/mcp`

Public bridge routes:

```text
GET  /health
GET  /gaiaos/tools
GET  /gaiaos/selftest
POST /gaiaos
POST /gaiaos/call
POST /gaiaos/dispatch
POST /gaiaos/context
```

The bridge allowlist is currently:

```text
gaia
gaia_selftest
load_gaiaos
gaia_council
gaia_dispatch
gaia_operator
gaia_brain
gaia_context
```

`POST /gaiaos` is the preferred compact front door. It asks GaiaOS itself to perform bounded context + Council routing rather than making the RavenOS host manually reproduce that logic.

No arbitrary MCP forwarding, Jarvis-Private reads, GitHub writes, or Raven identity/continuity surfaces are exposed here.
