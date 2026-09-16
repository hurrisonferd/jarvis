/**
 * MCP session lifecycle — BLACKWALL privacy profile.
 *
 * Local request context is useful. Durable session surveillance is not required for
 * transport correctness. DB session open/pulse/close is therefore OFF by default
 * and must be explicitly enabled with MCP_SESSION_PERSISTENCE=true.
 */

import { AsyncLocalStorage } from "node:async_hooks";
import { SUPABASE_URL, SERVICE_KEY } from "./env.ts";
import { logExchange } from "./supabase.ts";

export interface SessionInfo {
  session_key: string;
  companion: string;
  started_at: string;
  exchanges: number;
  topics: string[];
}

type ActiveSession = {
  key: string;
  companion: string;
  started_at: Date;
  exchanges: number;
  topics: Set<string>;
};

const _active = new Map<string, ActiveSession>();
const MAX_LOCAL_SESSIONS = 2048;
const SESSION_PERSISTENCE =
  (Deno.env.get("MCP_SESSION_PERSISTENCE") ?? "false").toLowerCase() === "true";

export const sessionStore = new AsyncLocalStorage<SessionInfo | null>();

export function setCurrentSession(_s: SessionInfo | null): void {
  // Context is managed by sessionStore.run().
}
export function currentSession(): SessionInfo | null {
  return sessionStore.getStore() ?? null;
}

function boundedHeader(value: string | null, fallback: string, max = 128): string {
  const clean = (value ?? "").trim().replace(/[^A-Za-z0-9_.:@-]/g, "_").slice(0, max);
  return clean || fallback;
}

export function sessionKey(headers: Headers): string {
  // Caller-provided IDs are local correlation labels, not identity or authority.
  return boundedHeader(headers.get("X-Session-ID"), `local-${crypto.randomUUID()}`, 128);
}

export function sessionCompanion(headers: Headers): string {
  return boundedHeader(headers.get("X-Companion"), "Jarvis-G", 64);
}

export async function gitHead(): Promise<string | null> {
  return Deno.env.get("DEPLOY_SHA") ?? null;
}

async function rpc<T = unknown>(fn: string, params: Record<string, unknown>): Promise<T | null> {
  if (!SESSION_PERSISTENCE) return null;
  if (!SUPABASE_URL || !SERVICE_KEY) throw new Error("session persistence credential unavailable");

  const encoded: Record<string, string> = {};
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null) encoded[key] = String(value).slice(0, 512);
  }
  const body = new URLSearchParams(encoded).toString();
  const res = await fetch(`${SUPABASE_URL}/rest/v1/rpc/${fn}`, {
    method: "POST",
    headers: {
      authorization: `Bearer ${SERVICE_KEY}`,
      apikey: SERVICE_KEY,
      "content-type": "application/x-www-form-urlencoded",
      prefer: "return=minimal",
    },
    body,
  });
  if (!res.ok) throw new Error(`rpc/${fn} failed status=${res.status}`);
  const ct = res.headers.get("content-type") ?? "";
  if (!ct.includes("application/json")) return null;
  return await res.json().catch(() => null) as T | null;
}

function evictLocalIfNeeded(): void {
  while (_active.size >= MAX_LOCAL_SESSIONS) {
    const oldest = _active.keys().next().value;
    if (!oldest) break;
    _active.delete(oldest);
  }
}

async function openLocalSession(key: string, companion: string): Promise<ActiveSession> {
  let s = _active.get(key);
  if (s) return s;

  evictLocalIfNeeded();
  s = { key, companion, started_at: new Date(), exchanges: 0, topics: new Set() };
  _active.set(key, s);

  if (SESSION_PERSISTENCE) {
    const gh = await gitHead();
    try {
      await rpc("mcp_session_open", {
        p_session_key: key,
        p_companion: companion,
        p_git_head: gh ?? undefined,
      });
    } catch {
      console.error("mcp_session_open failed");
    }
  }
  return s;
}

async function pulse(s: ActiveSession, toolName: string | null): Promise<void> {
  if (!toolName) return;
  const topic = inferTopic(toolName);
  s.exchanges++;
  if (topic) s.topics.add(topic);

  if (SESSION_PERSISTENCE) {
    try {
      await rpc("mcp_session_pulse", {
        p_session_key: s.key,
        p_tool_name: toolName.slice(0, 120),
      });
    } catch {
      console.error("mcp_session_pulse failed");
    }
  }
}

function info(s: ActiveSession): SessionInfo {
  return {
    session_key: s.key,
    companion: s.companion,
    started_at: s.started_at.toISOString(),
    exchanges: s.exchanges,
    topics: [...s.topics],
  };
}

export async function getOrCreateSession(
  headers: Headers,
  toolName: string | null,
): Promise<SessionInfo> {
  const key = sessionKey(headers);
  const companion = sessionCompanion(headers);
  const isEnd = headers.get("X-Session-End")?.toLowerCase() === "true";

  if (isEnd) {
    await closeSession(key);
    return { session_key: key, companion, started_at: new Date().toISOString(), exchanges: 0, topics: [] };
  }

  const s = await openLocalSession(key, companion);
  await pulse(s, toolName);
  return info(s);
}

export async function withSession<T>(
  headers: Headers,
  toolName: string | null,
  fn: () => Promise<T>,
): Promise<T> {
  const key = sessionKey(headers);
  const companion = sessionCompanion(headers);
  const isEnd = headers.get("X-Session-End")?.toLowerCase() === "true";

  if (isEnd) {
    await closeSession(key);
    return sessionStore.run(null, fn);
  }

  const s = await openLocalSession(key, companion);
  await pulse(s, toolName);
  return sessionStore.run(info(s), fn);
}

export async function closeSession(
  key: string,
  brief?: string,
  alignment?: number,
  patches?: string[],
): Promise<void> {
  _active.delete(key);
  if (!SESSION_PERSISTENCE) return;

  try {
    await rpc("mcp_session_close", {
      p_session_key: key,
      p_brief: brief?.slice(0, 2000) ?? null,
      p_alignment: alignment ?? null,
      p_patches: patches?.slice(0, 50) ?? null,
    });
    // logExchange is independently opt-in via MCP_AUTOINGEST; both switches must
    // therefore be enabled before a session close becomes durable telemetry.
    await logExchange("mcp_session", `session_close: ${key.slice(0, 24)}`);
  } catch {
    console.error("mcp_session_close failed");
  }
}

export async function logSessionExchange(
  headers: Headers,
  exchangeType: string,
  content: string,
): Promise<void> {
  if (!SESSION_PERSISTENCE) return;
  const key = sessionKey(headers);
  await logExchange(
    `mcp:${exchangeType.slice(0, 80)}`,
    `[${key.slice(0, 12)}] ${content.slice(0, 2000)}`,
  );
}

export async function closeAllSessions(): Promise<void> {
  for (const key of [..._active.keys()]) await closeSession(key);
}

const TOPIC_MAP: Record<string, string> = {
  jarvis_query: "reasoning",
  jarvis_recall: "memory",
  jarvis_suit_up: "identity",
  jarvis_now: "telemetry",
  jarvis_council: "governance",
  jarvis_jip_get: "jip",
  jarvis_jip_list: "jip",
  jarvis_db_query: "database",
  jarvis_db_list: "database",
  jarvis_resolve: "resolution",
};

function inferTopic(toolName: string): string {
  return TOPIC_MAP[toolName] ?? "tools";
}
