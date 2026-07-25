# Large Chat Corpus Ingestion Standard

## Scope

A chat export measured in hundreds of megabytes is a corpus, not a conversational attachment.

For a corpus of approximately 719 MB, preservation and recovery claims must be mechanical and auditable.

## Required ingestion order

```text
1. preserve original zip/export unchanged
2. create a working copy
3. generate a manifest: file names, sizes, dates, chat titles
4. extract text/markdown/json safely
5. route each chat to project families
6. build global index
7. only then start canon distillation
```

## Required evidence

No system may claim it read, preserved, or recovered the corpus without producing:

- original archive path;
- cryptographic hash for the untouched source;
- total byte size;
- file and conversation counts;
- extraction manifest;
- parse failures and skipped items;
- chat-title/date inventory where available;
- project-family routing index;
- source-to-canon links;
- unresolved and duplicate records;
- cold-start retrieval results.

## Handling rules

- Never overwrite or modify the original export.
- Perform extraction only from a working copy.
- Record every transformation step.
- Keep raw extracted material separate from canon.
- Do not ask Raven to manually review the corpus file by file.
- Do not begin large-scale canon distillation before manifest and routing coverage exist.
- Do not use conversational assurances as evidence of corpus coverage.

## Status vocabulary

```text
archive received
→ source exists but integrity may be unverified

archive hashed
→ original identity is mechanically recorded

manifested
→ contents are inventoried

extracted
→ parseable source material is available

routed
→ chats are mapped to project families

indexed
→ source, ledger, canon, implementation, overlap, and gaps are linked

cold-start tested
→ a new session rehydrates from evidence without Raven reconstructing it

complete
→ prohibited until audit coverage and cold-start criteria pass
```

## Core rule

> At corpus scale, preservation is demonstrated by hashes, counts, manifests, indexes, and retrieval tests—not by an AI saying it read everything.
