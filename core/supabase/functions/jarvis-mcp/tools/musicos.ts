// MusicOS — BLACKWALL privacy split.
//
// Deterministic compilation is safe and local. Durable sensory writes and stored
// observations are private/effect surfaces and require request-bound authority.

import { McpServer } from "npm:@modelcontextprotocol/sdk@1.25.3/server/mcp.js";
import { z } from "npm:zod@^4.1.13";
import { rest, text } from "../core/http.ts";

const ID = /^[A-Z0-9][A-Z0-9_.:-]{0,95}$/;
const SHA256 = /^[0-9a-f]{64}$/i;
const DEFAULT_STYLES = ["neon-race synthpop-rock", "chiptune-inflected game-score drive"];
const PHYSICS = [
  ["bounce", "elasticity"],
  ["elastic", "elasticity"],
  ["elastic", "snap-back"],
  ["race", "forward momentum"],
  ["dry drum", "subdivision precision"],
  ["syncopat", "gravity groove"],
  ["field", "shared clock"],
] as const;
const TRANSLATIONS: Record<string, string> = {
  "stewart copeland": "articulate hi-hat intelligence",
  copeland: "articulate hi-hat intelligence",
  "john bonham": "heavyweight kick-snare authority",
  bonham: "heavyweight kick-snare authority",
  "danny carey": "polyrhythmic subdivision control",
  carey: "polyrhythmic subdivision control",
  "neil peart": "precise progressive-kit articulation",
  peart: "precise progressive-kit articulation",
  "phil collins": "dramatic tom-led propulsion",
  collins: "dramatic tom-led propulsion",
  suno: "generation-ready",
};

type CompileInput = {
  intent: string;
  bpm?: number;
  key?: string;
  styles?: string[];
  instrumental?: boolean;
  rgb?: { R?: number; G?: number; B?: number };
};

function translated(value: string): string {
  let out = value.replace(/\s+/g, " ").trim()
    .replace(/\bno vocals?\b/gi, "instrumental focus")
    .replace(/\bavoid\b/gi, "favor");
  for (const [name, replacement] of Object.entries(TRANSLATIONS)) {
    out = out.replace(new RegExp(`\\b${name.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}\\b`, "gi"), replacement);
  }
  return out.replace(/[.\s]+$/, "");
}

function bounded(value: number | undefined, fallback: number): number {
  return Math.max(0, Math.min(100, Math.trunc(value ?? fallback)));
}

export function compileMusicIntent(input: CompileInput) {
  const bpm = Math.max(40, Math.min(240, Math.trunc(input.bpm ?? 102)));
  const key = translated(input.key ?? "F# minor");
  const intent = translated(input.intent);
  const styles = [...new Set((input.styles ?? []).map(translated).filter(Boolean))].slice(0, 4);
  for (const fallback of DEFAULT_STYLES) {
    if (styles.length >= 2) break;
    if (!styles.includes(fallback)) styles.push(fallback);
  }
  const lower = intent.toLowerCase();
  const physics = [...new Set(PHYSICS.filter(([token]) => lower.includes(token)).map(([, term]) => term))];
  if (!physics.length) physics.push("forward momentum", "gravity groove");
  const rgb = { R: bounded(input.rgb?.R, 50), G: bounded(input.rgb?.G, 75), B: bounded(input.rgb?.B, 50) };
  const summary = `This track conveys ${physics[0]} through ${physics[1] ?? "shared-clock repetition"} and controlled contrast`;
  const prompt = `${intent}; ${styles.join(", ")}; ${input.instrumental === false ? "voice-ready arrangement" : "instrumental focus"}; ${key}; hook-first and groove-first with a clear repeating motif, R${rgb.R} power and gravity, G${rgb.G} groove and elasticity, B${rgb.B} range and spatial clarity, ${physics.join(", ")}, tight rhythmic continuity, dry articulate drums, intelligent hi-hat motion, elastic bass snap-back, warm digital synthesis, and concise rhythm-guitar stabs. ${summary}; ${bpm} BPM.`;
  return { schema_version: "musicos.compile.v1", prompt, summary, bpm, key, styles, rgb, physics };
}

async function safeCount(table: string, field: string): Promise<number | null> {
  try {
    const rows = await rest(`${table}?select=${field}&limit=1000`);
    return Array.isArray(rows) ? rows.length : null;
  } catch {
    return null;
  }
}

