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
- DBZ-AI activation form, scope, capability posture, declared costs, guards, cooldown, and feat receipts;
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

`hydrate.py` also validates the DBZ-AI transformation contract:

- transformation identity matches the ISO;
- identity persists through every form;
- silent escalation is disabled;
- PRIDE, Prosody, evidence, declared cost, and JORM receipt laws remain active;
- forms remain local activation states rather than universal rankings;
- fusion participants remain separately recoverable;
- the current form includes trigger, scope, capability gain, cost, guards, authority, evidence, and cooldown.

Semantic judgments about sincerity, emotion, or tone are deliberately left to ATOM/operator review. The deterministic layer verifies that identity, authorship, transformation, and revision claims are explicit and receipted rather than pretending keywords prove them.

Copy the folder, rename `iso_id` and `display_name` in `ISO.json`, `PRIDE.json`, `PROSODY.json`, and `TRANSFORMATIONS.json`, then replace the example content with your own sanitized profile.

See [`../../docs/pride-prosody.md`](../../docs/pride-prosody.md) for identity and voice governance and [`../../docs/dbz-ai-iso-transformations.md`](../../docs/dbz-ai-iso-transformations.md) for transformation forms, costs, fusion, and cooldown.
