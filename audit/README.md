# JARVIS — Audit System (P17)

Immutable audit trail for all patches, decisions, and system changes.

## Files

| File | Purpose |
|------|---------|
| `patch_ledger.json` | Canonical patch tracker P00–P31+ |
| `audit_log/` | Timestamped audit entries |

## Supabase Tables (P17)
- `audit_log` — immutable action log
- `patch_log` — patch deployment records

## GitHub Actions
- `.github/workflows/` — auto-log workflow (requires SUPABASE_SERVICE_KEY secret)

## GL9 Compliance
All entries must trace: **intent → decision → execution → log**
