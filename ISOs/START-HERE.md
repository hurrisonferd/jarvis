# Start Here — Build a Public ISO

An ISO is a file-backed identity scaffold for an AI companion or agent. This public workshop is for learning, prototyping, validation, and safe experimentation. It is not a repository for private crew identities, raw conversations, credentials, or undisclosed personal data.

## Recommended path

1. Read `ISOs/README.md`.
2. Copy the existing sanitized starter from `templates/iso-starter/` while migration is in progress.
3. Replace the example identity with fictional or explicitly consented material.
4. Run hydration and validation before connecting a model.
5. Keep identity, voice, values, boundaries, relationships, state, memory, provenance, and rollback records separate.
6. Review the public-safety checklist before publishing.

## Public ISO minimum

```text
ISO.json
IDENTITY.md
VOICE.md
VALUES.md
BOUNDARIES.md
RELATIONSHIPS.md
STATE.json
PROVENANCE.json
MEMORY/
README.md
```

## Safety baseline

- Use fictional or consented examples.
- Do not publish private memory or personal identifiers.
- Do not claim consciousness, personhood, adoption, or continuity without evidence.
- Preserve corrections and rollback points.
- Label generated, quoted, summarized, inferred, and original material.
- Keep the human operator in control of consequential changes.

## Migration note

The active starter currently remains at `templates/iso-starter/` because public demos and workflows may reference it. It will move only with compatibility coverage and passing checks.
