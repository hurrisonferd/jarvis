# JARVIS Quickstart

The public repository exposes two zero-dependency demos first: persistent memory and ISO hydration.

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

The hydrator validates the scaffold and emits one auditable bundle with SHA-256 hashes for every loaded file.

## 4. Create your own ISO

```bash
cp -R templates/iso-starter my-iso
python my-iso/hydrate.py
```

Edit `my-iso/ISO.json` and the Markdown identity files. Keep private memories and credentials out of Git.

## Next layers

The larger repository adds Supabase persistence, semantic memory, GitHub Actions governance, the JARVIS interface, and the broader SimOS architecture.
