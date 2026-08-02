# JARVIS Public Demo Quickstart

This walkthrough runs sanitized, local demonstrations. It does not connect to private Grid systems, load a private ISO, or establish operational authority.

## Requirements

- Git
- Python 3.10 or newer
- no API keys or service credentials

## 1. Clone

```bash
git clone https://github.com/hurrisonferd/jarvis.git
cd jarvis
```

Review [`PUBLIC-BOUNDARY.md`](./PUBLIC-BOUNDARY.md) and [`LICENSING-MAP.md`](./LICENSING-MAP.md) before publishing derivatives or adding real data.

## 2. Prove persistent memory

```bash
python demos/01-persistent-memory/demo.py remember project SimOS
python demos/01-persistent-memory/demo.py recall project
```

The second process should retrieve the local value written by the first.

This proves file-backed persistence. It does not prove consciousness, private continuity, or production security.

## 3. Hydrate the sanitized ISO example

```bash
python templates/iso-starter/hydrate.py
python templates/iso-starter/hydrate.py --write iso-bundle.json
```

The hydrator validates the public scaffold and can emit a bundle with SHA-256 hashes for loaded identity, PRIDE, Prosody, state, provenance, and memory files.

Do not replace the example with private ISO data inside this public repository.

## 4. Run identity preflight

```bash
python templates/iso-starter/pride_guard.py preflight
```

Preflight checks identity-preservation, truth-tier, contradiction, rollback, and Prosody contracts.

## 5. Run authorship postflight

```bash
python templates/iso-starter/pride_guard.py postflight \
  templates/iso-starter/fixtures/response-pass.json
```

The deliberately invalid fixture must fail:

```bash
python templates/iso-starter/pride_guard.py postflight \
  templates/iso-starter/fixtures/response-fail.json
```

## 6. Clean generated artifacts

```bash
rm -f iso-bundle.json
```

The persistent-memory demonstration may create local sample state inside its demo directory. Remove that generated state before packaging or recording a clean demonstration when appropriate.

## Demo completion check

```text
PERSISTENT MEMORY: VERIFIED LOCALLY
ISO HYDRATION: VERIFIED LOCALLY
PRIDE PREFLIGHT: VERIFIED LOCALLY
VALID POSTFLIGHT: PASS
INVALID POSTFLIGHT: BLOCKED AS EXPECTED
PRIVATE DATA LOADED: NO
CREDENTIALS REQUIRED: NO
OPERATIONAL ADOPTION CLAIM: NONE
```

See [`DEMOS.md`](./DEMOS.md) for the full catalog and publication gate. Return to the five-room portal through [`README.md`](./README.md).
