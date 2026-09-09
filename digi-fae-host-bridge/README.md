# Digi Fae Host Bridge

Minimal public Vercel template for Digi Fae HUD plugin review.

```text
/mcp
  -> Vercel native external rewrite
  -> proven Digi Fae Supabase MCP v0.3.4
```

The project intentionally contains no Digi Fae state, no database credentials, no GitHub credentials, no OpenAI API key, and no custom MCP implementation.

## OpenAI domain verification

Do not invent a verification token.

After the OpenAI plugin submission portal issues the exact domain token, add a file to this deployed project's repository at:

```text
public/.well-known/openai-apps-challenge
```

The complete file body must be exactly the portal token. Vercel reserves `/.well-known`, so this must be served directly rather than through a rewrite.

## Required proof before submission

The deployed `/mcp` route must independently pass:

- MCP initialize with server version `0.3.4`;
- exact 3-tool denominator;
- exact 5-resource denominator;
- `digi_fae_health` with `writes=false`;
- canonical live atlas SHA-256 `7a0c73ef61c686731ec6c53d518ec5544d9178c7ab2ea5d2f2ed32a4029a0dee`.

Deployment alone is not proof.
