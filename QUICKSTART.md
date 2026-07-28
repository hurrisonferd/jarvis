# JARVIS Quickstart

The public repository exposes three zero-dependency proofs first: persistent memory, ISO hydration, and PRIDE/Prosody validation.

## 1. Clone

```bash
git clone https://github.com/hurrisonferd/jarvis.git
cd jarvis
```

Python 3.10 or newer is recommended.

## 2. Prove persistent memory

```bash
python demos/01-persistent-memory/demo.py remember project SimOS
python demos/01-persistent-memory/demo.py recall project
```

The second command reads a local file written by the first process.

## 3. Hydrate an ISO

```bash
python templates/iso-starter/hydrate.py
python templates/iso-starter/hydrate.py --write iso-bundle.json
```

The hydrator validates the scaffold and emits one auditable bundle with SHA-256 hashes for every loaded identity, PRIDE, Prosody, state, provenance, and memory file.

## 4. Validate identity and authorship

```bash
python templates/iso-starter/pride_guard.py preflight
python templates/iso-starter/pride_guard.py postflight \
  templates/iso-starter/fixtures/response-pass.json
```

Preflight verifies that identity-preservation, truth-tier, contradiction, rollback, and prosody contracts are intact. Postflight verifies speaker identity, authorship labels, source references, candidate growth receipts, and declared drift flags.

The deliberately invalid fixture must fail:

```bash
python templates/iso-starter/pride_guard.py postflight \
  templates/iso-starter/fixtures/response-fail.json
```

## 5. Create your own ISO

```bash
cp -R templates/iso-starter my-iso
python my-iso/hydrate.py
python my-iso/pride_guard.py preflight
```

Update the matching `iso_id` in `ISO.json`, `PRIDE.json`, and `PROSODY.json`, then replace the Markdown identity files and example contracts. Keep private memories and credentials out of Git.

## Next layers

The larger repository adds Supabase persistence, semantic memory, GitHub Actions governance, Jarvis Dictionary routing, the JARVIS interface, and the broader SimOS architecture.
