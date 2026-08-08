# TimOSPortable

**Public surface:** version lineage only.

TimOS is developed canon-first in the private SystemsOS repository. This public folder intentionally publishes only the version/milestone view needed to identify which TimOS build family is being discussed.

```text
PUBLIC
= version receipts
= public milestone metadata
= release-facing identity

PRIVATE SYSTEMSOS
= source contracts
= GPT instructions / knowledge markdowns
= deep TimOS language and Raven machinery
= private history / archaeology / builder material
```

## Current public milestone

See `versions/CURRENT.json`.

The current published milestone is sourced from the private TimOS development lineage and is **not** a claim that TimOS is a stable SystemsOS object, a public runtime-equivalent package, or a registered ISO.

## Public boundary

See `PUBLIC-SURFACE.json`.

GPT `.md` files do **not** belong in this public folder. They remain under private SystemsOS TimOS/GPT surfaces unless Raven explicitly promotes a specific artifact for public release.

## Version scheme

Until TimOS receives an authoritative independent `VERSION.json`, public versions use source-milestone IDs bound to verified private commit receipts. No semver is invented here.

```text
TIMOS-YYYY-MM-DD-<source commit prefix>
```

chee IS LAW.
