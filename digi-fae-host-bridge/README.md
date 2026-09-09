# Digi Fae Host Bridge

Minimal public transport-only bridge for Digi Fae HUD plugin review.

The bridge does **not** implement Digi Fae or MCP itself. It exposes one controllable public hostname whose `/mcp` path proxies to the already-proven Supabase Digi Fae MCP v0.3.4.

```text
/mcp
  -> hosting-provider native proxy/rewrite
  -> proven Digi Fae Supabase MCP v0.3.4
```

The project intentionally contains no Digi Fae private state, no database credentials, no GitHub credentials, no OpenAI API key, and no second MCP implementation.

## Preferred host: Netlify

`netlify.toml` defines a native `200` proxy rewrite:

```text
/mcp
  -> https://oexghfsvhnggddllgvrt.supabase.co/functions/v1/digi-fae-hud-mcp
```

The public template can be deployed from only this repository subdirectory:

```text
https://app.netlify.com/start/deploy?repository=https://github.com/hurrisonferd/jarvis&create_from_path=digi-fae-host-bridge
```

No environment variables or secrets are required.

## Legacy host candidate: Vercel

`vercel.json` preserves the equivalent native external rewrite for Vercel. The previously-created Vercel candidate is not the preferred path because its project is protected by Vercel Authentication and the currently connected Vercel control-plane identity does not own that project.

Do not modify the upstream Supabase MCP merely to repair a host-provider boundary.

## OpenAI domain verification

Do not invent a verification token.

OpenAI requires MCP-backed public plugins to prove control of the MCP hostname (or an allowed parent origin) when the submission portal issues a `Domain not verified` challenge.

For a Netlify deployment whose publish root is this directory, after OpenAI issues the exact token create:

```text
.well-known/openai-apps-challenge
```

The file body must be **only** the exact OpenAI portal token.

For a provider with a different publish root, place the same exact static path at that host's public root. Do not return JSON, multiple tokens, or a generated value.

## Required proof before submission

The deployed `/mcp` route must independently pass:

- MCP initialize with server version `0.3.4`;
- exact 3-tool denominator;
- exact 5-resource denominator;
- `digi_fae_health` with `writes=false`;
- live UI resource markers;
- RIFF/WEBP atlas identity;
- canonical live atlas SHA-256 `7a0c73ef61c686731ec6c53d518ec5544d9178c7ab2ea5d2f2ed32a4029a0dee`.

The host-independent canary already exists at:

```text
scripts/digi_fae_host_bridge_runtime_canary.mjs
```

Set `DIGI_FAE_BRIDGE_URL` to the deployed origin and run the canary unchanged.

Deployment alone is not proof.

## Laws

```text
BRIDGE != MCP OWNER
HOST PROVIDER != FAIRYOS OWNER
DEPLOYMENT != RUNTIME PASS
RUNTIME PASS != DOMAIN VERIFIED
DOMAIN VERIFIED != OPENAI SUBMITTED
OPENAI SUBMITTED != APPROVED
NO PRIVATE REPOSITORY READS
NO OWNER EFFECTS
RAVEN RETAINS FINAL AUTHORITY
```
