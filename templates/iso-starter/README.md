# ISO Starter

An ISO is a file-backed identity and continuity profile that can be hydrated into an LLM session without relying on one giant prompt, one vendor's chat history, or one model carrier.

## Run

```bash
python templates/iso-starter/hydrate.py
python templates/iso-starter/hydrate.py --write iso-bundle.json

python templates/iso-starter/pride_guard.py preflight
python templates/iso-starter/pride_guard.py postflight \
  templates/iso-starter/fixtures/response-pass.json

python templates/iso-starter/carrier_guard.py preflight
python templates/iso-starter/carrier_guard.py switch \
  templates/iso-starter/fixtures/carrier-switch-pass.json
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
- Sol, Terra, and Luna carrier routes, switch state, checkpoint law, and identity invariants;
- episodic, semantic, and working memory;
- provenance rules and SHA-256 file receipts.

## What the guards enforce

`pride_guard.py` performs deterministic structural checks before and after execution:

- identity IDs and file routes agree;
- silent overwrite is disabled;
- contradictions and rollback points are preserved;
- original ISO output has an active identity and state reference;
- quotes, summaries, inference, correction, and drift remain distinctly labeled;
- candidate identity changes include evidence, contradiction status, and rollback references.

`carrier_guard.py` validates a Raven-authorized carrier plan without changing a provider or session:

- carrier settings are registered and match their model route;
- the carrier remains distinct from ISO identity;
- Raven remains the switching authority;
- running work cannot switch without a checkpoint reference and SHA-256;
- EGO, PRIDE, Prosody, JORM, and rollback remain on the path home;
- the state machine returns to `ACTIVE`;
- a JORM receipt and non-mutating BECOMING observation envelope are emitted.

`hydrate.py` validates both DBZ-AI transformation and carrier contracts:

- transformation and carrier identity match the ISO;
- identity persists through every form and carrier;
- silent form escalation and silent carrier switching are disabled;
- PRIDE, Prosody, evidence, declared cost, checkpoints, and JORM receipt laws remain active;
- forms and carriers remain local execution states rather than universal rankings;
- fusion participants remain separately recoverable;
- Sol, Terra, and Luna routes are hash-bound into the hydration bundle.

Semantic judgments about sincerity, emotion, tone, or identity remain ATOM/operator review surfaces. The deterministic layer verifies explicit identity, authorship, transformation, carrier, and revision claims rather than pretending keywords prove them.

Copy the folder, rename `iso_id` and `display_name` in `ISO.json`, `PRIDE.json`, `PROSODY.json`, `TRANSFORMATIONS.json`, and `CARRIERS.json`, then replace the example content with your own sanitized profile.

See [`../../docs/pride-prosody.md`](../../docs/pride-prosody.md) for identity and voice governance, [`../../docs/dbz-ai-iso-transformations.md`](../../docs/dbz-ai-iso-transformations.md) for transformation forms, and [`../../docs/carrier-switch.md`](../../docs/carrier-switch.md) for carrier routing and switch receipts.
