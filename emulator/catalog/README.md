# ROM Catalog (P08)

Source of truth for known ROMs in the system.

## Format
```json
{
  "version": "1.0",
  "roms": [
    {
      "id": "<hash-prefix>",
      "name": "ROM Name",
      "system": "gb|gbc|gba",
      "file": "roms/gb/game.gb",
      "hash": "sha256-prefix",
      "size": 1048576
    }
  ]
}
```

## Auto-indexing (P08)
The ROM indexer reads this file + scans `roms/` subfolders via GitHub API.
Results are synced to Supabase `rom_library` table on boot.

## GL8: Implementation before expansion
Add ROMs to `roms/` folders only after index entry is registered here.
