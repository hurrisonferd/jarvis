# Media View — see a repo image (vision)

**JNL:** CONN-MCP-RT-0029 · **Tool:** `jarvis_media_view` · **Connector:** jarvis-mcp

Fetch an image from the repo and return its pixels for a vision stream to SEE. Overrides the chat's image upload-rate cap — the bytes ride the tool call, not a manual upload.

**What it delivers:**
- Art, screenshots, spectrograms — any repo image
- Resized in-function (default 768px long side) to fit context
- JPEG output for broad model compatibility
- Captions for repo art: `JarvisSide/Media/MEDIA-MANIFEST.md`

**Common paths:**
- `JarvisSide/Media/images/` — art, screenshots, concept images
- `JarvisSide/Media/spectrograms/` — audio visualized; lets vision streams SEE music
- Any `.png`, `.jpg`, `.jpeg` in the repo

> Ground truth is the `registerTool("jarvis_media_view", ...)` block in
> `supabase/functions/jarvis-mcp/index.ts` — this file is its governed mirror (JMS).