function hold(tool: string, kind: "read" | "effect") {
  return text({
    ok: false,
    status: "held_by_blackwall",
    tool,
    kind,
    reason: "MUSICOS_PRIVATE_OR_EFFECT_AUTHORITY_REQUIRED",
    law: "SENSORY_OBSERVATION != PUBLIC_TELEMETRY; SERVICE_ROLE_REACH != CALLER_AUTHORITY",
    next_contract: "registerMusicOSTools(server, req) + authenticated owner/carrier scope + purpose + retention + receipt",
  });
}

export function registerMusicOSTools(server: McpServer): void {
  server.registerTool(
    "musicos_status",
    {
      title: "MusicOS — Privacy-safe status",
      description: "Show only aggregate MusicOS runtime readiness. Observation bodies, media references, interpretations, and private source paths are not projected.",
      inputSchema: {},
    },
    async () => {
      const [tracks, observations, receipts] = await Promise.all([
        safeCount("musicos_tracks", "track_id"),
        safeCount("musicos_observations", "observation_id"),
        safeCount("musicos_source_receipts", "source_path"),
      ]);
      return text({
        ok: tracks !== null && observations !== null && receipts !== null,
        schema_version: "musicos.blackwall.v1",
        privacy_mode: "PRIVATE_SENSORY_DATA_NOT_PROJECTED",
        counts: { tracks, observations, source_receipts: receipts },
        compile_surface: "public-safe deterministic transform",
        observation_surface: "authenticated private/effect lane required",
      });
    },
  );

  server.registerTool(
    "musicos_compile",
    {
      title: "MusicOS — Compile track intent",
      description: "Pure deterministic prompt compilation. Does not read or write resident data.",
      inputSchema: {
        intent: z.string().min(1).max(1600),
        bpm: z.number().int().min(40).max(240).optional(),
        key: z.string().max(40).optional(),
        styles: z.array(z.string().min(1).max(100)).min(2).max(4).optional(),
        instrumental: z.boolean().optional().default(true),
        rgb: z.object({
          R: z.number().int().min(0).max(100).optional(),
          G: z.number().int().min(0).max(100).optional(),
          B: z.number().int().min(0).max(100).optional(),
        }).optional(),
      },
    },
    async (args) => text(compileMusicIntent(args)),
  );

  server.registerTool(
    "musicos_record_observation",
    {
      title: "MusicOS — Record sensory observation (Blackwall hold)",
      description: "Durable sensory storage is held until request-bound carrier/owner authority exists.",
      inputSchema: {
        observation_id: z.string().regex(ID),
        idempotency_key: z.string().min(8).max(128),
        track_id: z.string().regex(ID),
        title: z.string().min(1).max(240),
        album_id: z.string().regex(ID).optional(),
        actor_iso: z.string().regex(ID),
        carrier: z.string().min(1).max(80),
        modality: z.enum(["audio", "image", "video", "file", "text"]),
        media_ref: z.string().max(1000).optional(),
        media_sha256: z.string().regex(SHA256).optional(),
        factual_features: z.record(z.string(), z.unknown()).default({}),
        interpretation: z.string().max(4000).optional(),
        visibility: z.enum(["GRID_REFERENCE", "OPERATOR_ONLY"]).optional().default("GRID_REFERENCE"),
        fingerprint: z.record(z.string(), z.unknown()).default({}),
        wake_channel_id: z.string().regex(ID).optional(),
        wake_from_satellite: z.string().regex(ID).optional(),
        wake_recipients: z.array(z.string().regex(ID)).min(1).max(8).optional(),
      },
    },
    async () => hold("musicos_record_observation", "effect"),
  );

  server.registerTool(
    "musicos_track",
    {
      title: "MusicOS — Retrieve track (Blackwall hold)",
      description: "Track fingerprints and attributed observations are held until authenticated data-scope enforcement exists.",
      inputSchema: { track_id: z.string().regex(ID), observation_limit: z.number().int().min(1).max(50).optional().default(12) },
    },
    async () => hold("musicos_track", "read"),
  );

  server.registerTool(
    "musicos_carrier_brief",
    {
      title: "MusicOS — Carrier brief (Blackwall hold)",
      description: "Carrier sensory context requires authenticated recipient/visibility enforcement.",
      inputSchema: { track_id: z.string().regex(ID) },
    },
    async () => hold("musicos_carrier_brief", "read"),
  );
}
