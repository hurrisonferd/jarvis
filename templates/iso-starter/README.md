# ISO Starter

An ISO is a file-backed identity and continuity profile that can be hydrated into an LLM session without relying on one giant prompt or one vendor's chat history.

## Run

```bash
python templates/iso-starter/hydrate.py
python templates/iso-starter/hydrate.py --write iso-bundle.json
```

## What is loaded

- identity and purpose;
- voice and interaction style;
- values and boundaries;
- relationships and authority;
- current state;
- episodic, semantic, and working memory;
- provenance rules and SHA-256 file receipts.

Copy the folder, rename `iso_id` and `display_name`, then replace the example content with your own sanitized profile.
