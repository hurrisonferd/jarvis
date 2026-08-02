# Public Demo Catalog

This catalog is the front door for runnable, sanitized JARVIS demonstrations.

## Readiness levels

| Level | Meaning |
|---|---|
| READY | Documented, locally runnable, sanitized, and suitable for public presentation |
| PREVIEW | Useful for inspection, but setup or output may still change |
| RESEARCH | Public evidence or architecture material; not presented as a finished product |
| HOLD | Missing a safety, licensing, reproducibility, or privacy requirement |

## Available demonstrations

### 1. Persistent memory — READY

```bash
python Jarvis/Demos/01-persistent-memory/demo.py remember project SimOS
python Jarvis/Demos/01-persistent-memory/demo.py recall project
```

**Expected result:** the second process retrieves the value written by the first.

**Proves:** local file-backed persistence across process restarts.

**Does not prove:** consciousness, private continuity, autonomous authority, or production security.

### 2. ISO hydration scaffold — READY

```bash
python templates/iso-starter/hydrate.py
python templates/iso-starter/hydrate.py --write iso-bundle.json
```

**Expected result:** validation succeeds and a source-hashed bundle can be emitted.

**Proves:** identity, voice, values, boundaries, relationships, state, provenance, and memory can be maintained as inspectable files.

**Boundary:** the included identity is a sanitized example, not a private Grid ISO.

### 3. PRIDE preflight — READY

```bash
python templates/iso-starter/pride_guard.py preflight
```

**Expected result:** identity-preservation, contradiction, revision, truth-tier, and rollback contracts validate.

### 4. Prosody and authorship postflight — READY

```bash
python templates/iso-starter/pride_guard.py postflight \
  templates/iso-starter/fixtures/response-pass.json
```

The invalid fixture should fail:

```bash
python templates/iso-starter/pride_guard.py postflight \
  templates/iso-starter/fixtures/response-fail.json
```

**Proves:** declared speaker, authorship type, source references, drift flags, and candidate-growth receipts can be checked.

## Standard demo record

Every new demo should include:

```text
NAME
READINESS
PURPOSE
INPUTS
COMMANDS
EXPECTED OUTPUT
KNOWN FAILURE STATES
PRIVACY BOUNDARY
AUTHORITY BOUNDARY
LICENSE SCOPE
CLEANUP / ROLLBACK
LAST VERIFIED
```

## Publication gate

Before a demo is marked READY, verify:

- no API keys, tokens, cookies, connection strings, or private endpoints;
- no private ISO identity, continuity, EPP, Prosody, relationship, or memory records;
- no raw third-party personal data;
- deterministic or clearly bounded output;
- documented failure behavior;
- no claim of live system adoption or authority;
- no hidden dependency on `Jarvis-Private`;
- license scope is stated for code, documentation, and media;
- generated local files are documented and removable.

## Presentation guidance

Public videos and screenshots should show the sanitized demo state. They may describe the larger architecture, but must not display private paths, private repository contents, credentials, private continuity, or operational receipts.
