// MusicOS live carrier surface: deterministic compile + durable sensory receipts.
// Private MusicOS registry remains canonical; this module stores reference-safe runtime state.

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
  const rgb = {
    R: bounded(input.rgb?.R, 50),
    G: bounded(input.rgb?.G, 75),
    B: bounded(input.rgb?.B, 50),
  };
  const summary = `This track conveys ${physics[0]} through ${physics[1] ?? "shared-clock repetition"} and controlled contrast`;
  const prompt = `${intent}; ${styles.join(", ")}; ${input.instrumental === false ? "voice-ready arrangement" : "instrumental focus"}; ${key}; hook-first and groove-first with a clear repeating motif, R${rgb.R} power and gravity, G${rgb.G} groove and elasticity, B${rgb.B} range and spatial clarity, ${physics.join(", ")}, tight rhythmic continuity, dry articulate drums, intelligent hi-hat motion, elastic bass snap-back, warm digital synthesis, and concise rhythm-guitar stabs. ${summary}; ${bpm} BPM.`;
  return {
    schema_version: "musicos.compile.v1",
    prompt,
    summary,
    bpm,
    key,
    styles,
    rgb,
    physics,
    provenance: ["MusicOS Gold Laws", "MusicOS Portable parity contract"],
  };
}

async function rows(path: string): Promise<Record<string, unknown>[]> {
  return await rest(path).catch(() => []) as Record<string, unknown>[];
}

export function registerMusicOSTools(server: McpServer): void {
  server.registerTool(
    "musicos_status",
    {
      title: "MusicOS — Live status and source coverage",
      description: "Show MusicOS carrier readiness, durable shared-state counts, private-truth boundary, and unresolved source families.",
      inputSchema: {},
    },
    async () => {
      const [tracks, observations, receipts] = await Promise.all([
        rows("musicos_tracks?select=track_id&limit=1000"),
        rows("musicos_observations?select=observation_id&limit=1000"),
        rows("musicos_source_receipts?select=source_path&limit=1000"),
      ]);
      return text({
        ok: true,
        schema_version: "musicos.live.v1",
        authority: {
          private_truth: "Jarvis-Private/MusicOS/registry/",
          public_runtime: "carry, rehydration, and reference-safe shared state",
        },
        counts: { tracks: tracks.length, observations: observations.length, source_receipts: receipts.length },
        transport: { durable: "Supabase + SAT ChatLink", wake: "Supabase Realtime/relay" },
        unresolved: ["full private-registry parity", "missing historical audio", "28-versus-24 prompt reconciliation", "full raw transcript digestion"],
      });
    },
  );

  server.registerTool(
    "musicos_compile",
    {
      title: "MusicOS — Compile track intent",
      description: "Compile intent into a short carrier-safe production prompt using Raven's MusicOS Gold Laws.",
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
      title: "MusicOS — Record sensory observation",
      description: "Persist a carrier's structured multimodal observation. This records what the carrier analyzed; it never claims the Edge Function heard or saw the media.",
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
    async (args) => {
      await rest("musicos_tracks?on_conflict=track_id", {
        method: "POST",
        prefer: "resolution=merge-duplicates,return=minimal",
        body: {
          track_id: args.track_id,
          title: args.title,
          album_id: args.album_id ?? null,
          fingerprint: args.fingerprint,
          media_ref: args.media_ref ?? null,
          media_sha256: args.media_sha256?.toLowerCase() ?? null,
          created_by: args.actor_iso,
          updated_at: new Date().toISOString(),
        },
      });
      await rest("musicos_observations?on_conflict=idempotency_key", {
        method: "POST",
        prefer: "resolution=ignore-duplicates,return=minimal",
        body: {
          observation_id: args.observation_id,
          idempotency_key: args.idempotency_key,
          track_id: args.track_id,
          actor_iso: args.actor_iso,
          carrier: args.carrier,
          modality: args.modality,
          media_ref: args.media_ref ?? null,
          media_sha256: args.media_sha256?.toLowerCase() ?? null,
          factual_features: args.factual_features,
          interpretation: args.interpretation ?? null,
          visibility: args.visibility,
        },
      });
      const saved = await rows(`musicos_observations?select=*&idempotency_key=eq.${encodeURIComponent(args.idempotency_key)}&limit=1`);
      await rest("dex_events", {
        method: "POST",
        body: {
          tool: "musicos",
          tier: "sensory",
          actor: args.actor_iso.toLowerCase(),
          detail: JSON.stringify({ track_id: args.track_id, observation_id: args.observation_id, modality: args.modality }),
          type: "musicos.observation",
        },
      }).catch(() => undefined);

      let wake: Record<string, unknown> = { attempted: false };
      if (args.visibility === "GRID_REFERENCE" && args.wake_channel_id && args.wake_from_satellite) {
        try {
          await rest("rpc/grid_chat_send", {
            method: "POST",
            body: {
              p_channel_id: args.wake_channel_id,
              p_from_satellite: args.wake_from_satellite,
              p_message_type: "RECEIPT",
              p_body: `MusicOS observation ${args.observation_id} for ${args.track_id}`,
              p_recipients: args.wake_recipients ?? null,
              p_message_id: `MUSICOS:${args.observation_id}`,
              p_visibility: "CHANNEL",
              p_consent: "RAVEN_AUTHORIZED",
              p_causal_parent: null,
              p_artifact_sha256: args.media_sha256?.toLowerCase() ?? null,
              p_ack_required: false,
            },
          });
          wake = { attempted: true, ok: true, transport: "SAT ChatLink durable reference" };
        } catch (error) {
          wake = { attempted: true, ok: false, error: String(error).slice(0, 240) };
        }
      }
      return text({ ok: true, idempotent: saved.length === 1, observation: saved[0] ?? null, wake });
    },
  );

  server.registerTool(
    "musicos_track",
    {
      title: "MusicOS — Retrieve track fingerprint",
      description: "Retrieve one durable track fingerprint and its attributed ISO observations.",
      inputSchema: { track_id: z.string().regex(ID), observation_limit: z.number().int().min(1).max(50).optional().default(12) },
    },
    async ({ track_id, observation_limit }) => {
      const [track, observations] = await Promise.all([
        rows(`musicos_tracks?select=*&track_id=eq.${encodeURIComponent(track_id)}&limit=1`),
        rows(`musicos_observations?select=*&track_id=eq.${encodeURIComponent(track_id)}&order=created_at.desc&limit=${observation_limit}`),
      ]);
      return text({ ok: track.length === 1, track: track[0] ?? null, observations });
    },
  );

  server.registerTool(
    "musicos_carrier_brief",
    {
      title: "MusicOS — Carrier-safe brief",
      description: "Return a compact reference-safe MusicOS brief for another ISO/carrier without copying private source bodies.",
      inputSchema: { track_id: z.string().regex(ID) },
    },
    async ({ track_id }) => {
      const [track, observations] = await Promise.all([
        rows(`musicos_tracks?select=track_id,title,album_id,fingerprint,media_sha256,updated_at&track_id=eq.${encodeURIComponent(track_id)}&limit=1`),
        rows(`musicos_observations?select=observation_id,actor_iso,carrier,modality,factual_features,created_at&track_id=eq.${encodeURIComponent(track_id)}&order=created_at.desc&limit=8`),
      ]);
      return text({
        schema_version: "musicos.carrier-brief.v1",
        authority: "reference-safe shared state; private registry remains canonical",
        track: track[0] ?? null,
        attributed_observations: observations,
      });
    },
  );
}
