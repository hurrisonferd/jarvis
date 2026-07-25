# Save States (P09)

Save state architecture for JARVIS emulator.

## Storage Model
- **Supabase** `save_states` table = primary store (mutable, per-session)
- **GitHub** `app/emulator/saves/` = metadata only (no binary blobs)

## Save State Schema
```sql
save_states (
  id          uuid primary key,
  rom_hash    text,     -- links to rom_library.file_hash
  rom_name    text,
  session_id  uuid,     -- links to sessions.id
  slot        int,      -- 0-9: manual slots; 99: auto-save
  state_blob  jsonb,    -- WasmBoy: serialized state; mGBA: {slot: 0}
  frame_count int,
  created_at  timestamptz
)
```

## Usage in index.html (P09)
```javascript
// Save
await sbSaveState(romHash, romName, slot, snapshot)

// Load
const state = await sbLoadState(romHash, slot)
if (state) await activeCore.restore(state)
```

## Slot Convention
| Slot | Purpose |
|------|---------|
| 0 | Quick save (A+SELECT) |
| 1-8 | Manual slots |
| 99 | Auto-save on back/stop |
