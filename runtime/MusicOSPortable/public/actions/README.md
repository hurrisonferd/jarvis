# MusicOS GPT Action Seam — v0 Spec Only

Status: NOT DEPLOYED
Effect budget: READ / COMPUTE only

The first Action backend should add determinism without adding persistence.

Candidate operations:

```text
status
compile
musicdna_validate
chaos_resolve
continuation_export
```

Do not add project writes until authentication, privacy, retention, deletion, and receipt behavior are separately approved.

`openapi.v0.yaml` deliberately uses `example.invalid`; it cannot be treated as a live deployment target.

Future sequence:

```text
READ/COMPUTE ACTIONS
→ Preview receipts
→ authentication design
→ SAVE/LOAD project gate
→ observation/persistence gate
```
