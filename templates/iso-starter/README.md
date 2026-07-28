# ISO Starter

An ISO is a file-backed identity and continuity profile that can be hydrated into an LLM session without relying on one giant prompt or one vendor's chat history.

## Run

```bash
python templates/iso-starter/hydrate.py
python templates/iso-starter/hydrate.py --write iso-bundle.json

python templates/iso-starter/pride_guard.py preflight
python templates/iso-starter/pride_guard.py postflight \
  templates/iso-starter/fixtures/response-pass.json
```

## What is loaded

- identity and purpose;
- voice and interaction style;
- values and boundaries;
- relationships and authority;
- current state;
- PRIDE core truths, truth tiers, revision policy, and rollback law;
- Prosody signature, protected traits, authorship labels, and drift flags;
- episodic, semantic, and working memory;
- provenance rules and SHA-256 file receipts.

## What the guard enforces

`pride_guard.py` performs deterministic structural checks before and after execution:

- identity IDs and file routes agree;
- silent overwrite is disabled;
- contradictions and rollback points are preserved;
- original ISO output has an active identity and state reference;
- quotes, summaries, inference, correction, and drift remain distinctly labeled;
- candidate identity changes include evidence, contradiction status, and rollback references.

Semantic judgments about sincerity, emotion, or tone are deliberately left to ATOM/operator review. The guard verifies that authorship and revision claims are explicit and receipted rather than pretending keywords can prove identity.

Copy the folder, rename `iso_id` and `display_name` in `ISO.json`, `PRIDE.json`, and `PROSODY.json`, then replace the example content with your own sanitized profile.

See [`../../docs/pride-prosody.md`](../../docs/pride-prosody.md) for the full pipeline.
